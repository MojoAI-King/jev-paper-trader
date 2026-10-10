"""The funnel, bet gates, sizing, the fake-money ledgers, settlement and reporting.

Several strategies (policy.json "strategies") each trade their own fake bankroll on the same
markets. They differ in where the probability comes from (Jev with research, Jev alone, Claude directly)
and in their rules: gates, bet sizing and market filters. The learning loop tunes any strategy's rules by
itself (coach.retro, rules.json; Joey, 2026-09-28), except "original", which keeps main's starting rules
as the yardstick. Fees, the price screen, market data and settlement are the same for all and out of the
loop's reach. "main" is the headline.

The daily funnel: fetch -> free filters -> group by event -> research each event -> screen the
facts -> Jev without and with research, Claude direct -> gates and sizing per strategy -> bet.
Every stage's counts are logged to scans.jsonl.
"""
from __future__ import annotations

import gzip
import json
import math
import random
import time
from datetime import datetime, timedelta, timezone
from itertools import zip_longest
from pathlib import Path

from .jev_client import PROJECT_ROOT, JevClient, JevError

from . import learn
from . import markets as mk
from . import news
from . import odds
from .judge import QUESTION_SET_VERSION, QUESTIONS, build_state

POLICY_PATH = PROJECT_ROOT / "policy.json"
DATA = PROJECT_ROOT / "papertrade_data"
PORTFOLIO = DATA / "portfolio.json"  # v1's single ledger; moved to portfolios/main.json on first load
PORTFOLIOS = DATA / "portfolios"
JUDGMENTS = DATA / "judgments.jsonl"
RESOLUTIONS = DATA / "resolutions.json"
VOIDS = DATA / "voids.json"  # markets settled at a value, not yes/no (Kalshi "scalar"): paid out, never scored
SCANS = DATA / "scans.jsonl"
REVIEWS = DATA / "reviews.jsonl"
RESEARCH = DATA / "research.jsonl"  # one record per research run, reused for a while
SUMMARY = DATA / "summary.json"  # what the public page reads (straight from the GitHub repo)
PLAYBOOK = DATA / "playbook.json"  # research lessons learned from reviews; coach.py keeps it, research reads it
PLAYBOOK_LOG = DATA / "playbook_history.jsonl"  # every change to the playbook, with the reviews behind it
RETROS = DATA / "retros.jsonl"  # the daily reviews (weekly until 2026-09-28)
PROPOSALS = DATA / "proposals.json"  # changes the retrospectives proposed; approved challengers run from here
TUNED = DATA / "rules.json"  # each strategy's rules as the learning loop tuned them (only the changes)
ODDS = DATA / "odds.json"  # the sharp sportsbook lines, refreshed within the quota (papertrade/odds.py)
TUNED_LOG = DATA / "rules_history.jsonl"  # every rule change: what, from what to what, why, how it will be judged
SITE = PROJECT_ROOT / "site"  # the public page shell: built by `publish`, deployed to Cloudflare
MAIN = "main"
TS = "%Y-%m-%dT%H:%M:%SZ"
_clock = time.monotonic  # swapped out in tests


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime(TS)


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text())


def key(m: dict) -> str:
    return f"{m['source']}:{m['market_id']}"


def strategies(policy: dict, retired: bool = False) -> dict:
    """policy.json's strategies, plus any challenger the learning loop is running, each with the rules the
    loop has tuned (rules.json). Each has its own fake bankroll. Challengers and tuned rules are re-checked
    on every load, so a hand edit past the bounds, or to the frozen yardstick, is ignored, not traded on.
    retired=True adds the challengers that were retired (marked retired=True): they no longer bet, but
    their ledgers still settle and the page still shows their record."""
    out = {k: dict(v, rules_version=1) for k, v in policy["strategies"].items()
           if not k.startswith("_") and (retired or not v.get("retired"))}  # a retired one keeps its record
    props = load_json(PROPOSALS, {"proposals": []})["proposals"]
    for p in props:
        if (p.get("status") == "running" and p.get("strategy") and p["id"] not in out
                and learn.challenger_problem(p["strategy"], policy) is None):
            out[p["id"]] = dict(p["strategy"], challenger=True, rules_version=1, slot=p.get("slot"))
    if retired:
        for p in props:
            if (p.get("kind") == "challenger" and p.get("status") == "retired" and p.get("strategy")
                    and p.get("started") and p["id"] not in out and learn.challenger_problem(p["strategy"], policy) is None):
                out[p["id"]] = dict(p["strategy"], challenger=True, retired=True, rules_version=1)
    frozen = set(policy["learning"].get("frozen_strategies") or ())
    tuned = load_json(TUNED, {}).get("strategies")
    for name, t in (tuned.items() if isinstance(tuned, dict) else ()):
        if name not in out or name in frozen or not isinstance(t, dict) or out[name].get("retired"):
            continue
        rules, version = t.get("rules"), t.get("version")
        if (learn.rules_problem(rules, policy) is None and None not in rules.values()
                and learn.rules_problem({**strategy_rules(out[name]), **rules}, policy) is None
                and isinstance(version, int) and not isinstance(version, bool) and version > 1):
            out[name] = dict(out[name], tuned=rules, rules_version=version, tuned_at=t.get("since"))
    return out


def strategy_rules(strat: dict) -> dict:
    """Everything one strategy sets over the shared defaults: its starting overrides (policy.json, or a
    challenger's config), then what the learning loop tuned. Later wins."""
    merged = {**(strat.get("gate_overrides") or {}), **(strat.get("rules") or {}), **(strat.get("tuned") or {})}
    return {k: v for k, v in merged.items() if not k.startswith("_") and v is not None}


def strategy_policy(policy: dict, strat: dict) -> dict:
    """The policy one strategy decides with: the shared gates and sizing with that strategy's own rules on
    top, plus its market filters (learn.FILTER_RULES). Fees, slippage and the price screen are the same for
    all. A rule naming something that doesn't exist is refused, so a typo can't silently do nothing."""
    r = strategy_rules(strat)
    known = {k for k in (*policy["gates"], *policy["sizing"]) if not k.startswith("_")} | set(learn.FILTER_RULES)
    unknown = sorted(set(r) - known)
    if unknown:
        raise ValueError(f"strategy '{strat.get('label')}' sets unknown rules: {', '.join(unknown)}")
    if not r:
        return policy
    return dict(policy, gates={**policy["gates"], **{k: v for k, v in r.items() if k in policy["gates"]}},
                sizing={**policy["sizing"], **{k: v for k, v in r.items() if k in policy["sizing"]}},
                filters={k: r[k] for k in learn.FILTER_RULES if k in r})


# ---------------- storage ----------------

def load_json(path: Path, default):
    return json.loads(path.read_text()) if path.exists() else default


def save_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(obj, indent=2))
    tmp.replace(path)


def append_jsonl(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(obj) + "\n")


def _archives(path: Path) -> list[Path]:
    return sorted((path.parent / "archive").glob(f"{path.stem}-*.jsonl.gz"))


def read_jsonl(path: Path) -> list[dict]:
    """Every record, oldest first: the rotated archives (archive/<name>-<first ts>.jsonl.gz), then the file."""
    rows = []
    for part in _archives(path):
        with gzip.open(part, "rt") as f:
            rows.extend(json.loads(l) for l in f if l.strip())
    if path.exists():
        rows.extend(json.loads(l) for l in path.read_text().splitlines() if l.strip())
    return rows


def rotate_log(path: Path, max_mb: float) -> Path | None:
    """Move a log past `max_mb` into a gzipped archive and start it afresh. GitHub refuses files over
    100 MB, and the judgment log grows several MB a day; read_jsonl still reads every archive."""
    if not path.exists() or path.stat().st_size < max_mb * 1e6:
        return None
    first = json.loads(next(l for l in path.read_text().splitlines() if l.strip()))
    stamp = str(first.get("ts", now_iso())).replace("-", "").replace(":", "")
    target = path.parent / "archive" / f"{path.stem}-{stamp}.jsonl.gz"
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".tmp")
    with gzip.open(tmp, "wt") as f:
        f.write(path.read_text())
    tmp.replace(target)
    path.write_text("")
    return target


def portfolio_path(name: str) -> Path:
    return PORTFOLIOS / f"{name}.json"


def load_portfolio(policy: dict, name: str = MAIN) -> dict:
    path = portfolio_path(name)
    if name == MAIN and not path.exists() and PORTFOLIO.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        PORTFOLIO.replace(path)  # one-time move of the v1 ledger, contents untouched
    return load_json(path, {
        "created": now_iso(), "starting_bankroll": policy["starting_bankroll"],
        "cash": float(policy["starting_bankroll"]), "open": [], "closed": [],
    })


def save_portfolio(name: str, pf: dict) -> None:
    save_json(portfolio_path(name), pf)


def load_books(policy: dict) -> dict:
    return {name: load_portfolio(policy, name) for name in strategies(policy)}


def all_books(policy: dict) -> dict:
    """Every ledger, including challengers that have stopped running: their open bets still settle."""
    books = {name: load_portfolio(policy, name) for name in strategies(policy, retired=True)}
    for path in sorted(PORTFOLIOS.glob("*.json")) if PORTFOLIOS.exists() else ():
        if path.stem not in books:
            books[path.stem] = load_json(path, None)
    return books


def equity_at_cost(pf: dict) -> float:
    return pf["cash"] + sum(p["total_cost"] for p in pf["open"])


# ---------------- decision logic (pure) ----------------

def fee_per_contract(source: str, price: float, policy: dict, market: dict | None = None) -> float:
    """The taker fee per contract at `price`. Kalshi: 0.07 x the series' fee multiplier x p x (1 - p) (a
    market saved without one pays the full rate). Polymarket: the market's own
    published rate x p x (1 - p) (`fee_rate`, read from its feeSchedule); a market that doesn't publish one,
    such as one saved before 2026-10-09, pays the usual rate (`fees.polymarket_default_rate`)."""
    f = policy["fees"]
    if source == "kalshi":
        mult = (market or {}).get("fee_multiplier")  # the series' published multiplier (MLB games 0.5, a few 0)
        return f["kalshi_taker_coef"] * (1.0 if mult is None else mult) * price * (1 - price)
    rate = (market or {}).get("fee_rate")
    if rate is None:
        rate = f["polymarket_default_rate"]
    return rate * price * (1 - price)


def decide(market: dict, answers: dict, policy: dict, equity: float, open_cost: float,
           cash: float, sizing: dict | None = None) -> dict:
    """Gates, then the stake. `sizing` (from skill_sizing) sizes by the forecaster's measured skill: Kelly on a
    forecast shrunk toward the market by its λ, or a small probe stake while λ is 0, with one stake budget per
    event (docs/REBUILD_PLAN.md phase 1). None keeps the sizing used before 2026-10-09, which the frozen
    yardstick `original` still bets with."""
    g, s = policy["gates"], policy["sizing"]
    p = float(answers["p_yes"]["noul"])
    rules_clear = float(answers["rules_clear"]["noul"])
    info_ok = float(answers["info_sufficient"]["noul"])
    reasons = []

    sides = []
    for side, q, ask in (("yes", p, market["yes_ask"]), ("no", 1 - p, market["no_ask"])):
        cost = ask + fee_per_contract(market["source"], ask, policy, market) + policy["fees"]["slippage"]
        sides.append({"side": side, "q": q, "ask": ask, "cost": round(cost, 4),
                      "edge": round(q - cost, 4)})
    best = max(sides, key=lambda x: x["edge"])
    out = {"bet": False, "cleared_gates": False, **best, "p_yes": p, "rules_clear": rules_clear,
           "info_sufficient": info_ok, "min_edge": g["min_edge"], "reasons": reasons}

    if best["edge"] < g["min_edge"]:
        reasons.append(f"edge {best['edge']:+.3f} < {g['min_edge']}")
    if rules_clear < g["min_rules_clear"]:
        reasons.append(f"rules_clear {rules_clear:.2f} < {g['min_rules_clear']}")
    if info_ok < g["min_info_sufficient"]:
        reasons.append(f"needs recent info ({info_ok:.2f} < {g['min_info_sufficient']})")
    f = policy.get("filters") or {}
    if f.get("skip_categories"):
        cat = learn.category(market)
        if cat in f["skip_categories"]:
            reasons.append(f"skips {cat} markets")
    if f.get("min_ask") is not None and best["ask"] < f["min_ask"]:
        reasons.append(f"skips prices under {f['min_ask']:.2f} (ask {best['ask']:.2f})")
    if f.get("max_ask") is not None and best["ask"] > f["max_ask"]:
        reasons.append(f"skips prices over {f['max_ask']:.2f} (ask {best['ask']:.2f})")
    if answers.get("p_no") is not None:
        # Asked both ways, a consistent answer has p_yes + p_no near 1. A big gap means Jev is unsure of itself.
        gap = abs(p + float(answers["p_no"]["noul"]) - 1)
        out["framing_gap"] = round(gap, 4)
        if gap > g["max_framing_gap"]:
            reasons.append(f"YES/NO answers disagree (gap {gap:.2f} > {g['max_framing_gap']})")
    if sizing is not None and not real_price(market):
        reasons.append(f"no real price (spread {market['yes_ask'] + market['no_ask'] - 1:.2f} > {PAIRED_MAX_SPREAD})")
    if reasons:
        return out
    out["cleared_gates"] = True
    if sizing is not None:
        return _size_by_skill(out, market, policy, equity, open_cost, cash, sizing)

    c = best["cost"]
    kelly = (best["q"] - c) / (1 - c) if c < 1 else 0.0
    room = max(0.0, s["max_total_exposure_pct"] * equity - open_cost)
    stake = min(s["kelly_fraction"] * kelly * equity, s["max_stake_pct"] * equity, room, cash)
    contracts = math.floor(stake / c) if c > 0 else 0
    if contracts < 1:
        reasons.append("no room: " + ("open-bet limit reached" if room < c else "out of cash" if cash < c
                                      else "stake under one contract (Kelly fraction or max bet too small)"))
        return out
    out.update(bet=True, contracts=contracts, total_cost=round(contracts * c, 2),
               kelly=round(kelly, 4))
    reasons.append(f"BET {best['side'].upper()} x{contracts} @ {c:.3f}: p {best['q']:.2f} "
                   f"vs cost {c:.3f}, edge {best['edge']:+.3f}")
    return out


def _size_by_skill(out: dict, market: dict, policy: dict, equity: float, open_cost: float, cash: float,
                   sizing: dict) -> dict:
    """Report 12 (docs/research/12-bet-sizing.md). The forecast is shrunk toward the market's mid by the
    forecaster's measured λ: q_s = m + λ(q − m). Kelly on q_s, scaled down as equity nears 70% of its peak.
    While λ is 0 (no measured edge, which is every forecaster on 2026-10-09) or Kelly on q_s is not positive, a
    probe stake instead: small, at most `skill.max_probes_per_day` a day, so the page keeps trading and real
    costs keep being measured. All open bets in one event share one `max_stake_pct` budget."""
    s, k, reasons = policy["sizing"], policy["skill"], out["reasons"]
    c, q = out["cost"], out["q"]
    m = market["mid"] if out["side"] == "yes" else 1 - market["mid"]
    lam = sizing["lambda"]
    q_s = m + lam * (q - m)
    kelly = (q_s - c) / (1 - c) if c < 1 else 0.0
    out.update(**{"lambda": lam, "q_shrunk": round(q_s, 4)})
    group_room = max(0.0, s["max_stake_pct"] * equity - sizing["event_cost"])
    room = max(0.0, s["max_total_exposure_pct"] * equity - open_cost)
    if lam > 0 and kelly > 0:
        floor = k["drawdown_floor"]
        cushion = max(0.0, equity - floor * sizing["peak"]) / (1 - floor)
        stake, mode = min(s["kelly_fraction"] * kelly * cushion, s["max_stake_pct"] * equity, group_room, room, cash), "kelly"
    else:
        if sizing["probes_today"] >= k["max_probes_per_day"]:
            reasons.append(f"probe limit reached ({k['max_probes_per_day']} today; no measured edge yet)")
            return out
        stake, mode = min(k["probe_stake_pct"] * equity, group_room, room, cash), "probe"
    contracts = math.floor(stake / c) if c > 0 else 0
    if contracts < 1:
        reasons.append("no room: " + ("this event already has a full stake" if group_room < c else
                                      "open-bet limit reached" if room < c else "out of cash" if cash < c
                                      else "drawdown cushion used up" if mode == "kelly" else "stake under one contract"))
        return out
    out.update(bet=True, contracts=contracts, total_cost=round(contracts * c, 2), kelly=round(kelly, 4),
               sizing=mode, probe=mode == "probe")
    reasons.append(f"{'PROBE' if mode == 'probe' else 'BET'} {out['side'].upper()} x{contracts} @ {c:.3f}: p {q:.2f} "
                   f"(shrunk {q_s:.2f}, lambda {lam:.2f}) vs cost {c:.3f}, edge {out['edge']:+.3f}")
    return out


def skill_sizing(pf: dict, m: dict, lam: float, stamp: str, event_of: dict) -> dict:
    """What `_size_by_skill` needs from a strategy's book: its peak equity (kept on the book), the cost already
    open in this market's event, and how many probes it placed today."""
    eq = equity_at_cost(pf)
    pf["peak_equity"] = round(max(pf.get("peak_equity", pf["starting_bankroll"]), eq), 2)
    ev = m.get("event")
    return {"lambda": lam, "peak": pf["peak_equity"],
            "event_cost": sum(x["total_cost"] for x in pf["open"] if ev and (x.get("event") or event_of.get(x["key"])) == ev),
            "probes_today": sum(1 for x in pf["open"] + pf["closed"] if x.get("probe") and x["opened"][:10] == stamp[:10])}


def strategy_answers(strategy: dict, signals: dict) -> dict | None:
    """Probability from one source, eligibility gates from another (they are the same for Jev strategies)."""
    prob, gates = signals.get(strategy["probability"]), signals.get(strategy["gates"])
    if prob is None or gates is None:
        return None
    answers = dict(gates, p_yes=prob["p_yes"])
    if strategy["probability"] != strategy["gates"]:
        answers.pop("p_no", None)  # the YES/NO consistency check belongs to the source that answered both
    return answers


def passes_free_filters(m: dict, mf: dict, now: datetime) -> str | None:
    """Reason a market fails the free filters, or None. Re-checked here before any paid research."""
    if not (mf["min_price"] <= m["mid"] <= mf["max_price"]):
        return "price"
    if (m.get("volume") or 0) < mf["min_volume"]:
        return "volume"
    try:
        ct = datetime.fromisoformat(str(m["close_time"]).replace("Z", "+00:00"))
    except ValueError:
        return "close date"
    if ct.tzinfo is None:
        ct = ct.replace(tzinfo=timezone.utc)
    if not (now + timedelta(hours=12) <= event_time(m) <= ct <= now + timedelta(days=mf["days_ahead"])):
        return "close date"
    starts = _when(m.get("starts"))
    if starts and starts < now + timedelta(hours=mf.get("min_hours_before_start", 1)):
        return "started"  # a match under way or over: its price may already know what the forecasters don't
    return None


def _when(v) -> datetime | None:
    try:
        d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def event_time(m: dict) -> datetime:
    """When the market's event is decided: the earlier of its close and, on Kalshi, its expected expiration
    (a Kalshi game's close_time falls a median 1.9 days after the game). The 12-hour rule uses this, so
    no bet is placed on an event that is under way or over."""
    times = [d for d in (_when(m.get("close_time")), _when(m.get("expected_expiration"))) if d]
    return min(times) if times else datetime.max.replace(tzinfo=timezone.utc)


def soonest(m: dict) -> datetime:
    """The earliest thing known about when a market plays out: its event time or, for a match, its start."""
    return min(d for d in (event_time(m), _when(m.get("starts"))) if d)


# ---------------- scan: the funnel ----------------

def last_judged() -> dict:
    """key -> (time of the latest judgment, the market's mid price then, the strategies that decided on it)."""
    out = {}
    for j in read_jsonl(JUDGMENTS):
        out[j["key"]] = (j.get("ts", ""), j.get("market", {}).get("mid"), frozenset(j.get("decisions") or ()))
    return out


def due(m: dict, seen: dict, cutoff: str, move: float, names=()) -> bool:
    """Judge again when it's never been judged, the last judgment is old, the price has moved, or a
    strategy in `names` has never decided on it (a newly added strategy gets a first look next cycle).

    The price only decides *when* to look again; no forecaster ever sees it.
    """
    ts, mid, decided = seen.get(key(m), ("", None, frozenset()))
    return (ts < cutoff or (mid is not None and abs(float(m["mid"]) - float(mid)) >= move)
            or not set(names) <= decided)


def _interleave(lists: list[list]) -> list:
    return [m for group in zip_longest(*lists) for m in group if m is not None]


def latest_research() -> dict:
    """event -> its most recent research record (research is reused for a while, not redone hourly)."""
    out = {}
    for r in read_jsonl(RESEARCH):
        out[r["event"]] = r
    return out


def research_count(day: str) -> int:
    return sum(1 for r in read_jsonl(RESEARCH) if str(r.get("ts", "")).startswith(day))


def last_claude_rate(now: datetime) -> dict | None:
    """The plan usage Claude reported on the last call, with windows that have since reset dropped."""
    rate = None
    for s in read_jsonl(SCANS):
        if (s.get("claude") or {}).get("rate"):
            rate = s["claude"]["rate"]
    if not rate:
        return None
    windows = {k: v for k, v in (rate.get("unifiedWindows") or {}).items()
               if (v or {}).get("resetsAt", 0) > now.timestamp()}
    return dict(rate, unifiedWindows=windows)


PROBE_HOURS = 2


def probe_due(now: datetime) -> bool:
    """True when no cycle in the last PROBE_HOURS sent a probe call past a stored busy reading."""
    cutoff = (now - timedelta(hours=PROBE_HOURS)).strftime(TS)
    return not any((s.get("claude") or {}).get("probe") and s.get("ts", "") > cutoff for s in read_jsonl(SCANS))


def _bet(name: str, pf: dict, m: dict, d: dict, stamp: str, log, rules_version: int = 1) -> None:
    pf["cash"] = round(pf["cash"] - d["total_cost"], 2)
    pf["open"].append({
        "key": key(m), "source": m["source"], "market_id": m["market_id"],
        "question": m["question"], "url": m["url"], "close_time": m["close_time"],
        "side": d["side"], "contracts": d["contracts"], "cost_per": d["cost"],
        "total_cost": d["total_cost"], "p_side": round(d["q"], 4),
        "market_ask": d["ask"], "edge": d["edge"], "opened": stamp,
        "question_set": QUESTION_SET_VERSION, "rules_version": rules_version,
        "event": m.get("event"), "sizing": d.get("sizing") or "kelly (old rules)",
        "probe": bool(d.get("probe")), "lambda": d.get("lambda"),
    })
    save_portfolio(name, pf)  # saved per bet, so an interrupted run can't lose one
    log(f"+ [{name}] {'probe ' if d.get('probe') else ''}{d['side'].upper():3} ${d['total_cost']:>8,.2f}  edge {d['edge']:+.2f}  "
        f"[{m['source']}] {m['question'][:60]}")


def scan(policy: dict, client: JevClient | None = None, fetchers=None, log=print, claude=None,
         researcher=None, forecaster=None, limit: int | None = None, now: datetime | None = None) -> dict:
    """One pass of the funnel. Jev judges every due market (pennies); Claude researches only where it
    can change a bet, rationed so it never crowds out Joey's own use of the Claude plan."""
    fetchers = fetchers or mk.FETCHERS
    client = client or JevClient(model=policy["model"])
    now = now or datetime.now(timezone.utc)
    started = _clock()
    for path in (JUDGMENTS, RESEARCH):
        rotate_log(path, policy.get("storage", {}).get("rotate_logs_mb", 20))
    today, stamp = now.strftime("%Y-%m-%d"), now.strftime(TS)  # one clock for filtering and logging
    mf, rc, strats = policy["market_filters"], policy["research"], strategies(policy)
    spolicy = {name: strategy_policy(policy, s) for name, s in strats.items()}  # fails fast on a bad override
    books = load_books(policy)
    playbook = load_json(PLAYBOOK, {"version": 0, "rules": []})
    cmap = learn.calibration_map(read_jsonl(REVIEWS), policy["learning"])
    waiting = {"jev_calibrated": f"still learning: calibrates once {cmap['need']} researched markets have "
                                 f"resolved ({cmap['n']} so far)"}
    seen = last_judged()
    cutoff = (now - timedelta(hours=mf["rejudge_after_hours"])).strftime(TS)
    funnel = {"fetched": 0, "passed_filters": 0, "judged": 0, "events": 0, "researched_new": 0,
              "research_reused": 0, "with_research": 0,
              "cleared_gates": {s: 0 for s in strats}, "bets": {s: 0 for s in strats}}
    cl = {"calls": 0, "limited": False, "rate": None, "api_equivalent_usd": 0.0, "note": None}
    stats = {"funnel": funnel, "claude": cl, "errors": 0, "facts_kept": 0, "facts_dropped": 0, "deferred": 0,
             "problems": []}
    # each forecaster's measured skill sizes the bets (docs/REBUILD_PLAN.md phase 1); the frozen yardstick keeps
    # the old sizing
    judged_before = read_jsonl(JUDGMENTS)
    skills = skill(judged_before, load_json(RESOLUTIONS, {}), policy["skill"]["min_markets"])
    event_of = {j["key"]: j["event"] for j in judged_before if j.get("event")}
    del judged_before
    stats["skill"] = skills
    frozen = set(policy["learning"].get("frozen_strategies") or ())

    def warn(msg: str) -> None:  # printed, and kept with the scan so the health check and the page can show it
        stats["problems"].append(msg[2:302])
        log(msg)

    # 1-2. fetch, then the free filters; only markets due for a look
    per_source = []
    keep = lambda m: passes_free_filters(m, mf, now) is None  # the free filters, before the top-N cut
    for src in policy["sources"]:
        mk.LAST_FETCH.pop(src, None)
        try:
            ms = fetchers[src](mf["days_ahead"], mf["min_volume"], mf["markets_per_source"], keep)
        except Exception as e:  # one broken source shouldn't stop the other
            warn(f"! {src}: could not fetch markets ({e})")
            stats["errors"] += 1
            continue
        fetch = mk.LAST_FETCH.get(src)
        if fetch:
            funnel.setdefault("fetch", {})[src] = fetch
            if fetch.get("error"):
                warn(f"! {src}: fetch stopped after {fetch['pages']} pages ({fetch['error']}); kept what it had")
            if fetch.get("cut_short"):
                warn(f"! {src}: fetch hit its page limit after {fetch['pages']} pages; far-dated markets left out")
        funnel["fetched"] += len(ms)
        funnel.setdefault("by_source", {})[src] = len(ms)
        per_source.append([m for m in ms if due(m, seen, cutoff, mf["rejudge_on_price_move"], strats)
                           and passes_free_filters(m, mf, now) is None])
    candidates = [dict(m, category=learn.category(m)) for m in _interleave(per_source)]
    candidates.sort(key=lambda m: seen.get(key(m), ("",))[0])  # never judged first, then judged longest ago
    funnel["passed_filters"] = len(candidates)
    todo = candidates[: policy["max_jev_calls_per_scan"] // 2]  # up to two Jev calls per market
    stats["deferred"] = len(candidates) - len(todo)
    mk.add_kalshi_fees(todo)  # each series' published fee multiplier, for the markets about to be judged
    sharp = {}  # market key -> Pinnacle's fair price for that outcome (papertrade/odds.py); never shown to a forecaster
    if any(s["probability"] == "sharp" for s in strats.values()):
        okey = odds.api_key()
        if okey:
            cache = odds.load_events(policy["sharp"], okey, load_json(ODDS, {}), now, warn=warn)
            save_json(ODDS, cache)
            sharp = odds.match(odds.all_events(cache), todo, policy["sharp"], now)
            stats["sharp"] = {"games": len(odds.all_events(cache)), "matched": len(sharp),
                              "quota_left": odds.LAST.get("remaining")}
            waiting["sharp"] = "no sharp line matched this market"
        else:
            waiting["sharp"] = "waiting for an ODDS_API_KEY (The Odds API) to be set"

    # 3. Jev without research, for every market: this is also the "Jev alone" strategy
    plain = {}
    for m in todo:
        try:
            plain[key(m)] = client.ask(build_state(m, today), QUESTIONS)
        except JevError as e:
            warn(f"! Jev error on {m['question'][:60]}: {e}")
            stats["errors"] += 1
    events = {}
    for m in todo:
        if key(m) in plain:
            events.setdefault(m.get("event") or key(m), []).append(m)
    funnel["events"] = len(events)

    # 4. which events get research: reuse a recent one, research anew (rationed), or skip
    cache, fresh_cut = latest_research(), (now - timedelta(hours=rc["research_after_hours"])).strftime(TS)
    reuse, need, why_not = {}, [], {}
    for ek, ms in events.items():
        c = cache.get(ek)
        moved = c is not None and any(abs(m["mid"] - c["mids"].get(key(m), m["mid"])) >= rc["research_on_price_move"]
                                      for m in ms)
        if c and c["ts"] >= fresh_cut and not moved:
            reuse[ek] = c
        elif any(plain[key(m)]["answers"]["rules_clear"]["noul"] >= rc["triage_min_rules_clear"] for m in ms):
            need.append(ek)  # research can only unlock a bet where the rules are clear
        else:
            why_not[ek] = "rules unclear to Jev, so not researched"
    used = research_count(today)
    allowed = rc["max_research_per_day"] - used
    if rc.get("pace_through_day"):
        # spread the day's research over the UTC day, so it never runs out by morning (it did at 5 AM ET)
        hours = now.hour + now.minute / 60
        allowed = min(allowed, math.ceil(rc["max_research_per_day"] * (hours + 1) / 24) - used)
    budget = min(rc["max_research_per_cycle"], max(0, allowed))
    if rc.get("order") == "soonest":  # results come back soonest, so the learning loop hears back sooner
        need.sort(key=lambda ek: min(soonest(m) for m in events[ek]))
    if limit is not None:
        budget = min(budget, limit)
    for ek in need[budget:]:
        why_not[ek] = "research cap reached; picked up in a later cycle"
    need = need[:budget]

    fresh = {}
    if need:
        try:
            if claude is None and (researcher is None or forecaster is None):
                claude = news.ClaudeCode(rc)
            researcher = researcher or news.Researcher(rc, claude)
            forecaster = forecaster or news.DirectForecaster(rc, claude)
            if claude is not None:
                claude.last_rate = claude.last_rate or last_claude_rate(now)
                if claude.last_rate and not claude.usage_ok() and probe_due(now):
                    # The busy reading is from an earlier cycle, maybe another account (Joey swapped the token
                    # on 2026-10-01 and research stayed off until the old account's week would have reset).
                    # One call this cycle gets a fresh reading; at most one probe every PROBE_HOURS.
                    claude.last_rate = None
                    cl["probe"] = True
        except news.NewsError as e:
            warn(f"! research unavailable this cycle: {e}")
            stats["errors"] += 1
            cl["note"] = str(e)
            for ek in need:
                why_not[ek] = f"research unavailable: {e}"
            need = []
    # Claude calls stop starting once the cycle has used its research time, so a run of stalled calls can't
    # push the job past GitHub's 55-minute limit (which would throw the whole cycle away)
    out_of_time = lambda: _clock() - started > rc.get("max_minutes_per_cycle", 25) * 60
    failed_in_a_row = 0
    for i, ek in enumerate(need):
        if out_of_time() or failed_in_a_row >= 2:
            why_not[ek] = ("research time for this cycle used up" if failed_in_a_row < 2 else
                           "research failing this cycle") + "; picked up in a later cycle"
            continue
        if claude is not None and not claude.usage_ok():
            cl["limited"] = True
            why_not[ek] = "Claude plan busy (our share is used); research resumes when it frees up"
            continue
        lessons = learn.lessons_for(playbook, events[ek][0]["category"])
        try:
            r = researcher.research(events[ek], today, lessons=lessons)
            cl["calls"] += 1
            cl["api_equivalent_usd"] += r["meta"].get("api_equivalent_usd", 0.0)
        except news.NewsError as e:
            cl["calls"] += 1
            cl["api_equivalent_usd"] += e.meta.get("api_equivalent_usd", 0.0)
            cl["limited"] = cl["limited"] or e.limited
            why_not[ek] = "Claude plan busy; research resumes when it frees up" if e.limited else f"research failed: {e}"
            if not e.limited:
                stats["errors"] += 1
                failed_in_a_row += 1
                warn(f"! research failed for {events[ek][0]['question'][:60]}: {e}")
            if e.fatal:
                for rest in need[i + 1:]:
                    why_not.setdefault(rest, why_not[ek])
                break
            continue
        rec = {"ts": stamp, "id": f"{ek}@{stamp}", "event": ek, "keys": [key(m) for m in events[ek]],
               "mids": {key(m): m["mid"] for m in events[ek]}, "raw_facts": r["raw_facts"],
               "source_urls": r["source_urls"], "meta": r["meta"],
               "playbook_version": playbook.get("version", 0), "lessons": [x["id"] for x in lessons]}
        append_jsonl(RESEARCH, rec)
        fresh[ek] = rec
        failed_in_a_row = 0
    funnel["researched_new"], funnel["research_reused"] = len(fresh), len(reuse)

    # 5-6. judge with research where there is some, then each strategy decides
    for ek, ms in events.items():
        rec = fresh.get(ek) or reuse.get(ek)
        facts = dropped = None
        if rec:
            # Screened against the prices of right now, not the prices when the research was done.
            facts, dropped = news.screen_facts(rec["raw_facts"], ms, today, rec["source_urls"], rc["max_facts_per_event"])
            stats["facts_kept"] += len(facts)
            stats["facts_dropped"] += len(dropped)
        for m in ms:
            p = plain[key(m)]
            rich = direct = state = None
            if rec:
                state = build_state(m, today, recent_facts=facts)
                try:
                    rich = client.ask(state, QUESTIONS)
                except JevError as e:
                    warn(f"! Jev error on {m['question'][:60]}: {e}")
                    stats["errors"] += 1
                if (rich and ek in fresh and forecaster is not None and not out_of_time()
                        and (claude is None or claude.usage_ok())):
                    try:
                        direct = forecaster.forecast(state)
                        cl["calls"] += 1
                        cl["api_equivalent_usd"] += direct["meta"].get("api_equivalent_usd", 0.0)
                    except news.NewsError as e:
                        cl["calls"] += 1
                        cl["limited"] = cl["limited"] or e.limited
                        if not e.limited:
                            stats["errors"] += 1
                            warn(f"! Claude direct failed on {m['question'][:60]}: {e}")
            funnel["judged"] += 1
            funnel["with_research"] += int(rich is not None)
            calibrated = (learn.apply_map(cmap, float(rich["answers"]["p_yes"]["noul"]))
                          if rich and cmap["active"] else None)
            line = sharp.get(key(m))
            signals = {"jev_plain": p["answers"], "jev_research": rich["answers"] if rich else None,
                       "claude_direct": {"p_yes": {"noul": direct["p_yes"]}} if direct else None,
                       "jev_calibrated": {"p_yes": {"noul": calibrated}} if calibrated is not None else None,
                       # a price-based forecast: the rules are a game's result and the line is the information
                       "sharp": {"p_yes": {"noul": line["p_yes"]}, "rules_clear": {"noul": 1.0},
                                 "info_sufficient": {"noul": 1.0}} if line else None}
            decisions = {}
            for name, strat in strats.items():
                pf = books[name]
                answers = strategy_answers(strat, signals)
                if answers is None:
                    why = (waiting.get("sharp") if strat["probability"] == "sharp" else
                           why_not.get(ek) if rich is None else waiting.get(strat["probability"]))
                    decisions[name] = {"bet": False, "cleared_gates": False,
                                       "reasons": [why or "no probability this cycle"]}
                    continue
                if key(m) in {x["key"] for x in pf["open"]}:
                    decisions[name] = {"bet": False, "cleared_gates": False, "reasons": ["already holding this market"]}
                    continue
                open_cost = sum(x["total_cost"] for x in pf["open"])
                sz = None if name in frozen else skill_sizing(
                    pf, m, skills.get(strat["probability"], {}).get("lambda", 0.0), stamp, event_of)
                d = decide(m, answers, spolicy[name], equity_at_cost(pf), open_cost, pf["cash"], sz)
                decisions[name] = d
                funnel["cleared_gates"][name] += int(d["cleared_gates"])
                if d["bet"]:
                    _bet(name, pf, m, d, stamp, log, strat["rules_version"])
                    funnel["bets"][name] += 1
            append_jsonl(JUDGMENTS, {
                "ts": stamp, "key": key(m), "event": ek, "question_set": QUESTION_SET_VERSION,
                "model": p["model"], "market": m,
                "recent_facts": state["recent_facts"] if state else None,
                "fact_urls": [f["url"] for f in facts] if facts is not None else None,
                "facts_dropped": dropped,
                "research": {"id": rec["id"], "fresh": ek in fresh, "done_at": rec["ts"],
                             "playbook": rec.get("playbook_version", 0)} if rec else None,
                "answers": rich["answers"] if rich else None, "answers_no_news": p["answers"],
                "claude_direct": {"p_yes": direct["p_yes"], **direct["meta"]} if direct else None,
                "jev_calibrated": calibrated,
                "sharp": line,
                "calibration_map": {k: cmap[k] for k in ("a", "b", "n")} if calibrated is not None else None,
                "decision": decisions.get(MAIN), "decisions": decisions,
                "latency_ms": rich["latency_ms"] if rich else None, "latency_ms_no_news": p["latency_ms"],
            })
    for name, pf in books.items():
        save_portfolio(name, pf)
    if claude is not None and claude.last_rate:
        r = claude.last_rate
        cl["rate"] = {"status": r.get("status"), "unifiedWindows": r.get("unifiedWindows") or {}}
    cl["api_equivalent_usd"] = round(cl["api_equivalent_usd"], 4)
    _record_scan(stats, stamp)
    return stats


def _record_scan(stats: dict, stamp: str) -> None:
    append_jsonl(SCANS, {"ts": stamp, "question_set": QUESTION_SET_VERSION, **stats})


# ---------------- settle ----------------

def settle(policy: dict, resolvers=None, log=print, batch=None) -> dict:
    """Record outcomes and pay out bets. `batch` sources (Kalshi) are checked every cycle whatever the
    stored close time; the rest once their close time has passed. A market settled at a value instead of
    yes/no goes to voids.json: its bets are paid at that value, and it is never scored."""
    if batch is None:
        batch = mk.BATCH_RESOLVERS if resolvers is None else {}
    resolvers = resolvers or mk.RESOLVERS
    books = all_books(policy)
    resolved, voids = load_json(RESOLUTIONS, {}), load_json(VOIDS, {})
    now = datetime.now(timezone.utc)

    closes = {}
    for pf in books.values():
        for p in pf["open"]:
            closes[p["key"]] = p["close_time"]
    for j in read_jsonl(JUDGMENTS):
        closes.setdefault(j["key"], j["market"]["close_time"])
        starts = _when(j["market"].get("starts"))
        if starts:  # a match: check a few hours after it starts, not a week later at the listed close
            after = (starts + timedelta(hours=policy["market_filters"].get("check_hours_after_start", 3))).strftime(TS)
            closes[j["key"]] = min(closes[j["key"]], after)

    stats = {"checked": 0, "resolved": 0, "voided": 0, "settled_bets": 0, "by_strategy": {}}
    pending = sorted(set(closes) - set(resolved) - set(voids))
    for src, check in batch.items():
        ids = [k.split(":", 1)[1] for k in pending if k.startswith(src + ":")]
        if not ids:
            continue
        try:
            found = check(ids)
        except Exception as e:
            log(f"! could not check {src} results: {e}")
            continue
        for err in (mk.LAST_FETCH.get(f"{src}_check") or {}).get("errors") or []:
            log(f"! {src} results: one batch failed ({err}); checked again next cycle")
        stats["checked"] += len(ids)
        for mid, outcome in found.items():
            k = f"{src}:{mid}"
            if isinstance(outcome, tuple) and outcome[0] == "void":
                voids[k] = outcome[1]
                stats["voided"] += 1
            elif outcome in ("yes", "no"):
                resolved[k] = outcome
                stats["resolved"] += 1
    for k in sorted(set(closes) - set(resolved) - set(voids)):
        if k.split(":", 1)[0] in batch:
            continue  # checked above, every cycle
        ct = closes.get(k)
        try:
            if ct and datetime.fromisoformat(ct.replace("Z", "+00:00")) > now:
                continue  # not closed yet
        except ValueError:
            pass
        src, mid = k.split(":", 1)
        stats["checked"] += 1
        try:
            outcome = resolvers[src](mid)
        except Exception as e:
            log(f"! could not check {k}: {e}")
            continue
        if outcome:
            resolved[k] = outcome
            stats["resolved"] += 1

    for name, pf in books.items():
        still_open, n = [], 0
        for p in pf["open"]:
            outcome = resolved.get(p["key"])
            if p["key"] in voids:  # settled at a value: YES is paid the value per contract, NO the rest
                value = float(voids[p["key"]])
                outcome, payout = "void", round(float(p["contracts"]) * (value if p["side"] == "yes" else 1 - value), 2)
            elif outcome:
                payout = float(p["contracts"]) if p["side"] == outcome else 0.0
            else:
                still_open.append(p)
                continue
            pnl = round(payout - p["total_cost"], 2)
            pf["cash"] = round(pf["cash"] + payout, 2)
            pf["closed"].append({**p, "outcome": outcome, "payout": payout, "pnl": pnl, "settled": now_iso()})
            n += 1
            log(f"{'WIN ' if pnl > 0 else 'LOSS'} [{name}] {pnl:+10,.2f}  {p['question'][:60]}")
        pf["open"] = still_open
        save_portfolio(name, pf)
        stats["by_strategy"][name] = n
        stats["settled_bets"] += n
    save_json(RESOLUTIONS, resolved)
    if voids:
        save_json(VOIDS, voids)
    return stats


# ---------------- report ----------------

def brier(pairs):
    return sum((p - y) ** 2 for p, y in pairs) / len(pairs) if pairs else None


SOURCES = [("jev_research", "Jev + research"), ("jev_plain", "Jev alone"),
           ("claude_direct", "Claude direct"), ("jev_calibrated", "Jev + research, calibrated"),
           ("market", "Market price")]


def _prob(j: dict, source: str):
    if source == "jev_research":
        a = j.get("answers")
        return float(a["p_yes"]["noul"]) if a else None
    if source == "jev_plain":
        a = j.get("answers_no_news")
        return float(a["p_yes"]["noul"]) if a else None
    if source == "claude_direct":
        c = j.get("claude_direct")
        return float(c["p_yes"]) if c else None
    if source == "jev_calibrated":
        c = j.get("jev_calibrated")
        return float(c) if c is not None else None
    if source == "sharp":
        c = j.get("sharp")
        return float(c["p_yes"]) if c else None
    return float(j["market"]["mid"])


def calibration(judgments: list[dict], resolved: dict) -> dict:
    """Brier score per forecast source on resolved markets (latest judgment, current question set).

    Shared by the text report and the dashboard so both show the same numbers.
    """
    latest = {}
    for j in judgments:
        if j.get("question_set") == QUESTION_SET_VERSION:
            latest[j["key"]] = j  # last judgment per market
    done = [(j, 1.0 if resolved[k] == "yes" else 0.0) for k, j in latest.items() if k in resolved]
    sources = []
    for name, label in SOURCES:
        pairs = [(p, y) for j, y in done if (p := _prob(j, name)) is not None]
        sources.append({"name": name, "label": label, "brier": brier(pairs), "n": len(pairs)})
    return {"judged": len(latest), "resolved": len(done), "sources": sources, "paired": paired(judgments, resolved)}


PAIRED = ("market", "jev_research", "claude_direct", "jev_plain")
# A look counts only if the market had a real two-sided price: yes ask + no ask - 1 at most this. Where nobody
# bids, the mid is a number nobody can trade at, not the market's forecast, and it made the market look bad
# (BACKLOG B25; docs/research/CHECKS.md).
PAIRED_MAX_SPREAD = 0.10


def real_price(m: dict) -> bool:
    ya, na = m.get("yes_ask"), m.get("no_ask")
    return ya is not None and na is not None and ya + na - 1 <= PAIRED_MAX_SPREAD


def paired(judgments: list[dict], resolved: dict) -> dict:
    """Each source in PAIRED scored on the same resolved markets: per market, the latest look (current
    question set) where all of them gave a forecast and the market had a real price. The per-source scores
    above each use whatever markets that source happened to cover, so they can't be compared head to head
    (proposal p7, Joey 2026-10-02). `left_out` counts markets whose every such look lacked a real price."""
    looks, wide = {}, set()
    for j in judgments:
        if (j.get("question_set") == QUESTION_SET_VERSION and j["key"] in resolved
                and all(_prob(j, s) is not None for s in PAIRED)):
            if real_price(j["market"]):
                looks[j["key"]] = j
            else:
                wide.add(j["key"])
    labels = dict(SOURCES)
    sources = [{"name": s, "label": labels[s],
                "brier": brier([(_prob(j, s), 1.0 if resolved[k] == "yes" else 0.0) for k, j in looks.items()])}
               for s in PAIRED]
    return {"n": len(looks), "left_out": len(wide - looks.keys()), "sources": sources}


SKILL_SOURCES = ("jev_plain", "jev_research", "claude_direct", "jev_calibrated", "sharp")


def skill(judgments: list[dict], resolved: dict, min_markets: int = 300, boot: int = 200) -> dict:
    """Each forecaster's measured edge over the market price, λ (report 12, docs/REBUILD_PLAN.md phase 1).

    For each source, on resolved markets at its first look that carries the source's forecast and a real price
    (current question set): λ̂ = Σ(y − m)(q − m) / Σ(q − m)², the share of the forecast's distance from the
    mid that came true. It is shrunk for noise, λ = λ̂·λ̂² / (λ̂² + se²) capped at 1, with se from a bootstrap
    that resamples whole events (markets in one event resolve together). λ is 0 below `min_markets` or when
    λ̂ ≤ 0. On 2026-10-09 every source measured about 0 (docs/research/CHECKS.md)."""
    first: dict[str, dict] = {s: {} for s in SKILL_SOURCES}
    for j in judgments:
        k = j.get("key")
        if j.get("question_set") != QUESTION_SET_VERSION or k not in resolved or resolved[k] not in ("yes", "no"):
            continue
        m = j.get("market") or {}
        if m.get("mid") is None or not real_price(m):
            continue
        for s in SKILL_SOURCES:
            if k not in first[s] and (q := _prob(j, s)) is not None:
                first[s][k] = (1.0 if resolved[k] == "yes" else 0.0, float(m["mid"]), q, m.get("event") or k)
    out = {}
    for s in SKILL_SOURCES:
        rows = list(first[s].values())
        lam_of = lambda rs: (sum((y - m) * (q - m) for y, m, q, _ in rs) / den
                             if (den := sum((q - m) ** 2 for _, m, q, _ in rs)) > 0 else 0.0)
        raw, se = (lam_of(rows) if rows else 0.0), 0.0
        if len(rows) >= min_markets and raw > 0:
            groups: dict = {}
            for r in rows:
                groups.setdefault(r[3], []).append(r)
            keys, rnd = list(groups), random.Random(7)
            draws = [lam_of([r for g in (rnd.choice(keys) for _ in keys) for r in groups[g]]) for _ in range(boot)]
            mean = sum(draws) / len(draws)
            se = (sum((d - mean) ** 2 for d in draws) / (len(draws) - 1)) ** 0.5
        lam = min(1.0, raw * raw * raw / (raw * raw + se * se)) if len(rows) >= min_markets and raw > 0 else 0.0
        out[s] = {"lambda": round(lam, 4), "raw": round(raw, 4), "se": round(se, 4), "n": len(rows)}
    return out


def report(policy: dict) -> str:
    books = load_books(policy)
    pf = books[MAIN]
    start = pf["starting_bankroll"]
    open_cost = sum(p["total_cost"] for p in pf["open"])
    realized = sum(p["pnl"] for p in pf["closed"])
    wins = sum(1 for p in pf["closed"] if p["pnl"] > 0)
    eq = equity_at_cost(pf)
    lines = [
        f"Main fake bankroll: ${start:,.0f} start  ->  ${eq:,.2f} now (open bets valued at cost)",
        f"Cash ${pf['cash']:,.2f}   Open bets {len(pf['open'])} (${open_cost:,.2f} at risk)",
        f"Settled {len(pf['closed'])}: {wins} won / {len(pf['closed']) - wins} lost   "
        f"Realized P&L {realized:+,.2f}"
        + (f"   ROI on settled stakes {realized / sum(p['total_cost'] for p in pf['closed']):+.1%}"
           if pf["closed"] else ""),
        "\nStrategies (each its own fake bankroll, same markets and gates):",
    ]
    for name, strat in strategies(policy).items():
        b = books[name]
        e, r = equity_at_cost(b), sum(p["pnl"] for p in b["closed"])
        lines.append(f"  {strat['label']:<24} ${e:>12,.2f}  P&L {r:+10,.2f}  open {len(b['open']):>3}  "
                     f"settled {len(b['closed']):>3}")

    cal = calibration(read_jsonl(JUDGMENTS), load_json(RESOLUTIONS, {}))
    lines.append(f"\nMarkets judged: {cal['judged']}   resolved so far: {cal['resolved']}")
    scored = [s for s in cal["sources"] if s["brier"] is not None]
    if scored:
        lines.append("Brier score (lower is better):")
        for s in scored:
            lines.append(f"  {s['label']:<16} {s['brier']:.4f}   (n={s['n']})")
        by = {s["name"]: s["brier"] for s in scored}
        if "jev_research" in by and "market" in by:
            lines.append("  -> " + ("Jev with research is beating the market's own forecast so far."
                                    if by["jev_research"] < by["market"] else
                                    "The market is still the better forecaster; edges are likely noise."))
        if cal["resolved"] < 50:
            lines.append(f"  (only {cal['resolved']} resolved markets; treat as noise until ~50+)")
        pr = cal["paired"]
        if pr["n"]:
            lines.append(f"Head to head, the same {pr['n']} resolved markets with a real price "
                         f"({pr['left_out']} without one left out):")
            for s in sorted(pr["sources"], key=lambda s: s["brier"]):
                lines.append(f"  {s['label']:<16} {s['brier']:.4f}")
    else:
        lines.append("No judged markets have resolved yet. Run `settle` after markets close.")

    if pf["open"]:
        lines.append("\nMain portfolio open bets:")
        for p in sorted(pf["open"], key=lambda p: p["close_time"] or ""):
            lines.append(f"  {p['side'].upper():3} ${p['total_cost']:>8,.2f}  p {p['p_side']:.2f} vs "
                         f"{p['market_ask']:.2f}  closes {str(p['close_time'])[:10]}  {p['question'][:60]}")
    return "\n".join(lines)

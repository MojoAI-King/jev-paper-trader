"""The funnel, bet gates, sizing, the fake-money ledgers, settlement and reporting.

Several strategies (policy.json "strategies") each trade their own fake bankroll on the same
markets, with the same gates and sizing. They differ only in where the probability comes from:
Jev with research, Jev alone, or Claude directly. "main" is the pre-registered headline.

The daily funnel: fetch -> free filters -> group by event -> research each event -> screen the
facts -> Jev without and with research, Claude direct -> gates and sizing per strategy -> bet.
Every stage's counts are logged to scans.jsonl.
"""
from __future__ import annotations

import json
import math
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from itertools import zip_longest
from pathlib import Path

from .jev_client import PROJECT_ROOT, JevClient, JevError

from . import markets as mk
from . import news
from .judge import QUESTION_SET_VERSION, QUESTIONS, build_state

POLICY_PATH = PROJECT_ROOT / "policy.json"
DATA = PROJECT_ROOT / "papertrade_data"
PORTFOLIO = DATA / "portfolio.json"  # v1's single ledger; moved to portfolios/main.json on first load
PORTFOLIOS = DATA / "portfolios"
JUDGMENTS = DATA / "judgments.jsonl"
RESOLUTIONS = DATA / "resolutions.json"
SCANS = DATA / "scans.jsonl"
REVIEWS = DATA / "reviews.jsonl"
SITE = PROJECT_ROOT / "site"  # the public page: built by `publish`, deployed to Cloudflare
MAIN = "main"
TS = "%Y-%m-%dT%H:%M:%SZ"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime(TS)


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text())


def key(m: dict) -> str:
    return f"{m['source']}:{m['market_id']}"


def strategies(policy: dict) -> dict:
    return {k: v for k, v in policy["strategies"].items() if not k.startswith("_")}


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


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


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


def equity_at_cost(pf: dict) -> float:
    return pf["cash"] + sum(p["total_cost"] for p in pf["open"])


# ---------------- decision logic (pure) ----------------

def fee_per_contract(source: str, price: float, policy: dict) -> float:
    f = policy["fees"]
    if source == "kalshi":
        return f["kalshi_taker_coef"] * price * (1 - price)
    return f["polymarket_per_contract"]


def decide(market: dict, answers: dict, policy: dict, equity: float, open_cost: float,
           cash: float) -> dict:
    g, s = policy["gates"], policy["sizing"]
    p = float(answers["p_yes"]["noul"])
    rules_clear = float(answers["rules_clear"]["noul"])
    info_ok = float(answers["info_sufficient"]["noul"])
    reasons = []

    sides = []
    for side, q, ask in (("yes", p, market["yes_ask"]), ("no", 1 - p, market["no_ask"])):
        cost = ask + fee_per_contract(market["source"], ask, policy) + policy["fees"]["slippage"]
        sides.append({"side": side, "q": q, "ask": ask, "cost": round(cost, 4),
                      "edge": round(q - cost, 4)})
    best = max(sides, key=lambda x: x["edge"])
    out = {"bet": False, "cleared_gates": False, **best, "p_yes": p, "rules_clear": rules_clear,
           "info_sufficient": info_ok, "reasons": reasons}

    if best["edge"] < g["min_edge"]:
        reasons.append(f"edge {best['edge']:+.3f} < {g['min_edge']}")
    if rules_clear < g["min_rules_clear"]:
        reasons.append(f"rules_clear {rules_clear:.2f} < {g['min_rules_clear']}")
    if info_ok < g["min_info_sufficient"]:
        reasons.append(f"needs recent info ({info_ok:.2f} < {g['min_info_sufficient']})")
    if answers.get("p_no") is not None:
        # Asked both ways, a consistent answer has p_yes + p_no near 1. A big gap means Jev is unsure of itself.
        gap = abs(p + float(answers["p_no"]["noul"]) - 1)
        out["framing_gap"] = round(gap, 4)
        if gap > g["max_framing_gap"]:
            reasons.append(f"YES/NO answers disagree (gap {gap:.2f} > {g['max_framing_gap']})")
    if reasons:
        return out
    out["cleared_gates"] = True

    c = best["cost"]
    kelly = (best["q"] - c) / (1 - c) if c < 1 else 0.0
    room = max(0.0, s["max_total_exposure_pct"] * equity - open_cost)
    stake = min(s["kelly_fraction"] * kelly * equity, s["max_stake_pct"] * equity, room, cash)
    contracts = math.floor(stake / c) if c > 0 else 0
    if contracts < 1:
        reasons.append("no room: exposure cap or cash")
        return out
    out.update(bet=True, contracts=contracts, total_cost=round(contracts * c, 2),
               kelly=round(kelly, 4))
    reasons.append(f"BET {best['side'].upper()} x{contracts} @ {c:.3f}: p {best['q']:.2f} "
                   f"vs cost {c:.3f}, edge {best['edge']:+.3f}")
    return out


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
    if not (now + timedelta(hours=12) <= ct <= now + timedelta(days=mf["days_ahead"])):
        return "close date"
    return None


# ---------------- scan: the funnel ----------------

def last_judged() -> dict:
    """key -> (time of the latest judgment, the market's mid price then)."""
    out = {}
    for j in read_jsonl(JUDGMENTS):
        out[j["key"]] = (j.get("ts", ""), j.get("market", {}).get("mid"))
    return out


def due(m: dict, seen: dict, cutoff: str, move: float) -> bool:
    """Judge again when it's never been judged, the last judgment is old, or the price has moved.

    The price only decides *when* to look again; no forecaster ever sees it.
    """
    ts, mid = seen.get(key(m), ("", None))
    return ts < cutoff or (mid is not None and abs(float(m["mid"]) - float(mid)) >= move)


def spent_today(day: str) -> float:
    return sum(s.get("research_usd", 0.0) + s.get("forecast_usd", 0.0) + s.get("review_usd", 0.0)
               for s in read_jsonl(SCANS) if str(s.get("ts", "")).startswith(day))


def _interleave(lists: list[list]) -> list:
    return [m for group in zip_longest(*lists) for m in group if m is not None]


def _research_events(researcher, chosen, today, rc, log, stats) -> dict:
    """Research events a few at a time; stop starting new calls at the dollar ceiling or a fatal error."""
    out, conc, fatal = {}, max(1, int(rc.get("concurrency", 1))), False
    for i in range(0, len(chosen), conc):
        if fatal:
            break
        if stats["research_usd"] + stats["forecast_usd"] >= rc["max_usd_per_scan"]:
            log(f"! spend reached max_usd_per_scan (${rc['max_usd_per_scan']}); "
                f"{len(chosen) - i} events wait for the next run")
            break
        batch = chosen[i:i + conc]
        with ThreadPoolExecutor(max_workers=conc) as pool:
            futures = [(ek, ms, pool.submit(researcher.research, ms, today)) for ek, ms in batch]
        for ek, ms, fut in futures:
            try:
                r = fut.result()
            except news.NewsError as e:
                stats["research_usd"] += e.meta.get("cost_usd", 0.0)
                stats["errors"] += 1
                fatal = fatal or e.fatal
                log(f"! research failed for {ms[0]['question'][:60]}: {e}")
                continue
            stats["research_usd"] += r["meta"]["cost_usd"]
            out[ek] = r
    return out


def scan(policy: dict, client: JevClient | None = None, fetchers=None, log=print, researcher=None,
         forecaster=None, limit: int | None = None, now: datetime | None = None) -> dict:
    fetchers = fetchers or mk.FETCHERS
    client = client or JevClient(model=policy["model"])
    now = now or datetime.now(timezone.utc)
    today, stamp = now.strftime("%Y-%m-%d"), now.strftime(TS)  # one clock for filtering and logging
    mf, rc, strats = policy["market_filters"], policy["research"], strategies(policy)
    books = load_books(policy)
    seen = last_judged()
    cutoff = (now - timedelta(hours=mf["rejudge_after_hours"])).strftime(TS)
    funnel = {"fetched": 0, "passed_filters": 0, "events": 0, "researched": 0, "judged": 0,
              "cleared_gates": {s: 0 for s in strats}, "bets": {s: 0 for s in strats}}
    stats = {"funnel": funnel, "errors": 0, "research_usd": 0.0, "forecast_usd": 0.0,
             "facts_kept": 0, "facts_dropped": 0, "deferred": 0}

    # 1-2. fetch, then the free filters (and skip anything judged in the last 24h)
    per_source = []
    for src in policy["sources"]:
        try:
            ms = fetchers[src](mf["days_ahead"], mf["min_volume"], mf["markets_per_source"])
        except Exception as e:  # one broken source shouldn't stop the other
            log(f"! {src}: could not fetch markets ({e})")
            stats["errors"] += 1
            continue
        funnel["fetched"] += len(ms)
        per_source.append([m for m in ms if due(m, seen, cutoff, mf["rejudge_on_price_move"])
                           and passes_free_filters(m, mf, now) is None])
    candidates = _interleave(per_source)
    candidates.sort(key=lambda m: seen.get(key(m), ("",))[0])  # never judged first, then judged longest ago
    funnel["passed_filters"] = len(candidates)

    # 3. group by event; bounded by the Jev-call limit (2 calls per market) and a runaway guard
    events = {}
    for m in candidates:
        events.setdefault(m.get("event") or key(m), []).append(m)
    max_markets = policy["max_jev_calls_per_scan"] // 2
    max_events = rc["max_events_per_scan"] if limit is None else min(limit, rc["max_events_per_scan"])
    chosen, n = [], 0
    for ek, ms in events.items():
        if len(chosen) >= max_events:
            break
        if n + len(ms) <= max_markets:
            chosen.append((ek, ms))
            n += len(ms)
    stats["deferred"] = len(candidates) - n

    if chosen and spent_today(today) >= rc["max_usd_per_day"]:
        log(f"! today's spend already reached max_usd_per_day (${rc['max_usd_per_day']}); judging nothing this run")
        stats["deferred"] = len(candidates)
        _record_scan(stats, stamp)
        return stats

    if chosen and (researcher is None or forecaster is None):
        try:
            cc = news.ClaudeClient(rc["model"])
            researcher = researcher or news.Researcher(rc, cc)
            forecaster = forecaster or news.DirectForecaster(rc, cc)
        except news.NewsError as e:
            log(f"! research unavailable, judging nothing this run: {e}")
            stats["errors"] += 1
            stats["deferred"] = len(candidates)
            _record_scan(stats, stamp)
            return stats

    # 4. research each event
    results = _research_events(researcher, chosen, today, rc, log, stats)
    funnel["events"] = len(results)  # events actually researched, not just planned

    # 5-6. screen, judge three ways, decide per strategy
    for ek, ms in chosen:
        r = results.get(ek)
        if r is None:
            continue  # no research, no judgment: the market waits for the next run
        funnel["researched"] += len(ms)
        facts, dropped = news.screen_facts(r["raw_facts"], ms, today, r["source_urls"], rc["max_facts_per_event"])
        stats["facts_kept"] += len(facts)
        stats["facts_dropped"] += len(dropped)
        share = round(r["meta"]["cost_usd"] / len(ms), 5)
        for m in ms:
            state = build_state(m, today, recent_facts=facts)
            try:
                plain = client.ask(build_state(m, today), QUESTIONS)
                rich = client.ask(state, QUESTIONS)
            except JevError as e:
                log(f"! Jev error on {m['question'][:60]}: {e}")
                stats["errors"] += 1
                continue
            direct = None
            if stats["research_usd"] + stats["forecast_usd"] < rc["max_usd_per_scan"]:
                try:
                    direct = forecaster.forecast(state)
                    stats["forecast_usd"] += direct["meta"]["cost_usd"]
                except news.NewsError as e:
                    stats["forecast_usd"] += e.meta.get("cost_usd", 0.0)
                    stats["errors"] += 1
                    log(f"! Claude direct failed on {m['question'][:60]}: {e}")
            funnel["judged"] += 1
            signals = {"jev_research": rich["answers"], "jev_plain": plain["answers"],
                       "claude_direct": {"p_yes": {"noul": direct["p_yes"]}} if direct else None}
            decisions = {}
            for name, strat in strats.items():
                pf = books[name]
                answers = strategy_answers(strat, signals)
                if answers is None:
                    decisions[name] = {"bet": False, "cleared_gates": False, "reasons": ["no probability this run"]}
                    continue
                if key(m) in {p["key"] for p in pf["open"]}:
                    decisions[name] = {"bet": False, "cleared_gates": False, "reasons": ["already holding this market"]}
                    continue
                open_cost = sum(p["total_cost"] for p in pf["open"])
                d = decide(m, answers, policy, equity_at_cost(pf), open_cost, pf["cash"])
                decisions[name] = d
                funnel["cleared_gates"][name] += int(d["cleared_gates"])
                if d["bet"]:
                    pf["cash"] = round(pf["cash"] - d["total_cost"], 2)
                    pf["open"].append({
                        "key": key(m), "source": m["source"], "market_id": m["market_id"],
                        "question": m["question"], "url": m["url"], "close_time": m["close_time"],
                        "side": d["side"], "contracts": d["contracts"], "cost_per": d["cost"],
                        "total_cost": d["total_cost"], "p_side": round(d["q"], 4),
                        "market_ask": d["ask"], "edge": d["edge"], "opened": stamp,
                        "question_set": QUESTION_SET_VERSION,
                    })
                    save_portfolio(name, pf)  # saved per bet, so an interrupted run can't lose one
                    funnel["bets"][name] += 1
                    log(f"+ [{name}] {d['side'].upper():3} ${d['total_cost']:>8,.2f}  edge {d['edge']:+.2f}  "
                        f"[{m['source']}] {m['question'][:60]}")
            append_jsonl(JUDGMENTS, {
                "ts": stamp, "key": key(m), "event": ek, "question_set": QUESTION_SET_VERSION,
                "model": rich["model"], "market": m,
                "recent_facts": state["recent_facts"], "fact_urls": [f["url"] for f in facts],
                "facts_dropped": dropped, "research": dict(r["meta"], cost_share_usd=share),
                "answers": rich["answers"], "answers_no_news": plain["answers"],
                "claude_direct": {"p_yes": direct["p_yes"], **direct["meta"]} if direct else None,
                "decision": decisions.get(MAIN), "decisions": decisions,
                "latency_ms": rich["latency_ms"], "latency_ms_no_news": plain["latency_ms"],
            })
    for name, pf in books.items():
        save_portfolio(name, pf)
    stats["research_usd"] = round(stats["research_usd"], 4)
    stats["forecast_usd"] = round(stats["forecast_usd"], 4)
    _record_scan(stats, stamp)
    return stats


def _record_scan(stats: dict, stamp: str) -> None:
    append_jsonl(SCANS, {"ts": stamp, "question_set": QUESTION_SET_VERSION, **stats})


# ---------------- settle ----------------

def settle(policy: dict, resolvers=None, log=print) -> dict:
    resolvers = resolvers or mk.RESOLVERS
    books = load_books(policy)
    resolved = load_json(RESOLUTIONS, {})
    now = datetime.now(timezone.utc)

    closes = {}
    for pf in books.values():
        for p in pf["open"]:
            closes[p["key"]] = p["close_time"]
    for j in read_jsonl(JUDGMENTS):
        closes.setdefault(j["key"], j["market"]["close_time"])

    stats = {"checked": 0, "resolved": 0, "settled_bets": 0, "by_strategy": {}}
    for k in sorted(set(closes) - set(resolved)):
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
            if not outcome:
                still_open.append(p)
                continue
            payout = float(p["contracts"]) if p["side"] == outcome else 0.0
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
    return stats


# ---------------- report ----------------

def brier(pairs):
    return sum((p - y) ** 2 for p, y in pairs) / len(pairs) if pairs else None


SOURCES = [("jev_research", "Jev + research"), ("jev_plain", "Jev alone"),
           ("claude_direct", "Claude direct"), ("market", "Market price")]


def _prob(j: dict, source: str):
    if source == "jev_research":
        return float(j["answers"]["p_yes"]["noul"])
    if source == "jev_plain":
        a = j.get("answers_no_news")
        return float(a["p_yes"]["noul"]) if a else None
    if source == "claude_direct":
        c = j.get("claude_direct")
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
    return {"judged": len(latest), "resolved": len(done), "sources": sources}


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
    else:
        lines.append("No judged markets have resolved yet. Run `settle` after markets close.")

    if pf["open"]:
        lines.append("\nMain portfolio open bets:")
        for p in sorted(pf["open"], key=lambda p: p["close_time"] or ""):
            lines.append(f"  {p['side'].upper():3} ${p['total_cost']:>8,.2f}  p {p['p_side']:.2f} vs "
                         f"{p['market_ask']:.2f}  closes {str(p['close_time'])[:10]}  {p['question'][:60]}")
    return "\n".join(lines)

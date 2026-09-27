"""Bet gates, sizing, the fake-money ledger, settlement and reporting."""
from __future__ import annotations

import json
import math
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .jev_client import PROJECT_ROOT, JevClient, JevError

from . import markets as mk
from .judge import QUESTION_SET_VERSION, QUESTIONS, build_state

POLICY_PATH = PROJECT_ROOT / "policy.json"
DATA = PROJECT_ROOT / "papertrade_data"
PORTFOLIO = DATA / "portfolio.json"
JUDGMENTS = DATA / "judgments.jsonl"
RESOLUTIONS = DATA / "resolutions.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text())


def key(m: dict) -> str:
    return f"{m['source']}:{m['market_id']}"


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


def load_portfolio(policy: dict) -> dict:
    return load_json(PORTFOLIO, {
        "created": now_iso(), "starting_bankroll": policy["starting_bankroll"],
        "cash": float(policy["starting_bankroll"]), "open": [], "closed": [],
    })


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
    out = {"bet": False, **best, "p_yes": p, "rules_clear": rules_clear,
           "info_sufficient": info_ok, "reasons": reasons}

    if best["edge"] < g["min_edge"]:
        reasons.append(f"edge {best['edge']:+.3f} < {g['min_edge']}")
    if rules_clear < g["min_rules_clear"]:
        reasons.append(f"rules_clear {rules_clear:.2f} < {g['min_rules_clear']}")
    if info_ok < g["min_info_sufficient"]:
        reasons.append(f"needs recent info ({info_ok:.2f} < {g['min_info_sufficient']})")
    if reasons:
        return out

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
    reasons.append(f"BET {best['side'].upper()} x{contracts} @ {c:.3f}: Jev {best['q']:.2f} "
                   f"vs cost {c:.3f}, edge {best['edge']:+.3f}")
    return out


# ---------------- scan ----------------

def recently_judged(hours: float) -> set[str]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    seen = set()
    for j in read_jsonl(JUDGMENTS):
        try:
            ts = datetime.strptime(j["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except (KeyError, ValueError):
            continue
        if ts >= cutoff:
            seen.add(j["key"])
    return seen


def scan(policy: dict, client: JevClient | None = None, fetchers=None, log=print) -> dict:
    fetchers = fetchers or mk.FETCHERS
    client = client or JevClient(model=policy["model"])
    pf = load_portfolio(policy)
    mf = policy["market_filters"]
    held = {p["key"] for p in pf["open"]}
    skip = held | recently_judged(mf["rejudge_after_hours"])
    stats = {"fetched": 0, "judged": 0, "bets": 0, "errors": 0}

    candidates = []
    for src in policy["sources"]:
        try:
            ms = fetchers[src](mf["days_ahead"], mf["min_volume"], mf["markets_per_source"])
        except Exception as e:  # one broken source shouldn't stop the other
            log(f"! {src}: could not fetch markets ({e})")
            stats["errors"] += 1
            continue
        stats["fetched"] += len(ms)
        for m in ms:
            if key(m) in skip:
                continue
            if not (mf["min_price"] <= m["mid"] <= mf["max_price"]):
                continue
            candidates.append(m)

    for m in candidates[: policy["max_jev_calls_per_scan"]]:
        try:
            res = client.ask(build_state(m), QUESTIONS)
        except JevError as e:
            log(f"! Jev error on {m['question'][:60]}: {e}")
            stats["errors"] += 1
            continue
        stats["judged"] += 1
        open_cost = sum(p["total_cost"] for p in pf["open"])
        d = decide(m, res["answers"], policy, equity_at_cost(pf), open_cost, pf["cash"])
        append_jsonl(JUDGMENTS, {
            "ts": now_iso(), "key": key(m), "question_set": QUESTION_SET_VERSION,
            "model": res["model"], "market": m, "answers": res["answers"],
            "decision": d, "latency_ms": res["latency_ms"],
        })
        if d["bet"]:
            pf["cash"] = round(pf["cash"] - d["total_cost"], 2)
            pf["open"].append({
                "key": key(m), "source": m["source"], "market_id": m["market_id"],
                "question": m["question"], "url": m["url"], "close_time": m["close_time"],
                "side": d["side"], "contracts": d["contracts"], "cost_per": d["cost"],
                "total_cost": d["total_cost"], "p_side": round(d["q"], 4),
                "market_ask": d["ask"], "edge": d["edge"], "opened": now_iso(),
                "question_set": QUESTION_SET_VERSION,
            })
            stats["bets"] += 1
            log(f"+ {d['side'].upper():3} ${d['total_cost']:>8,.2f}  edge {d['edge']:+.2f}  "
                f"[{m['source']}] {m['question'][:70]}")
    save_json(PORTFOLIO, pf)
    return stats


# ---------------- settle ----------------

def settle(policy: dict, resolvers=None, log=print) -> dict:
    resolvers = resolvers or mk.RESOLVERS
    pf = load_portfolio(policy)
    resolved = load_json(RESOLUTIONS, {})
    now = datetime.now(timezone.utc)

    to_check = {p["key"] for p in pf["open"]}
    for j in read_jsonl(JUDGMENTS):
        if j["key"] not in resolved:
            to_check.add(j["key"])
    closes = {p["key"]: p["close_time"] for p in pf["open"]}
    for j in read_jsonl(JUDGMENTS):
        closes.setdefault(j["key"], j["market"]["close_time"])

    stats = {"checked": 0, "resolved": 0, "settled_bets": 0}
    for k in sorted(to_check):
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

    still_open = []
    for p in pf["open"]:
        outcome = resolved.get(p["key"])
        if not outcome:
            still_open.append(p)
            continue
        payout = float(p["contracts"]) if p["side"] == outcome else 0.0
        pnl = round(payout - p["total_cost"], 2)
        pf["cash"] = round(pf["cash"] + payout, 2)
        pf["closed"].append({**p, "outcome": outcome, "payout": payout, "pnl": pnl,
                             "settled": now_iso()})
        stats["settled_bets"] += 1
        log(f"{'WIN ' if pnl > 0 else 'LOSS'} {pnl:+10,.2f}  {p['question'][:70]}")
    pf["open"] = still_open
    save_json(RESOLUTIONS, resolved)
    save_json(PORTFOLIO, pf)
    return stats


# ---------------- report ----------------

def brier(pairs):
    return sum((p - y) ** 2 for p, y in pairs) / len(pairs) if pairs else None


def report(policy: dict) -> str:
    pf = load_portfolio(policy)
    resolved = load_json(RESOLUTIONS, {})
    start = pf["starting_bankroll"]
    open_cost = sum(p["total_cost"] for p in pf["open"])
    realized = sum(p["pnl"] for p in pf["closed"])
    wins = sum(1 for p in pf["closed"] if p["pnl"] > 0)
    eq = equity_at_cost(pf)
    lines = [
        f"Fake bankroll: ${start:,.0f} start  ->  ${eq:,.2f} now (open bets valued at cost)",
        f"Cash ${pf['cash']:,.2f}   Open bets {len(pf['open'])} (${open_cost:,.2f} at risk)",
        f"Settled {len(pf['closed'])}: {wins} won / {len(pf['closed']) - wins} lost   "
        f"Realized P&L {realized:+,.2f}"
        + (f"   ROI on settled stakes {realized / sum(p['total_cost'] for p in pf['closed']):+.1%}"
           if pf["closed"] else ""),
    ]

    # Calibration: Jev vs the market's own price, on every judged market that resolved.
    latest = {}
    for j in read_jsonl(JUDGMENTS):
        if j.get("question_set") == QUESTION_SET_VERSION:
            latest[j["key"]] = j  # last judgment per market
    jev_pairs, mkt_pairs = [], []
    for k, j in latest.items():
        if k in resolved:
            y = 1.0 if resolved[k] == "yes" else 0.0
            jev_pairs.append((float(j["answers"]["p_yes"]["noul"]), y))
            mkt_pairs.append((float(j["market"]["mid"]), y))
    lines.append(f"\nMarkets judged: {len(latest)}   resolved so far: {len(jev_pairs)}")
    bj, bm = brier(jev_pairs), brier(mkt_pairs)
    if bj is not None:
        lines.append(f"Brier score (lower is better):  Jev {bj:.4f}   Market price {bm:.4f}")
        lines.append("  -> " + ("Jev is beating the market's own forecast so far."
                                if bj < bm else
                                "The market is still the better forecaster; edges are likely noise."))
        if len(jev_pairs) < 50:
            lines.append(f"  (only {len(jev_pairs)} resolved markets; treat as noise until ~50+)")
    else:
        lines.append("No judged markets have resolved yet. Run `settle` after markets close.")

    if pf["open"]:
        lines.append("\nOpen bets:")
        for p in sorted(pf["open"], key=lambda p: p["close_time"] or ""):
            lines.append(f"  {p['side'].upper():3} ${p['total_cost']:>8,.2f}  Jev {p['p_side']:.2f} vs "
                         f"{p['market_ask']:.2f}  closes {str(p['close_time'])[:10]}  {p['question'][:60]}")
    return "\n".join(lines)

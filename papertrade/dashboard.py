"""One-page HTML dashboard of the fake portfolio: trades, cash split, P&L and forecast quality.

`python3 -m papertrade dashboard` writes papertrade_data/dashboard.html; `daily` refreshes it.
The page is a single self-contained file: open it in any browser, no server needed. Every number
is computed here in Python; the page's script only draws what it is given.
"""
from __future__ import annotations

import json
import shutil
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from . import coach, engine, learn, review

TEMPLATE = Path(__file__).with_name("dashboard_template.html")
SLOTS = 7  # categorical colors on the page; a strategy keeps its slot for good (color follows the entity)
RACE_POINTS = 240  # the race chart's resolution; settlements and the latest point are always kept
CALLS = 12  # how many recent researched calls the page shows


def last_scan(policy: dict, judgments: list[dict]) -> dict | None:
    """What the most recent day's scan judged and which gates stopped the bets."""
    if not judgments:
        return None
    current = [j for j in judgments if j.get("question_set") == engine.QUESTION_SET_VERSION]
    pool = current or judgments  # older question sets only when nothing newer exists
    latest = max(j["ts"] for j in pool)  # every judgment in one scan shares that scan's timestamp
    js = [j for j in pool if j["ts"] == latest]
    day = latest[:10]
    g = policy["gates"]
    ds = [j.get("decision") or {} for j in js]
    scored = [d for d in ds if "info_sufficient" in d]  # e.g. "already holding" decisions carry no gate scores
    return {
        "date": day, "judged": len(js), "bets": sum(1 for d in ds if d.get("bet")),
        "fail_info": sum(1 for d in scored if d["info_sufficient"] < g["min_info_sufficient"]),
        "fail_rules": sum(1 for d in scored if d["rules_clear"] < g["min_rules_clear"]),
        "fail_edge": sum(1 for d in scored if d["edge"] < g["min_edge"]),
        "sources": dict(Counter(j["market"]["source"] for j in js)),
    }


def funnel(scans: list[dict]) -> dict | None:
    """The latest scan's stage counts, from scans.jsonl."""
    scans = [s for s in scans if "funnel" in s]
    if not scans:
        return None
    s = scans[-1]
    f = s["funnel"]
    main = engine.MAIN
    cl = s.get("claude") or {}
    return {
        "ts": s.get("ts"),
        "stages": [["Fetched", f["fetched"]], ["Passed free filters", f["passed_filters"]],
                   ["Judged by Jev", f.get("judged", 0)], ["Judged with research", f.get("with_research", 0)],
                   ["Cleared every gate (main)", f["cleared_gates"].get(main, 0)],
                   ["Bets placed (main)", f["bets"].get(main, 0)]],
        "events": f.get("events", 0), "researched_new": f.get("researched_new", 0),
        "research_reused": f.get("research_reused", 0), "bets": f["bets"],
        "claude_calls": cl.get("calls", 0), "claude_limited": bool(cl.get("limited")), "claude_note": cl.get("note"),
        "facts_kept": s.get("facts_kept", 0), "facts_dropped": s.get("facts_dropped", 0),
        "by_source": f.get("by_source"), "problems": s.get("problems") or [], "cleared_gates": f["cleared_gates"],
        "judged": f.get("judged", 0), "with_research": f.get("with_research", 0),
    }


def plan_usage(scans: list[dict]) -> dict | None:
    """The latest usage Claude reported for Joey's plan (share of the 5-hour and weekly windows)."""
    for s in reversed(scans):
        rate = (s.get("claude") or {}).get("rate")
        if rate:
            w = rate.get("unifiedWindows") or {}
            return {"ts": s.get("ts"), "week": (w.get("seven_day") or {}).get("utilization"),
                    "week_resets": (w.get("seven_day") or {}).get("resetsAt"),
                    "five_hour": (w.get("five_hour") or {}).get("utilization")}
    return None


def last_prices(judgments: list[dict]) -> dict:
    """key -> (time, mid) of the last price we saw for each market (every judgment records it)."""
    out = {}
    for j in judgments:
        mid = (j.get("market") or {}).get("mid")
        if mid is not None:
            out[j["key"]] = (j["ts"], float(mid))
    return out


def _side_value(p: dict, mid: float) -> float:
    return p["contracts"] * (mid if p["side"] == "yes" else 1 - mid)


def strategy_rows(policy: dict, books: dict, prices: dict | None = None, cmap: dict | None = None) -> list[dict]:
    """One row per strategy. `marked` values open bets at the last price we saw (up to a few hours old);
    `equity` is the official number, with open bets at what they cost."""
    rows, prices = [], prices or {}
    for i, (name, strat) in enumerate(engine.strategies(policy).items()):
        b = books[name]
        eq = round(engine.equity_at_cost(b), 2)
        marked = b["cash"] + sum(_side_value(p, prices[p["key"]][1]) if p["key"] in prices else p["total_cost"]
                                 for p in b["open"])
        note = None
        if strat.get("probability") == "jev_calibrated" and cmap and not cmap.get("active"):
            note = f"Learning: {cmap['n']} of {cmap['need']} results in"
        rows.append({"name": name, "label": strat["label"], "short": strat.get("short") or strat["label"],
                     "main": name == engine.MAIN, "equity": eq,
                     "slot": i + 1 if i < SLOTS else None, "blurb": strat.get("blurb") or strat.get("_why") or "",
                     "challenger": bool(strat.get("challenger")), "note": note,
                     "gate_overrides": {k: v for k, v in (strat.get("gate_overrides") or {}).items() if not k.startswith("_")},
                     "marked": round(marked, 2), "unrealized": round(marked - eq, 2),
                     "change": round(eq - float(b["starting_bankroll"]), 2),
                     "realized": round(sum(p["pnl"] for p in b["closed"]), 2),
                     "open": len(b["open"]), "open_cost": round(sum(p["total_cost"] for p in b["open"]), 2),
                     "settled": len(b["closed"]), "wins": sum(1 for p in b["closed"] if p["pnl"] > 0)})
    return rows


def race(books: dict, judgments: list[dict], generated_at: str) -> list[dict]:
    """Each strategy's bankroll over time, open bets marked at the last price seen by then.

    Rebuilt from the ledgers and the judgment log on every cycle, so it needs no file of its own.
    Points: every scan, every settlement, and now; thinned to RACE_POINTS, keeping settlements."""
    history: dict[str, list] = {}
    for j in judgments:
        mid = (j.get("market") or {}).get("mid")
        if mid is not None:
            history.setdefault(j["key"], []).append((j["ts"], float(mid)))
    scans = sorted({j["ts"] for j in judgments})
    settles = sorted({p["settled"] for b in books.values() for p in b["closed"] if p.get("settled")})
    start = min((b.get("created") or generated_at) for b in books.values())
    times = sorted({t for t in scans + settles if t >= start} | {generated_at})
    if len(times) > RACE_POINTS:
        keep, step = set(settles) | {times[0], times[-1]}, len(times) / RACE_POINTS
        times = sorted({times[int(i * step)] for i in range(RACE_POINTS)} | (keep & set(times)))

    def price(key, t):
        last = None
        for ts, mid in history.get(key, ()):
            if ts > t:
                break
            last = mid
        return last

    out = []
    for name, b in books.items():
        bets = b["open"] + b["closed"]
        pts = []
        for t in times:
            cash, value = float(b["starting_bankroll"]), 0.0
            for p in bets:
                if (p.get("opened") or "") > t:
                    continue
                cash -= p["total_cost"]
                if p.get("settled") and p["settled"] <= t:
                    cash += p["payout"]
                else:
                    mid = price(p["key"], t)
                    value += _side_value(p, mid) if mid is not None else p["total_cost"]
            pts.append([t, round(cash + value, 2)])
        out.append({"name": name, "points": pts})
    return out


def open_bets(books: dict, prices: dict, judgments: list[dict]) -> list[dict]:
    """Every open bet across strategies, grouped by market, soonest to close first."""
    latest = {}
    for j in judgments:
        latest[j["key"]] = j
    by_key: dict[str, dict] = {}
    for name, b in books.items():
        for p in b["open"]:
            m = by_key.setdefault(p["key"], {
                "key": p["key"], "question": p["question"], "url": p["url"], "source": p["source"],
                "close_time": p["close_time"], "category": (latest.get(p["key"], {}).get("market") or {}).get("category"),
                "price": prices.get(p["key"], (None, None))[1], "price_at": prices.get(p["key"], (None, None))[0],
                "positions": []})
            m["positions"].append({"strategy": name, "side": p["side"], "contracts": p["contracts"],
                                   "cost_per": p["cost_per"], "total_cost": p["total_cost"], "p_side": p["p_side"],
                                   "edge": p["edge"], "opened": p["opened"],
                                   "value": round(_side_value(p, prices[p["key"]][1]), 2) if p["key"] in prices else None})
    return sorted(by_key.values(), key=lambda m: m["close_time"] or "")


def recent_settled(books: dict, n: int = 20) -> list[dict]:
    rows = [dict({k: p.get(k) for k in ("key", "question", "url", "source", "side", "total_cost", "cost_per", "p_side",
                                         "outcome", "payout", "pnl", "opened", "settled")}, strategy=name)
            for name, b in books.items() for p in b["closed"]]
    return sorted(rows, key=lambda r: r.get("settled") or "", reverse=True)[:n]


def calls(judgments: list[dict], n: int = CALLS) -> list[dict]:
    """The latest researched calls: what each forecaster said vs the market, and the facts behind it."""
    latest = {}
    for j in judgments:
        if j.get("question_set") == engine.QUESTION_SET_VERSION and j.get("answers"):
            latest[j["key"]] = j
    out = []
    for j in sorted(latest.values(), key=lambda j: j["ts"], reverse=True)[:n]:
        m, a = j["market"], j["answers"]
        out.append({
            "ts": j["ts"], "key": j["key"], "question": m["question"], "url": m.get("url"), "source": m["source"],
            "category": m.get("category") or learn.category(m), "close_time": m.get("close_time"),
            "market": m.get("mid"),
            "forecasts": {src: engine._prob(j, src) for src in ("jev_research", "jev_plain", "claude_direct", "jev_calibrated")},
            "info": a["info_sufficient"]["noul"], "rules": a["rules_clear"]["noul"],
            "decisions": {name: {"bet": d.get("bet", False), "side": d.get("side"),
                                 "why": (d.get("reasons") or [""])[0][:140]}
                          for name, d in (j.get("decisions") or {}).items()},
            "facts": [{k: f.get(k) for k in ("kind", "date", "source", "fact")} for f in (j.get("recent_facts") or [])[:6]],
            "facts_total": len(j.get("recent_facts") or []),
        })
    return out


def learning_state(policy: dict, reviews: list[dict], judgments: list[dict], resolved: dict) -> dict:
    """review.learning plus the loop's own state: playbook, calibration map, gate ledger, proposals, retro."""
    out = review.learning(reviews)
    pb = coach.load_playbook()
    strats = engine.strategies(policy)
    retros = [r for r in engine.read_jsonl(engine.RETROS) if not r.get("error")]
    hist = engine.read_jsonl(engine.PLAYBOOK_LOG)
    out.update({
        "playbook": {"version": pb["version"], "updated": pb.get("updated"),
                     "rules": [{k: r.get(k) for k in ("id", "category", "rule", "added")} for r in pb["rules"]],
                     "history": [{k: h.get(k) for k in ("ts", "version", "added", "revised", "retired", "changes")}
                                 | {"refused": len(h.get("dropped") or [])} for h in hist[-5:]][::-1]},
        "calibration_map": learn.calibration_map(reviews, policy["learning"]),
        "gate_ledger": learn.gate_ledger(policy, judgments, resolved,
                                         {n: engine.strategy_policy(policy, s) for n, s in strats.items()}),
        "by_category": learn.category_scores(judgments, resolved, engine._prob),
        "proposals": [{k: p.get(k) for k in ("id", "kind", "title", "why", "judge_by", "min_resolved", "status",
                                             "status_reason", "created")} for p in coach.load_proposals()["proposals"]][::-1],
        "suggested_areas": out.pop("proposals"),
        "retro": ({k: retros[-1].get(k) for k in ("ts", "headline", "went_well", "went_badly")} if retros else None),
        "auto_start": bool(policy["learning"]["auto_start_challengers"]),
    })
    return out


def summarize(policy: dict, books: dict, judgments: list[dict], resolved: dict, generated_at: str,
              scans: list[dict] | None = None, reviews: list[dict] | None = None, example: bool = False) -> dict:
    pf = books[engine.MAIN]
    start = float(pf["starting_bankroll"])
    open_cost = round(sum(p["total_cost"] for p in pf["open"]), 2)
    equity = round(pf["cash"] + open_cost, 2)
    closed = sorted(pf["closed"], key=lambda p: p.get("settled") or "")
    realized = round(sum(p["pnl"] for p in closed), 2)
    staked = sum(p["total_cost"] for p in closed)

    # Equity at cost only moves when a bet settles, so the curve is start + running realized P&L.
    curve, running = [{"t": pf.get("created"), "equity": start, "label": "Starting bankroll"}], start
    for p in closed:
        running += p["pnl"]
        curve.append({"t": p.get("settled"), "equity": round(running, 2), "label": p["question"]})
    curve.append({"t": generated_at, "equity": equity, "label": "Now (open bets valued at cost)"})

    prices = last_prices(judgments)
    cmap = learn.calibration_map(reviews or [], policy["learning"])
    by_source = Counter()
    for p in pf["open"]:
        by_source[p["source"]] += p["total_cost"]
    keep_open = ("question", "url", "source", "side", "contracts", "cost_per", "total_cost", "p_side",
                 "market_ask", "edge", "opened", "close_time")
    return {
        "generated": generated_at, "example": example, "question_set": engine.QUESTION_SET_VERSION,
        "start": start, "cash": round(pf["cash"], 2), "open_cost": open_cost, "equity": equity,
        "realized": realized, "roi_settled": (realized / staked) if staked else None,
        "wins": sum(1 for p in closed if p["pnl"] > 0), "settled": len(closed),
        "exposure_cap_pct": policy["sizing"]["max_total_exposure_pct"],
        "max_stake_pct": policy["sizing"]["max_stake_pct"],
        "by_source": {k: round(v, 2) for k, v in by_source.items()},
        "curve": curve,
        "open": [{k: p.get(k) for k in keep_open} for p in sorted(pf["open"], key=lambda p: p.get("close_time") or "")],
        "closed": [{k: p.get(k) for k in keep_open + ("outcome", "payout", "pnl", "settled")} for p in reversed(closed)],
        "calibration": engine.calibration(judgments, resolved),
        "last_scan": last_scan(policy, judgments),
        "funnel": funnel(scans or []),
        "strategies": strategy_rows(policy, books, prices, cmap),
        "race": race(books, judgments, generated_at),
        "open_bets": open_bets(books, prices, judgments),
        "settled_recent": recent_settled(books),
        "calls": calls(judgments),
        "plan_usage": plan_usage(scans or []),
        "research_runs_today": sum(1 for r in engine.read_jsonl(engine.RESEARCH) if str(r.get("ts", "")).startswith(generated_at[:10])),
        "cycles_24h": sum(1 for s in (scans or []) if "funnel" in s and s["ts"] >= _hours_before(generated_at, 24)),
        "learning": learning_state(policy, reviews or [], judgments, resolved),
        "repo_url": policy.get("site", {}).get("repo_url") or None,
    }


def _hours_before(stamp: str, hours: int) -> str:
    t = datetime.strptime(stamp, engine.TS).replace(tzinfo=timezone.utc) - timedelta(hours=hours)
    return t.strftime(engine.TS)


def build_html(summary: dict) -> str:
    # "</" is escaped so market text can never close the data <script> block early.
    blob = json.dumps(summary, ensure_ascii=False).replace("</", "<\\/")
    return TEMPLATE.read_text().replace("__DASHBOARD_DATA__", blob)


def current_summary(policy: dict) -> dict:
    """Built only from the real data files. Nothing here can mark data as example."""
    return summarize(policy, engine.load_books(policy), engine.read_jsonl(engine.JUDGMENTS),
                     engine.load_json(engine.RESOLUTIONS, {}), engine.now_iso(),
                     scans=engine.read_jsonl(engine.SCANS), reviews=engine.read_jsonl(engine.REVIEWS))


def raw_base(policy: dict) -> str | None:
    """Where the public repo's files can be read by a browser (GitHub serves them with CORS allowed)."""
    repo = (policy.get("site", {}).get("repo_url") or "").rstrip("/")
    prefix = "https://github.com/"
    if not repo.startswith(prefix):
        return None
    return f"https://raw.githubusercontent.com/{repo[len(prefix):]}/{policy['site'].get('branch', 'master')}/"


def write_summary(policy: dict) -> Path:
    """papertrade_data/summary.json: what the public page reads, committed with the ledgers every cycle."""
    s = current_summary(policy)
    base = raw_base(policy)
    s["ledger_base"] = base + "papertrade_data/" if base else None
    engine.save_json(engine.SUMMARY, s)
    return engine.SUMMARY


def build_site(policy: dict, out: Path | None = None, summary: dict | None = None) -> Path:
    """Write the public page shell into site/. It carries a snapshot and, when the repo is public,
    fetches the latest summary.json from GitHub each time it's opened. Refuses example data."""
    summary = dict(summary or current_summary(policy))
    if summary.get("example"):
        raise RuntimeError("refusing to publish: this summary is marked as example data")
    base = raw_base(policy)
    summary["data_url"] = base + "papertrade_data/summary.json" if base else None
    summary["ledger_base"] = base + "papertrade_data/" if base else None
    out = out or engine.SITE
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "index.html").write_text(build_html(summary))
    return out


def write_dashboard(policy: dict, out: Path | None = None) -> Path:
    summary = current_summary(policy)
    out = out or engine.DATA / "dashboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(summary))
    return out

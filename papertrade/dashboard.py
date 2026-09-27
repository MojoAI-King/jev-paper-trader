"""One-page HTML dashboard of the fake portfolio: trades, cash split, P&L and forecast quality.

`python3 -m papertrade dashboard` writes papertrade_data/dashboard.html; `daily` refreshes it.
The page is a single self-contained file: open it in any browser, no server needed. Every number
is computed here in Python; the page's script only draws what it is given.
"""
from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path

from . import engine, review

TEMPLATE = Path(__file__).with_name("dashboard_template.html")


def last_scan(policy: dict, judgments: list[dict]) -> dict | None:
    """What the most recent day's scan judged and which gates stopped the bets."""
    if not judgments:
        return None
    day = max(j["ts"][:10] for j in judgments)
    js = [j for j in judgments if j["ts"][:10] == day]
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
    return {
        "ts": s.get("ts"),
        "stages": [["Fetched", f["fetched"]], ["Passed free filters", f["passed_filters"]],
                   ["Researched", f["researched"]], ["Judged three ways", f["judged"]],
                   ["Cleared every gate (main)", f["cleared_gates"].get(main, 0)],
                   ["Bets placed (main)", f["bets"].get(main, 0)]],
        "events": f["events"], "bets": f["bets"],
        "research_usd": s.get("research_usd", 0.0), "forecast_usd": s.get("forecast_usd", 0.0),
        "facts_kept": s.get("facts_kept", 0), "facts_dropped": s.get("facts_dropped", 0),
    }


def strategy_rows(policy: dict, books: dict) -> list[dict]:
    rows = []
    for name, strat in engine.strategies(policy).items():
        b = books[name]
        eq = round(engine.equity_at_cost(b), 2)
        rows.append({"name": name, "label": strat["label"], "main": name == engine.MAIN, "equity": eq,
                     "change": round(eq - float(b["starting_bankroll"]), 2),
                     "realized": round(sum(p["pnl"] for p in b["closed"]), 2),
                     "open": len(b["open"]), "open_cost": round(sum(p["total_cost"] for p in b["open"]), 2),
                     "settled": len(b["closed"]), "wins": sum(1 for p in b["closed"] if p["pnl"] > 0)})
    return rows


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

    by_source = Counter()
    for p in pf["open"]:
        by_source[p["source"]] += p["total_cost"]
    keep_open = ("question", "url", "source", "side", "contracts", "cost_per", "total_cost", "p_side",
                 "market_ask", "edge", "opened", "close_time")
    spend = sum(s.get("research_usd", 0.0) + s.get("forecast_usd", 0.0) + s.get("review_usd", 0.0) for s in scans or [])
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
        "strategies": strategy_rows(policy, books),
        "research_spend": round(spend, 2) if scans else None,
        "learning": review.learning(reviews or []),
        "repo_url": policy.get("site", {}).get("repo_url") or None,
    }


def build_html(summary: dict) -> str:
    # "</" is escaped so market text can never close the data <script> block early.
    blob = json.dumps(summary, ensure_ascii=False).replace("</", "<\\/")
    return TEMPLATE.read_text().replace("__DASHBOARD_DATA__", blob)


def current_summary(policy: dict) -> dict:
    """Built only from the real data files. Nothing here can mark data as example."""
    return summarize(policy, engine.load_books(policy), engine.read_jsonl(engine.JUDGMENTS),
                     engine.load_json(engine.RESOLUTIONS, {}), engine.now_iso(),
                     scans=engine.read_jsonl(engine.SCANS), reviews=engine.read_jsonl(engine.REVIEWS))


# The raw ledgers published next to the page, at the same relative paths the page links to.
PUBLIC_FILES = ("scans.jsonl", "reviews.jsonl", "resolutions.json")


def build_site(policy: dict, out: Path | None = None, summary: dict | None = None) -> Path:
    """Write the public page and its raw ledgers into site/. Refuses example data."""
    summary = summary or current_summary(policy)
    if summary.get("example"):
        raise RuntimeError("refusing to publish: this summary is marked as example data")
    out = out or engine.SITE
    if out.exists():
        shutil.rmtree(out)
    (out / "portfolios").mkdir(parents=True)
    (out / "index.html").write_text(build_html(summary))
    for name in engine.strategies(policy):
        src = engine.portfolio_path(name)
        if src.exists():
            shutil.copyfile(src, out / "portfolios" / src.name)
    for f in PUBLIC_FILES:
        if (engine.DATA / f).exists():
            shutil.copyfile(engine.DATA / f, out / f)
    return out


def write_dashboard(policy: dict, out: Path | None = None) -> Path:
    summary = current_summary(policy)
    out = out or engine.DATA / "dashboard.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_html(summary))
    return out

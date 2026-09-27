"""python3 -m papertrade {cycle|scan|settle|review|report|dashboard|publish|ping|markets|reset}"""
from __future__ import annotations

import argparse
import subprocess
import sys

from . import dashboard, engine, review
from . import markets as mk
from .jev_client import JevClient, JevError


def cmd_ping(policy) -> int:
    try:
        res = JevClient(model=policy["model"]).ask(
            "The sky is blue on a clear day.",
            {"check": {"type": "noul", "instructions": "Is this statement true?"}})
    except JevError as e:
        print(f"Jev: FAILED  {e}")
        return 1
    print(f"Jev: OK  model={res['model']}  P(true)={res['answers']['check']['noul']:.2f}  "
          f"{res['latency_ms']} ms")
    return 0


def cmd_markets(policy) -> int:
    """Show what the market feeds return, without calling Jev or betting."""
    mf, ok = policy["market_filters"], 0
    for src in policy["sources"]:
        try:
            ms = mk.FETCHERS[src](mf["days_ahead"], mf["min_volume"], mf["markets_per_source"])
        except Exception as e:
            print(f"{src}: FAILED  {e}")
            continue
        ok += 1
        print(f"{src}: {len(ms)} markets")
        for m in ms[:5]:
            print(f"   yes {m['yes_ask']:.2f} / no {m['no_ask']:.2f}  closes {str(m['close_time'])[:10]}  "
                  f"{m['question'][:70]}")
    return 0 if ok else 1


def deploy() -> int:
    """Push site/ to Cloudflare Workers with the project's wrangler.jsonc. Prints the live URL."""
    r = subprocess.run(["npx", "--yes", "wrangler", "deploy"], cwd=engine.PROJECT_ROOT,
                       capture_output=True, text=True)
    lines = (r.stdout + r.stderr).splitlines()
    for line in lines:
        if "workers.dev" in line or "Deployed" in line or "Current Version" in line or "ERROR" in line:
            print("  " + line.strip())
    if r.returncode:
        print("Deploy FAILED. Run `npx wrangler deploy` in the project folder to see the full error.")
    return r.returncode


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="papertrade",
                                description="Jev paper trading on real prediction markets (fake money only)")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name, text in (("cycle", "One trading cycle, meant to run hourly: settle, scan, review, rebuild the page"),
                       ("daily", "Same as cycle (kept for the old name)")):
        c = sub.add_parser(name, help=text)
        c.add_argument("--limit", type=int, help="Research at most this many events (for a small test run)")
        c.add_argument("--deploy", action="store_true", help="Also rebuild and push the page shell to Cloudflare")
    sc = sub.add_parser("scan", help="Pull live markets, research them, ask Jev, place fake bets that pass every gate")
    sc.add_argument("--limit", type=int, help="Research at most this many events (for a small test run)")
    sub.add_parser("settle", help="Pay out fake bets on markets that have resolved")
    sub.add_parser("review", help="Score newly resolved markets; write post-mortems for the misses")
    sub.add_parser("report", help="Bankroll, P&L, and each forecaster vs the market")
    sub.add_parser("ping", help="Check the Jev API key and connection")
    sub.add_parser("markets", help="Preview live markets from each source (no Jev calls, no bets)")
    sub.add_parser("dashboard", help="Write papertrade_data/dashboard.html: trades, cash, P&L on one page")
    pb = sub.add_parser("publish", help="Build site/ (the public page shell; data comes from GitHub)")
    pb.add_argument("--deploy", action="store_true", help="Also push it to Cloudflare Workers")
    r = sub.add_parser("reset", help="Start over with a fresh fake bankroll (keeps a backup)")
    r.add_argument("--yes", action="store_true")
    a = p.parse_args(argv)
    policy = engine.load_policy()
    cycle = a.cmd in ("cycle", "daily")

    if a.cmd == "ping":
        return cmd_ping(policy)
    if a.cmd == "markets":
        return cmd_markets(policy)
    if a.cmd == "settle" or cycle:
        s = engine.settle(policy)
        print(f"Settle: checked {s['checked']} closed markets, {s['resolved']} resolved, "
              f"{s['settled_bets']} bets paid out.\n")
    if a.cmd == "scan" or cycle:
        s = engine.scan(policy, limit=getattr(a, "limit", None))
        f, cl = s["funnel"], s["claude"]
        print(f"\nScan funnel: fetched {f['fetched']} -> passed free filters {f['passed_filters']} -> "
              f"judged by Jev {f['judged']} -> with research {f['with_research']}")
        print(f"  Research: {f['researched_new']} new, {f['research_reused']} reused   "
              f"Claude calls {cl['calls']} (on the Claude plan; ~${cl['api_equivalent_usd']:.2f} API-equivalent, not billed)"
              + ("   PAUSED: plan busy" if cl["limited"] else ""))
        print("  Bets: " + ", ".join(f"{k} {v}" for k, v in f["bets"].items())
              + f"   ({s['deferred']} markets wait for the next cycle, {s['errors']} errors)")
        w = ((cl.get("rate") or {}).get("unifiedWindows") or {})
        if w:
            print(f"  Claude plan usage: week {100 * (w.get('seven_day') or {}).get('utilization', 0):.0f}%, "
                  f"5-hour {100 * (w.get('five_hour') or {}).get('utilization', 0):.0f}%")
        print(f"  Facts kept {s['facts_kept']}, dropped by the price screen {s['facts_dropped']}\n")
    if a.cmd == "review" or cycle:
        rv = review.review(policy)
        if rv["reviewed"]:
            engine.append_jsonl(engine.SCANS, {"ts": engine.now_iso(), "kind": "review", **rv})
        print(f"Review: {rv['reviewed']} newly resolved markets scored, {rv['post_mortems']} post-mortems"
              + (" (paused: Claude plan busy)" if rv.get("limited") else "") + f", {rv['errors']} errors.\n")
    if a.cmd == "report" or cycle:
        print(engine.report(policy))
    if a.cmd == "dashboard" or cycle:
        path = dashboard.write_dashboard(policy)
        print(f"\nDashboard: {path}  (open it in a browser)")
    if cycle:
        print(f"Summary for the public page: {dashboard.write_summary(policy)}")
    if a.cmd == "publish" or getattr(a, "deploy", False):
        out = dashboard.build_site(policy)
        print(f"Public page shell built: {out}/index.html (it loads the latest summary.json from GitHub)")
        if getattr(a, "deploy", False):
            return deploy()
    if a.cmd == "reset":
        if not a.yes:
            print("This wipes the fake portfolio and history. Re-run with --yes to confirm.")
            return 1
        import shutil, time
        if engine.DATA.exists():
            shutil.move(str(engine.DATA), str(engine.DATA) + time.strftime("-backup-%Y%m%d-%H%M%S"))
        print(f"Fresh ${policy['starting_bankroll']:,} fake bankroll ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

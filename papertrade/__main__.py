"""python3 -m papertrade {cycle|scan|settle|review|report|learn|health|approve|reject|retire|dashboard|publish|ping|markets|reset}"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone

from . import coach, dashboard, engine, learn, review
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


def cmd_learn(policy) -> int:
    """What the loop has learned so far, from the local data files (git pull first for the latest)."""
    reviews = engine.read_jsonl(engine.REVIEWS)
    judgments, resolved = engine.read_jsonl(engine.JUDGMENTS), engine.load_json(engine.RESOLUTIONS, {})
    L = review.learning(reviews)
    print(f"Resolved and reviewed: {L['reviewed']}   post-mortems of misses: {L['post_mortems']}   "
          f"reviews of wins: {L['win_reviews']}")
    if L["root_causes"]:
        print("  Why we missed: " + ", ".join(f"{k} {v}" for k, v in L["root_causes"].items()))
    if L["credits"]:
        print("  Why we won:    " + ", ".join(f"{k} {v}" for k, v in L["credits"].items()))
    cm = learn.calibration_map(reviews, policy["learning"])
    print(f"\nCalibration map: " + (f"active, a={cm['a']} b={cm['b']} from {cm['n']} markets "
                                     f"({'Jev is overconfident' if cm['a'] < 1 else 'Jev is too timid'})"
                                     if cm["active"] else f"learning, {cm['n']} of {cm['need']} resolved markets"))
    pb = coach.load_playbook()
    print(f"\nResearch playbook v{pb['version']} ({len(pb['rules'])} rules, updated {pb.get('updated') or 'never'}):")
    for r in pb["rules"]:
        print(f"  {r['id']:>4} [{r['category']}] {r['rule']}")
    strats = engine.strategies(policy)
    ledger = learn.gate_ledger(policy, judgments, resolved, coach.starting_policies(policy, strats))
    if ledger:
        print("\nGate ledger (a flat $100 on every edge the strategy saw, by what happened):")
        for name, rows in ledger.items():
            print(f"  {strats.get(name, {}).get('label', name)}:")
            for g in rows:
                print(f"    {g['label']:<34} n={g['n']:>3}  won {g['wins']:>3}  avg {g['pnl_per_100']:+7.2f} per $100")
    cats = learn.category_scores(judgments, resolved, engine._prob)
    if cats:
        print("\nBrier by category (lower is better):")
        for c in cats:
            print(f"  {c['category']:<9} n={c['n']:>3}  Jev+research {c.get('jev_research', float('nan')):.3f}  "
                  f"market {c.get('market', float('nan')):.3f}")
    frozen = set(policy["learning"].get("frozen_strategies") or ())
    print("\nRules now (the daily review tunes them; " + ("on" if policy["learning"].get("auto_tune") else "OFF") + "):")
    for name, s in strats.items():
        now_ = coach.effective_rules(engine.strategy_policy(policy, s))
        start = coach.effective_rules(engine.strategy_policy(policy, dict(s, tuned={})))
        diff = "; ".join(learn.describe_change(k, start[k], now_[k]) for k in learn.RULES if start[k] != now_[k])
        tag = "frozen" if name in frozen else f"v{s['rules_version']}"
        print(f"  {name:<15} {tag:<7} " + (diff + f"  (since {str(s.get('tuned_at') or '?')[:10]})" if diff else "starting rules"))
    for c in engine.read_jsonl(engine.TUNED_LOG)[-5:]:
        print(f"    {str(c.get('ts'))[:16]} {c.get('strategy')} v{c.get('version')}: {str(c.get('why') or '')[:110]}")
    props = coach.load_proposals()["proposals"]
    ideas = [p for p in props if p["kind"] in ("code", "research") and p["status"] == "proposed"]
    if ideas:
        print("\nIdeas waiting for Joey (python3 -m papertrade approve|reject <id>):")
        for p in ideas:
            print(f"  {p['id']:>4} {p['title']}: {p['why'][:160]}")
    if props:
        print("\nProposals:")
        for p in props:
            print(f"  {p['id']:>4} {p['status']:<9} [{p['kind']}] {p['title']}  ({p['status_reason']})")
    return 0


def _raw(policy, name):
    base = dashboard.raw_base(policy)
    with urllib.request.urlopen(urllib.request.Request(base + "papertrade_data/" + name,
                                                       headers={"Cache-Control": "no-cache"}), timeout=20) as r:
        return r.read().decode()


def cmd_health(policy) -> int:
    """Is it trading? Reads the live ledgers on GitHub (what the public page shows) and the last runs."""
    problems = []
    now = datetime.now(timezone.utc)
    if shutil.which("gh"):
        repo = policy["site"]["repo_url"].split("github.com/", 1)[1]
        r = subprocess.run(["gh", "run", "list", "--repo", repo, "--workflow", "trade.yml", "--limit", "6",
                            "--json", "event,status,conclusion,createdAt"], capture_output=True, text=True)
        runs = json.loads(r.stdout or "[]") if r.returncode == 0 else []
        print("Last runs: " + ("  ".join(f"{x['createdAt'][11:16]}Z {x['event'][:8]} {x['conclusion'] or x['status']}"
                                          for x in runs) or "none found"))
        if runs and runs[0]["conclusion"] not in ("success", "", None):
            problems.append(f"the latest run ended {runs[0]['conclusion']}")
        # Cycles are started by the Cloudflare trigger (shown as workflow_dispatch) or GitHub's schedule;
        # which one doesn't matter, only that cycles keep landing (the age check below).
    try:
        scans = [json.loads(l) for l in _raw(policy, "scans.jsonl").splitlines() if l.strip()]
        summary = json.loads(_raw(policy, "summary.json"))
    except Exception as e:
        print(f"Could not read the live data from GitHub: {e}")
        return 1
    last = [x for x in scans if "funnel" in x][-1]
    age_h = (now - datetime.strptime(last["ts"], engine.TS).replace(tzinfo=timezone.utc)).total_seconds() / 3600
    f, cl = last["funnel"], last.get("claude") or {}
    print(f"Last cycle: {last['ts']} ({age_h:.1f} h ago)   fetched {f['fetched']} "
          f"{f.get('by_source') or ''} -> judged {f['judged']} -> with research {f['with_research']}")
    print("  Bets that cycle: " + ", ".join(f"{k} {v}" for k, v in f["bets"].items()))
    for msg in last.get("problems") or []:
        print(f"  problem: {msg}")
    w = (cl.get("rate") or {}).get("unifiedWindows") or {}
    if w:
        print(f"  Claude plan: week {100 * (w.get('seven_day') or {}).get('utilization', 0):.0f}%, "
              f"5-hour {100 * (w.get('five_hour') or {}).get('utilization', 0):.0f}%")
    for s in summary.get("strategies") or []:
        print(f"  {s['label']:<34} ${s['equity']:>12,.2f}  open {s['open']:>3}  settled {s['settled']:>3}")
    if age_h > 1.5:
        problems.append(f"the last cycle was {age_h:.1f} hours ago (cycles should land about every 30 minutes; "
                        "is GITHUB_DISPATCH_TOKEN set on the Cloudflare Worker? see docs/OPERATIONS.md)")
    if last.get("problems"):
        problems.append(f"{len(last['problems'])} problem(s) in the last cycle")
    print("\nHealthy." if not problems else "\nNeeds a look: " + "; ".join(problems))
    return 0 if not problems else 1


def cmd_due(minutes: int) -> int:
    """For the scheduler: print run=true when the last cycle is at least `minutes` old (GitHub drops some
    scheduled slots, so the workflow offers several an hour and this keeps the cadence even)."""
    scans = [s for s in engine.read_jsonl(engine.SCANS) if "funnel" in s]
    if scans:
        last = datetime.strptime(scans[-1]["ts"], engine.TS).replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - last).total_seconds() / 60
        print(f"run={'true' if age >= minutes else 'false'}")
        print(f"The last cycle was {age:.0f} minutes ago; the minimum gap is {minutes}.", file=sys.stderr)
    else:
        print("run=true")
    return 0


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
    sub.add_parser("learn", help="What the learning loop has learned: playbook, calibration, gate ledger, proposals")
    sub.add_parser("health", help="Is it trading? Checks the live ledgers on GitHub and the last hourly runs")
    du = sub.add_parser("due", help="For the scheduler: print run=true if the last cycle is old enough")
    du.add_argument("--minutes", type=int, default=25)
    for name, text in (("approve", "Approve a proposal (a challenger starts on its own fake $100k next cycle)"),
                       ("reject", "Reject a proposal"), ("retire", "Stop a running challenger (its ledger is kept)")):
        c = sub.add_parser(name, help=text)
        c.add_argument("id")
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
    if a.cmd == "learn":
        return cmd_learn(policy)
    if a.cmd == "health":
        return cmd_health(policy)
    if a.cmd == "due":
        return cmd_due(a.minutes)
    if a.cmd in ("approve", "reject", "retire"):
        print(coach.set_status(a.id, {"approve": "running", "reject": "rejected", "retire": "retired"}[a.cmd], policy))
        return 0
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
        print(f"Review: {rv['reviewed']} newly resolved markets scored, {rv['post_mortems']} post-mortems, "
              f"{rv['win_reviews']} reviews of wins" + (" (paused: Claude plan busy)" if rv.get("limited") else "")
              + f", {rv['errors']} errors.\n")
    if cycle:
        c, r = coach.coach(policy), coach.retro(policy)
        if c["ran"] or r["ran"] or c.get("error") or r.get("error"):
            engine.append_jsonl(engine.SCANS, {"ts": engine.now_iso(), "kind": "learning", "coach": c, "retro": r})
        print(f"Learning: playbook v{c['version']}" + (" (updated)" if c["ran"] else "")
              + (", daily review written" if r["ran"] else "")
              + (f", rules changed: {', '.join(r['tuned'])}" if r.get("tuned") else "") + "\n")
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
        import time
        if engine.DATA.exists():
            shutil.move(str(engine.DATA), str(engine.DATA) + time.strftime("-backup-%Y%m%d-%H%M%S"))
        print(f"Fresh ${policy['starting_bankroll']:,} fake bankroll ready.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""python3 -m papertrade {daily|scan|settle|report|ping|markets|reset}"""
from __future__ import annotations

import argparse
import sys

from . import engine
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


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="papertrade",
                                description="Jev paper trading on real prediction markets (fake money only)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("daily", help="The once-a-day routine: settle, then scan, then report")
    sub.add_parser("scan", help="Pull live markets, ask Jev, place fake bets that pass every gate")
    sub.add_parser("settle", help="Pay out fake bets on markets that have resolved")
    sub.add_parser("report", help="Bankroll, P&L, and Jev-vs-market calibration")
    sub.add_parser("ping", help="Check the Jev API key and connection")
    sub.add_parser("markets", help="Preview live markets from each source (no Jev calls, no bets)")
    r = sub.add_parser("reset", help="Start over with a fresh fake bankroll (keeps a backup)")
    r.add_argument("--yes", action="store_true")
    a = p.parse_args(argv)
    policy = engine.load_policy()

    if a.cmd == "ping":
        return cmd_ping(policy)
    if a.cmd == "markets":
        return cmd_markets(policy)
    if a.cmd in ("settle", "daily"):
        s = engine.settle(policy)
        print(f"Settle: checked {s['checked']} closed markets, {s['resolved']} resolved, "
              f"{s['settled_bets']} bets paid out.\n")
    if a.cmd in ("scan", "daily"):
        s = engine.scan(policy)
        print(f"\nScan: fetched {s['fetched']} markets, Jev judged {s['judged']}, "
              f"placed {s['bets']} fake bets ({s['errors']} errors).\n")
    if a.cmd in ("report", "daily"):
        print(engine.report(policy))
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

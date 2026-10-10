"""The mention strategy's forward record so far, read from the committed ledgers (no network, writes nothing).

Two views, each NO bought at the logged ask plus Kalshi's taker fee and the policy's slippage, after fees, with a
95% range that resamples whole events:
  bets         the strategy's own settled bets (the keep-or-kill count in docs/EXPERIMENTS.md, less the one bet the
               registry leaves out)
  first looks  every market's first logged look priced 30-70c at least 6 hours before its event, bet or not: the
               same rule on many more markets, so an earlier read (not the pre-registered test)
Usage: python3 -I docs/research/scripts/mention_forward.py
"""
import collections, json, os, random, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
from papertrade import engine, markets as mk  # noqa: E402

LEFT_OUT = {"kalshi:KXBURNHAMMENTION-26SEP16-UKRA"}  # docs/EXPERIMENTS.md: no event date, decided before it settled


def ci(rows, n=2000):
    g = collections.defaultdict(list)
    for ev, r in rows:
        g[ev].append(r)
    ks, rnd, ms = list(g), random.Random(6), []
    for _ in range(n):
        x = [v for k in (rnd.choice(ks) for _ in ks) for v in g[k]]
        ms.append(sum(x) / len(x))
    ms.sort()
    return sum(r for _, r in rows) / len(rows), ms[int(0.025 * n)], ms[int(0.975 * n) - 1], len(ks)


def show(name, rows, pending):
    if not rows:
        print(f"  {name:12s} none settled yet ({pending} waiting)")
        return
    m, lo, hi, ne = ci(rows)
    print(f"  {name:12s} {len(rows):4d} settled in {ne:3d} events: {m:+6.1%} [{lo:+6.1%}, {hi:+6.1%}]  ({pending} waiting)")


def main():
    policy = json.load(open(os.path.join(ROOT, "policy.json")))
    cfg, slip = policy["mention"], policy["fees"]["slippage"]
    resolved = engine.load_json(engine.RESOLUTIONS, {})
    voids = engine.load_json(engine.VOIDS, {})
    pf = engine.load_portfolio(policy, "mention_no")
    bets = [(b["event"], b["pnl"] / b["total_cost"]) for b in pf["closed"] if b["key"] not in LEFT_OUT and b["total_cost"] > 0]
    first = {}
    for r in engine.read_jsonl(engine.MENTIONS):
        m, k = r["market"], r["key"]
        if k in first or not cfg["band"][0] <= m.get("mid", -1) <= cfg["band"][1] or m.get("no_ask") is None:
            continue
        when = m.get("event_time") or mk.kalshi_event_time(
            {"event_ticker": (m.get("event") or "").split(":", 1)[-1], "title": m.get("question"), "rules_primary": m.get("rules")})
        t = engine._when(when)
        if t is None or t - engine._when(r["ts"]) < engine.timedelta(hours=cfg["hours_before_event"]):
            continue
        first[k] = (r["event"], m["no_ask"], m.get("fee_multiplier"))
    looks, waiting = [], 0
    for k, (ev, ask, mult) in first.items():
        if k in voids:
            continue
        if k not in resolved:
            waiting += 1
            continue
        cost = ask + 0.07 * (1.0 if mult is None else mult) * ask * (1 - ask) + slip
        looks.append((ev, (1 / cost - 1) if resolved[k] == "no" else -1.0))
    print("mention_no forward record, NO after fees:")
    show("bets", bets, len(pf["open"]))
    show("first looks", looks, waiting)


if __name__ == "__main__":
    main()

"""Would resting NO bids beat taking the ask in the mention series the strategy keeps?

Reads the responses mention_timing.py cached under research_data/kalshi/ (one live request: the series list).
For every settled market outside earnings-call and Trump series with volume of 200 or more: at the moment of the
first real NO taker purchase at 30-70c at least 6 hours before the event (the live rule), a NO bid is placed `d`
cents under that price and left until 6 hours before the event. It fills only if a later real trade sold into a NO
bid at or under it (a YES taker printing a NO price at or below the bid), the rule of the honest maker test
(docs/research/CHECKS.md). Fees: taker 0.07, maker 0.0175, times p(1-p) and the series' multiplier.
95% ranges resample whole events.
Usage: python3 -I docs/research/scripts/mention_maker.py
"""
import collections, importlib.util, os, random
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mention_timing", os.path.join(HERE, "mention_timing.py"))
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
SKIP = ("EARNINGS", "TRUMP")


def ci(rows, n=1000):
    g = collections.defaultdict(list)
    for ev, r in rows:
        g[ev].append(r)
    ks, rnd, ms = list(g), random.Random(6), []
    for _ in range(n):
        x = [v for k in (rnd.choice(ks) for _ in ks) for v in g[k]]
        ms.append(sum(x) / len(x))
    ms.sort()
    return sum(r for _, r in rows) / len(rows), ms[int(0.025 * n)], ms[int(0.975 * n) - 1], len(ks)


def ret(price, fee, won):
    cost = price + fee
    return (1 / cost - 1) if won else -1.0


def main():
    series = [s for s in mt.get("/series", {}, cache=False)["series"] if s.get("category") == "Mentions"
              and not any(x in s["ticker"].upper() for x in SKIP)]
    taker, makers, fills = [], {d: [] for d in (0.01, 0.02, 0.04)}, {d: [0, 0, 0, 0] for d in (0.01, 0.02, 0.04)}
    for s in series:
        mult = s.get("fee_multiplier") if s.get("fee_multiplier") is not None else 1.0
        cursor, mks = None, []
        for _ in range(10):
            p = {"series_ticker": s["ticker"], "status": "settled", "limit": 1000}
            if cursor:
                p["cursor"] = cursor
            d = mt.get("/markets", p)
            if not d:
                break
            mks += d.get("markets", [])
            cursor = d.get("cursor")
            if not cursor:
                break
        for m in mks:
            res = (m.get("result") or "").lower()
            if res not in ("yes", "no") or not m.get("open_time") or float(m.get("volume_fp") or m.get("volume") or 0) < 200:
                continue
            trades, cursor = [], None
            for _ in range(30):
                p = {"ticker": m["ticker"], "limit": 1000}
                if cursor:
                    p["cursor"] = cursor
                d = mt.get("/markets/trades", p)
                if not d:
                    break
                trades += d.get("trades", [])
                cursor = d.get("cursor")
                if not cursor:
                    break
            tr = sorted((mt.ts(t["created_time"]), t["taker_side"], float(t["no_price_dollars"]))
                        for t in trades if not t.get("is_block_trade") and t.get("no_price_dollars") is not None)
            if not tr:
                continue
            ev = m.get("event_ticker") or m["ticker"]
            e = mt.get(f"/events/{ev}", {})
            E = mt.event_start(m, ((e or {}).get("event") or {}).get("sub_title") or "", tr[-1][0])
            if E is None:
                continue
            cut = E - timedelta(hours=6)
            first = next((t for t in tr if t[1] == "no" and 0.3 <= t[2] <= 0.7 and t[0] <= cut), None)
            if not first:
                continue
            won = res == "no"
            p0 = first[2]
            taker.append((ev, ret(p0, 0.07 * mult * p0 * (1 - p0), won)))
            for dd in makers:
                bid = round(p0 - dd, 4)
                hit = next((t for t in tr if first[0] < t[0] <= cut and t[1] == "yes" and t[2] <= bid + 1e-9), None)
                f = fills[dd]
                f[0] += 1
                if hit:
                    f[1] += 1
                    f[2] += won
                    makers[dd].append((ev, ret(bid, 0.0175 * mult * bid * (1 - bid), won)))
                else:
                    f[3] += won
    print(f"kept series: {len(series)}; markets with a live-rule purchase: {len(taker)}")
    m, lo, hi, ne = ci(taker)
    print(f"  taking the ask      n={len(taker):5d} events={ne:4d} return {m:+6.1%} [{lo:+6.1%}, {hi:+6.1%}]")
    for dd, rows in makers.items():
        f = fills[dd]
        if len(rows) < 30:
            print(f"  bid {dd * 100:.0f}c under: too few fills ({len(rows)})")
            continue
        m, lo, hi, ne = ci(rows)
        unfilled = f[0] - f[1]
        print(f"  bid {dd * 100:.0f}c under   filled {f[1]}/{f[0]} ({f[1] / f[0]:.0%}) return {m:+6.1%} [{lo:+6.1%}, {hi:+6.1%}]"
              f"  NO won when filled {f[2] / max(f[1], 1):.0%}, when not {f[3] / max(unfilled, 1):.0%}")


if __name__ == "__main__":
    main()

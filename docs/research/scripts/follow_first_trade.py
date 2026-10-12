"""Does following a new market's first trade pay at prices we could really get? (Kalshi mention markets.)

Hypothesis (docs/research/CHECKS.md, "First trades and the trade-print trap"): the first taker in a new mention market
is often informed. A strategy can see that first trade only after it prints, so here the entry is the QUOTED ask
DELTA minutes after the first trade's timestamp (minute candles: the candle that ends at or after t0 + DELTA), never a
trade print. Side S = the first trade's taker side.

Rules, each on markets in series without EARNINGS or TRUMP, quote two-sided with a spread of 10c or less, the side's
ask 0.30-0.85, the entry at least 6 hours before the event start (mention_timing.event_start):
  follow     buy S                      (split: S = NO, S = YES)
  placebo    buy NO whatever S was
  fade       buy the side opposite S
Scored after Kalshi's taker fee at the series' multiplier; 95% ranges resample events; halves by close date.
Uses mention_timing.py's cached listings and trade lists (research_data/kalshi/); fetches one minute-candle window per
market (t0 .. t0 + 70 min). Usage: python3 -I docs/research/scripts/follow_first_trade.py
"""
import collections, importlib.util, json, os
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("mention_timing", os.path.join(HERE, "mention_timing.py"))
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
ROOT = mt.ROOT
OUT = os.path.join(ROOT, "research_data", "follow_first_trade_rows.jsonl")
DELTAS = (1, 5, 15, 30, 60)
SKIP = ("EARNINGS", "TRUMP")


def full_ts(s):
    """Kalshi's created_time with its fraction of a second kept."""
    from datetime import datetime, timezone
    return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)


def quote_at(candles, t):
    """(yes_bid, yes_ask) from the first minute candle ending at or after t, or None."""
    for c in candles:
        if c["end_period_ts"] >= t:
            try:
                bid = float((c.get("yes_bid") or {}).get("close_dollars") or 0)
                ask = float((c.get("yes_ask") or {}).get("close_dollars") or 1)
            except ValueError:
                return None
            return (bid, ask) if 0 < bid < ask < 1 and ask - bid <= 0.10 else None
    return None


def collect():
    series = [s for s in mt.get("/series", {}, cache=False)["series"]
              if s.get("category") == "Mentions" and not any(x in s["ticker"].upper() for x in SKIP)]
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(l)["ticker"] for l in open(OUT) if l.strip()}
    out = open(OUT, "a")
    n = 0
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
            if res not in ("yes", "no") or not m.get("open_time") or m["ticker"] in done:
                continue
            trades, cursor = [], None
            for _ in range(30):  # the full list, as mention_timing cached it (newest first, paged to the end)
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
            # full-precision times, no tie-break on side (a same-second YES and NO must not resolve to "no" by spelling)
            tr = sorted(((full_ts(t["created_time"]), i), t["taker_side"]) for i, t in enumerate(reversed(trades))
                        if not t.get("is_block_trade"))
            tr = [(x[0][0], x[1]) for x in tr]
            if not tr:
                continue
            ev = m.get("event_ticker") or m["ticker"]
            e = mt.get(f"/events/{ev}", {})
            E = mt.event_start(m, ((e or {}).get("event") or {}).get("sub_title") or "", tr[-1][0])
            t0, side = tr[0]
            if E is None or t0 + timedelta(minutes=1) > E - timedelta(hours=6):
                continue
            c = mt.get(f"/series/{s['ticker']}/markets/{m['ticker']}/candlesticks",
                       {"start_ts": int(t0.timestamp()) - 60, "end_ts": int((t0 + timedelta(minutes=70)).timestamp()),
                        "period_interval": 1}) or {}
            cs = sorted(c.get("candlesticks") or [], key=lambda x: x["end_period_ts"])
            row = {"ticker": m["ticker"], "series": s["ticker"], "event": ev, "close": m["close_time"], "result": res,
                   "mult": mult, "first_side": side, "quotes": {}}
            for dmin in DELTAS:
                t = t0 + timedelta(minutes=dmin)
                if t > E - timedelta(hours=6):
                    continue
                q = quote_at(cs, int(t.timestamp()))
                if q:
                    row["quotes"][str(dmin)] = q
            out.write(json.dumps(row) + "\n")
            out.flush()
            done.add(m["ticker"])
            n += 1
            if n % 250 == 0:
                print(f"  markets {n}, requests {mt.requests}", flush=True)
    out.close()
    print(f"done: markets {len(done)}, requests {mt.requests}", flush=True)


def ret(price, mult, won):
    cost = price + 0.07 * mult * price * (1 - price)
    return (1 / cost - 1) if won else -1.0


def summarize():
    rows = [json.loads(l) for l in open(OUT) if l.strip()]
    print(f"markets: {len(rows)}; first trade NO: {sum(r['first_side'] == 'no' for r in rows)}, YES: "
          f"{sum(r['first_side'] == 'yes' for r in rows)}")
    for dmin in DELTAS:
        cuts = collections.defaultdict(list)
        for r in rows:
            q = r["quotes"].get(str(dmin))
            if not q:
                continue
            bid, ask = q
            price = {"yes": ask, "no": 1 - bid}
            S, other = r["first_side"], ("no" if r["first_side"] == "yes" else "yes")
            for rule, buy in ((f"follow (S={S.upper()})", S), ("follow (any)", S), ("placebo NO", "no"), ("fade", other)):
                p = price[buy]
                if 0.30 <= p <= 0.85:
                    cuts[rule].append((r["event"], r["close"], ret(p, r["mult"], r["result"] == buy)))
        print(f"\nDELTA {dmin} min after the first trade, at the quoted ask:")
        for rule in sorted(cuts):
            v = cuts[rule]
            if len({e for e, _, _ in v}) < 20:
                print(f"  {rule:18s} too few ({len(v)})")
                continue
            m, lo, hi, ne = mt.ci([{"ev": e, "r": x} for e, _, x in v])
            v.sort(key=lambda x: x[1])
            h = len(v) // 2
            older, newer = sum(x for _, _, x in v[:h]) / h, sum(x for _, _, x in v[h:]) / (len(v) - h)
            print(f"  {rule:18s} n={len(v):5d} events={ne:4d} {m:+6.1%} [{lo:+6.1%},{hi:+6.1%}] halves {older:+6.1%} / {newer:+6.1%}")


if __name__ == "__main__":
    import sys
    summarize() if "--summarize" in sys.argv else collect()

"""Is the first price in a newly listed Kalshi market wrong in a steady direction, in every kind of market?

The mention markets' edge sat in brand-new markets (+35.9% when our purchase was the market's first trade, +2.8%
otherwise; docs/research/CHECKS.md). This tests that idea everywhere. Kalshi public data only.

Sample: the series in research_data/edge_scan_rows_v2.jsonl (active, non-mention), each one's cached settled listing,
events spread evenly across the listing's time range (never chosen by outcome or volume), every market of an event
with 4 or fewer, else a random 4 seeded by the event. For each market, the trades in its first 48 hours
(/markets/trades with min_ts and max_ts, one request), and the first real taker purchase of each side that came at
least 12 hours before the scheduled occurrence_datetime (set in advance; so before the outcome could be known), scored
after Kalshi's taker fee at the series' multiplier. `first` marks a purchase that was the market's very first trade.

--summarize: by category, side and price band, and split by first-trade or not: purchases, events, return after fees,
95% range resampling events, and the older and newer halves by close date. A lead needs the range above zero, both
halves above zero and 30+ events; the number of cuts tested and the leads expected by chance are printed.

Usage: python3 -I docs/research/scripts/first_trade_scan.py [--per-series 30] [--max-requests 25000]
       python3 -I docs/research/scripts/first_trade_scan.py --summarize
"""
import argparse, collections, hashlib, importlib.util, json, os, random
from datetime import timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("edge_scan", os.path.join(HERE, "edge_scan.py"))
es = importlib.util.module_from_spec(spec)
spec.loader.exec_module(es)
ROOT = es.ROOT
ROWS = os.path.join(ROOT, "research_data", "first_trade_rows.jsonl")
LISTING_TAG = "2026-10-10"  # the day edge_scan cached the settled listings


def spread(items, k):
    """k items spread evenly through a list (or all of it when shorter)."""
    if len(items) <= k:
        return items
    step = len(items) / k
    return [items[int(i * step)] for i in range(k)]


def collect(a):
    v2 = [json.loads(l) for l in open(os.path.join(ROOT, "research_data", "edge_scan_rows_v2.jsonl")) if l.strip()]
    series = sorted({r["series"] for r in v2})
    cat = {r["series"]: r["category"] for r in v2}
    meta = {s["ticker"]: s for s in (es.get("/series", {}, tag=LISTING_TAG) or {}).get("series", [])}
    done = set()
    if os.path.exists(ROWS):
        done = {json.loads(l)["ticker"] for l in open(ROWS) if l.strip()}
    out = open(ROWS, "a")
    start = es.requests
    print(f"series: {len(series)}", flush=True)
    for i, t in enumerate(series):
        if es.requests - start >= a.max_requests:
            print(f"request budget reached at series {i}/{len(series)}", flush=True)
            break
        mult = (meta.get(t) or {}).get("fee_multiplier")
        mult = 1.0 if mult is None else mult
        d = es.get("/markets", {"series_ticker": t, "status": "settled", "limit": 200}, tag=LISTING_TAG) or {}
        by_event = collections.defaultdict(list)
        for m in d.get("markets", []):
            if (m.get("result") or "").lower() in ("yes", "no") and m.get("open_time") and m.get("occurrence_datetime") \
                    and not str(m.get("ticker", "")).upper().startswith("KXMVE"):
                by_event[m.get("event_ticker") or m["ticker"]].append(m)
        events = sorted(by_event, key=lambda ev: min(x["close_time"] for x in by_event[ev]))
        picked = []
        for ev in spread(events, max(1, a.per_series // 2)):
            ms = sorted(by_event[ev], key=lambda x: x["ticker"])
            if len({x["occurrence_datetime"] for x in ms}) != 1:
                continue
            rnd = random.Random(int(hashlib.sha1(ev.encode()).hexdigest()[:8], 16))
            picked += ms if len(ms) <= 4 else rnd.sample(ms, 4)
        for m in picked[: a.per_series]:
            if m["ticker"] in done:
                continue
            opened, occ, close = es.ts(m["open_time"]), es.ts(m["occurrence_datetime"]), es.ts(m["close_time"])
            last_ok = min(opened + timedelta(hours=48), occ - timedelta(hours=12), close)
            row = {"ticker": m["ticker"], "series": t, "category": cat.get(t), "event": m.get("event_ticker"),
                   "close": m["close_time"], "result": m["result"].lower(), "mult": mult, "buys": {}}
            if last_ok > opened:
                tr = es.get("/markets/trades", {"ticker": m["ticker"], "min_ts": int(opened.timestamp()),
                                                "max_ts": int(last_ok.timestamp()), "limit": 1000}) or {}
                trades = sorted((es.ts(x["created_time"]), x["taker_side"], float(x["yes_price_dollars"]), float(x["no_price_dollars"]))
                                for x in tr.get("trades", []) if not x.get("is_block_trade"))
                for side in ("yes", "no"):
                    j = next((k for k, x in enumerate(trades) if x[1] == side), None)
                    if j is None:
                        continue
                    price = trades[j][2] if side == "yes" else trades[j][3]
                    if not 0.02 <= price <= 0.98:
                        continue
                    cost = price + 0.07 * mult * price * (1 - price)
                    won = row["result"] == side
                    row["buys"][side] = {"price": price, "first": j == 0, "r": (1 / cost - 1) if won else -1.0,
                                         "hours_after_open": round((trades[j][0] - opened).total_seconds() / 3600, 2)}
            out.write(json.dumps(row) + "\n")
            out.flush()
            done.add(m["ticker"])
        if (i + 1) % 50 == 0:
            print(f"  series {i + 1}/{len(series)}: markets {len(done)}, requests {es.requests - start}", flush=True)
    out.close()
    print(f"done: markets {len(done)}, requests {es.requests - start}; rows in {ROWS}", flush=True)


def summarize(min_events=30):
    rows = [json.loads(l) for l in open(ROWS) if l.strip()]
    print(f"markets: {len(rows)} in {len({r['series'] for r in rows})} series; with a purchase: "
          f"{sum(1 for r in rows if r['buys'])}")
    cuts = collections.defaultdict(list)
    for r in rows:
        for side, b in r["buys"].items():
            band = next((x for x in es.BANDS if x[0] <= b["price"] < x[1]), None)
            if not band:
                continue
            for split in ("any", "first trade" if b["first"] else "after others"):
                cuts[(r["category"], side, band, split)].append((r["event"], r["close"], b["r"]))
    table, leads, tested = [], [], 0
    for k, v in cuts.items():
        if len({e for e, _, _ in v}) < min_events:
            continue
        tested += 1
        m, lo, hi, ne = es.ci([(e, x) for e, _, x in v])
        v.sort(key=lambda x: x[1])
        h = len(v) // 2
        older, newer = sum(x for _, _, x in v[:h]) / h, sum(x for _, _, x in v[h:]) / (len(v) - h)
        rec = (k, len(v), ne, m, lo, hi, older, newer)
        table.append(rec)
        if lo > 0 and older > 0 and newer > 0:
            leads.append(rec)
    fmt = lambda r: (f"{str(r[0][0])[:22]:22s} {r[0][1]:3s} {r[0][2][0]:.2f}-{r[0][2][1]:.2f} {r[0][3]:12s} n={r[1]:5d} "
                     f"ev={r[2]:4d} {r[3]:+6.1%} [{r[4]:+6.1%},{r[5]:+6.1%}] halves {r[6]:+6.1%} / {r[7]:+6.1%}")
    print("\nEvery cut with 30+ events (first real taker purchase in the first 48 h, 12 h+ before the scheduled time):")
    for r in sorted(table, key=lambda r: (str(r[0][0]), r[0][1], r[0][2], r[0][3])):
        print("  " + fmt(r))
    print(f"\nLeads: {len(leads)} of {tested} cuts; about {tested * 0.015:.0f} expected by chance alone")
    for r in sorted(leads, key=lambda r: -r[3]):
        print("  " + fmt(r))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-series", type=int, default=30)
    ap.add_argument("--max-requests", type=int, default=25000)
    ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args()
    summarize() if a.summarize else collect(a)

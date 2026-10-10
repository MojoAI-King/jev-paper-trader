"""Scan every Kalshi market family for prices that are wrong in a steady direction: the mention-market finding
(docs/research/CHECKS.md), tried everywhere. Kalshi public data only, no account.

Phase 1: the series trading now (open events, paged: about 80 requests), then each one's most recent settled markets
closed within --days (one request per series). Phase 2: up to --per-series markets per series, at most --per-event
per event, volume of --min-volume or more: the hourly candles for the week before each market's close (one request
each; Kalshi moves close_time to the real close when a market closes early). At 24 and 72 hours before the close,
where the quote is real (bid above 0, ask under 1, spread 10c or less), it scores buying YES at the ask and NO at one
minus the bid, after Kalshi's taker fee at the series' multiplier. Rows are appended to
research_data/edge_scan_rows.jsonl as they come, so --summarize can read a partial run, and a rerun skips what is done.

--summarize: by category and by series, each side, price band and horizon: purchases, events, return after fees, a
95% range that resamples events, and the older and newer halves by close date. A lead needs the range above zero, both
halves above zero and 30+ events. Hundreds of cuts are tried, so some pass by luck: a lead earns a forward test, not
money.

Usage: python3 -I docs/research/scripts/edge_scan.py [--days 120] [--max-candles 30000] [--limit-series N]
       python3 -I docs/research/scripts/edge_scan.py --summarize
"""
import argparse, collections, hashlib, json, os, random, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from itertools import zip_longest

API = "https://api.elections.kalshi.com/trade-api/v2"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CACHE = os.path.join(ROOT, "research_data", "kalshi")
ROWS = os.path.join(ROOT, "research_data", "edge_scan_rows.jsonl")
BANDS = ((0.02, 0.15), (0.15, 0.30), (0.30, 0.50), (0.50, 0.70), (0.70, 0.85), (0.85, 0.98))
requests = 0


def get(path, params, tag=""):
    """GET with retries; cached by path, params and `tag` (a day stamp for lists that change)."""
    global requests
    q = urllib.parse.urlencode(sorted(params.items()))
    f = os.path.join(CACHE, hashlib.sha1(f"{tag}{path}?{q}".encode()).hexdigest() + ".json")
    if os.path.exists(f):
        with open(f) as fh:
            return json.load(fh)
    req = urllib.request.Request(f"{API}{path}?{q}", headers={"User-Agent": "jev-paper-trader research"})
    d = None
    for a in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                break
            time.sleep(2 + 4 * a)
        except Exception:
            time.sleep(2 + 4 * a)
    requests += 1
    time.sleep(0.12)
    if d is not None:
        os.makedirs(CACHE, exist_ok=True)
        with open(f, "w") as fh:
            json.dump(d, fh)
    return d


def ts(s):
    return datetime.strptime(s[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


def fee(p, mult):
    return 0.07 * mult * p * (1 - p)


def collect(a):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    since = datetime.now(timezone.utc) - timedelta(days=a.days)
    meta = {s["ticker"]: s for s in (get("/series", {}, tag=today) or {}).get("series", [])}
    print(f"series known: {len(meta)}", flush=True)
    active, cursor, pages = collections.Counter(), "", 0
    while pages < 400:  # open events, paged (about 80 pages): the series that are trading now
        p = {"status": "open", "limit": 200}
        if cursor:
            p["cursor"] = cursor
        d = get("/events", p, tag=today)
        pages += 1
        if not d:
            break
        for e in d.get("events", []):
            if e.get("series_ticker"):
                active[e["series_ticker"]] += 1
        cursor = d.get("cursor") or ""
        if not cursor or not d.get("events"):
            break
    by_cat = collections.defaultdict(list)  # busiest first within each category
    for t, _ in active.most_common():
        cat = (meta.get(t) or {}).get("category")
        if cat != "Mentions":
            by_cat[cat].append(t)
    # categories in turn, so a run cut short by its budget still covers every kind of market
    series = [t for group in zip_longest(*by_cat.values()) for t in group if t]
    if a.limit_series:
        series = series[: a.limit_series]
    print(f"series with open events: {len(active)}; scanning {len(series)} (Mentions done separately); "
          f"event pages {pages}", flush=True)
    done = set()
    if os.path.exists(ROWS):
        with open(ROWS) as fh:
            done = {json.loads(l)["ticker"] for l in fh if l.strip()}
    candles = 0
    out = open(ROWS, "a")
    for i, t in enumerate(series):
        if candles >= a.max_candles:
            print(f"candle budget reached at series {i}/{len(series)}", flush=True)
            break
        s = meta.get(t) or {}
        mult = s.get("fee_multiplier") if s.get("fee_multiplier") is not None else 1.0
        d = get("/markets", {"series_ticker": t, "status": "settled", "limit": 200}, tag=today) or {}
        by_event = collections.defaultdict(list)
        for m in d.get("markets", []):
            if (m.get("result") or "").lower() not in ("yes", "no") or not m.get("close_time"):
                continue
            if float(m.get("volume_fp") or m.get("volume") or 0) < a.min_volume or ts(m["close_time"]) < since:
                continue
            if str(m.get("ticker", "")).upper().startswith("KXMVE"):
                continue
            by_event[m.get("event_ticker") or m["ticker"]].append(m)
        picked = []
        for ev, ms in sorted(by_event.items(), key=lambda kv: max(x["close_time"] for x in kv[1]), reverse=True):
            ms.sort(key=lambda x: float(x.get("volume_fp") or x.get("volume") or 0), reverse=True)
            picked += ms[: a.per_event]
            if len(picked) >= a.per_series:
                break
        for m in picked[: a.per_series]:
            if m["ticker"] in done:
                continue
            close = ts(m["close_time"])
            c = get(f"/series/{t}/markets/{m['ticker']}/candlesticks",
                    {"start_ts": int((close - timedelta(days=7)).timestamp()), "end_ts": int(close.timestamp()),
                     "period_interval": 60})
            candles += 1
            cs = (c or {}).get("candlesticks") or []
            row = {"ticker": m["ticker"], "series": t, "category": s.get("category"), "event": m.get("event_ticker"),
                   "close": m["close_time"], "result": m["result"].lower(), "mult": mult, "at": {}}
            for h in (24, 72):
                before = [x for x in cs if x["end_period_ts"] <= int((close - timedelta(hours=h)).timestamp())]
                if not before:
                    continue
                q = before[-1]
                try:
                    bid = float((q.get("yes_bid") or {}).get("close_dollars") or 0)
                    ask = float((q.get("yes_ask") or {}).get("close_dollars") or 1)
                except ValueError:
                    continue
                if bid <= 0 or ask >= 1 or ask <= bid or ask - bid > 0.10:
                    continue
                won_yes = row["result"] == "yes"
                no = 1 - bid
                row["at"][str(h)] = {"bid": bid, "ask": ask,
                                     "r_yes": (1 / (ask + fee(ask, mult)) - 1) if won_yes else -1.0,
                                     "r_no": (1 / (no + fee(no, mult)) - 1) if not won_yes else -1.0}
            out.write(json.dumps(row) + "\n")
            out.flush()
            done.add(m["ticker"])
        if (i + 1) % 50 == 0:
            print(f"  series {i + 1}/{len(series)}: candles {candles}, requests {requests}", flush=True)
    out.close()
    print(f"done: candles {candles}, requests {requests}; rows in {ROWS}", flush=True)


def ci(rows, n=500):
    g = collections.defaultdict(list)
    for ev, r in rows:
        g[ev].append(r)
    ks, rnd, ms = list(g), random.Random(6), []
    for _ in range(n):
        x = [v for k in (rnd.choice(ks) for _ in ks) for v in g[k]]
        ms.append(sum(x) / len(x))
    ms.sort()
    return sum(r for _, r in rows) / len(rows), ms[int(0.025 * n)], ms[int(0.975 * n) - 1], len(ks)


def summarize(min_events=30):
    rows = [json.loads(l) for l in open(ROWS) if l.strip()]
    print(f"markets scored: {len(rows)} in {len({r['series'] for r in rows})} series")
    cuts = collections.defaultdict(list)  # (level, name, side, band, h) -> [(event, close, return)]
    for r in rows:
        for h, q in r["at"].items():
            for side in ("yes", "no"):
                price = q["ask"] if side == "yes" else 1 - q["bid"]
                band = next((b for b in BANDS if b[0] <= price < b[1]), None)
                if not band:
                    continue
                for level, name in (("category", r["category"]), ("series", r["series"])):
                    cuts[(level, name, side, band, h)].append((r["event"], r["close"], q[f"r_{side}"]))
    leads, table = [], []
    for k, v in cuts.items():
        evs = {e for e, _, _ in v}
        if len(evs) < min_events:
            continue
        m, lo, hi, ne = ci([(e, x) for e, _, x in v])
        v.sort(key=lambda x: x[1])
        half = len(v) // 2
        older = sum(x for _, _, x in v[:half]) / max(half, 1)
        newer = sum(x for _, _, x in v[half:]) / max(len(v) - half, 1)
        rec = (k, len(v), ne, m, lo, hi, older, newer)
        if k[0] == "category" and k[4] == "24":
            table.append(rec)
        if lo > 0 and older > 0 and newer > 0:
            leads.append(rec)
    fmt = lambda r: (f"{r[0][0]:8s} {str(r[0][1])[:28]:28s} {r[0][2]:3s} {r[0][3][0]:.2f}-{r[0][3][1]:.2f} {r[0][4]:>2s}h "
                     f"n={r[1]:5d} ev={r[2]:4d} {r[3]:+6.1%} [{r[4]:+6.1%},{r[5]:+6.1%}] halves {r[6]:+6.1%} / {r[7]:+6.1%}")
    print("\nBy category, 24 hours before close (return after taker fees; 95% range resamples events):")
    for r in sorted(table, key=lambda r: (str(r[0][1]), r[0][2], r[0][3])):
        print("  " + fmt(r))
    print(f"\nLeads (range above zero, both halves above zero, {min_events}+ events): {len(leads)}")
    for r in sorted(leads, key=lambda r: -r[3])[:60]:
        print("  " + fmt(r))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=120)
    ap.add_argument("--per-series", type=int, default=20)
    ap.add_argument("--per-event", type=int, default=3)
    ap.add_argument("--min-volume", type=float, default=100)
    ap.add_argument("--max-candles", type=int, default=30000)
    ap.add_argument("--limit-series", type=int, default=0)
    ap.add_argument("--summarize", action="store_true")
    a = ap.parse_args()
    summarize() if a.summarize else collect(a)

"""Does the YES optimism in Kalshi mention markets still pay when NO is bought later in a market's life?

Kalshi public data only, no account. For every settled market with volume of 200 or more in every "Mentions" series
(closed within --days), it finds real NO taker purchases and scores them after Kalshi's taker fee at the series'
multiplier. A purchase's timing is measured against the event's start E, the earliest of: the market's occurrence
time (when more than a day before its close), a date in the event's subtitle or the market's rules ("On Oct 13,
2026", read as midnight New York time), the date in the event ticker (-26OCT13), and the market's last trade
(these markets close early when the event ends). 95% ranges resample whole events.

Rules reported, each on the purchases at 30-70c:
  first48   the first NO purchase within 48 hours of listing (and the first quarter of its life): the 2026-10-10 test
  live      the first NO purchase priced 30-70c at least 6 hours before E: what the live strategy does
  before:X  the first NO purchase in a window of hours before E
  after_E   the first NO purchase after E, before the last trade: a bet during or after the event

Raw responses are cached under research_data/kalshi/ (gitignored), so a rerun spends no requests.
Usage: python3 -I docs/research/scripts/mention_timing.py [--days 400]
"""
import argparse, collections, hashlib, json, os, random, re, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

API = "https://api.elections.kalshi.com/trade-api/v2"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CACHE = os.path.join(ROOT, "research_data", "kalshi")
MON = {m: i for i, m in enumerate("JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split(), 1)}
TEXT_DATE = re.compile(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2}),?\s+(20\d\d)\b")
TICKER_DATE = re.compile(r"-(\d\d)(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)(\d\d)(?![0-9])")
requests = 0


def get(path, params, cache=True):
    global requests
    q = urllib.parse.urlencode(sorted(params.items()))
    f = os.path.join(CACHE, hashlib.sha1(f"{path}?{q}".encode()).hexdigest() + ".json")
    if cache and os.path.exists(f):
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
            if e.code == 404:
                return None
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


def day_start(y, mo, d):
    return datetime(y, mo, d, 4, tzinfo=timezone.utc)  # midnight in New York (EDT); an hour early in winter


def event_start(m, sub_title, last_trade):
    """The earliest credible time the event could start (see the module docstring)."""
    c = []
    occ, close = m.get("occurrence_datetime"), m.get("close_time")
    if occ and close and ts(occ) < ts(close) - timedelta(days=1):
        c.append(ts(occ))
    for text in (sub_title or "", m.get("rules_primary") or ""):
        for mo, d, y in TEXT_DATE.findall(text):
            try:
                c.append(day_start(int(y), MON[mo.upper()[:3]], int(d)))
            except ValueError:
                pass
    t = TICKER_DATE.search(m.get("event_ticker") or "")
    if t:
        try:
            c.append(day_start(2000 + int(t.group(1)), MON[t.group(2)], int(t.group(3))))
        except ValueError:
            pass
    if last_trade:
        c.append(last_trade)
    opened = ts(m["open_time"])
    c = [x for x in c if x > opened]
    return min(c) if c else None


def kind(series):
    s = series.upper()
    for k in ("EARNINGS", "FED", "TRUMP", "DEBATE", "NFL", "NBA", "MLB", "NHL", "NCAA", "SNL"):
        if k in s:
            return {"NFL": "sports", "NBA": "sports", "MLB": "sports", "NHL": "sports", "NCAA": "sports"}.get(k, k.lower())
    return "other"


def ci(rows, n=1000):
    g = collections.defaultdict(list)
    for r in rows:
        g[r["ev"]].append(r["r"])
    ks, rnd, ms = list(g), random.Random(6), []
    for _ in range(n):
        x = [v for k in (rnd.choice(ks) for _ in ks) for v in g[k]]
        ms.append(sum(x) / len(x))
    ms.sort()
    return sum(r["r"] for r in rows) / len(rows), ms[int(0.025 * n)], ms[int(0.975 * n) - 1], len(ks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=400)
    a = ap.parse_args()
    since = datetime.now(timezone.utc) - timedelta(days=a.days)
    series = [s for s in get("/series", {}, cache=False)["series"] if s.get("category") == "Mentions"]
    print(f"Mentions series: {len(series)}", flush=True)
    rows, n_mk, events_meta = collections.defaultdict(list), 0, {}
    for i, s in enumerate(series):
        mult = s.get("fee_multiplier") if s.get("fee_multiplier") is not None else 1.0
        cursor, mks = None, []
        for _ in range(10):
            p = {"series_ticker": s["ticker"], "status": "settled", "limit": 1000}
            if cursor:
                p["cursor"] = cursor
            d = get("/markets", p)
            if not d:
                break
            mks += d.get("markets", [])
            cursor = d.get("cursor")
            if not cursor:
                break
        for m in mks:
            res = (m.get("result") or "").lower()
            if res not in ("yes", "no") or not m.get("open_time") or not m.get("close_time"):
                continue
            if float(m.get("volume_fp") or m.get("volume") or 0) < 200 or ts(m["close_time"]) < since:
                continue
            trades, cursor = [], None
            for _ in range(30):
                p = {"ticker": m["ticker"], "limit": 1000}
                if cursor:
                    p["cursor"] = cursor
                d = get("/markets/trades", p)
                if not d:
                    break
                trades += d.get("trades", [])
                cursor = d.get("cursor")
                if not cursor:
                    break
            tr = sorted((ts(t["created_time"]), t["taker_side"], float(t["no_price_dollars"]))
                        for t in trades if not t.get("is_block_trade") and t.get("no_price_dollars") is not None)
            if not tr:
                continue
            ev = m.get("event_ticker") or m["ticker"]
            if ev not in events_meta:
                e = get(f"/events/{ev}", {})
                events_meta[ev] = ((e or {}).get("event") or {}).get("sub_title") or ""
            E = event_start(m, events_meta[ev], tr[-1][0])
            if E is None:
                continue
            n_mk += 1
            opened, closed = ts(m["open_time"]), ts(m["close_time"])
            nos = [t for t in tr if t[1] == "no"]

            def score(rule, t):
                pr = t[2]
                if not 0.02 <= pr <= 0.98:
                    return
                cost = pr + 0.07 * mult * pr * (1 - pr)
                rows[rule].append({"p": pr, "r": (1 / cost - 1) if res == "no" else -1.0, "won": res == "no",
                                   "ev": ev, "kind": kind(s["ticker"]), "h": (E - t[0]).total_seconds() / 3600})

            end48 = opened + min(timedelta(hours=48), max(timedelta(hours=1), (closed - opened) / 4))
            t = next((t for t in nos if t[0] <= end48 and t[0] < E), None)
            if t:
                score("first48", t)
            t = next((t for t in nos if 0.3 <= t[2] <= 0.7 and t[0] <= E - timedelta(hours=6)), None)
            if t:
                score("live", t)
            for lo, hi in ((168, 1e5), (72, 168), (24, 72), (6, 24), (0, 6)):  # 1e5 hours: about 11 years, i.e. any time
                t = next((t for t in nos if E - timedelta(hours=hi) <= t[0] < E - timedelta(hours=lo)), None)
                if t:
                    score(f"before:{lo}-{hi if hi < 1e5 else 'inf'}h", t)
            t = next((t for t in nos if t[0] >= E), None)
            if t:
                score("after_E", t)
        if (i + 1) % 25 == 0:
            print(f"  series {i + 1}/{len(series)}: markets scored {n_mk}, requests {requests}", flush=True)
    out = os.path.join(ROOT, "research_data", "mention_timing_rows.json")
    with open(out, "w") as fh:
        json.dump(rows, fh)
    print(f"\nsettled mention markets scored: {n_mk}; requests {requests}; rows saved to {out}")
    print("\nNO at 30-70c after the taker fee (95% range resamples events):")
    for rule in ["first48", "live", "before:168-infh", "before:72-168h", "before:24-72h", "before:6-24h", "before:0-6h", "after_E"]:
        rs = [r for r in rows.get(rule, []) if 0.3 <= r["p"] <= 0.7]
        if len(rs) < 30:
            print(f"  {rule:16s} too few ({len(rs)})")
            continue
        m, lo, hi, ne = ci(rs)
        won, implied = sum(r["won"] for r in rs) / len(rs), sum(r["p"] for r in rs) / len(rs)
        print(f"  {rule:16s} n={len(rs):5d} events={ne:4d} won {won:.1%} vs price {implied:.1%}  return {m:+6.1%} [{lo:+6.1%}, {hi:+6.1%}]")
    print("\nlive rule by kind of series:")
    for k in sorted({r["kind"] for r in rows.get("live", [])}):
        rs = [r for r in rows["live"] if r["kind"] == k and 0.3 <= r["p"] <= 0.7]
        if len(rs) < 30:
            print(f"  {k:10s} too few ({len(rs)})")
            continue
        m, lo, hi, ne = ci(rs)
        print(f"  {k:10s} n={len(rs):5d} events={ne:4d} return {m:+6.1%} [{lo:+6.1%}, {hi:+6.1%}]")


if __name__ == "__main__":
    main()

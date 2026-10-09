"""Read-only public market data from Polymarket (Gamma API) and Kalshi.

Every market is normalized to:
  {source, market_id, event, question, rules, close_time (ISO), yes_ask, no_ask, mid,
   volume, url}
`event` groups markets that share one real-world event (researched once, together).
Resolution check returns "yes", "no", or None (unresolved).
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

UA = {"User-Agent": "jev-papertrade/0.1", "Accept": "application/json"}
POLY = "https://gamma-api.polymarket.com"
KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
MAX_PAGES = 25   # hard stop per source per fetch, so a feed that never runs dry can't loop forever
POLY_PAGE = 100
RETRIES = 5      # tries per request on "too many requests" (429) or a server error (5xx): waits 3+6+12+24s
KALSHI_PAGE = 1000       # Kalshi's largest page (about 2 MB)
KALSHI_PAGE_PAUSE = 1.0  # seconds between Kalshi pages: GitHub's shared runners hit its rate limit (429)
KALSHI_MAX_PAGES = 60    # all slices together; the whole 30-day window was about 32 pages on 2026-09-28
KALSHI_SLICES = (timedelta(hours=12), timedelta(days=3), timedelta(days=7))  # slice edges, soonest first
KALSHI_BATCH = 50        # tickers per settlement check (61 came back in one call on 2026-09-28)
KALSHI_DEADLINE = 300    # seconds: a walk still going after this stops, keeping what it has (65 s measured)
LAST_FETCH: dict = {}    # source -> what the last fetch did (pages, seconds, cut short, error), for the scan log
_sleep = time.sleep  # swapped out in tests


def _retry_wait(e: urllib.error.HTTPError, attempt: int) -> float:
    try:
        return min(60.0, float(e.headers.get("Retry-After")))
    except (TypeError, ValueError):
        return 3.0 * 2 ** attempt  # 3, 6, 12, 24 seconds


def _get(url: str, params: dict | None = None, timeout: float = 20) -> object:
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    for attempt in range(RETRIES):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            # Keep the API's own explanation: a bare "422 Unprocessable Entity" hid a bad sort field.
            with e:
                detail = e.read().decode(errors="replace")[:300]
            if (e.code == 429 or e.code >= 500) and attempt < RETRIES - 1:
                _sleep(_retry_wait(e, attempt))
                continue
            raise RuntimeError(f"HTTP {e.code} from {url.split('?')[0]}: {detail}") from None


def _f(x, default=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _utc(s) -> str | None:
    """'2026-09-28 19:25:00+00' (Polymarket's gameStartTime) -> '2026-09-28T19:25:00Z', or None."""
    text = re.sub(r"([+-]\d\d)$", r"\1:00", str(s or "").strip().replace(" ", "T").replace("Z", "+00:00"))
    try:
        d = datetime.fromisoformat(text)
    except ValueError:
        return None
    return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------- Polymarket ----------

def _poly_fee_rate(m: dict) -> float | None:
    """The market's own taker fee rate (fee per share = rate x p x (1 - p), docs.polymarket.com/trading/fees),
    from its `feeSchedule`. 0 when `feesEnabled` is false; None when the market says nothing."""
    if m.get("feesEnabled") is False:
        return 0.0
    rate = _f((m.get("feeSchedule") or {}).get("rate"))
    return rate if m.get("feesEnabled") and rate is not None and rate >= 0 else None


def normalize_polymarket(m: dict) -> dict | None:
    try:
        outcomes = json.loads(m.get("outcomes") or "[]")
        prices = [float(p) for p in json.loads(m.get("outcomePrices") or "[]")]
    except (ValueError, TypeError):
        return None
    if [o.lower() for o in outcomes] != ["yes", "no"] or len(prices) != 2:
        return None  # binary Yes/No markets only
    best_bid, best_ask = _f(m.get("bestBid")), _f(m.get("bestAsk"))
    yes_ask = best_ask if best_ask else prices[0]
    no_ask = (1 - best_bid) if best_bid else prices[1]
    events = m.get("events") if isinstance(m.get("events"), list) else []
    return {
        "source": "polymarket",
        "market_id": str(m.get("id")),
        "event": f"polymarket:{events[0].get('id')}" if events and events[0].get("id") else f"polymarket:m{m.get('id')}",
        "question": m.get("question", ""),
        "rules": (m.get("description") or "")[:4000],
        "close_time": m.get("endDate"),
        # a sports market's endDate is about a week after the match; gameStartTime is the match itself.
        # Other markets' gameStartTime is the start of a counting period, so only sports keep it.
        "starts": _utc(m.get("gameStartTime")) if m.get("sportsMarketType") else None,
        "yes_ask": round(yes_ask, 4),
        "no_ask": round(no_ask, 4),
        "mid": round(prices[0], 4),
        "volume": _f(m.get("volumeNum"), 0.0),
        "url": f"https://polymarket.com/market/{m.get('slug', '')}",
        "fee_rate": _poly_fee_rate(m),
    }


def fetch_polymarket(days_ahead: int, min_volume: float, limit: int, keep=None) -> list[dict]:
    """Page through by 24h volume until `limit` Yes/No markets that `keep` accepts (the scan's free
    filters), so no slot goes to a market the filters would throw away (most pages are sports)."""
    now = datetime.now(timezone.utc)
    out, seen = [], set()
    for page in range(MAX_PAGES):
        raw = _get(f"{POLY}/markets", {
            "active": "true", "closed": "false", "limit": POLY_PAGE, "offset": page * POLY_PAGE,
            # camelCase field name: "volume_24hr" is rejected with HTTP 422 "order fields are not valid"
            "order": "volume24hr", "ascending": "false",
            "end_date_min": _iso(now + timedelta(hours=12)),
            "end_date_max": _iso(now + timedelta(days=days_ahead)),
            "volume_num_min": min_volume,
        })
        raw = raw if isinstance(raw, list) else []
        for m in raw:
            n = normalize_polymarket(m)
            if n and n["market_id"] not in seen:  # offset paging can repeat a market if rankings shift
                seen.add(n["market_id"])
                if keep is None or keep(n):
                    out.append(n)
        if len(out) >= limit or len(raw) < POLY_PAGE:
            break
    return out[:limit]


def resolve_polymarket(market_id: str) -> str | None:
    m = _get(f"{POLY}/markets/{market_id}")
    if not m.get("closed"):
        return None
    try:
        prices = [float(p) for p in json.loads(m.get("outcomePrices") or "[]")]
    except (ValueError, TypeError):
        return None
    if len(prices) == 2 and max(prices) >= 0.99:
        return "yes" if prices[0] >= 0.99 else "no"
    return None  # closed but not cleanly resolved yet


# ---------- Kalshi (public market data; field names handled both ways) ----------

def _kalshi_price(m: dict, name: str):
    if m.get(f"{name}_dollars") not in (None, ""):
        return _f(m[f"{name}_dollars"])
    cents = _f(m.get(name))
    return cents / 100 if cents is not None else None


def normalize_kalshi(m: dict) -> dict | None:
    if m.get("market_type", "binary") != "binary":
        return None
    if str(m.get("ticker", "")).upper().startswith("KXMVE"):
        return None  # multi-leg parlay markets: skip
    yes_ask, no_ask = _kalshi_price(m, "yes_ask"), _kalshi_price(m, "no_ask")
    yes_bid = _kalshi_price(m, "yes_bid")
    if not yes_ask or not no_ask or yes_ask >= 1 or no_ask >= 1:
        return None
    title = m.get("title", "")
    sub = m.get("yes_sub_title") or m.get("subtitle") or ""
    return {
        "source": "kalshi",
        "market_id": m.get("ticker"),
        "event": f"kalshi:{m.get('event_ticker') or m.get('ticker')}",
        "question": f"{title} ({sub})" if sub and sub not in title else title,
        "rules": ((m.get("rules_primary") or "") + "\n" + (m.get("rules_secondary") or ""))[:4000],
        "close_time": m.get("close_time"),
        "yes_ask": round(yes_ask, 4),
        "no_ask": round(no_ask, 4),
        "mid": round(((yes_bid or yes_ask) + yes_ask) / 2, 4),
        "volume": _f(m.get("volume_fp"), None) or _f(m.get("volume"), 0.0),
        "url": kalshi_url(m.get("event_ticker") or m.get("ticker") or "", m.get("series_ticker") or "", title),
        # when the event itself is expected to be decided; close_time can be days or weeks later
        "expected_expiration": m.get("expected_expiration_time"),
    }


def kalshi_url(event_ticker: str, series_ticker: str = "", title: str = "") -> str:
    """Kalshi's page for one event. kalshi.com/markets/<EVENT> is "Page not found"; the site wants
    /markets/<series>/<any slug>/<event> (checked in Chrome, 2026-09-28). A series ticker is the event
    ticker's first part (KXNBAGAME-26OCT20BOSDET -> KXNBAGAME)."""
    event = event_ticker.lower()
    series = (series_ticker or event.split("-")[0]).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60].strip("-") or "market"
    return f"https://kalshi.com/markets/{series}/{slug}/{event}"


_OLD_KALSHI = re.compile(r"^https://kalshi\.com/markets/([A-Za-z0-9]+-[A-Za-z0-9-]+)$")


def fix_url(url: str | None) -> str | None:
    """Links saved before 2026-09-28 used the Kalshi form that 404s; repair them on the way to the page."""
    old = _OLD_KALSHI.match(url or "")
    return kalshi_url(old.group(1)) if old else url


def fetch_kalshi(days_ahead: int, min_volume: float, limit: int, keep=None) -> list[dict]:
    """The `limit` highest-volume markets `keep` accepts, from the whole window.

    Kalshi lists markets latest-closing first, and stopping at the first pages used to leave only markets
    closing 2-4 weeks out (every Kalshi market judged before 2026-09-28). So the window is walked in slices,
    soonest first (12h-3d, 3d-7d, 7d-days_ahead), each paged to the end: if the page limit or an error cuts
    the walk short, what's lost is the far-dated end. What happened is left in LAST_FETCH for the scan log.
    """
    now, started = datetime.now(timezone.utc), time.monotonic()
    deadline = started + KALSHI_DEADLINE
    edges = [e for e in KALSHI_SLICES if e < timedelta(days=days_ahead)] + [timedelta(days=days_ahead)]
    out, seen, pages, cut_short, error = [], set(), 0, False, None
    for lo, hi in zip(edges, edges[1:]):
        cursor = None
        while not error:
            if pages >= KALSHI_MAX_PAGES or time.monotonic() > deadline:
                cut_short = True
                break
            if pages:
                _sleep(KALSHI_PAGE_PAUSE)
            params = {"status": "open", "limit": KALSHI_PAGE, "mve_filter": "exclude",
                      "min_close_ts": int((now + lo).timestamp()), "max_close_ts": int((now + hi).timestamp())}
            if cursor:
                params["cursor"] = cursor
            try:
                data = _get(f"{KALSHI}/markets", params)
            except Exception as e:  # after _get's own retries: keep what the earlier pages found
                error = str(e)
                break
            pages += 1
            for m in data.get("markets", []):
                n = normalize_kalshi(m)
                if n and n["market_id"] not in seen and n["volume"] >= min_volume and (keep is None or keep(n)):
                    seen.add(n["market_id"])
                    out.append(n)
            cursor = data.get("cursor")
            if not cursor or not data.get("markets"):
                break
        if error or cut_short:
            break
    LAST_FETCH["kalshi"] = {"pages": pages, "seconds": round(time.monotonic() - started, 1),
                            "cut_short": cut_short, "error": error, "passing": len(out)}
    if error and not out:
        raise RuntimeError(error)
    out.sort(key=lambda m: m["volume"], reverse=True)
    return out[:limit]


def check_kalshi(tickers: list[str]) -> dict:
    """ticker -> "yes" / "no", or ("void", value) for a market settled at a value rather than yes/no.

    One request per KALSHI_BATCH tickers, whatever their stored close times: Kalshi's close_time is a late
    upper bound (a market decided on Sep 28 still showed Oct 15), so waiting for it held results back weeks.
    Only finalized results count ("determined" can still be disputed); it's checked again next cycle. A
    failed request loses only its own batch; what went wrong is left in LAST_FETCH["kalshi_check"].
    """
    out, errors = {}, []
    for i in range(0, len(tickers), KALSHI_BATCH):
        if i:
            _sleep(KALSHI_PAGE_PAUSE)
        chunk = tickers[i:i + KALSHI_BATCH]
        try:
            data = _get(f"{KALSHI}/markets", {"tickers": ",".join(chunk), "limit": len(chunk)})
        except Exception as e:
            errors.append(str(e)[:200])
            continue
        for m in data.get("markets", []):
            if m.get("status") not in ("finalized", "settled"):
                continue
            result = (m.get("result") or "").lower()
            if result in ("yes", "no"):
                out[m.get("ticker")] = result
            elif result == "scalar":
                value = _f(m.get("settlement_value_dollars"), None)
                if value is not None and 0 <= value <= 1:
                    out[m.get("ticker")] = ("void", value)
    LAST_FETCH["kalshi_check"] = {"batches": -(-len(tickers) // KALSHI_BATCH), "errors": errors}
    if errors and not out and len(errors) * KALSHI_BATCH >= len(tickers):
        raise RuntimeError(errors[0])
    return out


def resolve_kalshi(ticker: str) -> str | None:
    m = _get(f"{KALSHI}/markets/{ticker}").get("market", {})
    result = (m.get("result") or "").lower()
    if m.get("status") in ("determined", "finalized", "settled") and result in ("yes", "no"):
        return result
    return None


FETCHERS = {"polymarket": fetch_polymarket, "kalshi": fetch_kalshi}
RESOLVERS = {"polymarket": resolve_polymarket, "kalshi": resolve_kalshi}
BATCH_RESOLVERS = {"kalshi": check_kalshi}  # checked every cycle, before the stored close time

"""Read-only public market data from Polymarket (Gamma API) and Kalshi.

Every market is normalized to:
  {source, market_id, event, question, rules, close_time (ISO), yes_ask, no_ask, mid,
   volume, url}
`event` groups markets that share one real-world event (researched once, together).
Resolution check returns "yes", "no", or None (unresolved).
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

UA = {"User-Agent": "jev-papertrade/0.1", "Accept": "application/json"}
POLY = "https://gamma-api.polymarket.com"
KALSHI = "https://api.elections.kalshi.com/trade-api/v2"
MAX_PAGES = 25   # hard stop per source per fetch, so a feed that never runs dry can't loop forever
POLY_PAGE = 100


def _get(url: str, params: dict | None = None, timeout: float = 20) -> object:
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        # Keep the API's own explanation: a bare "422 Unprocessable Entity" hid a bad sort field.
        with e:
            detail = e.read().decode(errors="replace")[:300]
        raise RuntimeError(f"HTTP {e.code} from {url.split('?')[0]}: {detail}") from None


def _f(x, default=None):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------- Polymarket ----------

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
        "yes_ask": round(yes_ask, 4),
        "no_ask": round(no_ask, 4),
        "mid": round(prices[0], 4),
        "volume": _f(m.get("volumeNum"), 0.0),
        "url": f"https://polymarket.com/market/{m.get('slug', '')}",
    }


def fetch_polymarket(days_ahead: int, min_volume: float, limit: int) -> list[dict]:
    """Page through by 24h volume until `limit` Yes/No markets (most pages are team-vs-team sports)."""
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
        "url": f"https://kalshi.com/markets/{m.get('event_ticker', '')}",
    }


def fetch_kalshi(days_ahead: int, min_volume: float, limit: int) -> list[dict]:
    now = datetime.now(timezone.utc)
    out, cursor = [], None
    for _ in range(MAX_PAGES):
        params = {"status": "open", "limit": 200, "mve_filter": "exclude",
                  "min_close_ts": int((now + timedelta(hours=12)).timestamp()),
                  "max_close_ts": int((now + timedelta(days=days_ahead)).timestamp())}
        if cursor:
            params["cursor"] = cursor
        data = _get(f"{KALSHI}/markets", params)
        for m in data.get("markets", []):
            n = normalize_kalshi(m)
            if n and n["volume"] >= min_volume:
                out.append(n)
        cursor = data.get("cursor")
        if len(out) >= limit or not cursor or not data.get("markets"):
            break
    out.sort(key=lambda m: m["volume"], reverse=True)
    return out[:limit]


def resolve_kalshi(ticker: str) -> str | None:
    m = _get(f"{KALSHI}/markets/{ticker}").get("market", {})
    result = (m.get("result") or "").lower()
    if m.get("status") in ("determined", "finalized", "settled") and result in ("yes", "no"):
        return result
    return None


FETCHERS = {"polymarket": fetch_polymarket, "kalshi": fetch_kalshi}
RESOLVERS = {"polymarket": resolve_polymarket, "kalshi": resolve_kalshi}

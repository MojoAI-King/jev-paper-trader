"""Sharp sportsbook prices from The Odds API (the-odds-api.com), matched to the Kalshi and Polymarket markets the
trader already loads (docs/research/09-sports-vs-sharp-books.md; docs/REBUILD_PLAN.md phase 2A, BACKLOG B27).

Pinnacle's price on a game, with its margin removed, is the reference ("sharp") forecast: professional bettors
measure themselves against it. It is a price, so it never reaches Jev or Claude (the price screen in news.py is
unchanged). It goes only to the strategy that bets on it and to the scoring. The key is ODDS_API_KEY, from the
environment or .env; it is sent only to the API and never printed, logged or saved.
"""
from __future__ import annotations

import json
import re
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

from .jev_client import read_env_key

API = "https://api.the-odds-api.com/v4"
# Up to 10 bookmakers cost one unit of quota per call. Pinnacle is the reference; Betfair's exchange is the fallback.
BOOKS = ("pinnacle", "betfair_ex_eu", "kalshi", "polymarket")
SHARP_BOOKS = ("pinnacle", "betfair_ex_eu")
LAST: dict = {}  # quota left after the last call, for the scan log
TS = "%Y-%m-%dT%H:%M:%SZ"


class OddsError(RuntimeError):
    pass


def api_key() -> str | None:
    return read_env_key(("ODDS_API_KEY",))


def _get(path: str, params: dict, key: str, timeout: float = 20, opener=urllib.request.urlopen):
    req = urllib.request.Request(f"{API}{path}?{urllib.parse.urlencode({**params, 'apiKey': key})}",
                                 headers={"User-Agent": "jev-paper-trader (paper trading)"})
    try:
        with opener(req, timeout=timeout) as r:
            LAST.update({k: r.headers.get(f"x-requests-{k}") for k in ("remaining", "used", "last")})
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:  # the message never carries the URL, which holds the key
        raise OddsError(f"{path}: HTTP {e.code}") from None
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        raise OddsError(f"{path}: {type(e).__name__}") from None


def active_sports(key: str, opener=urllib.request.urlopen) -> set[str]:
    """Sports in season now. This call doesn't use quota."""
    return {s["key"] for s in _get("/sports", {}, key, opener=opener) if s.get("active")}


def fetch_odds(sport: str, key: str, opener=urllib.request.urlopen) -> list[dict]:
    """Head-to-head prices for every upcoming game in one sport, from BOOKS. One unit of quota."""
    return _get(f"/sports/{sport}/odds", {"bookmakers": ",".join(BOOKS), "markets": "h2h", "oddsFormat": "decimal"},
                key, opener=opener)


def compact(events: list[dict]) -> list[dict]:
    """The parts of the API's reply we keep: each game, and each book's price on each outcome."""
    out = []
    for ev in events:
        books = {}
        for b in ev.get("bookmakers") or []:
            h2h = next((m for m in b.get("markets") or [] if m.get("key") == "h2h"), None)
            if h2h:
                books[b["key"]] = {"last_update": h2h.get("last_update") or b.get("last_update"),
                                   "prices": {o["name"]: o.get("price") for o in h2h.get("outcomes") or []}}
        out.append({"id": ev.get("id"), "sport": ev.get("sport_key"), "commence": ev.get("commence_time"),
                    "home": ev.get("home_team"), "away": ev.get("away_team"), "books": books})
    return out


def devig_power(prices: list) -> list[float] | None:
    """Fair probabilities from one book's decimal odds on every outcome of a game: p_i = (1/o_i)^k, with k chosen
    so they add up to 1 (the power method, which beats dividing by the sum in published comparisons; report 09).
    None if a price is missing or not above 1."""
    if len(prices) < 2 or any(not isinstance(o, (int, float)) or o <= 1 for o in prices):
        return None
    inv = [1 / o for o in prices]
    lo, hi = 0.01, 20.0  # each 1/o is below 1, so the sum falls as k rises
    for _ in range(200):
        k = (lo + hi) / 2
        if sum(x ** k for x in inv) > 1:
            lo = k
        else:
            hi = k
    k = (lo + hi) / 2
    return [x ** k for x in inv]


def _age_minutes(stamp: str | None, now: datetime) -> float | None:
    try:
        t = datetime.strptime(str(stamp)[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return (now - t).total_seconds() / 60


def fair(ev: dict, cfg: dict, now: datetime) -> dict | None:
    """The sharp fair probability of each outcome: the first of SHARP_BOOKS whose line is fresh enough and whose
    margin is small enough, de-vigged. None when no sharp line qualifies."""
    for book in SHARP_BOOKS:
        b = ev["books"].get(book)
        if not b:
            continue
        names = list(b["prices"])
        probs = devig_power([b["prices"][n] for n in names])
        age = _age_minutes(b.get("last_update"), now)
        if probs is None or age is None or age > cfg["max_line_age_minutes"]:
            continue
        margin = sum(1 / b["prices"][n] for n in names) - 1
        if margin > cfg["max_margin"]:
            continue
        return {"book": book, "probs": dict(zip(names, probs)), "age_min": round(age, 1), "margin": round(margin, 4)}
    return None


# ---------- matching a game to our markets ----------

_STOP = {"fc", "cf", "sc", "afc", "ac", "the", "of", "and", "city", "united", "state", "club", "de", "real", "sporting",
         "athletic", "university", "college", "team", "win", "wins", "winner", "will", "game", "match", "vs", "at"}
_ALIASES = {"turkiye": "turkey", "czechia": "czech", "usa": "united states"}
_NOT_H2H = re.compile(r"\b(by over|by more than|points?|spread|total|over/under|o/u|handicap|goals?|runs?|sets?|"
                      r"first half|1st half|quarter|period|map \d|both teams|exact score|margin)\b", re.I)
_DATE = re.compile(r"\b(20\d\d-\d\d-\d\d)\b")


def _words(s: str | None) -> set[str]:
    text = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    for a, b in _ALIASES.items():
        text = re.sub(rf"\b{a}\b", b, text)
    return {w for w in re.findall(r"[a-z0-9]+", text) if len(w) > 2 and w not in _STOP}


def _when(stamp) -> datetime | None:
    try:
        return datetime.strptime(str(stamp)[:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _outcome_for(text: str, ev: dict) -> str | None:
    """Which outcome of the game a YES on this market means, or None when that isn't clear-cut."""
    words = _words(text)
    if re.search(r"\b(draw|tie)\b", text or "", re.I):
        return "Draw" if "Draw" in next(iter(ev["books"].values()))["prices"] else None
    hits = [t for t in (ev["home"], ev["away"]) if _words(t) & words]
    return hits[0] if len(hits) == 1 else None


def match(events: list[dict], markets: list[dict], cfg: dict, now: datetime) -> dict:
    """Market key -> the sharp record for the markets that are clearly one game's head-to-head outcome.

    A Kalshi game market names both teams in its title and the YES team in `yes_side`, and is decided within
    `kickoff_window_hours` after the game starts. A Polymarket market names one team ("Will Turkey win on
    2026-09-28?") and starts within the window of the game, or carries the game's date. Spread, total and prop
    markets never match. Anything ambiguous is left out: only clear matches get a sharp price."""
    out, window = {}, timedelta(hours=cfg["kickoff_window_hours"])
    priced = [(ev, f) for ev in events if (f := fair(ev, cfg, now)) and _when(ev.get("commence"))]
    for m in markets:
        question = m.get("question") or ""
        if _NOT_H2H.search(question) or m.get("source") not in ("kalshi", "polymarket"):
            continue  # spreads, totals and props, judged on the question alone (rules text mentions points too)
        # Kalshi's game titles name one team ("Philadelphia wins", since October 2026); its rules name both
        # ("If Philadelphia wins the PHI Eagles vs JAC Jaguars Pro Football game ...")
        text = f"{question} {(m.get('rules') or '')[:600]}"
        found = []
        for ev, f in priced:
            start = _when(ev["commence"])
            if start <= now:
                continue  # in play: the line moves too fast for a 30-minute look
            teams = [bool(_words(ev["home"]) & _words(text)), bool(_words(ev["away"]) & _words(text))]
            if m["source"] == "kalshi":
                decided = _when(m.get("expected_expiration")) or _when(m.get("close_time"))
                if not (all(teams) and decided and start <= decided <= start + window):
                    continue
                outcome = _outcome_for(m.get("yes_side") or "", ev)
            else:
                begins, day = _when(m.get("starts")), _DATE.search(question)
                on_time = (begins and abs(begins - start) <= window) or (day and day.group(1) in (
                    start.strftime("%Y-%m-%d"), (start - timedelta(hours=12)).strftime("%Y-%m-%d")))
                if not (any(teams) and on_time):
                    continue
                outcome = _outcome_for(question, ev)
            if outcome and outcome in f["probs"]:
                found.append((ev, f, outcome))
        if len(found) == 1:
            ev, f, outcome = found[0]
            out[f"{m['source']}:{m['market_id']}"] = {
                "p_yes": round(f["probs"][outcome], 4), "outcome": outcome, "book": f["book"], "age_min": f["age_min"],
                "margin": f["margin"], "event_id": ev["id"], "sport": ev["sport"], "commence": ev["commence"]}
    return out


# ---------- the cache, refreshed within the quota ----------

def load_events(cfg: dict, key: str, cache: dict, now: datetime, opener=urllib.request.urlopen, warn=print) -> dict:
    """Refresh the cached odds for the sports in `cfg['sports']` that are in season and older than
    `refresh_minutes`, stopping when the quota left falls to `reserve`. Returns the updated cache
    ({sport: {"fetched": ts, "events": [...]}}); old sports stay until refreshed."""
    try:
        live = active_sports(key, opener=opener)
    except OddsError as e:
        warn(f"! odds: could not list sports ({e})")
        return cache
    for sport in cfg["sports"]:
        if sport not in live:
            continue
        got = cache.get(sport) or {}
        age = _age_minutes(got.get("fetched"), now)
        if age is not None and age < cfg["refresh_minutes"]:
            continue
        left = LAST.get("remaining")
        if left is not None and str(left).replace(".", "", 1).isdigit() and float(left) <= cfg["reserve"]:
            warn(f"! odds: quota down to {left}; keeping the cached lines")
            break
        try:
            cache[sport] = {"fetched": now.strftime(TS), "events": compact(fetch_odds(sport, key, opener=opener))}
        except OddsError as e:
            warn(f"! odds: {sport} failed ({e})")
    return cache


def all_events(cache: dict) -> list[dict]:
    return [ev for v in cache.values() for ev in v.get("events") or []]

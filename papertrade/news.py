"""Research for Jev: Claude gathers dated, sourced facts about each event; code screens them.

Jev must never see a market's price. Three layers keep it out of `recent_facts`:
  1. the prompt forbids odds, market prices, forecaster probabilities and predictions;
  2. prediction-market, sportsbook and odds sites are blocked at search and fetch time;
  3. screen_facts() drops any fact that still carries them. This layer is code, lives here and
     not in policy.json so a config edit can't loosen it, and is what the tests check.

Also here: the "Claude direct" forecaster, which reads the same screened facts and gives its own
probability, so the experiment can tell whether Jev adds anything over Claude alone.

Paid API. Spend is computed from each response's `usage`, never estimated.
"""
from __future__ import annotations

import json
import random
import re
import time
import urllib.error
import urllib.request
from datetime import date
from urllib.parse import urlparse

from .jev_client import read_env_key

API_URL = "https://api.anthropic.com/v1/messages"
RETRY_STATUSES = {429, 500, 502, 503, 529}
FATAL_STATUSES = {400, 401, 403, 404}

# USD per million tokens, from platform.claude.com/docs/en/about-claude/pricing (read 2026-09-27).
# A model missing here can't run: without prices the per-scan dollar ceiling can't be enforced.
MODELS = {"claude-opus-5-5": {"in": 4.0, "out": 20.0}}
USD_PER_SEARCH = 0.01  # $10 per 1,000 web searches; web fetch has no per-call fee

BLOCKED_DOMAINS = [
    "polymarket.com", "kalshi.com", "predictit.org", "manifold.markets", "metaculus.com",
    "betfair.com", "smarkets.com", "oddschecker.com", "oddsshark.com", "draftkings.com",
    "fanduel.com", "betmgm.com", "bet365.com", "williamhill.com", "actionnetwork.com",
    "covers.com", "vegasinsider.com", "electionbettingodds.com", "sportsbookreview.com",
]
FACT_KINDS = ("status_now", "event", "schedule", "base_rate", "rules")

RESEARCH_PROMPT = """You are the research desk for a forecasting team. A separate forecaster will estimate how some yes/no questions resolve. Your job is to give it the evidence, never a forecast.

Research the questions below thoroughly, with web search and by reading the most useful pages in full. Cover, where they apply:
- status_now: what the resolution source, standings, tallies, scores or official records show as of today. When the rules name a resolution source, read it.
- event: developments from roughly the last 30 days that bear on the outcome.
- schedule: what is still due to happen before the questions close (games left, votes, releases, deadlines).
- base_rate: how often comparable situations turned out each way in the past, stated as counts or frequencies, for example "11 of the last 14 ...".
- rules: how the resolution source measures or reports the outcome, when that isn't obvious.

Every fact needs:
- "kind": one of status_now, event, schedule, base_rate, rules
- "date": when it happened or was published, as YYYY-MM-DD, never after today
- "source": the publication or organization that reported it
- "url": the page where you found it
- "fact": one or two plain sentences with the specific numbers

Never include, even when a source mentions them:
- betting odds, betting lines, point spreads, or which side bookmakers favor
- prices or probabilities from prediction markets (Polymarket, Kalshi, PredictIt, Manifold, Metaculus, Betfair or any other)
- win probabilities or forecasts from models or forecasters (538, Silver Bulletin, The Economist or any other), or phrases like "a 60% chance"
- predictions, expectations or opinions about the outcome, including your own

Reply with only a JSON array of up to {max_facts} facts covering all the questions, most decisive first, and no other text. If nothing relevant turns up, reply []."""

DIRECT_PROMPT = """You are a careful forecaster. You get a yes/no question, its resolution rules, today's date and a dossier of dated, sourced facts gathered today. Estimate the probability that the question resolves YES under its rules.

Use only what you are given plus your general knowledge. Reply with only a JSON object and no other text: {"p_yes": <a number from 0 to 1>}"""


class NewsError(RuntimeError):
    """A research or forecast call failed. `fatal` means every later call would fail the same way."""

    def __init__(self, message: str, fatal: bool = False, meta: dict | None = None):
        super().__init__(message)
        self.fatal = fatal
        self.meta = meta or {}


class _HTTPError(Exception):
    def __init__(self, status: int, detail: str, retry_after: float | None):
        super().__init__(f"HTTP {status}: {detail}")
        self.status, self.detail, self.retry_after = status, detail, retry_after


def _http_post(url: str, body: dict, headers: dict, timeout: float) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        with e:
            detail = e.read().decode(errors="replace")[:500]
        ra = e.headers.get("retry-after") if e.headers else None
        raise _HTTPError(e.code, detail, float(ra) if ra and ra.replace(".", "", 1).isdigit() else None) from None
    except urllib.error.URLError as e:
        raise _HTTPError(0, f"network error: {e.reason}", None) from None
    except TimeoutError:
        raise _HTTPError(0, f"timed out after {timeout}s", None) from None


def cost_usd(model: str, usage: dict) -> float:
    p = MODELS[model]
    tokens_in = (usage.get("input_tokens", 0) + 1.25 * usage.get("cache_creation_input_tokens", 0)
                 + 0.1 * usage.get("cache_read_input_tokens", 0))
    searches = (usage.get("server_tool_use") or {}).get("web_search_requests", 0)
    return round(tokens_in * p["in"] / 1e6 + usage.get("output_tokens", 0) * p["out"] / 1e6
                 + searches * USD_PER_SEARCH, 5)


class ClaudeClient:
    """Minimal Messages API client (stdlib only, like the Jev client)."""

    def __init__(self, model: str, api_key: str | None = None, transport=None, timeout: float = 600.0,
                 max_retries: int = 4):
        if model not in MODELS:
            raise NewsError(f"model {model!r} has no price row in news.MODELS", fatal=True)
        self.model, self.timeout, self.max_retries = model, timeout, max_retries
        self._transport = transport or _http_post
        self._api_key = api_key or ("" if transport else read_env_key(("ANTHROPIC_API_KEY",)))
        if not self._api_key and not transport:
            raise NewsError("No ANTHROPIC_API_KEY in the environment or .env", fatal=True)

    def post(self, body: dict) -> dict:
        headers = {"x-api-key": self._api_key, "anthropic-version": "2023-06-01",
                   "content-type": "application/json"}
        attempt = 0
        while True:
            try:
                return self._transport(API_URL, body, headers, self.timeout)
            except _HTTPError as e:
                if e.status in FATAL_STATUSES:
                    raise NewsError(str(e), fatal=True) from None
                if (e.status not in RETRY_STATUSES and e.status != 0) or attempt >= self.max_retries:
                    raise NewsError(str(e)) from None
                wait = e.retry_after if e.retry_after is not None else min(60.0, 2.0 * 2 ** attempt)
                time.sleep(min(wait, 120.0) + random.random())
                attempt += 1


def _add_usage(total: dict, usage: dict) -> None:
    for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"):
        total[k] = total.get(k, 0) + (usage.get(k) or 0)
    stu = usage.get("server_tool_use") or {}
    agg = total.setdefault("server_tool_use", {})
    for k, v in stu.items():
        agg[k] = agg.get(k, 0) + (v or 0)


def _text(content: list) -> str:
    return "".join(b.get("text", "") for b in content if b.get("type") == "text")


def _urls(content: list) -> set[str]:
    """Every URL the call actually saw: search results, fetched pages, and citations."""
    out = set()
    for b in content:
        t, c = b.get("type"), b.get("content")
        if t == "web_search_tool_result" and isinstance(c, list):
            out.update(r.get("url") for r in c if isinstance(r, dict) and r.get("url"))
        elif t == "web_fetch_tool_result" and isinstance(c, dict) and c.get("url"):
            out.add(c["url"])
        elif t == "text":
            out.update(x.get("url") for x in b.get("citations") or [] if isinstance(x, dict) and x.get("url"))
    return out


def _parse_json(text: str, want):
    """Last JSON value of type `want` in the text (the reply may carry preamble or citation splits)."""
    dec, i, found = json.JSONDecoder(), 0, None
    opener = "[" if want is list else "{"
    while True:
        i = text.find(opener, i)
        if i == -1:
            return found
        try:
            obj, end = dec.raw_decode(text, i)
        except ValueError:
            i += 1
            continue
        if isinstance(obj, want) and (want is not list or all(isinstance(x, dict) for x in obj)):
            found = obj
        i = end


class Researcher:
    """One Claude call per event: web search + page reading -> raw facts (unscreened)."""

    MAX_CONTINUATIONS = 6  # server-side tool loops pause after 10 steps; resume up to this many times

    def __init__(self, cfg: dict, client: ClaudeClient | None = None):
        self.cfg = cfg
        self.client = client or ClaudeClient(cfg["model"])

    def body(self, markets: list[dict], today: str) -> dict:
        c = self.cfg
        lines = [f"Today is {today}.", "", "Questions (all from one event):"]
        for m in markets:
            lines += [f"- Question: {m['question']}",
                      f"  Resolution rules: {(m.get('rules') or '').strip()[:2500]}",
                      f"  Closes: {m['close_time']}"]
        return {
            "model": self.client.model, "max_tokens": 16000,
            "system": RESEARCH_PROMPT.replace("{max_facts}", str(c["max_facts_per_event"])),
            "messages": [{"role": "user", "content": "\n".join(lines)}],
            "tools": [
                {"type": "web_search_20260318", "name": "web_search", "max_uses": c["max_searches_per_event"],
                 "blocked_domains": BLOCKED_DOMAINS},
                {"type": "web_fetch_20260209", "name": "web_fetch", "max_uses": c["max_fetches_per_event"],
                 "max_content_tokens": 20000, "blocked_domains": BLOCKED_DOMAINS},
            ],
            "output_config": {"effort": c["effort"]},
        }

    def research(self, markets: list[dict], today: str) -> dict:
        body = self.body(markets, today)
        usage, urls, content, calls, start = {}, set(), [], 0, time.monotonic()
        stop = None
        while True:
            data = self.client.post(body)
            calls += 1
            _add_usage(usage, data.get("usage") or {})
            content = data.get("content") or []
            urls |= _urls(content)
            stop = data.get("stop_reason")
            if stop != "pause_turn" or calls > self.MAX_CONTINUATIONS:
                break
            # Resume a paused server-side loop: send the paused turn back unchanged, no new user message.
            body = dict(body, messages=body["messages"] + [{"role": "assistant", "content": content}])
        meta = {"model": self.client.model, "calls": calls, "stop_reason": stop,
                "searches": (usage.get("server_tool_use") or {}).get("web_search_requests", 0),
                "fetches": (usage.get("server_tool_use") or {}).get("web_fetch_requests", 0),
                "input_tokens": usage.get("input_tokens", 0), "output_tokens": usage.get("output_tokens", 0),
                "cost_usd": cost_usd(self.client.model, usage),
                "latency_ms": round((time.monotonic() - start) * 1000)}
        if stop in ("refusal", "pause_turn", "max_tokens"):
            raise NewsError(f"research stopped: {stop}", meta=meta)
        facts = _parse_json(_text(content), list)
        if facts is None:
            raise NewsError("research reply had no JSON list of facts", meta=meta)
        return {"raw_facts": facts, "source_urls": sorted(urls), "meta": meta}


class DirectForecaster:
    """Claude's own probability from the same screened state Jev sees (no tools, no price)."""

    def __init__(self, cfg: dict, client: ClaudeClient | None = None):
        self.cfg = cfg
        self.client = client or ClaudeClient(cfg["model"])

    def forecast(self, state: dict) -> dict:
        start = time.monotonic()
        data = self.client.post({
            "model": self.client.model, "max_tokens": 8000, "system": DIRECT_PROMPT,
            "messages": [{"role": "user", "content": json.dumps(state, ensure_ascii=False, indent=1)}],
            "output_config": {"effort": self.cfg["effort"]},
        })
        usage = data.get("usage") or {}
        meta = {"model": self.client.model, "cost_usd": cost_usd(self.client.model, usage),
                "latency_ms": round((time.monotonic() - start) * 1000)}
        if data.get("stop_reason") in ("refusal", "max_tokens"):
            raise NewsError(f"forecast stopped: {data.get('stop_reason')}", meta=meta)
        obj = _parse_json(_text(data.get("content") or []), dict)
        try:
            p = float(obj["p_yes"])
        except (TypeError, KeyError, ValueError):
            raise NewsError("forecast reply had no p_yes", meta=meta) from None
        if not 0.0 <= p <= 1.0:
            raise NewsError(f"forecast p_yes out of range: {p}", meta=meta)
        return {"p_yes": round(p, 4), "meta": meta}


# ---------------- the price screen (layer 3) ----------------

_NUM = r"\d+(?:\.\d+)?"
LEAK_RULES = [
    ("names a prediction market or sportsbook", re.compile(
        r"polymarket|kalshi|predictit|manifold markets|metaculus|betfair|smarkets|draftkings|fanduel|betmgm|"
        r"bet365|william hill|paddy ?power|ladbrokes|bovada|betrivers|pinnacle sports|oddschecker|oddsshark|"
        r"action network|vegas ?insider|caesars sportsbook|prediction markets?|betting markets?|"
        r"sportsbooks?|bookmakers?|bookies?", re.I)),
    ("betting language", re.compile(
        r"\bodds\b|\bbet(?:s|ting|tors?)?\b|\bwager|\bmoney ?line\b|point spread|against the spread|"
        r"over/under|\bo/u\b|\bfavou?rites?\b|\bunderdogs?\b|\bpunters?\b|\bgamblers?\b", re.I)),
    ("market trading", re.compile(
        rf"\bimplied (?:probability|chance|odds)|\bpriced in\b|\bpriced at {_NUM}\s*(?:%|¢|cents?\b|percent)|"
        rf"\btraders? (?:are |were )?(?:pricing|giving|betting|see|put)\b|\b(?:yes|no) (?:shares|contracts)\b|"
        rf"\btrading at {_NUM}\s*(?:%|¢|cents?\b|percent)", re.I)),
    ("cites a forecaster", re.compile(
        r"fivethirtyeight|\b538(?:'s)?\s+(?:forecast|model|average|gives)|silver bulletin|nate silver|"
        r"superforecast|good judgment|forecast(?:ing)? model|election model|prediction model|"
        r"\bwin probability|\bchances? of winning", re.I)),
    ("makes a prediction", re.compile(
        r"\bpredict(?:s|ed|ing|ion|ions)?\b|\bforecasts?\b|\bforecasted\b|\bprojected to\b|\bprojections?\b|"
        r"\b(?:expected|likely|favou?red|tipped) to (?:win|lose|beat|pass|fail|finish|take|clinch|advance|be elected)\b",
        re.I)),
]
_PCT = re.compile(rf"({_NUM})\s*(?:%|percent\b|per cent\b|pct\b|¢|cents?\b)", re.I)
_DEC = re.compile(r"(?<![\d.])\$?0?\.(\d{2})(?!\d)")
_PROB_WORDS = re.compile(r"\bchances?\b|\bprobabilit|\blikelihood\b|\bodds\b|\bimplied\b", re.I)


def _price_points(markets: list[dict]) -> set[int]:
    pts = set()
    for m in markets:
        for x in (m.get("mid"), m.get("yes_ask"), None if m.get("no_ask") is None else 1 - m["no_ask"]):
            if x is not None:
                v = round(100 * float(x))
                pts |= {v, 100 - v}
    return pts


def _figures(text: str) -> list[float]:
    return [float(x) for x in _PCT.findall(text)] + [float(x) for x in _DEC.findall(text)]


def leak_reason(text: str, markets: list[dict]) -> str | None:
    """Why this text could reveal a market price, or None if it looks clean."""
    for name, rx in LEAK_RULES:
        if rx.search(text):
            return name
    if _PCT.search(text) and _PROB_WORDS.search(text):
        return "a percentage used as a probability"
    pts = _price_points(markets)
    for f in _figures(text):
        if any(abs(f - p) <= 1 for p in pts):
            return "a figure within 1 point of this market's price"
    return None


def _domain(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def _same_site(a: str, b: str) -> bool:
    return a == b or a.endswith("." + b) or b.endswith("." + a)


def screen_facts(raw: list, markets: list[dict], today: str, source_urls, max_facts: int):
    """-> (kept, dropped). Kept facts are exactly what goes into Jev's state (plus their url, for the log)."""
    seen_sites = {_domain(u) for u in source_urls if u}
    kept, dropped, texts = [], [], set()
    for f in raw:
        if not isinstance(f, dict):
            dropped.append({"fact": str(f)[:300], "reason": "not an object"})
            continue
        fact, source, url = (str(f.get(k) or "").strip() for k in ("fact", "source", "url"))
        rec = {"kind": f.get("kind") if f.get("kind") in FACT_KINDS else "event",
               "date": str(f.get("date") or "").strip(), "source": source, "fact": fact[:600], "url": url}
        reason = None
        try:
            d = date.fromisoformat(rec["date"])
            if d > date.fromisoformat(today):
                reason = "dated after today"
        except ValueError:
            reason = "no valid YYYY-MM-DD date"
        if not reason and (not fact or not source):
            reason = "missing fact or source"
        if not reason and not (url.startswith(("https://", "http://")) and
                               any(_same_site(_domain(url), s) for s in seen_sites)):
            reason = "source not among the pages the research call saw"
        if not reason:
            reason = leak_reason(" ".join((fact, source, url)), markets)
        if not reason and fact.lower() in texts:
            reason = "duplicate"
        if not reason and len(kept) >= max_facts:
            reason = "over the fact cap"
        if reason:
            dropped.append(dict(rec, reason=reason))
        else:
            texts.add(fact.lower())
            kept.append(rec)
    return kept, dropped

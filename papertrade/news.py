"""Research for Jev: Claude gathers dated, sourced facts about each event; code screens them.

Claude runs through Claude Code on Joey's Max plan, never an API key. Claude Code bills an API
account instead of the plan whenever ANTHROPIC_API_KEY (or ANTHROPIC_AUTH_TOKEN) is set, so this
module refuses to start if either is set, and strips them from the child process as well.
Research shares the plan's usage limits with Joey's own Claude use; every call reports how much of
the 5-hour and weekly windows is used, and the engine stops calling Claude before they fill up.

Jev must never see a market's price. Three layers keep it out of `recent_facts`:
  1. the prompt forbids odds, market prices, forecaster probabilities and predictions;
  2. page reads on prediction-market, sportsbook and odds sites are denied;
  3. screen_facts() drops any fact that still carries them. This layer is code, lives here and
     not in policy.json so a config edit can't loosen it, and is what the tests check.

Also here: the "Claude direct" forecaster, which reads the same screened facts and gives its own
probability, so the experiment can tell whether Jev adds anything over Claude alone.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import time
from datetime import date
from urllib.parse import urlparse

CLAUDE_BIN = "claude"
BILLING_VARS = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")  # either one switches Claude Code to API billing

BLOCKED_DOMAINS = [
    "polymarket.com", "kalshi.com", "predictit.org", "manifold.markets", "metaculus.com",
    "betfair.com", "smarkets.com", "oddschecker.com", "oddsshark.com", "draftkings.com",
    "fanduel.com", "betmgm.com", "bet365.com", "williamhill.com", "actionnetwork.com",
    "covers.com", "vegasinsider.com", "electionbettingodds.com", "sportsbookreview.com",
]
FACT_KINDS = ("status_now", "event", "schedule", "base_rate", "rules")
_LIMIT_TEXT = re.compile(r"usage limit|session limit|weekly limit|rate limit|hit your .*limit", re.I)

RESEARCH_PROMPT = """You are the research desk for a forecasting team. A separate forecaster will estimate how some yes/no questions resolve. Your job is to give it the evidence, never a forecast.

Research the questions thoroughly but efficiently: use at most {max_searches} web searches and read at most {max_fetches} pages in full. Cover, where they apply:
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
    """A Claude call failed. `fatal`: every later call would fail the same way this run.
    `limited`: the plan's usage limit (or our share of it) is reached; try again next cycle."""

    def __init__(self, message: str, fatal: bool = False, meta: dict | None = None, limited: bool = False):
        super().__init__(message)
        self.fatal = fatal or limited
        self.limited = limited
        self.meta = meta or {}


def _run_claude(args: list[str], env: dict, cwd: str, timeout: float) -> tuple[int, str, str]:
    try:
        r = subprocess.run(args, env=env, cwd=cwd, stdin=subprocess.DEVNULL, capture_output=True,
                           text=True, timeout=timeout)
    except FileNotFoundError:
        raise NewsError("Claude Code (`claude`) is not installed on this machine", fatal=True) from None
    except subprocess.TimeoutExpired:
        raise NewsError(f"Claude Code timed out after {timeout:.0f}s") from None
    return r.returncode, r.stdout, r.stderr


def parse_stream(stdout: str) -> dict:
    """Read Claude Code's stream-json output: the final result, every URL its tools returned, usage."""
    out = {"result": None, "urls": set(), "rate": None, "searches": 0, "fetches": 0}
    for line in stdout.splitlines():
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        kind = msg.get("type")
        if kind == "rate_limit_event":
            out["rate"] = msg.get("rate_limit_info")
        elif kind == "assistant":
            for b in (msg.get("message") or {}).get("content") or []:
                if b.get("type") == "tool_use":
                    out["searches"] += b.get("name") == "WebSearch"
                    out["fetches"] += b.get("name") == "WebFetch"
        elif kind == "user":
            for b in (msg.get("message") or {}).get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    out["urls"].update(re.findall(r"https?://[^\s\"'<>)\]\\]+", json.dumps(b.get("content"))))
        elif kind == "result":
            out["result"] = msg
    out["urls"] = sorted(u.rstrip(".,;") for u in out["urls"])
    return out


class ClaudeCode:
    """Claude Code in print mode, on the plan's login. Web search and page reading only, no files, no shell."""

    def __init__(self, cfg: dict, runner=None, workdir: str | None = None):
        leaked = [v for v in BILLING_VARS if os.environ.get(v)]
        if leaked:
            raise NewsError(f"{' and '.join(leaked)} is set, so Claude Code would bill an API account instead of "
                            f"the Claude plan. Unset it to run research.", fatal=True)
        self.cfg = cfg
        self.model = cfg["model"]
        self._run = runner or _run_claude
        self.workdir = workdir or tempfile.mkdtemp(prefix="papertrade-claude-")  # outside the repo: no CLAUDE.md
        self.last_rate = None

    def usage_ok(self) -> bool:
        """False once the plan's windows are fuller than our share allows (research then waits a cycle)."""
        w = (self.last_rate or {}).get("unifiedWindows") or {}
        week = (w.get("seven_day") or {}).get("utilization")
        five = (w.get("five_hour") or {}).get("utilization")
        return not ((week is not None and week >= self.cfg["max_week_used"]) or
                    (five is not None and five >= self.cfg["max_five_hour_used"]))

    def ask(self, system: str, prompt: str, web: bool, timeout: float | None = None) -> dict:
        if not self.usage_ok():
            raise NewsError("our share of the Claude plan's usage is used up for now", limited=True)
        args = [CLAUDE_BIN, "-p", prompt, "--system-prompt", system, "--model", self.model,
                "--effort", self.cfg["effort"], "--permission-mode", "dontAsk", "--setting-sources", "",
                "--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence",
                "--max-budget-usd", str(self.cfg["max_api_equivalent_usd_per_call"]),
                "--output-format", "stream-json", "--verbose"]
        if web:
            args += ["--tools", "WebSearch,WebFetch", "--allowedTools", "WebSearch", "WebFetch",
                     "--disallowedTools", *[f"WebFetch(domain:{d})" for d in BLOCKED_DOMAINS]]
        else:
            args += ["--tools", ""]
        env = {k: v for k, v in os.environ.items() if k not in BILLING_VARS}
        start = time.monotonic()
        code, stdout, stderr = self._run(args, env, self.workdir, timeout or self.cfg["timeout_seconds"])
        s = parse_stream(stdout)
        if s["rate"]:
            self.last_rate = s["rate"]
        res = s["result"] or {}
        meta = {"model": self.model, "api_equivalent_usd": round(float(res.get("total_cost_usd") or 0), 5),
                "searches": s["searches"], "fetches": s["fetches"], "turns": res.get("num_turns"),
                "latency_ms": round((time.monotonic() - start) * 1000), "billing": "claude_plan"}
        text = res.get("result") or ""
        if s["rate"] and s["rate"].get("status") == "rejected" or (res.get("is_error") and _LIMIT_TEXT.search(text)):
            raise NewsError(f"Claude plan usage limit reached: {text[:200]}", meta=meta, limited=True)
        if code != 0 or res.get("is_error") or not res:
            detail = (text or stderr or "no result").strip().splitlines()
            raise NewsError(f"Claude Code failed (exit {code}): {detail[-1][:300] if detail else ''}", meta=meta)
        return {"text": text, "urls": s["urls"], "meta": meta}


def _parse_json(text: str, want):
    """Last JSON value of type `want` in the text (the reply may carry preamble)."""
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
    """One Claude Code run per event: web search + page reading -> raw facts (unscreened)."""

    def __init__(self, cfg: dict, claude: ClaudeCode):
        self.cfg, self.claude = cfg, claude

    def prompt(self, markets: list[dict], today: str) -> str:
        lines = [f"Today is {today}.", "", "Questions (all from one event):"]
        for m in markets:
            lines += [f"- Question: {m['question']}",
                      f"  Resolution rules: {(m.get('rules') or '').strip()[:2500]}",
                      f"  Closes: {m['close_time']}"]
        return "\n".join(lines)

    def research(self, markets: list[dict], today: str) -> dict:
        c = self.cfg
        system = (RESEARCH_PROMPT.replace("{max_facts}", str(c["max_facts_per_event"]))
                  .replace("{max_searches}", str(c["max_searches_per_event"]))
                  .replace("{max_fetches}", str(c["max_fetches_per_event"])))
        r = self.claude.ask(system, self.prompt(markets, today), web=True)
        facts = _parse_json(r["text"], list)
        if facts is None:
            raise NewsError("research reply had no JSON list of facts", meta=r["meta"])
        return {"raw_facts": facts, "source_urls": r["urls"], "meta": r["meta"]}


class DirectForecaster:
    """Claude's own probability from the same screened state Jev sees (no tools, no price)."""

    def __init__(self, cfg: dict, claude: ClaudeCode):
        self.cfg, self.claude = cfg, claude

    def forecast(self, state: dict) -> dict:
        r = self.claude.ask(DIRECT_PROMPT, json.dumps(state, ensure_ascii=False, indent=1), web=False, timeout=300)
        obj = _parse_json(r["text"], dict)
        try:
            p = float(obj["p_yes"])
        except (TypeError, KeyError, ValueError):
            raise NewsError("forecast reply had no p_yes", meta=r["meta"]) from None
        if not 0.0 <= p <= 1.0:
            raise NewsError(f"forecast p_yes out of range: {p}", meta=r["meta"])
        return {"p_yes": round(p, 4), "meta": r["meta"]}


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

"""The feedback loop: look back at every resolved market and learn from it.

For each market that resolved since the last review, score every forecaster and record which
signals it had. When the researched forecast was confidently wrong, or any strategy lost money on
it, Claude writes a post-mortem: what actually happened, what we missed, the root cause, and one
suggested change. When we were right and the market wasn't (or a bet won), Claude writes a "why
were we right" review, so the loop learns what works as well as what fails.

Reviews never change betting on their own. coach.py turns their lessons into the research
playbook, and the daily review turns patterns into rule changes and proposals (docs/LEARNING.md).
"""
from __future__ import annotations

import json
import time
from collections import Counter

from . import engine, news
from .judge import QUESTION_SET_VERSION

ROOT_CAUSES = {
    "missing_info": "the deciding information existed, but the research didn't find it",
    "stale_info": "the facts were out of date when the market was judged",
    "misread_rules": "the forecast misunderstood what counts as YES",
    "overconfident": "the evidence was thin or mixed, but the probability was extreme",
    "research_error": "a fact the forecaster was given was wrong",
    "resolution_quirk": "it resolved on a technicality or an unusual ruling",
    "unlucky": "the forecast was reasonable and the less likely outcome happened",
}
AREAS = ("research", "questions", "gates", "none")
WIN_CAUSES = {
    "research_found_it": "the research surfaced the fact that decided it",
    "read_the_rules": "the forecast understood exactly what counts as YES when others didn't",
    "base_rate": "history and base rates carried the call",
    "market_slow": "the market hadn't caught up with public information yet",
    "lucky": "the call was close to a coin flip and went our way",
}

POSTMORTEM_PROMPT = """You review forecasts after the fact so a forecasting team can learn from its mistakes. You get a yes/no question, its resolution rules, the facts the forecaster had when it judged, the probabilities it and the others gave, the market's price at that time, and the actual outcome.

Search the web (a few searches at most) to find out what actually happened and why. Then explain, plainly and specifically, why the forecast was off.

Reply with only a JSON object and no other text:
{"root_cause": one of %s,
 "what_happened": "one or two sentences",
 "what_we_missed": "one or two sentences; empty if nothing could have been known",
 "lesson": "one sentence a future forecaster could act on",
 "suggested_change": {"area": one of %s, "change": "one sentence"}}

Root causes: %s""" % (
    json.dumps(list(ROOT_CAUSES)), json.dumps(list(AREAS)),
    "; ".join(f"{k}: {v}" for k, v in ROOT_CAUSES.items()))


WIN_PROMPT = """You review forecasts after the fact so a forecasting team can learn what works. You get a yes/no question, its resolution rules, the facts the forecaster had when it judged, the probabilities it and the others gave, the market's price at that time, and the actual outcome. The forecaster did well on this one.

Search the web (a few searches at most) to find out what actually happened. Then explain, plainly and specifically, why the forecast was right, and be honest when it was luck.

Reply with only a JSON object and no other text:
{"credit": one of %s,
 "what_happened": "one or two sentences",
 "what_worked": "one or two sentences: which facts or reasoning carried it",
 "lesson": "one sentence a future researcher could act on to repeat it",
 "suggested_change": {"area": one of %s, "change": "one sentence"}}

Credits: %s""" % (
    json.dumps(list(WIN_CAUSES)), json.dumps(list(AREAS)),
    "; ".join(f"{k}: {v}" for k, v in WIN_CAUSES.items()))


class PostMortem:
    """A Claude Code run on the plan (web search allowed) that explains one miss, or one win."""

    def __init__(self, cfg: dict, review_cfg: dict, claude: news.ClaudeCode | None = None):
        self.cfg, self.rcfg = cfg, review_cfg
        self.claude = claude or news.ClaudeCode(cfg)

    def explain(self, case: dict) -> dict:
        r = self.claude.ask(POSTMORTEM_PROMPT, json.dumps(case, ensure_ascii=False, indent=1), web=True)
        obj = news._parse_json(r["text"], dict)
        if not obj or obj.get("root_cause") not in ROOT_CAUSES:
            raise news.NewsError("post-mortem reply had no valid root_cause", meta=r["meta"])
        sc = obj.get("suggested_change") if isinstance(obj.get("suggested_change"), dict) else {}
        return {"root_cause": obj["root_cause"],
                "what_happened": str(obj.get("what_happened", ""))[:600],
                "what_we_missed": str(obj.get("what_we_missed", ""))[:600],
                "lesson": str(obj.get("lesson", ""))[:400],
                "suggested_change": {"area": sc.get("area") if sc.get("area") in AREAS else "none",
                                     "change": str(sc.get("change", ""))[:400]},
                "meta": r["meta"], "kind": "miss"}

    def explain_win(self, case: dict) -> dict:
        r = self.claude.ask(WIN_PROMPT, json.dumps(case, ensure_ascii=False, indent=1), web=True)
        obj = news._parse_json(r["text"], dict)
        if not obj or obj.get("credit") not in WIN_CAUSES:
            raise news.NewsError("win review reply had no valid credit", meta=r["meta"])
        sc = obj.get("suggested_change") if isinstance(obj.get("suggested_change"), dict) else {}
        return {"root_cause": obj["credit"],
                "what_happened": str(obj.get("what_happened", ""))[:600],
                "what_worked": str(obj.get("what_worked", ""))[:600],
                "lesson": str(obj.get("lesson", ""))[:400],
                "suggested_change": {"area": sc.get("area") if sc.get("area") in AREAS else "none",
                                     "change": str(sc.get("change", ""))[:400]},
                "meta": r["meta"], "kind": "win"}


def review(policy: dict, analyst=None, log=print, now_stamp: str | None = None) -> dict:
    """Review every newly resolved market once. Returns counts and spend."""
    rv = policy["review"]
    resolved = engine.load_json(engine.RESOLUTIONS, {})
    done = {r["key"] for r in engine.read_jsonl(engine.REVIEWS)}
    latest = {}
    for j in engine.read_jsonl(engine.JUDGMENTS):
        if j.get("question_set") == QUESTION_SET_VERSION:
            latest[j["key"]] = j
    todo = [(k, j) for k, j in latest.items() if k in resolved and k not in done]
    books = engine.load_books(policy)
    stats = {"reviewed": 0, "post_mortems": 0, "win_reviews": 0, "errors": 0, "api_equivalent_usd": 0.0,
             "limited": False}
    if not todo:
        return stats
    lc = policy["learning"]
    day = (now_stamp or engine.now_iso())[:10]
    today = [r for r in engine.read_jsonl(engine.REVIEWS)
             if r.get("post_mortem") and str(r.get("ts", "")).startswith(day)]
    allowance = max(0, rv["max_postmortems_per_day"] - sum(1 for r in today if r["post_mortem"].get("kind", "miss") == "miss"))
    win_allowance = max(0, lc["max_win_reviews_per_day"] - sum(1 for r in today if r["post_mortem"].get("kind") == "win"))

    for k, j in todo:
        y = 1.0 if resolved[k] == "yes" else 0.0
        probs = {name: engine._prob(j, name) for name, _ in engine.SOURCES}
        errors = {name: round(abs(p - y), 4) for name, p in probs.items() if p is not None}
        bets = {name: round(sum(p["pnl"] for p in pf["closed"] if p["key"] == k), 2)
                for name, pf in books.items() if any(p["key"] == k for p in pf["closed"])}
        a = j.get("answers") or j.get("answers_no_news") or {}
        row = {
            "ts": now_stamp or engine.now_iso(), "key": k, "question": j["market"]["question"],
            "url": j["market"].get("url"), "outcome": resolved[k], "judged_at": j["ts"],
            "category": j["market"].get("category"), "playbook": (j.get("research") or {}).get("playbook"),
            "probs": probs, "errors": errors, "bets": bets,
            "signals": {q: a[q]["noul"] for q in ("rules_clear", "info_sufficient", "already_decided", "p_no") if q in a},
            "fact_kinds": dict(Counter(f.get("kind", "event") for f in j.get("recent_facts") or [])),
            "post_mortem": None,
        }
        # Worth a written post-mortem: a strategy lost money, or the researched forecast was confidently wrong.
        miss = any(v < 0 for v in bets.values()) or errors.get("jev_research", 0) >= rv["miss_threshold"]
        # Worth a "why were we right": a bet won, or research beat the market's own forecast by a wide margin.
        win = not miss and (any(v > 0 for v in bets.values()) or (
            "jev_research" in errors and errors["market"] - errors["jev_research"] >= lc["win_margin"]))
        if (miss and stats["post_mortems"] < allowance) or (win and stats["win_reviews"] < win_allowance):
            try:
                analyst = analyst or PostMortem(policy["research"], rv)
                case = {"question": j["market"]["question"], "resolution_rules": j["market"].get("rules", ""),
                        "judged_at": j["ts"], "facts_the_forecaster_had": j.get("recent_facts") or [],
                        "forecasts": {"jev_with_research": probs["jev_research"], "jev_alone": probs["jev_plain"],
                                      "claude_direct": probs["claude_direct"]},
                        "bets_by_strategy": bets,
                        "market_price_at_judgment": probs["market"], "actual_outcome": resolved[k]}
                pm = analyst.explain(case) if miss else analyst.explain_win(case)
                stats["api_equivalent_usd"] += pm["meta"].get("api_equivalent_usd", 0.0)
                row["post_mortem"] = pm
                stats["post_mortems" if miss else "win_reviews"] += 1
            except news.NewsError as e:
                stats["api_equivalent_usd"] += e.meta.get("api_equivalent_usd", 0.0)
                stats["limited"] = stats["limited"] or e.limited
                row["post_mortem_error"] = str(e)
                if not e.limited:
                    stats["errors"] += 1
                    log(f"! post-mortem failed for {j['market']['question'][:60]}: {e}")
                if e.fatal:
                    allowance = win_allowance = 0  # stop asking Claude this run; keep scoring
        engine.append_jsonl(engine.REVIEWS, row)
        stats["reviewed"] += 1
    stats["api_equivalent_usd"] = round(stats["api_equivalent_usd"], 4)
    return stats


def learning(reviews: list[dict]) -> dict:
    """What the reviews add up to: calibration of the researched forecaster, root causes, what worked."""
    rows = [r for r in reviews if r.get("probs", {}).get("jev_research") is not None]
    buckets = []
    for lo, hi in ((0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)):
        b = [r for r in rows if lo <= r["probs"]["jev_research"] < hi]
        if b:
            buckets.append({"range": f"{int(lo * 100)}–{min(100, int(hi * 100))}%", "n": len(b),
                            "predicted": round(sum(r["probs"]["jev_research"] for r in b) / len(b), 3),
                            "actual": round(sum(r["outcome"] == "yes" for r in b) / len(b), 3)})
    pms = [r for r in reviews if r.get("post_mortem")]
    misses = [r for r in pms if r["post_mortem"].get("kind", "miss") == "miss"]
    wins = [r for r in pms if r["post_mortem"].get("kind") == "win"]
    proposals = Counter((r["post_mortem"]["suggested_change"]["area"]) for r in pms
                        if r["post_mortem"]["suggested_change"]["area"] != "none")

    def card(r):
        pm = r["post_mortem"]
        return {"question": r["question"], "url": r.get("url"), "outcome": r["outcome"], "category": r.get("category"),
                "p": r["probs"].get("jev_research"), "market": r["probs"].get("market"), "ts": r["ts"],
                "bets": r.get("bets") or {}, "kind": pm.get("kind", "miss"), "root_cause": pm["root_cause"],
                "what_happened": pm["what_happened"], "what_we_missed": pm.get("what_we_missed", ""),
                "what_worked": pm.get("what_worked", ""), "lesson": pm["lesson"],
                "suggested_change": pm["suggested_change"]}
    return {
        "reviewed": len(reviews), "post_mortems": len(misses), "win_reviews": len(wins),
        "calibration": buckets,
        "root_causes": dict(Counter(r["post_mortem"]["root_cause"] for r in misses)),
        "credits": dict(Counter(r["post_mortem"]["root_cause"] for r in wins)),
        "proposals": dict(proposals),
        "recent": [card(r) for r in reversed(misses[-6:])],
        "recent_wins": [card(r) for r in reversed(wins[-6:])],
    }

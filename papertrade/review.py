"""The feedback loop: look back at every resolved market and learn from it.

For each market that resolved since the last review, score every forecaster and record which
signals it had. When the main forecast was confidently wrong, or a bet lost money, Claude writes a
post-mortem: what actually happened, what we missed, the root cause, and one suggested change.

Reviews never change trading on their own. Suggested changes are collected as proposals; Joey
approves them, and each approved change runs as a new strategy version next to the old one, so
the before/after comparison stays honest (PLAN.md).
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


class PostMortem:
    """A Claude Code run on the plan (web search allowed) that explains one miss."""

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
                "meta": r["meta"]}


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
    stats = {"reviewed": 0, "post_mortems": 0, "errors": 0, "api_equivalent_usd": 0.0, "limited": False}
    if not todo:
        return stats
    day = (now_stamp or engine.now_iso())[:10]
    done_today = sum(1 for r in engine.read_jsonl(engine.REVIEWS)
                     if r.get("post_mortem") and str(r.get("ts", "")).startswith(day))
    allowance = max(0, rv["max_postmortems_per_day"] - done_today)

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
            "probs": probs, "errors": errors, "bets": bets,
            "signals": {q: a[q]["noul"] for q in ("rules_clear", "info_sufficient", "already_decided", "p_no") if q in a},
            "fact_kinds": dict(Counter(f.get("kind", "event") for f in j.get("recent_facts") or [])),
            "post_mortem": None,
        }
        # Worth a written post-mortem: main lost money, or main's researched forecast was confidently wrong.
        miss = bets.get(engine.MAIN, 0) < 0 or errors.get("jev_research", 0) >= rv["miss_threshold"]
        if miss and stats["post_mortems"] < allowance:
            try:
                analyst = analyst or PostMortem(policy["research"], rv)
                case = {"question": j["market"]["question"], "resolution_rules": j["market"].get("rules", ""),
                        "judged_at": j["ts"], "facts_the_forecaster_had": j.get("recent_facts") or [],
                        "forecasts": {"jev_with_research": probs["jev_research"], "jev_alone": probs["jev_plain"],
                                      "claude_direct": probs["claude_direct"]},
                        "market_price_at_judgment": probs["market"], "actual_outcome": resolved[k]}
                pm = analyst.explain(case)
                stats["api_equivalent_usd"] += pm["meta"].get("api_equivalent_usd", 0.0)
                row["post_mortem"] = pm
                stats["post_mortems"] += 1
            except news.NewsError as e:
                stats["api_equivalent_usd"] += e.meta.get("api_equivalent_usd", 0.0)
                stats["limited"] = stats["limited"] or e.limited
                row["post_mortem_error"] = str(e)
                if not e.limited:
                    stats["errors"] += 1
                    log(f"! post-mortem failed for {j['market']['question'][:60]}: {e}")
                if e.fatal:
                    allowance = 0  # stop asking Claude this run; keep scoring
        engine.append_jsonl(engine.REVIEWS, row)
        stats["reviewed"] += 1
    stats["api_equivalent_usd"] = round(stats["api_equivalent_usd"], 4)
    return stats


def learning(reviews: list[dict]) -> dict:
    """What the reviews add up to: calibration of the main forecaster, root causes, proposals."""
    rows = [r for r in reviews if r.get("probs", {}).get("jev_research") is not None]
    buckets = []
    for lo, hi in ((0, .2), (.2, .4), (.4, .6), (.6, .8), (.8, 1.01)):
        b = [r for r in rows if lo <= r["probs"]["jev_research"] < hi]
        if b:
            buckets.append({"range": f"{int(lo * 100)}–{min(100, int(hi * 100))}%", "n": len(b),
                            "predicted": round(sum(r["probs"]["jev_research"] for r in b) / len(b), 3),
                            "actual": round(sum(r["outcome"] == "yes" for r in b) / len(b), 3)})
    pms = [r for r in reviews if r.get("post_mortem")]
    proposals = Counter((r["post_mortem"]["suggested_change"]["area"]) for r in pms
                        if r["post_mortem"]["suggested_change"]["area"] != "none")
    return {
        "reviewed": len(reviews), "post_mortems": len(pms),
        "calibration": buckets,
        "root_causes": dict(Counter(r["post_mortem"]["root_cause"] for r in pms)),
        "proposals": dict(proposals),
        "recent": [{"question": r["question"], "url": r.get("url"), "outcome": r["outcome"],
                    "p": r["probs"]["jev_research"], "ts": r["ts"], **{k: r["post_mortem"][k] for k in
                    ("root_cause", "what_happened", "what_we_missed", "lesson", "suggested_change")}}
                   for r in reversed(pms[-6:])],
    }

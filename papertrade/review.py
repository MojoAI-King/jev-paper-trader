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

Search the web to find out what actually happened and why. Then explain, plainly and specifically, why the forecast was off.

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
    def __init__(self, cfg: dict, review_cfg: dict, client: news.ClaudeClient | None = None):
        self.cfg, self.rcfg = cfg, review_cfg
        self.client = client or news.ClaudeClient(cfg["model"])

    def explain(self, case: dict) -> dict:
        start, usage, content, calls = time.monotonic(), {}, [], 0
        body = {
            "model": self.client.model, "max_tokens": 12000, "system": POSTMORTEM_PROMPT,
            "messages": [{"role": "user", "content": json.dumps(case, ensure_ascii=False, indent=1)}],
            "tools": [{"type": "web_search_20260318", "name": "web_search",
                       "max_uses": self.rcfg["max_searches_per_postmortem"]}],
            "output_config": {"effort": self.cfg["effort"]},
        }
        while True:
            data = self.client.post(body)
            calls += 1
            news._add_usage(usage, data.get("usage") or {})
            content = data.get("content") or []
            if data.get("stop_reason") != "pause_turn" or calls > 4:
                break
            body = dict(body, messages=body["messages"] + [{"role": "assistant", "content": content}])
        meta = {"cost_usd": news.cost_usd(self.client.model, usage),
                "latency_ms": round((time.monotonic() - start) * 1000)}
        if data.get("stop_reason") in ("refusal", "pause_turn", "max_tokens"):
            raise news.NewsError(f"post-mortem stopped: {data.get('stop_reason')}", meta=meta)
        obj = news._parse_json(news._text(content), dict)
        if not obj or obj.get("root_cause") not in ROOT_CAUSES:
            raise news.NewsError("post-mortem reply had no valid root_cause", meta=meta)
        sc = obj.get("suggested_change") if isinstance(obj.get("suggested_change"), dict) else {}
        return {"root_cause": obj["root_cause"],
                "what_happened": str(obj.get("what_happened", ""))[:600],
                "what_we_missed": str(obj.get("what_we_missed", ""))[:600],
                "lesson": str(obj.get("lesson", ""))[:400],
                "suggested_change": {"area": sc.get("area") if sc.get("area") in AREAS else "none",
                                     "change": str(sc.get("change", ""))[:400]},
                "meta": meta}


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
    stats = {"reviewed": 0, "post_mortems": 0, "errors": 0, "review_usd": 0.0}
    if not todo:
        return stats

    for k, j in todo:
        y = 1.0 if resolved[k] == "yes" else 0.0
        probs = {name: engine._prob(j, name) for name, _ in engine.SOURCES}
        errors = {name: round(abs(p - y), 4) for name, p in probs.items() if p is not None}
        bets = {name: round(sum(p["pnl"] for p in pf["closed"] if p["key"] == k), 2)
                for name, pf in books.items() if any(p["key"] == k for p in pf["closed"])}
        a = j["answers"]
        row = {
            "ts": now_stamp or engine.now_iso(), "key": k, "question": j["market"]["question"],
            "url": j["market"].get("url"), "outcome": resolved[k], "judged_at": j["ts"],
            "probs": probs, "errors": errors, "bets": bets,
            "signals": {q: a[q]["noul"] for q in ("rules_clear", "info_sufficient", "already_decided", "p_no") if q in a},
            "fact_kinds": dict(Counter(f.get("kind", "event") for f in j.get("recent_facts") or [])),
            "post_mortem": None,
        }
        miss = errors.get("jev_research", 0) >= rv["miss_threshold"] or any(v < 0 for v in bets.values())
        if miss and stats["post_mortems"] < rv["max_postmortems_per_run"]:
            try:
                analyst = analyst or PostMortem(policy["research"], rv)
                case = {"question": j["market"]["question"], "resolution_rules": j["market"].get("rules", ""),
                        "judged_at": j["ts"], "facts_the_forecaster_had": j.get("recent_facts") or [],
                        "forecasts": {"jev_with_research": probs["jev_research"], "jev_alone": probs["jev_plain"],
                                      "claude_direct": probs["claude_direct"]},
                        "market_price_at_judgment": probs["market"], "actual_outcome": resolved[k]}
                pm = analyst.explain(case)
                stats["review_usd"] += pm["meta"]["cost_usd"]
                row["post_mortem"] = pm
                stats["post_mortems"] += 1
            except news.NewsError as e:
                stats["review_usd"] += e.meta.get("cost_usd", 0.0)
                stats["errors"] += 1
                row["post_mortem_error"] = str(e)
                log(f"! post-mortem failed for {j['market']['question'][:60]}: {e}")
                if e.fatal:
                    analyst = None
                    rv = dict(rv, max_postmortems_per_run=0)  # stop trying this run; keep scoring
        engine.append_jsonl(engine.REVIEWS, row)
        stats["reviewed"] += 1
    stats["review_usd"] = round(stats["review_usd"], 4)
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

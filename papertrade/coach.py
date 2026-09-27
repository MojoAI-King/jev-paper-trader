"""The learning loop's Claude steps: the research playbook's coach and the weekly retrospective.

Both run through Claude Code on Joey's plan with no tools: they read only our own records. Neither
can change how money is bet on its own.

- The coach turns reviews (post-mortems of misses, "why were we right" reviews of wins) into the
  research playbook: short rules on HOW to research a kind of question, fed into every research call
  (news.Researcher). Code checks every rule: the full price screen (no odds, betting, market names,
  forecasts), a length cap, a known category, and evidence from a real review. Every version is kept
  in playbook_history.jsonl and every research record notes the version it used, so results can be
  compared before and after each change.
- The retrospective reads the week's numbers and writes up to two proposals. A proposed challenger
  (a strategy on its own fake $100k) starts only when Joey approves it (`python3 -m papertrade approve
  <id>`), or by itself within learning.challenger_bounds if he set auto_start_challengers to true.

How the loops fit together: docs/LEARNING.md.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timedelta, timezone

from . import engine, learn, news

COACH_PROMPT = """You keep the research playbook for a forecasting team's research desk. The desk researches yes/no questions on the web and hands dated, sourced facts to a forecaster. After questions resolve, reviewers write down what the research missed, or what carried a good call.

Update the playbook from the new reviews. A rule tells the researcher HOW to research a kind of question: which sources to read (the official resolution source named in the rules, a league's standings page, a government statistics release), what to check, which traps to avoid. A rule never says what the answer is or which side is likely, and never mentions odds, betting, bookmakers, prediction markets, market prices, forecasts, forecasters, predictions or chances.

Keep rules that still hold, sharpen ones the new reviews refine, merge duplicates, drop rules the evidence contradicts, and add a rule only when a review supports it. A review marked "lucky" or "unlucky" teaches nothing about research; don't make rules from it. At most {max_rules} rules, each one plain sentence under 280 characters, each tagged with one category from {categories}, or "general" if it fits every kind of question.

Reply with only a JSON object and no other text:
{"rules": [{"id": "<the existing id, or \\"new\\">", "category": "<category>", "rule": "<the rule>", "evidence": ["<review key>", ...]}],
 "changes": ["<one line per change: added, sharpened, merged or dropped, and why>"]}"""

RETRO_PROMPT = """You run the weekly review of a paper-trading experiment: forecasters (Jev, an AI judge; Claude) estimate yes/no prediction-market questions without ever seeing the market's price, several strategies each bet a fake $100,000 on the same markets, and every resolved market is scored. You get this week's numbers.

Write an honest review a curious friend could read, and propose at most two changes worth testing.

Rules for honesty:
- Small samples are noise. With fewer than 30 resolved markets behind a number, say so and don't propose changing anything because of it.
- The market's own price is a strong forecaster. Beating it is the goal; say plainly when we don't.
- Never propose changing the main strategy, bet sizing, fees, exposure caps or the price screen. Changes are tested as challengers: a new strategy with its own fake $100,000 next to the others.

A challenger may choose its probability source ("jev_research", "jev_plain", "claude_direct" or "jev_calibrated"), its gate source ("jev_research" or "jev_plain"), and move these gates within these ranges: {bounds}.

Reply with only a JSON object and no other text:
{"headline": "one sentence",
 "went_well": ["up to three short points, with numbers"],
 "went_badly": ["up to three short points, with numbers"],
 "proposals": [{"title": "short name",
                "why": "one or two sentences citing the numbers",
                "kind": "challenger" or "research" or "code",
                "strategy": {"label": "...", "probability": "...", "gates": "...", "gate_overrides": {"<gate>": <number>}},
                "judge_by": "how we will know it worked, decided now",
                "min_resolved": <resolved markets needed before judging>}]}
Include "strategy" only for kind "challenger"."""


def _now(now: datetime | None) -> datetime:
    return now or datetime.now(timezone.utc)


def load_playbook() -> dict:
    return engine.load_json(engine.PLAYBOOK, {"version": 0, "updated": None, "rules": []})


def load_proposals() -> dict:
    return engine.load_json(engine.PROPOSALS, {"proposals": []})


# ---------------- the coach ----------------

def new_reviews(playbook: dict, reviews: list[dict]) -> list[dict]:
    """Reviews with a written post-mortem or win review that the playbook hasn't learned from yet."""
    used = set(playbook.get("reviews_used") or [])
    return [r for r in reviews if r.get("post_mortem") and r["key"] not in used]


def coach_due(policy: dict, playbook: dict, reviews: list[dict], now: datetime) -> bool:
    lc = policy["learning"]
    day = now.strftime("%Y-%m-%d")
    if any(str(playbook.get(k) or "").startswith(day) for k in ("updated", "attempted")):
        return False  # at most once a day, and a failed attempt waits for tomorrow too
    return len(new_reviews(playbook, reviews)) >= lc["coach_min_new_reviews"]


def merge_rules(playbook: dict, proposed: list, known_reviews: set, max_rules: int) -> tuple[list, list, dict]:
    """Check the coach's rules in code. -> (rules to keep, dropped with reasons, what changed)."""
    old = {r["id"]: r for r in playbook.get("rules", [])}
    next_n = 1 + max([int(i[1:]) for i in old if i[1:].isdigit()] + [0] +
                     [int(i[1:]) for i in playbook.get("retired_ids", []) if i[1:].isdigit()])
    kept, dropped, change = [], [], {"added": [], "revised": [], "kept": []}
    for r in proposed if isinstance(proposed, list) else []:
        if not isinstance(r, dict):
            continue
        text = " ".join(str(r.get("rule") or "").split())
        cat = r.get("category")
        prev = old.get(r.get("id"))
        evidence = [e for e in (r.get("evidence") or []) if e in known_reviews]
        if prev and text == prev["rule"]:
            evidence = sorted(set(prev.get("evidence", [])) | set(evidence))
        reason = (learn.rule_problem(text) or
                  (None if cat in learn.CATEGORIES + ("general",) else f"unknown category {cat!r}") or
                  (None if evidence else "cites no review we have"))
        if not reason and len(kept) >= max_rules:
            reason = "over the rule cap"
        if not reason and any(k["rule"].lower() == text.lower() for k in kept):
            reason = "duplicate"
        if reason:
            dropped.append({"rule": text[:300], "reason": reason})
            continue
        if prev:
            rid = prev["id"]
            change["kept" if text == prev["rule"] else "revised"].append(rid)
            added = prev.get("added")
        else:
            rid, next_n = f"R{next_n}", next_n + 1
            change["added"].append(rid)
            added = None
        kept.append({"id": rid, "category": cat, "rule": text, "evidence": evidence, "added": added})
    change["retired"] = sorted(set(old) - {r["id"] for r in kept})
    return kept, dropped, change


class Coach:
    """One Claude Code call, no tools: current playbook + new reviews -> a revised playbook."""

    def __init__(self, cfg: dict, claude: news.ClaudeCode | None = None):
        self.cfg = cfg
        self.claude = claude or news.ClaudeCode(cfg)

    def propose(self, playbook: dict, reviews: list[dict], max_rules: int) -> dict:
        system = (COACH_PROMPT.replace("{max_rules}", str(max_rules))
                  .replace("{categories}", ", ".join(learn.CATEGORIES)))
        case = {"current_rules": [{k: r[k] for k in ("id", "category", "rule", "evidence")} for r in playbook["rules"]],
                "new_reviews": [_review_case(r) for r in reviews]}
        r = self.claude.ask(system, json.dumps(case, ensure_ascii=False, indent=1), web=False, timeout=600)
        obj = news._parse_json(r["text"], dict)
        if not obj or not isinstance(obj.get("rules"), list):
            raise news.NewsError("coach reply had no rules list", meta=r["meta"])
        return {"rules": obj["rules"], "changes": [str(c)[:300] for c in obj.get("changes") or []][:20],
                "meta": r["meta"]}


def _review_case(r: dict) -> dict:
    pm = r["post_mortem"]
    return {"key": r["key"], "category": r.get("category"), "question": r["question"], "outcome": r["outcome"],
            "review": "why we were right" if pm.get("kind") == "win" else "why we were wrong",
            "cause": pm["root_cause"], "what_happened": pm["what_happened"],
            "what_we_missed": pm.get("what_we_missed", ""), "what_worked": pm.get("what_worked", ""),
            "lesson": pm["lesson"], "suggested_change": pm["suggested_change"]}


def coach(policy: dict, coach_=None, log=print, now: datetime | None = None) -> dict:
    """Update the research playbook when enough new reviews have come in. Returns what happened."""
    now, lc = _now(now), policy["learning"]
    playbook, reviews = load_playbook(), engine.read_jsonl(engine.REVIEWS)
    out = {"ran": False, "version": playbook["version"]}
    if not coach_due(policy, playbook, reviews, now):
        return out
    fresh = new_reviews(playbook, reviews)
    try:
        coach_ = coach_ or Coach(policy["research"])
        prop = coach_.propose(playbook, fresh, lc["coach_max_rules"])
    except news.NewsError as e:
        log(f"! playbook coach: {e}")
        if not e.limited:  # a plan limit retries next cycle; a bad reply waits for tomorrow
            engine.save_json(engine.PLAYBOOK, dict(playbook, attempted=now.strftime(engine.TS)))
        return dict(out, error=str(e), limited=e.limited)
    rules, dropped, change = merge_rules(playbook, prop["rules"], {r["key"] for r in reviews}, lc["coach_max_rules"])
    stamp = now.strftime(engine.TS)
    retired = [r for r in playbook["rules"] if r["id"] in change["retired"]]
    changed = bool(change["added"] or change["revised"] or change["retired"])
    added_at = {r["id"]: r.get("added") or stamp for r in rules}
    new = {"version": playbook["version"] + (1 if changed else 0), "updated": stamp,
           "rules": [dict(r, added=added_at[r["id"]]) for r in rules],
           "reviews_used": sorted(set(playbook.get("reviews_used") or []) | {r["key"] for r in fresh}),
           "retired_ids": sorted(set(playbook.get("retired_ids") or []) | set(change["retired"]))}
    engine.save_json(engine.PLAYBOOK, new)
    engine.append_jsonl(engine.PLAYBOOK_LOG, {
        "ts": stamp, "from_version": playbook["version"], "version": new["version"], **change,
        "retired_rules": retired, "dropped": dropped, "changes": prop["changes"],
        "reviews": [r["key"] for r in fresh], "meta": prop["meta"]})
    log(f"Playbook: v{playbook['version']} -> v{new['version']}: {len(change['added'])} added, "
        f"{len(change['revised'])} sharpened, {len(change['retired'])} retired, {len(dropped)} refused by the checks")
    return dict(out, ran=True, version=new["version"], **{k: len(change[k]) for k in ("added", "revised", "retired")},
                dropped=len(dropped), api_equivalent_usd=prop["meta"].get("api_equivalent_usd", 0.0))


# ---------------- the weekly retrospective ----------------

def retro_due(policy: dict, now: datetime) -> bool:
    lc = policy["learning"]
    retros = engine.read_jsonl(engine.RETROS)
    done = [r for r in retros if not r.get("error")]
    if done and done[-1]["ts"] > (now - timedelta(days=lc["retro_every_days"])).strftime(engine.TS):
        return False
    if retros and retros[-1].get("error") and retros[-1]["ts"] > (now - timedelta(days=1)).strftime(engine.TS):
        return False  # a failed attempt waits a day
    return len(engine.read_jsonl(engine.REVIEWS)) >= lc["retro_min_reviews"]


def week_numbers(policy: dict, now: datetime) -> dict:
    """Everything the retrospective reads, computed here so Claude only interprets, never counts."""
    since = (now - timedelta(days=policy["learning"]["retro_every_days"])).strftime(engine.TS)
    judgments, resolved = engine.read_jsonl(engine.JUDGMENTS), engine.load_json(engine.RESOLUTIONS, {})
    reviews, books = engine.read_jsonl(engine.REVIEWS), engine.load_books(policy)
    strats = engine.strategies(policy)
    spol = {n: engine.strategy_policy(policy, s) for n, s in strats.items()}
    scans = [s for s in engine.read_jsonl(engine.SCANS) if "funnel" in s and s["ts"] >= since]
    week_reviews = [r for r in reviews if r["ts"] >= since]
    return {
        "since": since, "now": now.strftime(engine.TS),
        "strategies": [{"name": n, "label": s["label"], "probability": s["probability"], "gates": s["gates"],
                        "gate_overrides": s.get("gate_overrides") or {},
                        "equity": round(engine.equity_at_cost(books[n]), 2),
                        "realized": round(sum(p["pnl"] for p in books[n]["closed"]), 2),
                        "open": len(books[n]["open"]), "settled": len(books[n]["closed"]),
                        "wins": sum(1 for p in books[n]["closed"] if p["pnl"] > 0)} for n, s in strats.items()],
        "brier_all_time": engine.calibration(judgments, resolved),
        "by_category": learn.category_scores(judgments, resolved, engine._prob),
        "gate_ledger": learn.gate_ledger(policy, judgments, resolved, spol),
        "calibration_map": learn.calibration_map(reviews, policy["learning"]),
        "this_week": {"cycles": len(scans), "judged": sum(s["funnel"].get("judged", 0) for s in scans),
                      "with_research": sum(s["funnel"].get("with_research", 0) for s in scans),
                      "bets": dict(sum((Counter(s["funnel"]["bets"]) for s in scans), Counter())),
                      "resolved_and_reviewed": len(week_reviews),
                      "misses": dict(Counter(r["post_mortem"]["root_cause"] for r in week_reviews
                                             if r.get("post_mortem") and r["post_mortem"].get("kind", "miss") == "miss")),
                      "wins": dict(Counter(r["post_mortem"]["root_cause"] for r in week_reviews
                                           if r.get("post_mortem") and r["post_mortem"].get("kind") == "win"))},
        "playbook": {k: load_playbook().get(k) for k in ("version", "updated")},
        "proposals": [{k: p.get(k) for k in ("id", "title", "kind", "status", "created")}
                      for p in load_proposals()["proposals"]],
    }


class Retro:
    def __init__(self, cfg: dict, claude: news.ClaudeCode | None = None):
        self.cfg = cfg
        self.claude = claude or news.ClaudeCode(cfg)

    def write(self, numbers: dict, bounds: dict) -> dict:
        system = RETRO_PROMPT.replace("{bounds}", json.dumps(bounds))
        r = self.claude.ask(system, json.dumps(numbers, ensure_ascii=False, indent=1), web=False, timeout=600)
        obj = news._parse_json(r["text"], dict)
        if not obj or not str(obj.get("headline") or "").strip():
            raise news.NewsError("retrospective reply had no headline", meta=r["meta"])
        return dict(obj, meta=r["meta"])


def _clip(xs, n, width=300):
    return [str(x)[:width] for x in (xs if isinstance(xs, list) else [])][:n]


def retro(policy: dict, writer=None, log=print, now: datetime | None = None) -> dict:
    """Write the weekly retrospective when it's due, and file its proposals."""
    now, lc = _now(now), policy["learning"]
    if not retro_due(policy, now):
        return {"ran": False}
    numbers = week_numbers(policy, now)
    try:
        writer = writer or Retro(policy["research"])
        rep = writer.write(numbers, lc["challenger_bounds"])
    except news.NewsError as e:
        log(f"! weekly retrospective: {e}")
        if not e.limited:
            engine.append_jsonl(engine.RETROS, {"ts": now.strftime(engine.TS), "error": str(e)[:300]})
        return {"ran": False, "error": str(e), "limited": e.limited}
    stamp = now.strftime(engine.TS)
    book = load_proposals()
    names = set(policy["strategies"]) | {p["id"] for p in book["proposals"]}
    running = sum(1 for p in book["proposals"] if p.get("status") == "running")
    filed = []
    for raw in (rep.get("proposals") if isinstance(rep.get("proposals"), list) else [])[:2]:
        if not isinstance(raw, dict):
            continue
        kind = raw.get("kind") if raw.get("kind") in ("challenger", "research", "code") else "code"
        n = len(book["proposals"]) + 1
        pid = f"ch{n}" if kind == "challenger" else f"p{n}"
        while pid in names:
            n += 1
            pid = f"ch{n}" if kind == "challenger" else f"p{n}"
        names.add(pid)
        p = {"id": pid, "created": stamp, "kind": kind, "title": str(raw.get("title") or "")[:120],
             "why": str(raw.get("why") or "")[:600], "judge_by": str(raw.get("judge_by") or "")[:400],
             "min_resolved": raw.get("min_resolved") if isinstance(raw.get("min_resolved"), int) else 50,
             "status": "proposed", "status_reason": "waiting for Joey"}
        if kind == "challenger":
            s = raw.get("strategy") if isinstance(raw.get("strategy"), dict) else {}
            s = {k: s[k] for k in ("label", "probability", "gates", "gate_overrides") if k in s}
            problem = learn.challenger_problem(s, policy)
            p["strategy"] = s
            if problem:
                p.update(status="invalid", status_reason=problem)
            elif lc["auto_start_challengers"] and running < lc["max_running_challengers"]:
                p.update(status="running", status_reason="started automatically within the allowed bounds",
                         started=stamp)
                running += 1
        book["proposals"].append(p)
        filed.append(p)
    engine.save_json(engine.PROPOSALS, book)
    engine.append_jsonl(engine.RETROS, {
        "ts": stamp, "headline": str(rep["headline"])[:300], "went_well": _clip(rep.get("went_well"), 3),
        "went_badly": _clip(rep.get("went_badly"), 3), "proposals": [p["id"] for p in filed],
        "numbers": numbers, "meta": rep["meta"]})
    log(f"Weekly retrospective: {rep['headline'][:120]}  ({len(filed)} proposals)")
    return {"ran": True, "proposals": len(filed), "api_equivalent_usd": rep["meta"].get("api_equivalent_usd", 0.0)}


def set_status(pid: str, status: str, policy: dict, now: datetime | None = None) -> str:
    """Joey's decision on a proposal: approve (a challenger starts next cycle), reject, or retire."""
    book = load_proposals()
    p = next((x for x in book["proposals"] if x["id"] == pid), None)
    if p is None:
        return f"No proposal {pid}."
    stamp = _now(now).strftime(engine.TS)
    if status == "running":
        if p["kind"] != "challenger":
            p.update(status="approved", status_reason=f"approved by Joey {stamp[:10]}; needs a code session")
        else:
            problem = learn.challenger_problem(p.get("strategy") or {}, policy)
            if problem:
                return f"Can't start {pid}: {problem}"
            p.update(status="running", status_reason=f"approved by Joey {stamp[:10]}", started=stamp)
    else:
        p.update(status=status, status_reason=f"{status} by Joey {stamp[:10]}")
    engine.save_json(engine.PROPOSALS, book)
    return f"{pid}: {p['status']}. Commit and push papertrade_data/proposals.json so the hourly run picks it up."

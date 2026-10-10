"""The learning loop's Claude steps: the research playbook's coach and the daily review.

Both run through Claude Code on Joey's plan with no tools: they read only our own records.

- The coach turns reviews (post-mortems of misses, "why were we right" reviews of wins) into the
  research playbook: short rules on HOW to research a kind of question, fed into every research call
  (news.Researcher). Code checks every rule: the full price screen (no odds, betting, market names,
  forecasts), a length cap, a known category, and evidence from a real review. Every version is kept
  in playbook_history.jsonl and every research record notes the version it used, so results can be
  compared before and after each change.
- The review (retro) reads the numbers once a day and files up to learning.max_proposals_per_retro
  proposals. Joey, 2026-09-28: it may change any strategy's rules by itself (gates, bet size, open-bet
  limit, market filters; learn.rules_problem checks every one), main included, except the frozen yardstick,
  and at most once every learning.min_days_between_changes per strategy. It may start a challenger (a
  strategy on its own fake $100k) or retire one. It can't change code: a code idea waits for Joey
  (`python3 -m papertrade approve|reject <id>`). Every change is kept in rules_history.jsonl and shown on
  the page, and every bet records the rules version it was placed under.

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

RETRO_PROMPT = """You run the daily review of a paper-trading experiment: forecasters (Jev, an AI judge; Claude) estimate yes/no prediction-market questions without ever seeing the market's price, several strategies each bet a fake $100,000 on the same markets, and every resolved market is scored. You get the numbers: each strategy's rules and results (all time, and since its rules last changed), the forecasters' scores, what each gate stopped, and the recent rule changes.

Your job is to make the strategies make more money by experimenting. The money is fake, so trying things is cheap and is the point; every change is logged and shown to the people watching. Write an honest review a curious friend could read, then propose at most {max_proposals} changes.

What you may do:
- "tune": change any strategy's rules, main included. The rules and their allowed ranges: {bounds}. The gates: min_edge is how far the forecast must beat the price paid, after fees; min_rules_clear and min_info_sufficient are Jev's own 0-1 ratings of how clear the rules are and whether it has the information it needs; max_framing_gap is how far Jev's YES and NO answers may disagree. Sizing, as fractions of the strategy's bankroll (0.02 = 2%): kelly_fraction is the share of the Kelly stake bet, max_stake_pct caps one bet (and all open bets in one event together), max_total_exposure_pct caps all open bets together. Since 2026-10-09 every strategy but the yardstick sizes by its forecaster's measured edge over the market price ("skill": lambda per probability source, from finished markets with a real price). While a source's lambda is 0, its strategies place only small probe bets (0.25% of the bankroll, at most 5 a day) whatever kelly_fraction says; Kelly sizing on the forecast shrunk toward the price starts once lambda is positive on 300+ markets. So a sizing change does nothing until then: improve the gates and filters instead. "skip_categories" is a list drawn from {categories}; "min_ask" and "max_ask" bound the price paid for a contract. null puts a rule back to that strategy's starting value. You can't tune {frozen} (the yardstick the tuning is judged against), or a strategy whose "can_change_from" is still in the future.
- "challenger": start a new strategy on its own fake $100,000: a probability source ("jev_research", "jev_plain", "claude_direct" or "jev_calibrated"), a gate source ("jev_research" or "jev_plain"), and any rules as above. At most {max_challengers} run at a time.
- "retire": stop a running challenger that isn't earning its place, to free its slot.
- "code": an idea that needs a code change. You can't change code; Joey reads these and approves or rejects them.

Rules for honesty:
- Say how many results a number rests on. Under 30 resolved markets it is mostly noise: you may still experiment, but call it an experiment, not a finding.
- The market's own price is a strong forecaster. Beating it is the goal; say plainly when we don't.
- Judge a strategy's current rules by its results since they last changed ("since_change"), not all time.
- "by_price_paid" splits each strategy's settled bets into long shots (under 30c), coin flips and favourites. On 2026-10-01 long shots had lost 32.6k of the 35.7k lost (1 win in 21), so Joey set every strategy's min_ask to 0.30; lower it only if the numbers say long shots now pay.
- Whether tuning main pays is read from "yardstick": main against original on the bets both placed since original started.
- Every proposal says now how we'll know it worked ("judge_by") and after how many resolved markets.
- Fees, the price screen, research budgets and how results are scored are not yours to change.

Reply with only a JSON object and no other text:
{"headline": "one sentence",
 "went_well": ["up to three short points, with numbers"],
 "went_badly": ["up to three short points, with numbers"],
 "proposals": [{"kind": "tune" or "challenger" or "retire" or "code",
                "title": "short name",
                "why": "one or two sentences citing the numbers",
                "strategy": "<the strategy's name>" for tune and retire, or {"label": "...", "probability": "...", "gates": "...", "rules": {"<rule>": <value>}} for a challenger,
                "rules": {"<rule>": <value or null>} for tune,
                "judge_by": "how we will know it worked, decided now",
                "min_resolved": <resolved markets needed before judging>}]}"""


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
        r = self.claude.ask(system, json.dumps(case, ensure_ascii=False, indent=1), web=False, timeout=600, paced=False)
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


# ---------------- the daily review ----------------

KINDS = ("tune", "challenger", "retire", "code", "research")

def retro_due(policy: dict, now: datetime) -> bool:
    lc = policy["learning"]
    retros = engine.read_jsonl(engine.RETROS)
    done = [r for r in retros if not r.get("error")]
    if done and done[-1]["ts"] > (now - timedelta(days=lc["retro_every_days"])).strftime(engine.TS):
        return False
    if retros and retros[-1].get("error") and retros[-1]["ts"] > (now - timedelta(days=1)).strftime(engine.TS):
        return False  # a failed attempt waits a day
    return len(engine.read_jsonl(engine.REVIEWS)) >= lc["retro_min_reviews"]


def _normal(k: str, v):
    """One spelling per behaviour: a category list is sorted without repeats. An empty list stays an empty
    list when stored (it clears a starting skip list; null would put the starting list back)."""
    if k == "skip_categories" and isinstance(v, list):
        return sorted(set(v))
    return v


def effective_rules(spol: dict) -> dict:
    """Every rule's value in one strategy's policy (engine.strategy_policy), None where a filter is off, so a
    change that bets the same way (an empty skip list where there was none) compares equal."""
    out = {k: _normal(k, spol["gates"].get(k) if k in learn.GATE_RULES else spol["sizing"].get(k)
                      if k in learn.SIZING_RULES else (spol.get("filters") or {}).get(k)) for k in learn.RULES}
    out["skip_categories"] = out["skip_categories"] or None
    return out


def history(name: str) -> list[dict]:
    """Every logged rule change of one strategy, oldest first (rules_history.jsonl is append-only)."""
    return [c for c in engine.read_jsonl(engine.TUNED_LOG) if isinstance(c, dict) and c.get("strategy") == name]


PRICE_BANDS = ((0.0, 0.3, "under 30c"), (0.3, 0.6, "30-60c"), (0.6, 1.01, "60c and up"))


def by_price(positions: list[dict]) -> dict:
    """Settled record by the price paid per contract: long shots, coin flips, favourites (code idea p4,
    approved by Joey 2026-10-01 after long shots under 30c lost 32.6k of 35.7k)."""
    return {name: _record([p for p in positions if p.get("settled") and lo <= p["cost_per"] < hi])
            for lo, hi, name in PRICE_BANDS}


def _record(positions: list[dict]) -> dict:
    closed = [p for p in positions if p.get("settled")]
    return {"bets": len(positions), "open": len(positions) - len(closed), "settled": len(closed),
            "wins": sum(1 for p in closed if p["pnl"] > 0), "losses": sum(1 for p in closed if p["pnl"] <= 0),
            "pnl": round(sum(p["pnl"] for p in closed), 2), "staked": round(sum(p["total_cost"] for p in positions), 2)}


def yardstick(books: dict, name: str) -> dict:
    """Main against a frozen strategy on the same footing: bets opened since the frozen ledger began, leaving
    out markets main already held then (main couldn't bet them again; the fresh ledger could)."""
    main, yard = books[engine.MAIN], books[name]
    since = yard.get("created") or ""
    held = {p["key"] for p in main["open"] + main["closed"]
            if p["opened"] < since and (not p.get("settled") or p["settled"] > since)}
    pick = lambda pf: [p for p in pf["open"] + pf["closed"] if p["opened"] >= since and p["key"] not in held]
    return {"since": since, "note": "main vs this strategy on bets opened since it started, leaving out markets "
                                    "main already held then", engine.MAIN: _record(pick(main)), name: _record(pick(yard))}


def next_change(policy: dict, strat: dict, name: str | None = None) -> datetime | None:
    """When a strategy's rules may next change: min_days_between_changes after the last change, taken from
    rules.json and from the history, so undoing a change by hand doesn't also reset the wait."""
    times = [engine._when(strat.get("tuned_at"))] + [engine._when(c.get("ts")) for c in (history(name) if name else [])]
    times = [t for t in times if t]
    return max(times) + timedelta(days=policy["learning"]["min_days_between_changes"]) if times else None


def week_numbers(policy: dict, now: datetime) -> dict:
    """Everything the review reads, computed here so Claude only interprets, never counts."""
    lc = policy["learning"]
    since = (now - timedelta(days=lc["retro_every_days"])).strftime(engine.TS)
    judgments, resolved = engine.read_jsonl(engine.JUDGMENTS), engine.load_json(engine.RESOLUTIONS, {})
    reviews, books = engine.read_jsonl(engine.REVIEWS), engine.load_books(policy)
    strats = engine.strategies(policy)
    spol = {n: engine.strategy_policy(policy, s) for n, s in strats.items()}
    scans = [s for s in engine.read_jsonl(engine.SCANS) if "funnel" in s and s["ts"] >= since]
    week_reviews = [r for r in reviews if r["ts"] >= since]
    frozen = set(lc.get("frozen_strategies") or ())

    def row(n: str, s: dict) -> dict:
        b, nxt = books[n], next_change(policy, s, n)
        every = b["open"] + b["closed"]
        return {"name": n, "label": s["label"], "probability": s["probability"], "gates": s["gates"],
                "challenger": bool(s.get("challenger")), "frozen": n in frozen,
                "rules": effective_rules(spol[n]),
                "starting_rules": effective_rules(engine.strategy_policy(policy, dict(s, tuned={}))),
                "rules_version": s["rules_version"], "rules_changed": s.get("tuned_at"),
                "can_change_from": None if n in frozen or not nxt or nxt <= now else nxt.strftime(engine.TS),
                "equity": round(engine.equity_at_cost(b), 2), "all_time": _record(every),
                "since_change": _record([p for p in every if p.get("rules_version", 1) == s["rules_version"]]),
                "by_price_paid": by_price(every)}
    yard = {name: yardstick(books, name) for name in lc.get("frozen_strategies") or ()
            if name in books and engine.MAIN in books}
    return {
        "since": since, "now": now.strftime(engine.TS), "period_days": lc["retro_every_days"],
        "strategies": [row(n, s) for n, s in strats.items()],
        "yardstick": yard,
        "recent_rule_changes": [{k: c.get(k) for k in ("ts", "strategy", "version", "changed", "why", "judge_by")}
                                for c in engine.read_jsonl(engine.TUNED_LOG)[-10:]],
        "brier_all_time": engine.calibration(judgments, resolved),
        "skill": engine.skill(judgments + engine.read_jsonl(engine.MENTIONS), resolved, policy["skill"]["min_markets"]),
        "by_category": learn.category_scores(judgments, resolved, engine._prob),
        "gate_ledger": learn.gate_ledger(policy, judgments, resolved, starting_policies(policy, strats)),
        "calibration_map": learn.calibration_map(reviews, policy["learning"]),
        "recent": {"cycles": len(scans), "judged": sum(s["funnel"].get("judged", 0) for s in scans),
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

    def write(self, numbers: dict, limits: dict) -> dict:
        system = RETRO_PROMPT
        for k, v in limits.items():
            system = system.replace("{" + k + "}", v if isinstance(v, str) else json.dumps(v))
        r = self.claude.ask(system, json.dumps(numbers, ensure_ascii=False, indent=1), web=False, timeout=600, paced=False)
        obj = news._parse_json(r["text"], dict)
        if not obj or not str(obj.get("headline") or "").strip():
            raise news.NewsError("review reply had no headline", meta=r["meta"])
        return dict(obj, meta=r["meta"])


def _clip(xs, n, width=300):
    return [str(x)[:width] for x in (xs if isinstance(xs, list) else [])][:n]


def limits(policy: dict) -> dict:
    lc = policy["learning"]
    return {"bounds": lc["bounds"], "categories": list(learn.CATEGORIES),
            "frozen": ", ".join(lc.get("frozen_strategies") or ()) or "nothing",
            "max_proposals": str(lc["max_proposals_per_retro"]), "max_challengers": str(lc["max_running_challengers"])}


def tune_problem(policy: dict, strats: dict, name, rules) -> str | None:
    """Why a proposed rule change can't apply, whatever the timing, or None."""
    if not isinstance(name, str) or name not in strats:
        return f"no strategy named {str(name)[:40]!r}"
    if name in (policy["learning"].get("frozen_strategies") or ()):
        return f"{name} is the fixed yardstick and never changes"
    if not isinstance(rules, dict) or not rules:
        return "no rules given"
    return learn.rules_problem(rules, policy)


def tune(policy: dict, name, rules, now: datetime, why: str = "", judge_by: str = "", min_resolved: int = 50,
         pid: str | None = None, by: str = "the daily review", wait: bool = True) -> tuple[str, str]:
    """Change one strategy's rules. Returns (status, reason): "applied", "invalid" or "skipped".
    Every check is in code: the strategy exists and isn't frozen, every rule is one the loop may set and
    in range (learn.rules_problem), and the strategy's rules didn't change in the last
    min_days_between_changes. The new rules go to rules.json and the change to rules_history.jsonl."""
    stamp = now.strftime(engine.TS)
    strats = engine.strategies(policy)
    problem = tune_problem(policy, strats, name, rules)
    if problem:
        return "invalid", problem
    rules = {k: _normal(k, v) for k, v in rules.items()}
    cur = strats[name]
    nxt = next_change(policy, cur, name)
    if wait and nxt and now < nxt:  # Joey's own changes (wait=False) don't wait; the loop's always do
        last = nxt - timedelta(days=policy["learning"]["min_days_between_changes"])
        return "skipped", (f"{name}'s rules changed {last:%Y-%m-%d}; the next change is allowed from "
                           f"{nxt.strftime('%Y-%m-%d %H:%M')}Z")
    merged = {k: v for k, v in {**(cur.get("tuned") or {}), **rules}.items() if v is not None}
    new = dict(cur, tuned=merged)
    problem = learn.rules_problem({**engine.strategy_rules(dict(cur, tuned={})), **merged}, policy)
    if problem:
        return "invalid", problem
    try:
        before = effective_rules(engine.strategy_policy(policy, cur))
        after = effective_rules(engine.strategy_policy(policy, new))
    except ValueError as e:
        return "invalid", str(e)
    changed = {k: [before[k], after[k]] for k in learn.RULES if before[k] != after[k]}
    if not changed:
        return "skipped", "changes nothing"
    book = engine.load_json(engine.TUNED, {})
    saved = book.get("strategies") if isinstance(book.get("strategies"), dict) else {}
    # the next number after every version this strategy ever had, so a number is never reused (bets carry it)
    seen = [cur["rules_version"], (saved.get(name) or {}).get("version") if isinstance(saved.get(name), dict) else 1]
    seen += [c.get("version") for c in history(name)]
    version = max(v for v in seen if isinstance(v, int) and not isinstance(v, bool)) + 1
    saved[name] = {"version": version, "since": stamp, "rules": merged, "proposal": pid}
    engine.save_json(engine.TUNED, {"strategies": saved})
    engine.append_jsonl(engine.TUNED_LOG, {
        "ts": stamp, "strategy": name, "version": version, "changed": changed, "rules": merged,
        "why": str(why)[:600], "judge_by": str(judge_by)[:400], "min_resolved": min_resolved, "proposal": pid, "by": by})
    return "applied", f"{name} rules v{version}: " + "; ".join(learn.describe_change(k, *v) for k, v in changed.items())


def starting_policies(policy: dict, strats: dict) -> dict:
    """Each strategy's policy before any tuning: what every decision made before 2026-09-28 used."""
    return {n: engine.strategy_policy(policy, dict(s, tuned={})) for n, s in strats.items()}


def _retire(book: dict, target, stamp: str, why: str, by: str = "the daily review") -> tuple[str, str]:
    ch = next((x for x in book["proposals"] if x["id"] == target and x.get("kind") == "challenger"
               and x.get("status") == "running"), None)
    if ch is None:
        return "invalid", f"{str(target)[:40]!r} isn't a running challenger (only challengers can be retired)"
    ch.update(status="retired", status_reason=f"retired by {by} {stamp[:10]}: {why[:200]}", retired=stamp)
    return "applied", f"{target} retired; its open bets still settle and its record stays on the page"


def _label_taken(book: dict, label, pid: str) -> bool:
    """Another running or waiting challenger already has this name (case and spaces aside)."""
    want = str(label).strip().lower()
    return any(x.get("id") != pid and x.get("kind") == "challenger" and x.get("status") in ("running", "proposed")
               and str((x.get("strategy") or {}).get("label", "")).strip().lower() == want for x in book["proposals"])


def _free_slot(book: dict, pid: str | None = None):
    """A page colour for a challenger that is starting: one no other running challenger holds (7 or 8)."""
    held = {x.get("slot") for x in book["proposals"] if x.get("status") == "running" and x.get("id") != pid}
    return next((s for s in (7, 8) if s not in held), None)


def _start_waiting(book: dict, policy: dict, stamp: str) -> list[str]:
    """Start challengers that were waiting for a free slot, oldest first, now that one may have opened."""
    lc, started = policy["learning"], []
    if not lc["auto_start_challengers"]:
        return started
    for p in book["proposals"]:
        running = sum(1 for x in book["proposals"] if x.get("status") == "running")
        if running >= lc["max_running_challengers"]:
            break
        if (p.get("kind") == "challenger" and p.get("status") == "proposed"
                and str(p.get("status_reason", "")).startswith("waiting for a free slot")
                and learn.challenger_problem(p.get("strategy") or {}, policy) is None):
            p.update(status="running", status_reason="started automatically when a slot opened", started=stamp,
                     slot=_free_slot(book))
            started.append(p["id"])
    return started


def retro(policy: dict, writer=None, log=print, now: datetime | None = None) -> dict:
    """Write the daily review when it's due, and file (and, within the rules, apply) its proposals."""
    now, lc = _now(now), policy["learning"]
    if not retro_due(policy, now):
        return {"ran": False}
    numbers = week_numbers(policy, now)
    try:
        writer = writer or Retro(policy["research"])
        rep = writer.write(numbers, limits(policy))
    except news.NewsError as e:
        log(f"! daily review: {e}")
        if not e.limited:
            engine.append_jsonl(engine.RETROS, {"ts": now.strftime(engine.TS), "error": str(e)[:300]})
        return {"ran": False, "error": str(e), "limited": e.limited}
    stamp = now.strftime(engine.TS)
    book = load_proposals()
    names = set(policy["strategies"]) | {p["id"] for p in book["proposals"]}
    filed = []
    raws = [r for r in (rep.get("proposals") if isinstance(rep.get("proposals"), list) else [])
            if isinstance(r, dict)][:lc["max_proposals_per_retro"]]
    raws.sort(key=lambda r: r.get("kind") != "retire")  # a retire frees its slot before a new challenger asks
    waited = False
    for raw in raws:
        if raw.get("kind") != "retire" and not waited:  # after the retires, before anything new:
            _start_waiting(book, policy, stamp)         # the longest-waiting challenger gets a free slot first
            waited = True
        kind = raw.get("kind") if raw.get("kind") in KINDS else "code"
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
        running = sum(1 for x in book["proposals"] if x.get("status") == "running")
        try:
            _file(p, raw, kind, book, running, policy, now, stamp)
        except Exception as e:  # one malformed proposal must never cost the cycle (it's the only ledger writer)
            p.update(status="invalid", status_reason=f"could not be read: {type(e).__name__}")
        book["proposals"].append(p)
        filed.append(p)
    _start_waiting(book, policy, stamp)
    engine.save_json(engine.PROPOSALS, book)
    engine.append_jsonl(engine.RETROS, {
        "ts": stamp, "headline": str(rep["headline"])[:300], "went_well": _clip(rep.get("went_well"), 3),
        "went_badly": _clip(rep.get("went_badly"), 3), "proposals": [p["id"] for p in filed],
        "numbers": numbers, "meta": rep["meta"]})
    log(f"Daily review: {rep['headline'][:120]}  ({len(filed)} proposals, "
        f"{sum(1 for p in filed if p['kind'] == 'tune' and p['status'] == 'applied')} rule changes)")
    return {"ran": True, "proposals": len(filed), "tuned": [p["strategy"] for p in filed
                                                            if p["kind"] == "tune" and p["status"] == "applied"],
            "api_equivalent_usd": rep["meta"].get("api_equivalent_usd", 0.0)}


def _file(p: dict, raw: dict, kind: str, book: dict, running: int, policy: dict, now: datetime, stamp: str) -> None:
    """Check one proposal and, where the rules allow, act on it. Updates p in place."""
    lc = policy["learning"]
    if kind == "challenger":
        s = raw.get("strategy") if isinstance(raw.get("strategy"), dict) else {}
        s = {k: s[k] for k in ("label", "probability", "gates", "gate_overrides", "rules") if k in s}
        problem = learn.challenger_problem(s, policy)
        if not problem and _label_taken(book, s.get("label"), p["id"]):
            problem = f"a challenger named {s.get('label')!r} is already running or waiting"
        p["strategy"] = s
        if problem:
            p.update(status="invalid", status_reason=problem)
        elif lc["auto_start_challengers"] and running < lc["max_running_challengers"]:
            p.update(status="running", status_reason="started automatically within the allowed bounds", started=stamp,
                     slot=_free_slot(book))
        elif lc["auto_start_challengers"]:
            p.update(status_reason=f"waiting for a free slot ({running} challengers already running)")
    elif kind == "tune":
        target = raw.get("strategy") if isinstance(raw.get("strategy"), str) else ""
        rules = raw.get("rules") if isinstance(raw.get("rules"), dict) else {}
        p.update(strategy=target[:40], rules=rules)
        if lc["auto_tune"]:
            status, reason = tune(policy, target, rules, now, p["why"], p["judge_by"], p["min_resolved"], p["id"])
            p.update(status=status, status_reason=reason)
        else:
            problem = tune_problem(policy, engine.strategies(policy), target, rules)
            if problem:
                p.update(status="invalid", status_reason=problem)
    elif kind == "retire":
        target = raw.get("strategy") if isinstance(raw.get("strategy"), str) else ""
        p["strategy"] = target[:40]
        status, reason = _retire(book, target, stamp, p["why"])
        p.update(status=status, status_reason=reason)


def set_status(pid: str, status: str, policy: dict, now: datetime | None = None) -> str:
    """Joey's decision on a proposal: approve (a challenger starts next cycle; a rule change applies when
    auto_tune is off; a code idea is marked for a code session), reject, or retire."""
    book = load_proposals()
    p = next((x for x in book["proposals"] if x["id"] == pid), None)
    if p is None:
        return f"No proposal {pid}."
    stamp = _now(now).strftime(engine.TS)
    if p["kind"] == "challenger" and p["status"] == "retired":
        return f"{pid} is retired; its record stays on the page as it is."
    if status == "running":
        if p["kind"] == "tune":
            if p["status"] != "proposed":
                return f"{pid} is {p['status']}; only a proposed rule change can be approved."
            st, reason = tune(policy, p.get("strategy"), p.get("rules"), _now(now), p.get("why", ""),
                              p.get("judge_by", ""), p.get("min_resolved", 50), pid, by="Joey")
            if st != "applied":
                return f"Can't apply {pid}: {reason}"
            p.update(status="applied", status_reason=f"approved by Joey {stamp[:10]}; {reason}")
        elif p["kind"] != "challenger":
            p.update(status="approved", status_reason=f"approved by Joey {stamp[:10]}; needs a code session")
        else:
            if p["status"] == "running":
                return f"{pid} is already running."
            problem = learn.challenger_problem(p.get("strategy") or {}, policy)
            if not problem and _label_taken(book, (p.get("strategy") or {}).get("label"), pid):
                problem = "another running or waiting challenger has that name"
            if problem:
                return f"Can't start {pid}: {problem}"
            running = sum(1 for x in book["proposals"] if x.get("status") == "running")
            if running >= policy["learning"]["max_running_challengers"]:
                return (f"Can't start {pid}: {running} challengers are running (learning.max_running_challengers); "
                        "retire one first")
            p.update(status="running", status_reason=f"approved by Joey {stamp[:10]}", started=stamp,
                     slot=_free_slot(book, pid))
    elif p["kind"] == "challenger" and p["status"] == "running":  # reject or retire: either way it's retired,
        st, reason = _retire(book, pid, stamp, "by hand", by="Joey")  # so its record stays on the page
        if st != "applied":
            return f"Can't retire {pid}: {reason}"
        _start_waiting(book, policy, stamp)
    elif p["kind"] == "tune" and p["status"] == "applied":
        return (f"{pid} is already applied. To undo it, set its rules back with a new change, or turn "
                "learning.auto_tune off and edit papertrade_data/rules.json in a session.")
    elif status == "retired" and p["kind"] == "challenger":
        return f"Can't retire {pid}: it isn't running ({p['status']})."
    else:
        p.update(status=status, status_reason=f"{status} by Joey {stamp[:10]}")
    engine.save_json(engine.PROPOSALS, book)
    return f"{pid}: {p['status']}. Commit and push papertrade_data/ so the next cycle picks it up."

"""The self-improvement loop's numbers. Nothing here calls Claude or Jev, so it runs every cycle for free.

- category():        tags each market (sports, politics, crypto, ...) so results and lessons can be grouped.
- calibration_map(): learns how far to trust Jev's researched probabilities from resolved outcomes. The
                     "calibrated" strategy bets with the corrected probability once enough markets resolved.
- gate_ledger():     for every resolved market a strategy saw an edge on, what a flat $100 bet would have
                     made, grouped by which gate stopped it. This is the evidence for loosening or
                     tightening a gate, instead of a hunch.
- category_scores(): Brier score per category, per forecaster: where we beat the market and where we don't.

The parts that call Claude (the research playbook's coach and the weekly retrospective) are in coach.py.
How the loops fit together, and what may change without Joey: docs/LEARNING.md.
"""
from __future__ import annotations

import math
import re

from . import news
from .judge import QUESTION_SET_VERSION

# First match wins, so the specific kinds come before the broad ones (a "vs." is sports only after
# crypto, weather and culture had their say).
CATEGORY_RULES = [
    ("crypto", r"\bbitcoin|\bbtc\b|\bethereum|\beth\b|\bsolana|\bcrypto|\bdogecoin|\bxrp\b|KXBTC|KXETH"),
    ("weather", r"temperature|\bhigh temp|\brain(?:fall)?\b|\bsnow|hurricane|tropical storm|\bweather\b|KXHIGH|KXRAIN"),
    ("economy", r"\bcpi\b|inflation|\bfed\b|federal reserve|interest rate|\bgdp\b|unemployment|jobs report|payrolls|"
                r"recession|s&p 500|nasdaq|dow jones|stock price|treasury|tariff|KXCPI|KXFED|KXGDP|KXINX"),
    ("culture", r"rotten tomatoes|box office|billboard|album|\bsong\b|oscar|emmy|grammy|netflix|\bmovie|\bfilm\b|"
                r"tweets?\b|\bpost \d|youtube|tiktok|spotify|KXRT"),
    ("politics", r"election|president(?:ial)?\b|parliament|senate|\bcongress|governor|\bmayor|prime minister|"
                 r"\bvote\b|\bseats\b|\bpoll(?:s|ing)?\b|referendum|impeach|cabinet|\btrump\b|\bbiden\b|KXPRES|KXSENATE"),
    ("sports", r"\bnba\b|\bnfl\b|\bmlb\b|\bnhl\b|\bwnba\b|\bmls\b|pro baseball|pro basketball|pro football|"
               r"\bseries winner|\bnext team\b|\bchampionship|\bplayoffs?\b|\bleague\b|\bcup\b|grand prix|\bopen\b|"
               r"\bmatch\b|\bvs\.? |\bend in a draw|\bwin on \d{4}-|\bwins \||qualifying|KXNEXTTEAM|KXMLB|KXNBA|KXNFL"),
    ("world", r"ceasefire|\bwar\b|invasion|missile|sanction|pipeline|\boil\b|\bopec|nato|\bun\b security|treaty|"
              r"\biran\b|\bisrael|\bukraine|\brussia|\bgaza|\bsaudi"),
    ("tech", r"\bai\b|artificial intelligence|openai|\bgpt|anthropic|\bgoogle|\bapple\b|\bnvidia|\bspacex|launch|"
             r"\bchip|model\b"),
]
CATEGORIES = tuple(name for name, _ in CATEGORY_RULES) + ("other",)
_CATEGORY_RX = [(name, re.compile(rx, re.I)) for name, rx in CATEGORY_RULES]


def category(m: dict) -> str:
    """A market's category, from its question and event id. Used to group results and lessons, never to bet."""
    text = f"{(m.get('question') or '').strip()} | {m.get('event') or ''}"
    for name, rx in _CATEGORY_RX:
        if rx.search(text):
            return name
    return "other"


# ---------------- self-calibration ----------------

def _logit(p: float) -> float:
    p = min(0.99, max(0.01, p))
    return math.log(p / (1 - p))


def _sigmoid(x: float) -> float:
    return 1 / (1 + math.exp(-x)) if x >= 0 else math.exp(x) / (1 + math.exp(x))


def fit_calibration(pairs: list[tuple[float, float]], prior: float) -> dict:
    """Fit p' = sigmoid(a * logit(p) + b) to (forecast, outcome) pairs.

    `prior` pulls the fit toward a = 1, b = 0 ("Jev is already calibrated"), so a handful of results
    can't swing it. a < 1 means Jev is overconfident (the map pulls answers toward 50%); a > 1, too timid;
    b shifts everything toward YES (b > 0) or NO. Newton's method on the penalized log-likelihood.
    """
    a, b = 1.0, 0.0
    zs = [(_logit(p), y) for p, y in pairs]
    for _ in range(50):
        ga, gb = prior * (a - 1), prior * b
        haa = hbb = prior
        hab = 0.0
        for z, y in zs:
            q = _sigmoid(a * z + b)
            w = q * (1 - q)
            ga += (q - y) * z
            gb += q - y
            haa += w * z * z
            hab += w * z
            hbb += w
        det = haa * hbb - hab * hab
        if det <= 0:
            break
        da, db = (hbb * ga - hab * gb) / det, (haa * gb - hab * ga) / det
        a, b = a - da, b - db
        if abs(da) + abs(db) < 1e-9:
            break
    return {"a": round(a, 4), "b": round(b, 4), "n": len(pairs)}


def calibration_map(reviews: list[dict], lc: dict) -> dict:
    """The current map, learned from every resolved market Jev judged with research.

    Active only once `calibration_min_resolved` markets have resolved; until then the calibrated
    strategy waits and says how far along it is. Reviews exist only for markets that already
    resolved, so the map never learns from an outcome that wasn't known at the time.
    """
    pairs = [(float(r["probs"]["jev_research"]), 1.0 if r["outcome"] == "yes" else 0.0)
             for r in reviews if (r.get("probs") or {}).get("jev_research") is not None]
    need = lc["calibration_min_resolved"]
    if len(pairs) < need:
        return {"active": False, "n": len(pairs), "need": need}
    return dict(fit_calibration(pairs, lc["calibration_prior"]), active=True, need=need)


def apply_map(cmap: dict, p: float) -> float:
    return round(_sigmoid(cmap["a"] * _logit(p) + cmap["b"]), 4)


# ---------------- the gate ledger ----------------

GATE_WORDS = [("info", "needs recent info"), ("rules", "rules_clear"), ("framing", "disagree"),
              ("room", "no room"), ("holding", "already holding")]
GROUP_LABELS = {"bet": "Bets placed", "info": "Stopped only by the info gate",
                "rules": "Stopped only by the rules gate", "framing": "Stopped only by the YES/NO check",
                "several": "Stopped by more than one gate", "room": "No room left (exposure cap or cash)",
                "holding": "Already holding it"}


def _blocked_by(d: dict) -> str:
    if d.get("bet"):
        return "bet"
    hits = [name for name, word in GATE_WORDS if any(word in r for r in d.get("reasons") or [])]
    return hits[0] if len(hits) == 1 else "several"


def gate_ledger(policy: dict, judgments: list[dict], resolved: dict, strategy_policies: dict) -> dict:
    """What each gate saved or cost, per strategy, on markets that have resolved.

    For each resolved market, take the first judgment where the strategy saw an edge at least its
    min_edge (the moment it would have bet), and score a flat $100 on that side at that cost. Group
    by what happened: bet, or which gate stopped it. A gate that mostly stops winners is too strict;
    one that stops losers is earning its keep. Small samples are noise; the page says how many.
    """
    firsts: dict[tuple, tuple] = {}
    for j in judgments:
        if j.get("question_set") != QUESTION_SET_VERSION or j["key"] not in resolved:
            continue
        for name, d in (j.get("decisions") or {}).items():
            sp = strategy_policies.get(name)
            if sp is None or "edge" not in d or d["edge"] < sp["gates"]["min_edge"]:
                continue
            firsts.setdefault((name, j["key"]), (j, d))
    out = {}
    for (name, k), (j, d) in firsts.items():
        won = resolved[k] == d["side"]
        pnl = 100 * ((1 / d["cost"] if won else 0) - 1)
        g = out.setdefault(name, {}).setdefault(_blocked_by(d), {"n": 0, "wins": 0, "pnl": 0.0})
        g["n"] += 1
        g["wins"] += int(won)
        g["pnl"] += pnl
    return {name: [{"group": grp, "label": GROUP_LABELS[grp], "n": g["n"], "wins": g["wins"],
                    "pnl_per_100": round(g["pnl"] / g["n"], 2), "total_per_100": round(g["pnl"], 2)}
                   for grp, g in sorted(groups.items(), key=lambda x: list(GROUP_LABELS).index(x[0]))]
            for name, groups in out.items()}


# ---------------- where we beat the market ----------------

def category_scores(judgments: list[dict], resolved: dict, prob) -> list[dict]:
    """Brier score per category for each forecaster, on the latest judgment of each resolved market.
    `prob(j, source)` is engine._prob (passed in to keep this module free of engine imports)."""
    latest = {}
    for j in judgments:
        if j.get("question_set") == QUESTION_SET_VERSION and j["key"] in resolved:
            latest[j["key"]] = j
    by_cat: dict[str, dict] = {}
    for k, j in latest.items():
        y = 1.0 if resolved[k] == "yes" else 0.0
        c = by_cat.setdefault(j["market"].get("category") or category(j["market"]), {})
        for src in ("jev_research", "jev_plain", "claude_direct", "market"):
            p = prob(j, src)
            if p is not None:
                c.setdefault(src, []).append((p - y) ** 2)
    rows = []
    for cat, srcs in by_cat.items():
        n = max(len(v) for v in srcs.values())
        rows.append({"category": cat, "n": n,
                     **{src: round(sum(v) / len(v), 4) for src, v in srcs.items()},
                     **{f"n_{src}": len(v) for src, v in srcs.items()}})
    return sorted(rows, key=lambda r: -r["n"])


# ---------------- the research playbook (kept by coach.py) ----------------

def rule_problem(text: str) -> str | None:
    """Why a playbook rule can't be used, or None: the same screen as research facts, plus a length cap."""
    if not 20 <= len(text) <= 280:
        return "shorter than 20 or longer than 280 characters"
    return news.leak_reason(text, [])


def lessons_for(playbook: dict, cat: str) -> list[dict]:
    """The playbook rules a research call on this category should follow: its own and the general ones.
    Re-screened here, so a hand edit to playbook.json can't slip odds or market talk into research."""
    return [r for r in playbook.get("rules", []) if r.get("category") in ("general", cat)
            and rule_problem(str(r.get("rule") or "")) is None]


# ---------------- challengers ----------------

SIGNALS = ("jev_research", "jev_plain", "claude_direct", "jev_calibrated")


def challenger_problem(cfg: dict, policy: dict) -> str | None:
    """Why a proposed challenger strategy can't run, or None. Checked when it's proposed and every time
    it's loaded, so a hand edit can't slip past. A challenger may pick its probability source and move
    gates within learning.challenger_bounds; it can never touch sizing, fees, caps or the price screen."""
    lc = policy["learning"]
    allowed = {"label", "probability", "gates", "gate_overrides", "_why"}
    extra = sorted(set(cfg) - allowed)
    if extra:
        return f"not allowed to set {', '.join(extra)}"
    if not str(cfg.get("label") or "").strip():
        return "no label"
    if cfg.get("probability") not in SIGNALS or cfg.get("gates") not in ("jev_research", "jev_plain"):
        return "unknown probability or gate source"
    for gate, v in (cfg.get("gate_overrides") or {}).items():
        lo_hi = lc["challenger_bounds"].get(gate)
        if lo_hi is None:
            return f"gate {gate} can't be changed by a challenger"
        if not isinstance(v, (int, float)) or not lo_hi[0] <= v <= lo_hi[1]:
            return f"{gate} {v} is outside the allowed range {lo_hi[0]}-{lo_hi[1]}"
    return None

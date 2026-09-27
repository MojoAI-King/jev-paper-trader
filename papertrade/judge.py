"""The questions Jev answers about each market.

Jev never sees the market price: we want its independent view, then code compares.
Bump QUESTION_SET_VERSION whenever wording or state shape changes (old calibration stops applying).

v2 (2026-09-27): state may carry `recent_facts` (screened research); added `p_no` (the same
question framed the other way, a consistency check) and `already_decided`. The three v1 questions
keep their exact wording, so the with-research and no-research arms ask identical questions and
differ only in state.
"""
from __future__ import annotations

from datetime import datetime, timezone

QUESTION_SET_VERSION = "papertrade-v2"


def build_state(market: dict, today: str | None = None, recent_facts: list[dict] | None = None) -> dict:
    state = {
        "today": today or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "market": {
            "question": market["question"],
            "resolution_rules": market["rules"],
            "closes": market["close_time"],
        },
    }
    if recent_facts is not None:
        # Exactly the screened facts: kind, date, source, fact. Never urls, never prices.
        state["recent_facts"] = [{k: f[k] for k in ("kind", "date", "source", "fact")} for f in recent_facts]
    return state


QUESTIONS = {
    "p_yes": {
        "type": "noul",
        "instructions": "Will `market` resolve YES under its `market.resolution_rules` by the time it closes?",
        "criteria": {
            "true": "The event described happens in the way the rules require before the market closes",
            "false": "It does not happen, or does not meet the rules' requirements, before the market closes",
        },
    },
    "p_no": {
        "type": "noul",
        "instructions": "Will `market` resolve NO under its `market.resolution_rules` when it closes?",
        "criteria": {
            "true": "The event described does not happen in the way the rules require before the market closes",
            "false": "It happens in the way the rules require before the market closes",
        },
    },
    "rules_clear": {
        "type": "noul",
        "instructions": "Are `market.resolution_rules` clear and objective enough that a neutral person "
                        "would know exactly what outcome counts as YES?",
        "criteria": {
            "true": "A specific, checkable condition and source decide the outcome",
            "false": "The outcome depends on interpretation, vague wording, or unclear sources",
        },
    },
    "info_sufficient": {
        "type": "noul",
        "instructions": "Can the outcome of `market` be estimated well from `state` and general knowledge alone, "
                        "without news or data from the weeks before `today` that is not in `state`?",
        "criteria": {
            "true": "Base rates, schedules, or stable facts largely determine the outcome",
            "false": "A good estimate depends on recent news, polls, prices, injuries, or other current information",
        },
    },
    "already_decided": {
        "type": "noul",
        "instructions": "Given `state`, is the outcome of `market` effectively already decided as of `today`: "
                        "the deciding event has happened, or can no longer happen before the market closes?",
        "criteria": {
            "true": "The information shows the outcome is settled in practice even if not yet officially resolved",
            "false": "The outcome still depends on things that have not happened yet",
        },
    },
}

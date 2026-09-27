"""The questions Jev answers about each market.

Jev never sees the market price: we want its independent view, then code compares.
Bump QUESTION_SET_VERSION whenever wording changes (old calibration stops applying).
"""
from __future__ import annotations

from datetime import datetime, timezone

QUESTION_SET_VERSION = "papertrade-v1"


def build_state(market: dict, today: str | None = None) -> dict:
    return {
        "today": today or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "market": {
            "question": market["question"],
            "resolution_rules": market["rules"],
            "closes": market["close_time"],
        },
    }


QUESTIONS = {
    "p_yes": {
        "type": "noul",
        "instructions": "Will `market` resolve YES under its `market.resolution_rules` by the time it closes?",
        "criteria": {
            "true": "The event described happens in the way the rules require before the market closes",
            "false": "It does not happen, or does not meet the rules' requirements, before the market closes",
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
}

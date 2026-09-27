# Bold strategy (info bar 0.2) and no weekly research pause

Kind: Living. Decision entry.

- **ID:** 2026-09-27-bold-strategy-info-bar-0-2-and-no-weekly-5851
- **Status:** accepted
- **Date:** 2026-09-27

## Decision

1. A fourth strategy, **bold** ("Jev + research, bold"), trades its own fake $100,000. It is main in
   every way (Jev with research for the probability and the gates, same sizing, fees and caps) except
   that its information bar is 0.2 instead of 0.5. It is set in `policy.json` as
   `"gate_overrides": {"min_info_sufficient": 0.2}`; `engine.strategy_policy` applies it, and it
   refuses an override that names a gate that doesn't exist.
2. Main's gates are unchanged, and a test (`StrategyGateTests.test_main_keeps_its_pre_registered_gates`)
   now fails if main's gates change or main gets an override.
3. A newly added strategy gets a first look at every market in the next cycle: a market is due again
   when a current strategy never decided on it. Jev re-judges (pennies); research under 24 hours old
   is reused, so no new Claude research is spent on the catch-up.
4. Research no longer pauses at 85% of the Claude plan's weekly window (`max_week_used` is 1.0).
   It stops when the plan itself says the week is full, and still pauses at 70% of the 5-hour window.

## Why

Joey wants to see the system trade. In the first three cycles (81 judgments) nothing cleared main's
gates: with research, Jev's information score ranged from 0.14 to 0.43, always under 0.5. Replaying
those judgments with an information bar of 0.2 clears 8 distinct markets, including the Saudi pipeline
(edge +0.30) and Bolsonaro second place (edge +0.13). Running this as a separate strategy shows action
and also tests whether the information gate is too cautious, without changing main's
pre-registered rules. Asked about exactly this change, Joey replied on 2026-09-27 "I just want to
make sure that it's actually trading now and we can actually see it in action", taken as a yes. The weekly pause was lifted on Joey's instruction the same day ("Don't worry about pausing
research at 85%").

## Alternatives rejected

- Lowering main's information gate: it would move the pre-registered goalposts and blur the
  before/after comparison.
- A bar of 0.3: it would have cleared only one market in the replay, too few to show action.
- Letting the new strategy decide from old judgments without re-judging: the prices would be stale.

## Risk

- Bold bets on markets where Jev says it lacks information, so it will likely lose more often than
  main. That is the experiment; the page labels it as its own fake bankroll.
- With the weekly pause lifted, the hourly job can use the rest of Joey's weekly Claude allowance.
  If the week fills, research and Joey's own Claude use both stop until the weekly reset
  (Monday 3 AM ET at the time of writing).

## Reversibility

Remove `bold` from `policy.json` strategies (its ledger stays in `papertrade_data/portfolios/bold.json`)
and set `max_week_used` back to 0.85. Both are one-line edits.

## Evidence

- Replay of `papertrade_data/judgments.jsonl` (question set papertrade-v2, 81 judgments, 22 with
  research): info at least 0.5 clears 0 markets, at least 0.3 clears 1, at least 0.2 clears 8.
- 57 offline tests pass. The catch-up test fails when the catch-up is removed from `engine.scan`.

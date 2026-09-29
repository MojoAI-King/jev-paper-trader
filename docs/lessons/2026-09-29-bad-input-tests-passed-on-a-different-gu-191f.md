# Bad-input tests passed on a different guard than the one named

Kind: Living. Lesson entry.

- **ID:** 2026-09-29-bad-input-tests-passed-on-a-different-gu-191f
- **Status:** accepted
- **Date:** 2026-09-29

## What broke

A review's mutation run (2026-09-28) found that several guards in `learn.rules_problem` and around it
could be deleted with all 99 tests still green: the true/false refusal, the finite-number check, the
`learn.RULES` whitelist, the `None` filter in `engine.strategy_rules`, the combined starting-plus-tuned
check, `_retire`'s "must be running" check and the `since_change` filter. `"max_stake_pct": true` would
have passed and meant bets of 100% of the bankroll.

## The mechanism

Each "bad input" in the test was refused by some other check first. `{"min_edge": True}`: `True == 1`,
outside min_edge's 0-0.5 range, so the range check refused it whether or not the bool check existed.
Every bad key ("fees", "slippage") had no entry in `learning.bounds`, so "no allowed range" refused it
before the whitelist mattered. `since_change` was asserted only with zero bets, where the filtered and
unfiltered counts agree. The harness's own control, a planted failing test in `tests/zz_control.py`,
never ran, because unittest only collects `test*.py`.

## The fix

`TuningTests` gained inputs that only the named guard can refuse: `True` for rules whose range includes
1, a policy copy whose bounds are infinite (so only `isfinite` refuses inf/NaN) or that gives `slippage`
a range (so only the whitelist refuses it), bets of two rules versions for `since_change`, a challenger
with a null rule, a contradictory min/max ask. Commit 44b97f1.

## The rule

For each guard, use a bad input that only that guard can refuse, and prove it by removing the guard
alone and watching the named test go red. The harness's planted failure must be collected by the runner
(`tests/test_*.py`) and seen red first.

## What now enforces it

The 26 guards were each removed alone in a scratch copy and each turned at least one named test red
(script kept only in the session scratchpad: nothing in the repo reruns it yet). Tests:
`test_true_false_huge_and_infinite_values_are_refused_by_their_own_checks`,
`test_only_the_rules_the_loop_owns_pass_and_every_bad_spelling_is_refused` (with its passing control set),
and the others named in decision 2026-09-28-daily-review-tunes-any-strategy-s-rules-5495.

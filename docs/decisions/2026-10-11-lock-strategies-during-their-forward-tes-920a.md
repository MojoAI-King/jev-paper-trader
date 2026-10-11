# Lock strategies during their forward tests

Kind: Living. Decision entry.

- **ID:** 2026-10-11-lock-strategies-during-their-forward-tes-920a
- **Status:** accepted
- **Date:** 2026-10-11

## Decision

Joey, 2026-10-11 ("yes unless you disagree"; the assistant agreed): `learning.locked_strategies` (`sharp`,
`mention_no`) keeps the daily review from changing those strategies' rules while their pre-registered forward tests run.

- `coach.tune_problem` refuses any change to a locked strategy, whoever proposes it through the loop.
- `engine.strategies` ignores a tuned entry for a locked strategy on load, so it trades on its starting rules only.
- The review's prompt and its numbers mark locked strategies ("locked": true), so it doesn't propose changes to them.
- Unlike the frozen yardstick (`original`), locked strategies keep skill-based sizing: their stakes still grow only
  when their measured edge shows.

## Why

Each forward test asks one question with a keep-or-kill rule written in advance (`docs/EXPERIMENTS.md`). If the loop
moved `mention_no`'s edge bar or price band mid-test, the result would mix two rules and answer neither.

## Alternatives rejected

- **Add them to `frozen_strategies`:** that also switches them to the old sizing and treats them as the yardstick.
- **Turn auto-tuning off for everything:** the loop still has nothing else to tune today, but the lock is narrower.

## Risk

A genuinely needed fix to a locked strategy now needs a person (edit `policy.json` or the code), which is the point.

## Reversibility

Remove a name from `learning.locked_strategies` in `policy.json` to unlock it.

## Evidence

- `test_strategies_in_a_forward_test_are_locked_against_the_review`; 155 offline tests pass.

# Daily review tunes any strategy's rules; code ideas wait for Joey

Kind: Living. Decision entry.

- **ID:** 2026-09-28-daily-review-tunes-any-strategy-s-rules-5495
- **Status:** accepted
- **Date:** 2026-09-28

## Decision

Joey, 2026-09-28, choosing "free rein over the rules, not the code": the learning loop may change **any
strategy's betting rules by itself**, main included, and code changes are proposed to him to approve or
deny.

1. **The review runs daily** (`learning.retro_every_days` 1, was 7) and files up to
   `learning.max_proposals_per_retro` (4) proposals.
2. **Rule changes apply by themselves** (`learning.auto_tune`). A `tune` proposal may set, for any strategy
   but a frozen one: the four gates, `kelly_fraction`, `max_stake_pct` (the most one bet may be),
   `max_total_exposure_pct` (the open-bet limit), `min_ask`/`max_ask` and `skip_categories`, each within
   `learning.bounds`, which span each rule's whole sensible range (min_edge stays at 0 or more; the sizing
   rules keep a small floor, 0.05 / 0.005 / 0.05, so a change can't quietly stop a strategy). A strategy's
   rules change at most once every `learning.min_days_between_changes` (2) days. `null` returns a rule to that
   strategy's starting value. Checked in code (`coach.tune`, `learn.rules_problem`) and again every time the
   rules load (`engine.strategies`).
3. **The record:** the current rules go to `papertrade_data/rules.json` (only what differs from the start),
   every change to `rules_history.jsonl` (from what to what, why, `judge_by`, `min_resolved`), every bet carries
   `rules_version`, and the page's live feed shows each change (TUNE) and a tuned strategy's badge reads
   "tuned vN".
4. **A yardstick:** new strategy `original`, main's starting rules, frozen (`learning.frozen_strategies`), so
   the tuning is judged against leaving the rules alone.
5. **Challengers** may now set sizing and filters too (same checks), and the review may retire a running
   challenger; a retired challenger's open bets still settle (`engine.all_books`; before this, a retired
   challenger's open bets would never have settled) and its record stays on the page marked Retired, so
   the loop can't hide a loser. A challenger can't take another strategy's name.
6. **Code ideas wait for Joey:** a `code` (or `research`) proposal changes nothing; the feed shows it (IDEA),
   `learn` lists it, and `approve`/`reject` decide it. The same applies to code changes Claude thinks of in a
   session: ask Joey first.
7. Out of the loop's reach, unchanged: code, fees and slippage, the price screen, research budgets, market data,
   settlement and scoring, a strategy's probability source, and `original`.

Supersedes, in part: 2026-09-27-learning-loop-playbook-coach-win-reviews-ac5d (main never changes on its own;
weekly retrospective) and 2026-09-27-challengers-start-by-themselves-opposing-4dc1 (`challenger_bounds`, gates
only). `test_main_keeps_its_pre_registered_gates` is inverted into
`test_main_starts_from_its_pre_registered_gates_and_only_original_stays_on_them`.

## Why

Joey, 2026-09-28: "free rein ... to change any strategy rules that you find are being productive to make
money", "whatever bet size", "the limit is open on bets", "it's just a little safe fun watching ... a lot of
experimentation". He first asked for full autonomy including the trader rewriting and shipping its own code;
Claude Code's safety check refused to build an unattended job that edits and deploys this repo's code, and
Joey chose this option instead, adding: "if you are interested in making code changes, you just let me know
and I can either approve or deny."

The old rule (only challengers may try a change) protected the headline number from noise-chasing. That
risk stays real with 18 resolved markets; the record (rules versions, the history, results since each
change) and the frozen `original` are what let anyone see whether the tuning helps.

## Alternatives rejected

- **An unattended job that edits and ships code.** Joey's first ask; refused by Claude Code's safety check as
  an unsafe autonomous agent (it would rewrite and run its own code with the Jev key and Claude sign-in on the
  machine). Not built, and CLAUDE.md now says not to build one.
- **Code changes as GitHub pull requests Joey merges.** Offered as option 2; Joey chose option 1.
- **Letting the loop change fees.** Joey listed "whatever fees"; fees are what Kalshi and Polymarket charge,
  so lowering them would make the profits fake. Kept out, and said so to Joey.
- **No yardstick.** Without `original`, main's result after tuning can't be told apart from what it would
  have made anyway.

## Risk

- Tuning on small samples chases noise; main's P&L now mixes rule versions. Mitigated by the per-version
  record and `original`, not prevented.
- With `max_stake_pct` and `max_total_exposure_pct` up to 1.0 and `kelly_fraction` up to 1.0, a strategy can
  bet most of its fake bankroll quickly and go broke. Joey accepted this ("whatever bet size").
- The review is one Claude call a day on Joey's plan, up from one a week.
- `original` starts on 2026-09-28 with a fresh $100k, so main vs `original` is compared on bets from then.
- PLAN.md's return criteria now judge main as tuned; the Brier criteria are unaffected (tuning changes which
  bets are placed, not the forecasts).

## Reversibility

Set `learning.auto_tune` false: changes then wait for `approve`. Delete a strategy's entry from
`papertrade_data/rules.json` to put it back on its starting rules (the history stays). Set
`learning.retro_every_days` back to 7 for a weekly review. Every bet placed under a tuned version stays in
the ledgers with its `rules_version`.

## Evidence

A review workflow (4 reviewers, each checked by a skeptic) confirmed 20 findings on the first version,
4 of them major: a retired challenger's losses vanished from the page; the gate ledger re-scored old
decisions against today's tuned edge bar; a hand undo reused version numbers (twice). All fixed with a test
each. A second round over the fixes confirmed 8 more (1 major: the main-vs-`original` comparison counted
`original`'s bets on markets main already held and couldn't bet again), all fixed with tests. A third
round found no blocker or major, and 3 minors (approve/reject on a retired or same-named challenger, and
queue order when a slot opens without a retire), fixed with tests. Mutation check: each of 26 guards
removed alone turns at least one test red (a planted failing test proved the harness reports red).

117 offline tests pass (was 88), including `TuningTests`: every bad spelling of a rule refused, with a passing
control set (`test_only_the_rules_the_loop_owns_pass_and_every_bad_spelling_is_refused`); main tuned by the
review and betting bigger while `original` doesn't (`test_the_review_tunes_main_by_itself_and_the_new_rules_bet`);
frozen, unknown, too-soon and null-reset (`test_too_soon_frozen_unknown_and_out_of_range_changes_are_refused`);
hand edits re-checked on load; code ideas wait and show on the page; a retired challenger's bet settles; the
review prompt names every limit; each bet records its rules version through the real scan.

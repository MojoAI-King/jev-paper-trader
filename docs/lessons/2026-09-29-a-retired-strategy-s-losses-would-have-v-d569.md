# A retired strategy's losses would have vanished from the page

Kind: Living. Lesson entry.

- **ID:** 2026-09-29-a-retired-strategy-s-losses-would-have-v-d569
- **Status:** accepted
- **Date:** 2026-09-29

## What broke

Caught in review before it shipped (2026-09-28/29): once the daily review could retire a challenger by
itself, a retired loser's whole record (its row, its settled losses, its bets in the feed, its line on
the chart, its share of the totals) would have disappeared from the public page. A second review found
the same gap through Joey's `reject <id>` on a running challenger, and through any ledger no strategy
owns any more.

## The mechanism

`dashboard.current_summary` built the page from `engine.load_books(policy)`, which loads only
`engine.strategies(policy)`: policy.json's strategies plus challengers with status `running`. A retired
challenger's portfolio file still existed and still settled (`engine.all_books` in `settle`), but nothing
that builds the page read it. `coach.set_status` sent `rejected` through a generic branch that overwrote
the status without the `retired` stamp, so even `strategies(retired=True)` missed it.

## The fix

`engine.strategies(policy, retired=True)` adds retired challengers (marked `retired`);
`engine.all_books` loads every ledger; `dashboard.current_summary` uses `all_books`, and
`dashboard.strategy_rows` gives every ledger a row: badge "Retired" (grey slot 0), or "Stopped" for a
ledger no strategy owns. `coach.set_status` routes reject/retire of a running challenger through
`coach._retire`, and refuses to change a retired one. Commit 44b97f1.

## The rule

Every view of results is built from every ledger that ever held money, never from the set that is
active now. Any path that removes a strategy (the loop's retire, Joey's reject or retire, a policy edit)
must leave its record on the page.

## What now enforces it

`test_a_retired_challenger_keeps_its_record_on_the_page`, `test_every_ledger_has_a_row_and_every_running_challenger_a_colour`,
`test_joey_s_approve_and_reject_keep_challengers_honest`,
`test_a_retired_challenger_stays_retired_and_names_stay_unique_by_hand_too`; each fails with its guard
removed (mutation run, 2026-09-29).

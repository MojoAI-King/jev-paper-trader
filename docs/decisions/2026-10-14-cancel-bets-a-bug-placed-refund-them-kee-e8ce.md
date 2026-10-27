# Cancel bets a bug placed, refund them, keep them on record

Kind: Living. Decision entry.

- **ID:** 2026-10-14-cancel-bets-a-bug-placed-refund-them-kee-e8ce
- **Status:** accepted
- **Date:** 2026-10-14

## Decision

A bet that a bug placed, rather than the strategy's own rule, can be canceled by naming it in `policy.json`
`cancelled_bets` (`{strategy: {market key: why}}`). The trading cycle's settle step (`engine.cancel_bets`) refunds it
(its cost back, any payout taken back) and moves it from the ledger's open or closed list to a `cancelled` list with the
reason and the refund. It then counts in no P&L, win/loss or settled tally, on the page or in the strategy's evaluation.
The first one: sharp's YES on KXNFLTD-26OCT11LVNE-LVMWASHINGTON4-1 (−$249.55), a player touchdown market priced with
the team's moneyline by a matcher bug fixed 2026-10-11. Sharp's page blurb says so.

## Why

Joey, 2026-10-15: "Shouldn't you remove the bug bet then?" The bet came from a matching bug, not the sharp rule, so
its result says nothing about the strategy, and it was the whole of the page's loss. It was already left out of
sharp's pre-registered evaluation (docs/EXPERIMENTS.md, 2026-10-11, before it settled).

## Alternatives rejected

- **Delete it from the ledger by hand:** rewrites history, and GitHub Actions is the only writer of `papertrade_data/`.
- **Leave it:** the page total would keep showing a loss no strategy made.

## Risk

Canceling could be used to hide real losses. Guard: only bets a named bug placed, each with its reason in
`policy.json`, decided by a session with the bug's fix on record; the bet stays visible in the ledger.

## Reversibility

Remove the entry from `cancelled_bets` and move the bet back from `cancelled` to `closed`, taking its refund back out
of cash.

## Evidence

Offline tests 163 pass (`test_a_bet_placed_by_a_bug_is_refunded_and_kept_on_record_out_of_every_tally`,
`test_every_live_canceled_bet_names_a_reason`); an in-memory dry run on the live ledger refunded $249.55, leaving
sharp at $100,000 with 0 settled and 1 canceled.

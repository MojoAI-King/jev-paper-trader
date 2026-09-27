# Challengers start by themselves; opposing bets and thin markets stay allowed

Kind: Living. Decision entry.

- **ID:** 2026-09-27-challengers-start-by-themselves-opposing-4dc1
- **Status:** accepted
- **Date:** 2026-09-27

## Decision

Joey, 2026-09-27: "You can do contradicting bets if you think you can get an arbitrage. For skipping thin
markets, it's up to you... if you think there's a good bet there that it can make money, take it. For
challengers, start on their own."

1. **Challengers start by themselves.** `learning.auto_start_challengers` is true. A valid challenger from
   the weekly retrospective starts on its own fake $100,000, within `learning.challenger_bounds`, at most
   `learning.max_running_challengers` (2) at a time; an extra one waits for a free slot. The bounds are
   unchanged, and a challenger can still never change sizing, fees, exposure caps or the price screen
   (`learn.challenger_problem`, checked when proposed and on every load). Main never changes on its own.
2. **Opposing bets within one event stay allowed.** No rule blocks them. The case that raised it was not
   a contradiction: Bold bought YES on "Bitcoin above $86,000 on Sep 28" (Jev 24% vs 15¢) and NO on
   "above $84,000" (Jev 58% vs 73¢). Jev's numbers were ordered correctly (above $86k no likelier than
   above $84k), and each bet had an edge at its price; together they bet against Bitcoin landing between
   $84k and $86k. What would be wrong is Jev's probabilities within one event not fitting together; making
   them fit is BACKLOG B3, an improvement to build, not a block.
3. **Thin markets stay allowed (Claude's call, delegated by Joey).** A wide bid-ask spread is already
   counted: every edge is measured against the price we would pay (the ask plus 1¢ and fees), not the mid.
   What a thin market does get wrong is fill size: the simulation assumes a $2,000 order fills at the
   listed ask however little is offered there. Sizing fills to the market's displayed depth is BACKLOG B15.

## Why

Joey's instructions above. Starting challengers automatically is safe because they run on separate fake
bankrolls against future markets and can only move gates within fixed bounds; the headline strategy and
its pre-registered rules are untouched.

## Alternatives rejected

- A rule forbidding a strategy from holding both sides within one event: it would have blocked a
  consistent, positive-edge pair of bets.
- A bid-ask spread filter: it would drop bets whose edge already covers the spread.

## Risk

- Up to two challengers can run without Joey looking; each adds a fake bankroll to the page.
- Until B15, fills in thin markets are optimistic about size.

## Reversibility

Set `learning.auto_start_challengers` to false; `python3 -m papertrade retire <id>` stops a running
challenger and keeps its ledger.

## Evidence

`RetroTests.test_challengers_start_by_themselves_but_only_within_bounds_and_slots` (a valid challenger
starts, an out-of-bounds one is marked invalid, a third waits for a free slot) and
`test_with_auto_start_off_nothing_starts_until_approved` (the switch still works when off). 72 tests pass.

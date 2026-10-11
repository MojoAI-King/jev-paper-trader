# Scoring real taker trades credited us with other traders' information

Kind: Living. Lesson entry.

- **ID:** 2026-10-11-scoring-real-taker-trades-credited-us-wi-3639
- **Status:** accepted
- **Date:** 2026-10-11

## What broke

The live mention strategy was built on "+15.8% after fees" (later "+35.9% when our purchase was the market's first
trade"), measured by `docs/research/scripts/mention_timing.py` at the prices of real NO taker purchases. Tested at
quoted prices, the way the live strategy actually buys, the same rule measured +0.5% [−10.2, +11.3] (779 buys, 112
events). The first-trade scan's Economics lead (+37%) failed the same way: a strategy trading first made −2.7%.

## The mechanism

A taker trade happens when someone decides to trade, often because they know something (here: which way the day's
gas price moved, or how a speech was going). Scoring "the first NO taker purchase" therefore selects the moments and
markets where an informed trader chose NO. In the same mention markets at the same listing price, buying NO made
+46.6% where the first trade turned out to be a NO buy and −33.0% where it was a YES buy. A strategy that buys at
posted prices on its own schedule gets both groups, so it gets roughly the average: break-even.

## The fix

- `docs/research/CHECKS.md` ("First trades and the trade-print trap") records the quote-based results; the
  `mention_no` registry row and the page blurb now say the expectation is about break-even, and its pre-registered
  forward test (at quoted asks, its own bets) decides.
- Quote-based tests use candle bid and ask (`/series/{s}/markets/{t}/candlesticks`, minute or hourly) at times the
  strategy's own rule fixes.

## The rule

Score a backtest at the price the strategy itself could have paid at a time its own rule chose: the quoted ask at a
clock time or a rule-triggered moment that uses only past information. Never at the price of a real trade whose
existence or timing is part of the selection, unless the strategy really would follow that trade after it printed
(and then at the quote after it, not the trade's own price).

## What now enforces it

Nothing in code. Every future research script must state which price it scores and why the strategy could have paid
it; a reviewer checks that before any strategy is built on the result.

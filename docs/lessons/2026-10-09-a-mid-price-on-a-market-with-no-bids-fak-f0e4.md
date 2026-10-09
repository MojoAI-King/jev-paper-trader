# A mid price on a market with no bids faked an edge

Kind: Living. Lesson entry.

- **ID:** 2026-10-09-a-mid-price-on-a-market-with-no-bids-fak-f0e4
- **Status:** accepted
- **Date:** 2026-10-09

## What broke

Measured 2026-10-09, Claude direct looked 0.094 ± 0.015 Brier better than the market on 98 pre-game sports
markets, which is implausible against sports pricing. It would have pointed the rebuild at the wrong target.

## The mechanism

All 98 were Polymarket markets, most of them tennis "Completed Match" markets: yes ask 0.97–1.00, no ask 0.91–0.92,
and no bids on either side, so the median spread (yes_ask + no_ask − 1) was 0.835. `market.mid` for these is about
0.53, a number nobody can trade at, and it was scored as the market's forecast. Claude said about 0.94, the outcome
was YES, and the market looked terrible. Across all first looks, 146 of 1,133 have spreads over 10¢.

## The fix

Analysis: score the market only where spread ≤ 10¢. Then Claude in sports is +0.011 ± 0.005 *worse* than the market
(205 markets), and every forecaster is worse overall (327 markets). Code: not yet; `engine.paired` and the Forecasters
panel still use the mid on every market (BACKLOG B25, waiting for Joey).

## The rule

Before scoring anything against a market price, drop markets without a real two-sided price and say how many were
dropped. When one subgroup shows a dramatic edge, print a handful of its rows before believing it.

## What now enforces it

Nothing yet. B25 would add the spread filter to `engine.paired` with a test that a wide-spread market is left out.

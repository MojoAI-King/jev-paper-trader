# Polymarket bets pay each market's real fee; forecasters scored only where the price is real

Kind: Living. Decision entry.

- **ID:** 2026-10-09-polymarket-bets-pay-each-market-s-real-f-5d58
- **Status:** accepted
- **Date:** 2026-10-09

## Decision

Joey, 2026-10-09: "yes" to B26 and B25, and "your choice, keep working on the fixes based on the feedback".

1. **Real Polymarket fees (B26).** Each Polymarket market now pays its own published taker fee, `rate × p × (1 − p)`
   per contract. The rate comes from the market's `feeSchedule` in Polymarket's API: `markets.normalize_polymarket`
   saves it as `fee_rate`, 0 when `feesEnabled` is false. `engine.fee_per_contract` charges it. A Polymarket market
   that doesn't publish a rate, including every market saved before this change, pays `fees.polymarket_default_rate`
   (0.05) rather than nothing. Kalshi is unchanged (0.07 × p × (1 − p)). Bets already placed keep the cost they
   were charged; nothing in the ledgers is rewritten.
2. **Scoring only where the price is real (B25).** The head-to-head scores (`engine.paired`, the page's Forecasters
   panel, the report's "Head to head" lines and the daily review's data) count a market only at looks where yes ask
   + no ask − 1 is 10¢ or less (`PAIRED_MAX_SPREAD`), and report how many markets were left out.
3. **No category skips for now.** Reports 06 and 07 suggested keeping AI forecasts off price-threshold and weather
   markets. The losses since the 30¢ floor come from sports (−13%, 58 bets) and other markets (−22%, 36 bets), not
   from those. Weather made +18% on 18 bets, which is noise. So no category was skipped (`docs/research/CHECKS.md`).

## Why

Joey's rule is that fees stay real. Research report 01 found, and Polymarket's own fee page confirmed (read
2026-10-09), that Polymarket charges takers by category (crypto 0.07; sports, economics, culture, weather, other 0.05;
politics, finance, tech, mentions 0.04; geopolitics 0) while the trader charged 0. That flattered every Polymarket
bet by 1 to 3.5 points at mid prices. Polymarket's API publishes each market's rate (seen live: `politics_fees` at
0.04, and a geopolitics market with fees off). Using it avoids guessing Polymarket's categories from our own text
matcher, which files oil and gold markets under "world".

On markets where nobody bids (for example tennis "Completed Match" markets, asks 97–99¢ and 91–92¢), the mid isn't a
forecast. Scoring the market by it made the market look worse than it is, and once made Claude look 0.094 better
than the market on 98 sports markets when it is slightly worse.

## Alternatives rejected

- **A fee table keyed by our own categories.** Our categories come from a text matcher, not from Polymarket; the
  market's published rate is exact.
- **Charging 0 when a market publishes nothing.** That repeats the old error; the default is the most common rate.
- **Recharging past bets.** That would rewrite the ledgers. The change applies from now on, and this record says
  so.
- **Kalshi's per-order rounding up to the cent.** Left out: on our order sizes (hundreds to thousands of
  contracts) it is under a cent per order.

## Risk

Fewer Polymarket bets clear the edge bar, because each costs 1–3.5 points more at mid prices. A rate that
Polymarket changes is picked up from the next fetch. A market with an exponent other than 1 in its `feeSchedule`
hasn't been seen; the docs give only the plain formula, so that case isn't handled.

## Reversibility

Set `fees.polymarket_default_rate` to 0 and stop reading `fee_rate` (`engine.fee_per_contract`), or set
`PAIRED_MAX_SPREAD` to 1.0 to score every market again.

## Evidence

`FeeTests` (each market's own rate, fee-free markets, the default for unpublished and old markets, the rate read
from `feeSchedule`, the fee deciding a bet) and the updated
`test_forecasters_are_scored_head_to_head_on_the_same_markets` (a no-bid market is left out and counted; a market's
latest real-priced look counts). Each new check fails if its fix is removed. 125 offline tests pass. On live data
the head-to-head covers 562 markets (101 left out): market 0.155, Claude direct 0.198, Jev + research 0.214, Jev
alone 0.247.

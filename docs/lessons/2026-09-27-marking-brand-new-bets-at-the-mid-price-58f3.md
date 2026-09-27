# Marking brand-new bets at the mid price made them read as losses

Kind: Living. Lesson entry.

- **ID:** 2026-09-27-marking-brand-new-bets-at-the-mid-price-58f3
- **Status:** accepted
- **Date:** 2026-09-27

## What broke

Joey saw Bold at −3% within an hour of its first bets and asked whether the losses were real. No bet
had settled.

## The mechanism

`dashboard.strategy_rows` and `race` value open bets at the market's last mid price
(`contracts × mid`, or `× (1 − mid)` for NO), while `engine.decide` fills at the ask plus 1¢ slippage
(plus Kalshi's fee). So every bet is worth less than it cost the moment it is placed. Measured on the
15 open bets at 14:43 ET: cost $31,997, worth $28,868 at the mid, −$3,129; of that, −$3,381 was paid
above the mid at entry, and price moves since were +$252. One thin tennis market alone was −$1,020:
NO bought at 50¢ while the mid put NO at 24.5¢, because nobody was bidding.

## The fix

The page shows settled money (final) and open money (valued at today's prices, not final) apart
(decision 2026-09-27-show-settled-and-unsettled-money-apart-p-f0c2). The valuation itself is unchanged:
the entry cost is real.

## The rule

Any display that marks positions to market must show realized and unrealized separately and say which
is final; a single combined number reads as a loss the moment a trade is placed.

## What now enforces it

Nothing automated; the page's strategy rows and equity header carry both numbers. A filter for markets
with a very wide bid-ask spread is proposed in BACKLOG B14, waiting for Joey.

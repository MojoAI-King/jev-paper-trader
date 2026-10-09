# Research brief 06: Pricing crypto, oil, gold and stock-index thresholds

Kind: Reference. One of 14 narrow research briefs for the trader's rebuild (BACKLOG B24), each run as its own
Claude Code session in a VS Code tab. To start it, type in a new tab:
`Run research brief 06: read docs/research/briefs/06-price-threshold-markets.md and follow it.`

Before you start, read `docs/research/README.md` (rules for sessions running side by side, evidence standards, the
report format) and the "What the data says" section of `docs/REBUILD_SCOPE.md`.

## Question

How should we compute the probability that a price touches, or closes above, a threshold by a given time (crypto, oil, gold, stock indices) from live prices and volatility, and how close are Kalshi and Polymarket prices to those numbers?

## What we already know

- These come up often: "Will Bitcoin reach $X by [date]", "BTC above $X at 5pm", WTI oil, gold, the S&P 500. Crypto is 147 of our 1,133 finished markets.
- In crypto our AI forecasts are worse than the market (Brier: Claude direct 0.186, market 0.146, on 61 markets).
- The WTI miss: 81–93% that oil would hit $95 in September, market price 7¢, and it didn't.

## Find out

- The math: touch (barrier) vs close-above probability under a lognormal model, the reflection-principle shortcut, drift, fat tails and jumps, and when a simple model is good enough.
- Volatility inputs: implied volatility (Deribit's DVOL and options for BTC and ETH, VIX for the S&P 500, OVX for oil, GVZ for gold) vs realized, and free ways to get each.
- Free price feeds and their limits (exchange APIs, FRED and others), and exactly which reference price each market settles on (for example the BTC index Kalshi uses, the oil contract and settlement time, a 5pm ET fix), with time zones and rounding.
- Evidence on how efficient these prediction markets are against options-implied probabilities, and any documented gaps or bots.

## Leave out

Weather (brief 07); economic releases (08).

## Deliverable

Write `docs/research/06-price-threshold-markets.md` in the report format from `docs/research/README.md`, and include
the formula with a worked example, the data sources, and a backtest plan.

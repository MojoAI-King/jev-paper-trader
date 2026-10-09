# Research brief 09: Sports prices against the sharp sportsbooks

Kind: Reference. One of 14 narrow research briefs for the trader's rebuild (BACKLOG B24), each run as its own
Claude Code session in a VS Code tab. To start it, type in a new tab:
`Run research brief 09: read docs/research/briefs/09-sports-vs-sharp-books.md and follow it.`

Before you start, read `docs/research/README.md` (rules for sessions running side by side, evidence standards, the
report format) and the "What the data says" section of `docs/REBUILD_SCOPE.md`.

## Question

Do Kalshi and Polymarket sports prices lag or differ from sharp sportsbook prices by enough to profit after fees, and exactly how would a small bot run that strategy?

## What we already know

- Sports are 606 of our 1,133 finished markets. On the 205 real-priced sports markets that Claude forecast, its own forecast was slightly worse than the market (Brier +0.011 ± 0.005). Always buying the favourite at the ask lost 1.6% ± 2.6% (606 markets).
- Many Polymarket sports markets are illiquid, for example tennis "Completed Match" markets with asks of 97¢ and 92¢ and no bids.

## Find out

- How prediction-market sports prices compare with sharp books (Pinnacle, Circa, exchanges such as Betfair): documented gaps by league and market type, and timing (opening vs closing, after news).
- Removing the bookmaker's margin (multiplicative, power and Shin methods) and which works best.
- Odds data: The Odds API (tiers, which bookmakers including sharp ones, limits, cost), free alternatives, and delays.
- Closing-line value as the measure of skill in sports betting, and how to compute it here.
- Fees on sports markets (Kalshi's curve), whether the gaps survive them, and which markets to avoid.

## Leave out

Markets still trading after games end (brief 03); fees in general (10).

## Deliverable

Write `docs/research/09-sports-vs-sharp-books.md` in the report format from `docs/research/README.md`, and include
a step-by-step strategy with entry rules, the data source and its cost, the expected edge with evidence, and a backtest plan.

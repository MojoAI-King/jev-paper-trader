# Research brief 12: Bet sizing when our probabilities are uncertain

Kind: Reference. One of 14 narrow research briefs for the trader's rebuild (BACKLOG B24), each run as its own
Claude Code session in a VS Code tab. To start it, type in a new tab:
`Run research brief 12: read docs/research/briefs/12-bet-sizing.md and follow it.`

Before you start, read `docs/research/README.md` (rules for sessions running side by side, evidence standards, the
report format) and the "What the data says" section of `docs/REBUILD_SCOPE.md`.

## Question

How should we size bets when our probability estimates are noisy and many bets are correlated, so the bankroll can grow without blowing up?

## What we already know

- Every strategy starts at quarter-Kelly, at most 2% of equity per bet and 50% of equity in open bets; the daily review can change all three within bounds (`policy.json`, `learning.bounds`).
- One wrong WTI oil call hit four strategies at once; one strategy held both sides of the same fight (BACKLOG B17); several thresholds on one price are really one bet.
- Our forecasts are overconfident (expected 99.8 wins, got 62), which is exactly when Kelly sizing over-bets.

## Find out

- Kelly under estimation error: fractional, Bayesian or shrunk Kelly, and how much to shrink given a forecaster's measured accuracy against the market.
- Correlated and simultaneous bets: per-event and per-underlying caps, portfolio approximations of Kelly, treating a ladder of thresholds as one position.
- Drawdown control: when to cut size or stop a strategy, and how to size a new strategy before its edge is proven.

## Leave out

Deciding which bets have an edge (briefs 04, 05); fills (11).

## Deliverable

Write `docs/research/12-bet-sizing.md` in the report format from `docs/research/README.md`, and include
sizing formulas and limits to put in code, with the reasoning behind each number.

# Research brief 04: What makes an AI forecaster more accurate

Kind: Reference. One of 14 narrow research briefs for the trader's rebuild (BACKLOG B24), each run as its own
Claude Code session in a VS Code tab. To start it, type in a new tab:
`Run research brief 04: read docs/research/briefs/04-ai-forecasting-techniques.md and follow it.`

Before you start, read `docs/research/README.md` (rules for sessions running side by side, evidence standards, the
report format) and the "What the data says" section of `docs/REBUILD_SCOPE.md`.

## Question

Which techniques measurably improve an LLM's accuracy on real-world forecasting questions, by how much, and which fit a system that forecasts about 200 markets every 30 minutes on a fixed subscription?

## What we already know

- On 327 finished markets with a real price, Claude direct (Claude's own probability after its research) scores a Brier of 0.207, the market 0.172, Jev with the same research 0.215, and Jev alone 0.245.
- Overconfidence: on bets placed since the 30¢ floor, our forecasts expected 99.8 wins, the market's prices implied 65.7, and 62 came in.
- A big miss: 81–93% that WTI oil would hit $95 in September, against a market price of 7¢.
- Research today: Claude gathers facts by web search (screened so no prices leak in), up to about 150 runs a day.

## Find out

- What benchmarks and studies show as of 2026 (for example ForecastBench, the retrieval-augmented system of Halawi et al. 2024, Metaculus's AI benchmark tournaments, ensembles of models compared with human crowds, superforecaster comparisons), and how far the best systems are from crowds and liquid markets.
- Measured gains from each technique: retrieval quality and recency, breaking a question into parts, base rates and reference classes, ensembles of samples or models (median vs mean), extremizing, calibration on resolved questions (Platt or isotonic), longer reasoning.
- Known failure modes and their fixes: overconfidence, anchoring on recent news, misreading resolution rules and deadlines, questions about numbers crossing thresholds.

## Leave out

Combining a forecast with the market price (brief 05); Jev specifics (14); model-based pricing of numeric markets (06–08).

## Deliverable

Write `docs/research/04-ai-forecasting-techniques.md` in the report format from `docs/research/README.md`, and include
a ranked list of techniques with the expected Brier gain, the cost per forecast, and the strength of the evidence.

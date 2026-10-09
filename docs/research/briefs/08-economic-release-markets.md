# Research brief 08: Pricing economic-data and Fed markets

Kind: Reference. One of 14 narrow research briefs for the trader's rebuild (BACKLOG B24), each run as its own
Claude Code session in a VS Code tab. To start it, type in a new tab:
`Run research brief 08: read docs/research/briefs/08-economic-release-markets.md and follow it.`

Before you start, read `docs/research/README.md` (rules for sessions running side by side, evidence standards, the
report format) and the "What the data says" section of `docs/REBUILD_SCOPE.md`.

## Question

How should we price markets on CPI, payrolls, unemployment, GDP and Fed decisions from nowcasts, consensus forecasts and futures, and are Kalshi's prices already as good as those?

## What we already know

- 51 of our 1,133 finished markets were economics. On the only 6 that all three forecasters covered, the market scored a Brier of 0.087 and Claude direct 0.306: a tiny sample, but the same direction as everywhere else.
- Example: a bet on the unemployment rate (U-3 above 3.9% for September) at about 9.5¢.

## Find out

- Sources: the Cleveland Fed inflation nowcast, the Atlanta Fed's GDPNow, consensus surveys (which ones are free), and CME FedWatch (fed funds futures) for Fed decisions, with their update times.
- The historical spread of surprises (actual minus consensus) for each release, to turn a point forecast into probabilities for each bin.
- Exactly how Kalshi's economics markets resolve (which release, revisions, rounding, timing).
- Evidence comparing Kalshi's economics markets with consensus and futures, 2023–2026.

## Leave out

Price thresholds (brief 06); weather (07).

## Deliverable

Write `docs/research/08-economic-release-markets.md` in the report format from `docs/research/README.md`, and include
for each release type, the model, the data sources and a backtest plan, plus a verdict on whether any edge is plausible.

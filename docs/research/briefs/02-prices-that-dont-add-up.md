# Research brief 02: Prices that don't add up

Kind: Reference. One of 14 narrow research briefs for the trader's rebuild (BACKLOG B24), each run as its own
Claude Code session in a VS Code tab. To start it, type in a new tab:
`Run research brief 02: read docs/research/briefs/02-prices-that-dont-add-up.md and follow it.`

Before you start, read `docs/research/README.md` (rules for sessions running side by side, evidence standards, the
report format) and the "What the data says" section of `docs/REBUILD_SCOPE.md`.

## Question

How often do identical or logically linked markets carry prices that can't all be right, within Kalshi, within Polymarket, or between the two, and is the gap big enough to capture after fees?

## What we already know

- Each cycle fetches 100 markets from each venue, but nothing matches the same event across venues.
- Linked markets aren't made consistent: Jev once gave 38% and 23% to the two candidates in a two-way race, where the market had 43% and 57% (BACKLOG B3).
- Our price data is the best ask on each side about every 30 minutes; we don't store order-book depth.

## Find out

- Across venues: how often the same event differs between Kalshi and Polymarket by more than the fees on both legs, how long gaps last, and the traps (different resolution sources, deadlines or wording; settlement timing; money tied up until resolution).
- Within an event: multi-outcome markets whose YES prices sum to more or less than 100% (the buy-every-NO or buy-every-YES trade), and threshold ladders priced out of order (for example P(BTC above $110k) priced above P(BTC above $100k)).
- How traders and bots find these automatically, including matching one event across venues by its text, and how much is left after fees.
- Evidence from studies or documented arbitrage on these venues, 2024–2026.

## Leave out

Markets that keep trading after the answer is known (brief 03). Fees in detail (10).

## Deliverable

Write `docs/research/02-prices-that-dont-add-up.md` in the report format from `docs/research/README.md`, and include
a recipe for automatic detection (matching rules, thresholds net of fees on both legs) and the frequency to expect.

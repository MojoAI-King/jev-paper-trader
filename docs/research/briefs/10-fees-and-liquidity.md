# Research brief 10: What trading actually costs on each venue

Kind: Reference. One of 14 narrow research briefs for the trader's rebuild (BACKLOG B24), each run as its own
Claude Code session in a VS Code tab. To start it, type in a new tab:
`Run research brief 10: read docs/research/briefs/10-fees-and-liquidity.md and follow it.`

Before you start, read `docs/research/README.md` (rules for sessions running side by side, evidence standards, the
report format) and the "What the data says" section of `docs/REBUILD_SCOPE.md`.

## Question

What exactly are the fees on Kalshi and Polymarket today, by market type, for makers and takers, and what do spreads and order-book depth typically look like?

## What we already know

- Our cost model: Kalshi taker fee 0.07 × P × (1 − P) per contract, Polymarket free, plus 1¢ slippage, always buying at the best ask (`fee_per_contract` in `papertrade/engine.py`, `fees` in `policy.json`).
- Measured: buying at the ask costs about 8.4% of each bet (crossing the spread about 3.8%, fees and slippage about 4.6%).

## Find out

- Kalshi: the fee formula and its rounding (per contract or per order), maker fees and which markets have them, special schedules (sports, indices), and changes in 2025–2026, with links and dates.
- Polymarket: which markets charge fees and how much (2025–2026 changes, including any taker fees on fast crypto markets), the US platform vs the international one, and any other costs.
- Typical spreads and displayed depth by market type and price level, and how to read the order book through each public API.
- Anything else that costs money or blocks a trade: position limits, minimum sizes, tick sizes.

## Leave out

Fill simulation (brief 11); sizing (12).

## Deliverable

Write `docs/research/10-fees-and-liquidity.md` in the report format from `docs/research/README.md`, and include
the exact fee functions to put in code, each with its source and date, and what's wrong with our current model.

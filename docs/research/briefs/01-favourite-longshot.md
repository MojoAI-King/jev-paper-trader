# Research brief 01: How mispriced are cheap and expensive contracts?

Kind: Reference. One of 14 narrow research briefs for the trader's rebuild (BACKLOG B24), each run as its own
Claude Code session in a VS Code tab. To start it, type in a new tab:
`Run research brief 01: read docs/research/briefs/01-favourite-longshot.md and follow it.`

Before you start, read `docs/research/README.md` (rules for sessions running side by side, evidence standards, the
report format) and the "What the data says" section of `docs/REBUILD_SCOPE.md`.

## Question

On Kalshi and Polymarket, what return does buying a contract at each price level earn (for example 1–10¢, 10–30¢, 30–50¢, 50–70¢, 70–90¢, 90–99¢), for takers and for makers, after fees, and does it differ by market type?

## What we already know

- Our own settled bets by price paid: under 30¢, 4 won of 78 when the prices implied 9.3 wins (−78% return); 30–50¢ −7.0% (73 bets); 50–70¢ −0.4% (81); 70¢ and up −21.6% (19, a small sample).
- Flat $100 on every finished market at the ask: always the favourite −2.8% ± 1.7% (1,133 markets); favourites priced 70–95¢ −1.5% ± 1.8% (544); always the underdog −31.9% ± 4.6%.
- Regressing outcomes on the market's log-odds puts a weight of about 1.35 on the price. Above 1 means prices sit too close to 50% in our sample: favourites slightly underpriced, long shots overpriced.

## Find out

- Published analyses of Kalshi and Polymarket trade data on returns by price level, maker vs taker (for example the 2025 academic study of Kalshi trades split by makers and takers), and older evidence from other betting markets for comparison.
- How the bias differs by category (sports, crypto, politics, weather, economics), by time to resolution, and by venue.
- Whether buying favourites, or buying NO on cheap YES contracts, is profitable after Kalshi's fee curve, or only for makers.
- Why the bias exists (risk-loving retail, attention, fees) and whether it has shrunk as volume grew from 2023 to 2026.

## Leave out

Price gaps across venues or within an event (brief 02), bet sizing (12). Fees in detail are brief 10, but use them.

## Deliverable

Write `docs/research/01-favourite-longshot.md` in the report format from `docs/research/README.md`, and include
a table of return by price bucket from the best source, with venue, period, sample size, and taker or maker.

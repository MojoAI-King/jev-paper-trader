# Claude stops picking bets too

Kind: Living. Decision entry.

- **ID:** 2026-10-11-claude-stops-picking-bets-too-8552
- **Status:** accepted
- **Date:** 2026-10-11

## Decision

Joey, 2026-10-11 ("retire retire", asked whether the Claude-picking strategies should keep running after Jev was
retired as a picker the same day, decision 2026-10-11-jev-stops-picking-bets-6267):

1. `claude_direct` is retired in `policy.json`; the challenger `ch16` ("Claude direct, sports only") is retired by hand
   (`python3 -m papertrade retire ch16`). Ledgers kept; open bets still settle; the page leaves them out.
2. `claude_direct` joins `learning.retired_probabilities`. With every forecaster source retired, the daily review can
   start no challenger at all (`learn.challenger_problem` refuses each), though it still reviews and may tune rules.
3. What still bets: `sharp` (Pinnacle's line through The Odds API), `mention_no` (the market's mid less a measured YES
   bias) and `original` (the frozen yardstick, still Jev + research, kept to show what the old approach does).

## Why

On 657 markets with a real two-sided price, Claude direct scored a Brier of 0.200 against the market price's 0.160,
and its measured skill beyond the price was −0.014: leaning on its view instead of the price made forecasts worse.
Its strategies were already reduced to probe bets losing slowly to fees.

## Alternatives rejected

- **Keep Claude direct for the scoreboard only:** its forecasts are still recorded wherever research runs (for
  `original`), so scoring continues without it betting.

## Risk

Claude research still runs for `original` on Joey's plan; that use can be cut later if the yardstick is not worth it.

## Reversibility

Remove `retired` from `claude_direct` and drop it from `learning.retired_probabilities`; `ch16` can be started again
with `python3 -m papertrade approve ch16`.

## Evidence

- `engine.skill` and `engine.paired`, read 2026-10-11 (decision 2026-10-11-jev-stops-picking-bets-6267 has the table).
- Offline tests: 154 pass (`RetiredJevTests` checks the live policy).

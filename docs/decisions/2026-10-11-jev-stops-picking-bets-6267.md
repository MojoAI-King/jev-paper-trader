# Jev stops picking bets

Kind: Living. Decision entry.

- **ID:** 2026-10-11-jev-stops-picking-bets-6267
- **Status:** accepted
- **Date:** 2026-10-11

## Decision

Joey, 2026-10-11 ("yyeess", to retiring the strategies that pick with Jev):

1. `main`, `bold` and `calibrated` are retired in `policy.json`; the running challenger `ch13` (probability
   `jev_calibrated`) is retired by hand (`python3 -m papertrade retire ch13`). Their ledgers stay and their open bets
   still settle; the page leaves them out (Joey's rule of the same day).
2. `learning.retired_probabilities` (`jev_plain`, `jev_research`, `jev_calibrated`) stops the daily review from starting
   a challenger that picks with Jev (`learn.challenger_problem`, checked when proposed and on every load). Jev may still
   be a gate (rules clear, enough information).
3. `original` stays as the frozen yardstick. `ch16` picks with Claude, not Jev (it was wrongly listed as a Jev
   strategy in the question to Joey), so it keeps running until he decides; so does `claude_direct`.
4. Code that assumed `main` is active now reads its ledger safely (`dashboard.summarize`, `dashboard.last_scan`,
   `engine.report`). The offline tests keep a copy of the policy with the Jev strategies on, because the machinery
   they test still serves the remaining strategies; `RetiredJevTests` checks the live policy.

## Why

On 657 markets with a real two-sided price (spread 10¢ or less), the Brier scores were: market price 0.160, Claude
direct 0.200, Jev with research 0.217, Jev alone 0.247 (a coin flip scores 0.25). Every forecaster's measured skill
beyond the price was negative: Jev alone −0.035 over 1,205 resolved markets, Jev with research −0.038 over 974,
calibrated Jev −0.044 over 905. Following Jev's view instead of the price made forecasts worse, and its strategies were
already reduced to probe bets that lose slowly to fees.

## Alternatives rejected

- **Keep them as probes for the record:** a slow drip of losses with nothing left to learn at this sample size.
- **Retire Claude direct too:** not asked; its skill is also negative (−0.014 over 657), so it is the next question
  for Joey.

## Risk

Jev could have value in a narrower job (reading rules, checking facts) that this does not test; that stays open as a
proposal (B30). The page now shows fewer strategies.

## Reversibility

Remove `retired` from the three strategies and empty `learning.retired_probabilities` in `policy.json`; `ch13` can be
started again with `python3 -m papertrade approve ch13`.

## Evidence

- `engine.skill` and `engine.paired` over `judgments.jsonl`, `mentions.jsonl`, `sharp.jsonl` and `resolutions.json`,
  read 2026-10-11.
- Offline tests: 154 pass, including `RetiredJevTests`.

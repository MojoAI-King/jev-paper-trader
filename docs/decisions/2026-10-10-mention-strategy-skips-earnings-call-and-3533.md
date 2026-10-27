# Mention strategy skips earnings-call and Trump series

Kind: Living. Decision entry.

- **ID:** 2026-10-10-mention-strategy-skips-earnings-call-and-3533
- **Status:** accepted
- **Date:** 2026-10-10

## Decision

Part of B32, on Joey's "ok yes ... get more and more data collected":

1. The mention strategy no longer reads or bets Kalshi mention series whose ticker contains EARNINGS or TRUMP
   (`mention.exclude_series`; `markets.fetch_kalshi_mentions(skip=...)` and `engine._mention_pass`).
2. `mention.yes_bias` is 0.10 (was 0.12): the measured gap between how often NO wins and the price paid in the kept
   series, about 9–10 points, plus the cent or so between the price paid and the mid.
3. All 20 open bets on earnings-call series are left out of the forward test's keep-or-kill count and reported on
   their own, decided before any of them settled (`docs/EXPERIMENTS.md`): 5 placed by 18:35Z, and 15 more at 18:50Z,
   in the one cycle between the daily limit rising to 30 and this rule going live (first run 38079351634, 19:19Z).

## Why

The timing test over every Mentions series (7,929 settled markets, `docs/research/CHECKS.md`) found the YES optimism
in the smaller political and TV mention markets, not in earnings calls or Trump:

- Outside earnings and Trump, NO at 30–70¢ won 8.9–9.7 points more often than its price: +15% to +18% after fees, in
  both the older and the newer half of history, under both buying rules tested.
- In earnings and Trump series, +0.5 to +2.5 points, under the ~2.8¢ of fee and slippage a bet pays; neither half
  clears zero.
- Across everything, the first test's +21% shrank to +9.8% (first 48 hours) and +4.5% (the live rule), so keeping the
  weak series would have diluted the edge and the strategy's measured skill (λ), which sizes its stakes.

## Alternatives rejected

- **Keep every series:** the live rule across all series is +4.5% with a range that includes zero.
- **Limit to markets listed within 48 hours instead:** +9.8% across all series, but inside the kept series buying
  late paid about as well as buying early, and the limit would cut most of the supply. The setting
  (`mention.max_hours_listed`) exists, off.
- **Finer cuts (individual politicians or shows):** too few events each; a split chosen that finely would fit noise.

## Risk

- The kinds were chosen after looking at the data. The split-half check is the guard: the pattern holds in both
  halves. The forward test, on new markets only, is the real judge.
- Earnings season (mid-October) offers many earnings-call markets; the strategy now passes on all of them.

## Reversibility

Easy: empty `mention.exclude_series` and set `yes_bias` back in `policy.json`.

## Evidence

- `docs/research/scripts/mention_timing.py` output, 2026-10-10 (summarized in `docs/research/CHECKS.md`, section
  "Mention markets: coverage and timing").
- Offline tests: 151 pass, including `test_earnings_call_and_trump_mention_series_are_left_alone`.

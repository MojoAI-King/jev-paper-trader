# A first edge measured on 639 markets was half as big on 7,929

Kind: Living. Lesson entry.

- **ID:** 2026-10-10-a-first-edge-measured-on-639-markets-was-7008
- **Status:** accepted
- **Date:** 2026-10-10

## What broke

The mention strategy went live on "+21.0% after fees, 95% range +6.1% to +35.5%" from 639 settled Kalshi mention
markets (the 90 most recently updated series). Re-run over every Mentions series (7,929 markets), the same rule gave
+9.8% [+4.1, +15.1], the rule the live strategy actually followed gave +4.5% [−1.4, +9.8], and in two whole kinds of
series (earnings calls, Trump) there was no edge at all. The live strategy had meanwhile bet on five earnings calls.

## The mechanism

- Selection: the mention lead was the best of about a dozen ideas tested on 2026-10-09/10, and the 30–70¢ band was
  picked from several bands. The winner of many tries over-states its effect (winner's curse), and a 95% range does
  not correct for the number of tries.
- A narrow sample: the 90 most recently updated series over-weighted the political and TV shows where the bias lives;
  the full set adds hundreds of earnings-call and Trump markets where it doesn't.
- Rule drift: the test bought within 48 hours of listing; the live code bought whenever a market was first seen in
  band, a different rule that was never measured until `docs/research/scripts/mention_timing.py` ran.

## The fix

- `docs/research/scripts/mention_timing.py`: the whole population, every timing window, by kind of series, with a
  split by event date to check a pattern holds in both halves (results in `docs/research/CHECKS.md`).
- `policy.json` `mention.exclude_series` (EARNINGS, TRUMP) and `yes_bias` 0.10, from the split-half result (+15% to
  +18% in both halves outside those series). Decision 2026-10-10-mention-strategy-skips-earnings-call-and-3533.
- The five earnings-call bets are left out of the keep-or-kill count, decided before they settle.

## The rule

Before money (even paper money) goes behind an edge found on history:

1. test it on the whole population, not a convenient slice;
2. test the exact rule the live code will follow (timing, filters, price), not a cousin of it;
3. split by time and require the effect in both halves;
4. expect it to be smaller than the first measurement, and say so in the registry.

## What now enforces it

Nothing in code; this is a research habit. The registry row (`docs/EXPERIMENTS.md`) now states the narrowed rule and
the smaller expected return, and the forward test on new markets only is the judge.

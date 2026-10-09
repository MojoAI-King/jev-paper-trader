# Size bets by measured skill; one stake per event; real Kalshi fees; slower, capped review

Kind: Living. Decision entry.

- **ID:** 2026-10-09-size-bets-by-measured-skill-one-stake-pe-d725
- **Status:** accepted
- **Date:** 2026-10-09

## Decision

Phase 1 of `docs/REBUILD_PLAN.md`, carried out on 2026-10-09 under Joey's words before Shabbat: "do everything
you [need] to do, you have my blessing". `original` keeps its old rules and sizing as the yardstick.

1. **Size by measured skill.** `engine.skill` measures, per forecaster, λ: the share of its forecast's distance from
   the market mid that came true, on finished markets with a real price at their first look. It is shrunk for noise
   with an event-clustered bootstrap, and 0 below 300 markets or when not positive. Every strategy but `original`:
   - while λ is 0, or Kelly on the shrunk forecast is not positive, places **probe bets**: 0.25% of equity, at most
     5 a day, marked `probe` on the bet and in the page's feed;
   - otherwise bets Kelly on the forecast shrunk toward the mid, q = m + λ(q − m), scaled by a drawdown cushion
     that reaches 0 at 70% of peak equity.
2. **One stake budget per event.** All open bets in one event share one `max_stake_pct` budget. Open bets saved
   before this change are matched to their event through the judgments log. Holding both sides of one market was
   already refused ("already holding this market").
3. **A real price is required** to bet (spread at most 10¢), for every strategy but `original`.
4. **Real Kalshi fees per series.** `markets.kalshi_fee_multiplier` reads each series' published `fee_multiplier`
   for the markets a run is about to judge (`markets.add_kalshi_fees`, cached per run, a handful of series a run). The fee is 0.07 × multiplier × p × (1 − p): MLB games 0.5, some series 0, most 1.
5. **A slower, capped review.**
   - `min_days_between_changes` 7 (was 1).
   - `learning.bounds` caps Kelly at 0.5, 3% a bet and 50% open (were 1.0 each).
   - `calibration_min_resolved` 300 (was 30).
   - The review's prompt explains that sizing changes do nothing while λ is 0, and its numbers include "skill".

## Why

Measured on 2026-10-09 (`docs/research/CHECKS.md`). On markets with a real price, every forecaster's λ is about
0: Claude direct −0.05 [−0.25, +0.18] on 330, Jev + research −0.03 on 608, Jev alone −0.06 on 1,006. Kelly sizing
on a forecast with no edge is pure over-betting (report 12): it lost 13% of stake after the 30¢ floor and 46%
before. The review changed rules 18 times in 11 days, each version judged on a median of 8 settled bets (report 13).
Before this change the bounds let it set a strategy to full Kelly at 100% a bet. Kalshi's API publishes per-series
fee multipliers that the trader ignored (report 10; KXMLBGAME 0.5 read live).

## Alternatives rejected

- **Stop betting entirely.** Joey wants a page with action. Probes keep the trades coming and measure real costs,
  at about a tenth of the old losses.
- **Keep Kelly but lower `kelly_fraction`.** Any fraction of a stake on a zero edge still loses. Shrinking toward the
  price with a measured λ is the version that grows stakes only as skill appears (report 12, F3).
- **Ceilings as constants in code** (report 12's preference). They stay in `policy.json`, which code checks on every
  load, as the other bounds do; moving them is a later code change.
- **Detecting opposite outcomes across markets in one event** (YES on A and YES on B in a two-way race). The data
  doesn't say which markets are mutually exclusive. The shared event budget caps the cost instead.

## Risk

- Probes still lose about the cost of trading: at 20–35 bets a day of about $250, roughly $400–700 a day across
  all strategies, against several thousand before.
- If a forecaster's λ turns positive by luck, its stakes grow. The 300-market minimum and the noise shrinkage limit
  that.
- Strategies far below their peak would bet tiny Kelly stakes even after λ turns positive (the cushion). Probes
  aren't cushioned.
- The page's totals keep falling slowly while old open bets settle.

## Reversibility

- Treat a strategy like the yardstick (old sizing) by adding it to `learning.frozen_strategies`; that also stops its
  tuning.
- Set `skill.probe_stake_pct` higher for bigger probes.
- Set `skill.min_markets` to 0 to use λ as measured.
- Revert the `learning` values in `policy.json`.
- The Kalshi multiplier falls back to the full rate when a series lookup fails.

## Evidence

`SkillSizingTests`:
- λ measured only on resolved, real-priced markets, 0 under 300 or for noise;
- probes and their daily cap;
- Kelly on the shrunk forecast with the drawdown cushion;
- the event budget and the real-price rule;
- the book supplying peak, event cost and today's probes.

`test_kalshi_charges_each_series_published_multiplier`, and the updated `test_each_bet_records_the_rules_version_it_was_placed_under`
(through the real scan, main probes $250 while `original` bets $2,000). The tuning tests were moved to the 7-day wait
and new caps, plus a check that a change at day 6 is refused. 131 offline tests pass.

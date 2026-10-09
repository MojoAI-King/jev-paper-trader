# Rebuild plan

Kind: Living. Written 2026-10-09 from the fourteen research reports in `docs/research/` and their checks
(`docs/research/CHECKS.md`). Owner: Joey. On 2026-10-09, leaving for Shabbat, Joey said "do everything you
[need] to do, you have my blessing", so phase 1 went ahead (see "Done" below). Anything that needs money,
an account or a person still waits for him.

## The verdict, in plain words

1. **Our AI forecasters don't know anything the market price doesn't.** On the finished markets with a real
   price, the market is more accurate than Jev alone, Jev + research and Claude direct. Once the price is
   known, none of them adds information (`docs/research/CHECKS.md`, reports 05 and 12). No published forecaster
   that can't see the price beats a liquid market. The best trail it by 0.015 to 0.04 Brier; ours trail by 0.035
   to 0.073 (report 04).
2. **Every bet starts about 8% down** (spread, fees, slippage). With no edge, each bet loses about that much on
   average, which is why a week of rule tuning didn't help.
3. **The quick wins don't work at our speed.** Price gaps between venues and "already decided" markets close in
   seconds to minutes; we look every 30 minutes (reports 02, 03). Weather and economic-data markets already beat
   the best public forecasts (07, 08).
4. **We bet as if we had an edge.** Bets are sized at quarter-Kelly on forecasts whose real edge measures zero, so
   every stake is an over-bet (12). The daily review changed rules 18 times in 11 days, each version judged on
   about 8 settled bets: that's chasing noise (13).
5. **Honest expectation:** nothing in the research makes money reliably after costs at our pace. The goals are
   (a) stop losing, (b) properly test the two or three ideas that could have an edge, and (c) keep it fun to
   watch.

## Phase 1: stop the bleeding, make the numbers honest

1. **Size by measured skill.** Each forecaster's edge over the price (λ, report 12) is measured from finished
   markets with a real price. While it is zero, as it is for all of them now, a strategy places small *probe*
   bets (0.25% of its bankroll, at most 5 a day) instead of Kelly bets. Probes keep the page active and measure
   real costs; they lose little. Once a forecaster shows a real edge on 300+ markets, its stakes grow with it.
   `original` keeps its old rules as the yardstick.
2. **One stake per event, never both sides.** All open bets in one event together count as one bet against the
   per-bet cap, and a strategy can't hold YES and NO in the same market (report 12, BACKLOG B17).
3. **Real Kalshi fees per series.** Kalshi publishes a fee multiplier for each series (MLB games 0.5, some
   series free). Charge it (report 10).
4. **Slow the daily review, and cap what it can set.**
   - A strategy's rules change at most once every 7 days (was daily).
   - The Kelly fraction is capped at 0.5, the per-bet cap at 3% and open bets at 50% (the old limits were 100%).
   - The self-calibration map needs 300 finished markets (was 30).

   Reports 12 and 13 show tuning on a handful of bets is noise.
5. **Judge forecasters by skill, bets by price movement.** The scoreboard is the head-to-head forecast score on
   markets with a real price (done: B25). Every bet also gets a closing-line check, meaning whether the price
   moved our way in the hours after the bet (reports 09, 13). Profit and loss is the slow, final word.

## Phase 2: the candidates that could have an edge

Each candidate is a new source of information. It is tested on the finished-market history first, then in a
forward test written down before its results come in. It bets more than probes only if it beats the market
(report 05's encompassing test plus report 13's forward test).

- **A. Sports against the sharp sportsbooks (report 09).** Buy only when a Kalshi or Polymarket price is at
  least 3¢ cheaper, after fees, than Pinnacle's price with the bookmaker's margin removed. Scored by
  closing-line value. **Needs Joey:** The Odds API at $30 a month (START 20K plan, confirmed on their pricing
  page). Expected result: zero or a small edge, but it's the most promising untested idea, and a month of data
  settles it.
- **B. Math pricing for price-threshold markets (06, 14).** Bitcoin, ETH, oil, gold and index "above $X" and
  "reach $X" markets are options. Price them from the live price and option volatility (Deribit is free), with
  Jev reading each market's rules (threshold, direction, deadline, which price settles it). Expected: about as
  accurate as the market, much better than our AI on these markets, and rarely a bet that beats costs.
- **C. Calibrate Claude direct on its own track record (04).** Cheap, with no extra Claude calls. It improves
  accuracy a little and cuts the overconfident bets. It doesn't create an edge by itself.
- **D. Make linked forecasts consistent (02, B3).** Probabilities on mutually exclusive outcomes add up to 1,
  and ladders fall as the threshold rises. Small.
- **E. New jobs for Jev (14).** Reading market rules for the math pricers, checking whether research facts show
  a market already decided, and labelling how two markets relate. Each job is measured on about 200 hand-checked
  cases before anything acts on it. Jev's own forecast is kept only as a logged yardstick.

## What we won't build, and why

- **Arbitrage across venues or within an event:** gaps last seconds, and it needs real accounts (02).
- **Sniping markets that are already decided:** the windows are minutes long, and the margin is about the same
  as the dispute risk (03).
- **A weather or economic-data pricer that bets:** the market already beats the best public forecasts (07, 08).
- **Resting limit orders:** they fill when the news turns against us (01, 05, 11).
- **Prompt tricks such as "think like a superforecaster":** no gain, or worse (04).

## Decisions only Joey can make

1. **$30 a month for sports odds data (phase 2A).** It needs an account and a payment, so it is his.
2. **Whether to retire some strategies.** Eleven strategies are mostly variants of one signal. Consolidating is a
   matter of taste for the page, so it's his call.
3. **Anything in phase 1 he'd rather undo.** Each change has one switch, listed in its decision record.

## Done

Filled in as work lands, with commits and evidence.

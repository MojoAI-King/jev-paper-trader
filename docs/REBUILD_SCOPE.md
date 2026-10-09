# Rebuild scope: what the data says, and the research briefs

Kind: Living. Written 2026-10-09, after about two weeks live. Owner: Joey. Next step: Joey runs the research
briefs in `docs/research/`; the results come back here and become the plan (each code change waits for Joey's OK).

## Why this exists

Joey, 2026-10-09: the strategies are "doing terrible", with no improvement, and the cause is that we went
straight into trading without enough research and planning: "if you were an actual trader... world class...
you would know so much more." He wants several deep research threads to produce a game plan, and a scope of
what to change.

## What the data says (measured 2026-10-09 on every finished market)

All numbers come from `papertrade_data/` at the 2026-10-09T20:38Z cycle. Accuracy uses each market's first
look (the earliest moment we could have bet) and the Brier score (0 is perfect, 0.25 is a coin flip).

1. **The market is a better forecaster than any of ours, and by a clear margin.** On the 327 finished markets
   with a real two-sided price (spread 10¢ or less) where all three forecast, the market's Brier is 0.172.
   Claude direct is worse by 0.035 ± 0.009, Jev + research by 0.043 ± 0.009, and Jev alone by 0.073 ± 0.010,
   each 4 to 7 standard errors. Betting rules can't turn a forecaster that is worse than the price into a
   winner, which is why a week of tuning didn't help.
2. **Jev is being used for a job it can't do.** It is asked one big question per market ("will this resolve
   YES?"), which needs world knowledge. On its own it scores like a coin flip (0.249 on 646 markets). Given
   Claude's research it does worse than Claude reading the same research (0.213 vs 0.184 on the same 646
   markets). Its "already decided?" signal almost never fires (11 of 939 markets) and, when it does, the
   market's favourite is right just as often.
3. **Trading costs eat about 8.4% of every bet.** If the market's mid price were exactly right, our post-floor
   bets would still lose 8.4% (crossing the spread about 3.8%, fees and slippage 4.6%). An edge has to be
   bigger than that to show a profit. We don't have one.
4. **Overconfidence.** On the 137 settled bets placed since the 30¢ floor, our forecasts expected 99.8 wins
   (a +64% return); the market's prices expected 65.7; 62 came in, for a −13.4% return (−46% before the
   floor). The worst group is betting *against* the market's favourite: bets at 30–50¢ won 15 of 55 when the
   market expected 22 (−35%). Bets at 50–70¢ (with the favourite) made +4.2%.
5. **Favourites vs long shots, in our own data.** Always buying the market's favourite at the ask on all
   1,133 finished markets: −2.8% ± 1.7%, about the cost of trading. Always buying the underdog: −31.9% ± 4.6%.
6. **Things that looked like fixes but aren't:**
   - *Blending each forecast with the market price* (fitted out of sample). It shows our forecasts carry a
     little information the price doesn't: weight 0.52 for Claude direct, 0.33 for Jev + research, 0.16 for
     Jev alone, against 1.35 for the market. Betting the blend at the ask still loses 13–21%.
   - *Waiting for a better price with resting orders.* Filling at the mid looked like +4% to +14%. A fill only
     counts if a later snapshot shows the price coming down to us, and with that rule results got worse
     (−16% to −31%), because orders fill when news turns against the bet.
   - *Claude "beating" the sports market.* The apparent edge, 0.094 better than the market before games start
     on 98 markets, came from Polymarket "Completed Match" tennis markets. There nobody bids, the asks sit at
     97–99¢ and 91–92¢, and the mid (about 53¢) is not a forecast. On real-priced sports markets Claude is
     slightly worse than the market (+0.011 ± 0.005, 205 markets).
7. **A measurement flaw to fix.** 146 of 1,133 first looks have spreads over 10¢, where the mid is not a real
   price. The Forecasters panel (2026-10-02) scores the market by its mid on all markets, so it makes the
   market look worse than it is. BACKLOG B25.
8. **We trusted small samples.** On 2026-10-02 I (Claude) said Jev + research was our best forecaster (112
   markets) and that it won 19 of 24 test bets. Neither held at 600+ markets. Rule of thumb from now on: no
   conclusions from fewer than a few hundred finished markets, and every number gets its ± range.

Volume is 20 to 35 bets a day across all strategies. Research runs about 150 a day on Joey's plan.

## What a professional would do differently (the hypotheses to research)

- **Start from the market price.** Treat the price as the best forecast and bet only where there is a
  specific, checkable reason it is wrong: information it hasn't absorbed, or a model it isn't using.
- **Specialise in the market types where an edge can exist and data is free:**
  - numeric threshold markets (crypto, oil, indices), priced with volatility math from live prices; the LLM
    gave 81–93% that WTI oil would hit $95 in September, the market said 7¢, and it didn't;
  - weather, from official forecast models;
  - economic releases, from nowcasts and consensus;
  - sports, by comparing with sharp sportsbook lines rather than asking an LLM;
  - structural gaps: favourite/long-shot pricing, the same event priced differently on Kalshi and Polymarket,
    and multi-outcome events that don't add up to 100%.
- **Give Jev the jobs it is built for** (typed checks over given information: reading resolution rules,
  verifying facts, triage) instead of world forecasting, or take it out of the forecasting seat.
- **Honest costs and sizing:** skip illiquid wide-spread markets; respect Kalshi's fee curve (highest at 50¢);
  cap correlated bets (one wrong WTI call hit four strategies at once); fractional Kelly on shrunk
  probabilities.
- **Fast, honest feedback:** test every idea on the finished-market history (1,133 markets with ~30-minute
  price snapshots) before it trades, score only real-priced markets, and use closing-line value as an early
  signal.
- **Fewer, genuinely different strategies.** Most of today's strategies are variations on one signal.

## The research

Joey, 2026-10-09: make each research run narrow, and run as many as it takes. The first draft's five broad briefs
became fourteen narrow ones in `docs/research/briefs/`, each run by its own Claude Code session in a VS Code tab,
all at once. Each session writes its report into `docs/research/`. The run sheet, the rules for sessions running
side by side, and the report format are in `docs/research/README.md`. The same list, with a copy button for each
tab's one-line prompt, is on a page private to Joey: https://claude.ai/artifact/2USu1tPk31NdbK2p1vj5ta.

- **Where an edge could come from:** 01 favourite and long-shot pricing, 02 prices that don't add up (across venues
  and within an event), 03 markets still trading after the answer is known.
- **Better forecasts:** 04 what makes an AI forecaster more accurate, 05 combining a forecast with the market price,
  14 using Jev for the jobs it's built for.
- **Pricing with models instead of guesses:** 06 crypto, oil, gold and index thresholds, 07 daily weather, 08
  economic data and Fed decisions, 09 sports against the sharp sportsbooks.
- **Costs and judging:** 10 fees and liquidity, 11 honest fill simulation, 12 bet sizing, 13 telling skill from luck.

## After the research

1. Each research session writes its report into `docs/research/`; the main session commits them and checks
   their claims against our data where possible.
2. Claude writes the game plan: a short list of strategies to build, each pre-registered in
   `docs/EXPERIMENTS.md` with the backtest it must pass first, and the code changes each needs. Joey approves
   or rejects each code change.
3. A reusable backtest tool (a code change, so it needs Joey's OK) so every idea is tested on the finished
   markets with honest costs before it trades.

Meanwhile the trader keeps running unless Joey says otherwise: its price snapshots and forecasts on markets
that finish are what every new idea will be tested on.

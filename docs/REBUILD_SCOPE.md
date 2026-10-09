# Rebuild scope: what the data says, and the research briefs

Kind: Living. Written 2026-10-09, after about two weeks live. Owner: Joey. Next step: Joey runs the research
briefs below; the results come back here and become the plan (each code change waits for Joey's OK).

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

## The research briefs

Each brief stands alone: paste one per tab into a deep research mode (claude.ai Research). Ask for links,
dates and sample sizes. Paste each report back into a session here; they get saved under `docs/research/`.
The same briefs, with a copy button each, are on a page private to Joey:
https://claude.ai/artifact/2USu1tPk31NdbK2p1vj5ta (built from the text between the `briefs` markers below).

The same context goes at the top of every brief.

<!-- briefs:start -->
### Shared context (included in each brief)

> CONTEXT. I run a paper-trading experiment (fake money, real markets) on Kalshi and Polymarket binary
> markets. Several strategies each hold a fake $100,000. Every 30 minutes an automated cycle fetches about 200
> open markets (100 per venue), forecasts P(YES) for each, and buys the side whose forecast beats the ask
> price after fees, sized by fractional Kelly. Forecasters: "Jev" (a typed-judgment model from TypeSafe that
> returns probabilities for questions about a state you give it), "Jev + research" (Jev reading
> facts Claude gathers with web search, screened so no prices leak in), and "Claude direct" (Claude's own
> probability from the same research). Today the forecasters never see the market price (an experimental
> choice; you may recommend changing it, but say why). After about two weeks and 1,133 resolved markets: on
> 327 markets with a real two-sided price (spread ≤10¢), every forecaster is less accurate than the market's
> mid price (Brier: market 0.172; Claude direct worse by 0.035 ± 0.009; Jev + research worse by 0.043;
> Jev alone worse by 0.073, about a coin flip). Settled bets lost 29% of stake overall (−46% before we stopped
> buying contracts under 30¢, −13% after). Buying at the ask costs about 8.4% per bet (spread ~3.8%, fees and
> slippage ~4.6%). Long shots under 30¢ lost almost every time; bets against the market favourite lost most;
> always buying the favourite at the ask lost only 2.8% ± 1.7% (n = 1,133). Constraints: fake money only;
> data must come from free or cheap public APIs; LLM work runs on a fixed subscription (about 150 research
> runs a day). We have a history of every market we looked at with price snapshots about every 30 minutes,
> our forecasts, and the outcomes, so any idea can be backtested.

### Brief 1: Where the real edges are

> QUESTION. Where do persistent edges exist in Kalshi and Polymarket binary markets today (prefer 2024–2026
> evidence), and which can a small automated system capture after fees?
>
> Cover: (1) the favourite–long-shot bias in prediction markets: size by price bucket, venue and category, and
> maker vs taker returns (for example academic studies of Kalshi trade data); (2) which market types are least
> efficient (sports, crypto price thresholds, weather, economic releases, politics, "mention" and culture
> markets) and why; (3) timing effects: early vs late in a market's life, reaction to news, and resolution lag
> (outcome effectively known while the market still trades); (4) structural gaps: the same event priced
> differently on Kalshi and Polymarket, multi-outcome events whose prices don't sum to 100%, related markets
> that contradict each other; (5) what profitable traders and bots on these venues actually do (documented, not
> hype) and realistic edge sizes after fees.
>
> DELIVERABLE. A ranked list of 5–10 edges. For each: the mechanism; the evidence with links, dates and sample
> sizes; expected return after fees; capacity; data needed; how to detect it automatically; and a simple test
> we could run on our own history of resolved markets with ~30-minute price snapshots. Mark anything
> anecdotal.

### Brief 2: LLM forecasting that actually works

> QUESTION. What does the best current evidence say about using LLMs to forecast real-world events well enough
> to trade, and how should an LLM's forecast be combined with the market price?
>
> Cover: benchmarks and studies (for example ForecastBench, retrieval-augmented forecasting systems, AI
> forecasting tournaments such as Metaculus's AI benchmark series, comparisons with superforecasters); which
> techniques measurably improve accuracy (retrieval quality, question decomposition, base rates, ensembling
> several models or samples, extremizing, calibration on resolved questions, using the market as a prior);
> known failure modes (overconfidence, anchoring on news, misreading resolution rules, date confusion, numeric
> thresholds); how to tell whether a forecaster adds information beyond the market; and any evidence of LLMs
> beating liquid markets. Our data point: fitting logit(p) = a + b·logit(market) + c·logit(model) out of sample
> gave b ≈ 1.35 and c ≈ 0.52 for Claude direct, 0.33 for Jev + research, 0.16 for Jev alone, yet bets on the
> blend still lost after paying the spread.
>
> DELIVERABLE. A concrete forecasting pipeline for our setup, step by step; the expected accuracy gain of each
> step with sources; what to stop doing; and how to validate each step on resolved markets.

### Brief 3: Pricing numeric markets with models, not guesses

> QUESTION. How should we price prediction markets whose outcome is a number crossing a threshold, using
> models and free data instead of an LLM's judgment?
>
> Market types we see: crypto ("Will Bitcoin reach $X by [date]", "BTC above $X at 5pm"), commodities and
> indices (WTI oil, S&P 500, gold), daily weather ("highest temperature in [city] on [date]" in 1–2 degree
> bins, rain), and economic releases (CPI, unemployment, payrolls, Fed decisions). Example failure: our LLM
> gave 81–93% that WTI crude would hit $95 in September while the market priced it at 7¢; it didn't.
>
> For each type: the right model (for example touch/barrier probability vs close-above probability from
> implied or realized volatility; ensemble weather forecasts and their error by lead time; nowcasts and
> consensus for economic data); free or cheap data sources with API details and limits (exchange price APIs,
> crypto options implied volatility, NWS/NOAA, Open-Meteo ensembles, the Cleveland Fed inflation nowcast, and
> so on); evidence on how these models compare with prediction-market prices; and pitfalls (the exact
> resolution source and weather station, time zones, rounding, settlement times).
>
> DELIVERABLE. Per market type: a formula or algorithm, the data sources, a backtest plan, and an honest
> estimate of whether the market is usually already efficient there.

### Brief 4: Sports against the sharp books

> QUESTION. Can a small automated system profit on Kalshi and Polymarket sports markets by comparing them with
> sharp sportsbook prices, and how exactly?
>
> Our data: on 205 real-priced sports markets Claude's own forecast was slightly worse than the market (Brier
> +0.011 ± 0.005); always buying the favourite at the ask lost 1.6% ± 2.6% (n = 606). Many Polymarket sports
> markets are illiquid (tennis "Completed Match" markets with asks of 97¢ and 92¢ and no bids).
>
> Cover: how prediction-market sports prices compare with sharp books (Pinnacle, Circa, betting exchanges):
> documented gaps, timing (opening vs closing), leagues and market types where they lag; sources for consensus
> and sharp odds (for example The Odds API tiers, free alternatives) and how to remove the bookmaker margin;
> closing-line value as the measure of skill; which markets to avoid; timing of injury and lineup news; and
> whether edges survive Kalshi's fee curve.
>
> DELIVERABLE. A step-by-step strategy with entry rules, data sources and their costs, expected edge with
> evidence, and a test plan using our price snapshots.

### Brief 5: Costs, execution, sizing and judging skill

> QUESTION. For a paper-trading system on Kalshi and Polymarket, what are the correct current costs, and the
> best practice for execution, bet sizing, risk limits, and telling quickly whether a strategy has real skill?
>
> Cover: (1) current fee schedules: Kalshi taker and maker fees by market type (the formula and its rounding),
> and Polymarket fees by market type, with dates and links; (2) execution: taker vs maker, and how to simulate
> limit-order fills honestly in a paper trader that only has ~30-minute snapshots of the best asks (our test:
> resting orders at the mid, counted as filled only when a later snapshot's ask reached our price, did worse
> than buying at the ask, because of adverse selection); (3) sizing: Kelly under estimation error, shrinkage,
> per-bet and per-event caps, correlated bets (the same underlying at several thresholds, across strategies),
> drawdown rules; (4) evaluation: closing-line value, Brier decomposition (reliability and resolution), paired
> tests against the market, the sample sizes needed to detect a 2–5% edge, multiple-testing and overfitting
> risk when testing many variants on one history, and walk-forward backtests.
>
> DELIVERABLE. A checklist and the exact formulas to put in code, with sources.
<!-- briefs:end -->

### Brief 6: Harnessing Jev (done here, not in a tab)

Claude does this one in a session, with the TypeSafe docs (docs.typesafe.ai) and the code: what System One is
designed for, which typed questions suit a trading pipeline (rules reading, fact checks, triage, ranking), and
a test of each on the finished-market history.

## After the research

1. Joey pastes each report into a session; Claude saves it under `docs/research/` and checks its claims
   against our data where possible.
2. Claude writes the game plan: a short list of strategies to build, each pre-registered in
   `docs/EXPERIMENTS.md` with the backtest it must pass first, and the code changes each needs. Joey approves
   or rejects each code change.
3. A reusable backtest tool (a code change, so it needs Joey's OK) so every idea is tested on the finished
   markets with honest costs before it trades.

Meanwhile the trader keeps running unless Joey says otherwise: its price snapshots and forecasts on markets
that finish are what every new idea will be tested on.

# Checks on the research reports

Kind: Living. The main session's check of each report in this folder: sources spot-checked, claims tested on our
own data (`papertrade_data/` at the 2026-10-09 cycles), and what changed because of it. Ranges here are 95%
intervals from bootstrap resampling of whole events; the ± values in `docs/REBUILD_SCOPE.md` and the briefs are one
standard error.

## 05 Combining our forecast with the market price (checked 2026-10-09)

- **Sources spot-checked.**
  - AIA Forecaster (arXiv 2511.07678, Nov 2025) exists. Its abstract confirms that the LLM trails market consensus
    on liquid markets, and that an ensemble with the market beats the market alone.
  - Kim et al. (arXiv 2602.21229, Feb 2026) exists. Its abstract confirms mention markets, the market probability
    used as a prior, and a mixture beating the market. It doesn't name Kalshi, which the report already noted.
- **Its flag on our numbers was right.** Refit on first looks with spread ≤10¢:

  | Fit | Markets | Weight on the market (b) | Weight on the forecaster (c) |
  |---|---|---|---|
  | Market alone | 1,006 | 1.12 [0.98, 1.28] | |
  | + Claude direct | 330 | 1.16 [0.83, 1.58] | −0.05 [−0.42, 0.31] |
  | + Jev + research | 608 | 1.09 [0.89, 1.34] | 0.03 [−0.32, 0.41] |
  | + Jev alone | 1,006 | 1.16 [1.02, 1.33] | −0.30 [−0.63, 0.07] |

  On all first looks, wide spreads included, c came out at 0.17 to 0.54. That was the source of the numbers in the
  first version of the briefs: fake mids. Corrected in `docs/REBUILD_SCOPE.md` and briefs 01 and 05.
- **Consequence.** On markets with a real price, none of our current forecasters adds information the price doesn't
  already contain. Under the report's encompassing gate every current source gets w = 0, and its betting rule
  would place no bets. Its framework (market-anchored blend, shrinkage, encompassing gate, cost-plus-haircut
  rule) stands for any new source the other briefs turn up.
- **Not run yet:** its tests 2–8. They matter once a candidate source exists.

## 01 How mispriced are cheap and expensive contracts? (checked 2026-10-09)

- **Source spot-checked.** docs.polymarket.com/trading/fees, read 2026-10-09:
  - Takers pay `shares × rate × p × (1 − p)`; makers pay nothing.
  - Rates: crypto 0.07; sports, economics, culture, weather and other 0.05; politics, finance, tech and mentions
    0.04; geopolitics 0.
  - The page gives no start dates.

  Our trader charges 0 on Polymarket, so every Polymarket bet and backtest is flattered (BACKLOG B26).
- **Its test T1 on our data.** Real-priced first looks; each market bought both ways at the ask, with our current
  cost model (Kalshi 0.07·P·(1−P) plus 1¢; Polymarket 1¢ only).

  | Price paid | Kalshi | Polymarket |
  |---|---|---|
  | 0–10¢ | −61% [−90, −31], n 106 | −57% [−91, −15], n 108 |
  | 10–30¢ | −20% [−45, +13], n 193 | −27% [−57, +1], n 149 |
  | 30–50¢ | −9% [−22, +2], n 309 | −2% [−27, +26], n 97 |
  | 50–70¢ | −6.5% [−14, +1], n 371 | −6% [−21, +11], n 92 |
  | 70–90¢ | −1% [−9, +6], n 182 | −2% [−11, +7], n 133 |
  | 90–100¢ | +1.0% [−2, +4], n 133 | +1.9% [−1, +5], n 139 |

  With a 0.05 Polymarket fee, Polymarket's 90–100¢ row is +1.6% [−1.1, +4.6]. The shape matches the literature:
  cheap contracts lose most of their money, and favourites are break-even within noise.
- **Its test T3** (slope from the price alone) is the 05 refit above: 1.12 [0.98, 1.28]. The price looks about
  calibrated; the "1.35" in the first briefs was wrong.
- **Its question about ±:** in the scope doc and briefs, ± is one standard error.

## 07 Pricing daily weather markets from forecast models (checked 2026-10-09)

- **Sources spot-checked.**
  - Crosier (arXiv 2609.23969, Sept 2026) exists. Its abstract says the Kalshi market beats the best single public
    forecast (the NBM) by about 10% in error in six of seven cities.
  - Kalshi's API (KXHIGHNY-26OCT10-T73) shows rules_primary settling on the maximum at "New York City (CLINYC)
    ... according to The Weather Company". That confirms the report's source and station.
- **Its step 1 on our data.** 28 finished weather markets are single temperature bins (71 looks). On those, the
  forecasts above 40% on one bin were:

  | Forecaster | Such forecasts | Markets | Came true |
  |---|---|---|---|
  | Jev alone | 3 | 2 | 0 |
  | Jev + research | 8 | 4 | 2 |
  | Claude direct | 4 | 3 | 2 |

  That is far too few to size anything. The report's case rests on its arithmetic: before the day, no 2°F bin can
  honestly get more than about 29–37%.
- **Its recommendation stands as a proposal:** keep AI forecasters off single temperature bins. Weather markets are
  not worth targeting unless a structural test (same-day truncation, hourly-vs-official gap, long-shot bins) shows
  an edge.

## 06 Pricing crypto, oil, gold and stock-index thresholds (checked 2026-10-09)

- **Source spot-checked.** Portnaya (arXiv 2606.19517, June 2026) exists. Its abstract matches the report: a mean
  gap of 5.6 points on the main contract, 6.3 pooled, about 11 against Deribit, a half-life of about 4 hours, and
  arbitrage "profitable after conservative transaction costs" with only marginal precision.
- **Its WTI explanation fits the market we bet** (one of its "not verified" items). Our big WTI loss was
  polymarket:5083130, "Will WTI Crude Oil (WTI) hit (HIGH) $95 in September?":
  - its rules pay only if "at any point after market creation" a Pyth 1-minute candle of the *active month of ICE
    WTI futures* reaches the price, not spot oil;
  - main, `original` and the self-calibrating strategy bought YES at 7¢ on 09-30 at 81–93%, and bold bought at
    28¢ on 09-29;
  - that matches the report's price history for the re-listed market (22.5¢ at 09-29 12Z, 2.5–3.2¢ on 09-30).
- **These markets don't have their own category.** Our text matcher files oil, gold and index markets under
  "world" (201 judgments) and "economy" (162). So `skip_categories` can't single them out; only "crypto" can be
  skipped as a group.
- **They aren't where the current losses come from.** No crypto, oil or index threshold bet placed since the 30¢
  floor has settled (every strategy but `original`). The losses since the floor are:

  | Category | Bets | Return |
  |---|---|---|
  | Sports | 58 | −13% |
  | Other | 36 | −22% |
  | Weather | 18 | +18% (noise) |

  The floor, and main's crypto skip, already keep these markets out.
- **Consequence.** Its main recommendation, computing these probabilities with an option-style model, goes into
  the plan as a new source of information, to be tested under report 05's encompassing gate. It needs no urgent
  fix. For the same reason, weather (report 07) gets no category skip now: it made money on its 18 bets since the
  floor, too few to mean anything either way.

## 02, 03, 04, 08, 09, 10, 11, 12, 13, 14 (checked 2026-10-09)

All ten were committed by accident in 8905d49, which staged the whole `docs/` folder. Each file had last been
written (21:58–22:09Z) before that commit and hasn't changed since, so the committed text is final. Lesson:
`docs/lessons/2026-10-09-staging-a-folder-swept-up-other-sessions-work.md`.

- **02 Prices that don't add up.** No source check. Its verdict needs none: gaps last seconds, our snapshots are
  30 minutes apart, and we can't fill two legs. Arbitrage is out. Event coherence (BACKLOG B3) is a small,
  cheap fix.
- **03 Stale markets.** No source check. It finds no measurement either way, and its mechanism (Kalshi closes
  early, Polymarket winners drift to ~99.9¢) fits our own data: Jev's "already decided" signal fired on 11 of 939
  markets with no edge. Don't build it.
- **04 AI forecasting techniques.** Its gap figures agree with report 05's sources: the AIA Forecaster trails the
  market by 0.015 (0.1258 against 0.1106). Ours trails by 0.035–0.073 on real-priced markets. Its cheapest win,
  calibrating Claude direct on our own resolved forecasts, is untested on our data.
- **08 Economic data.** Source spot-checked: "Kalshi and the Rise of Macro Markets" (Diercks, Katz and Wright,
  FEDS 2026-010) exists (title page read). Its CPI and Fed numbers weren't re-read. Our own sample is 6 markets.
- **09 Sports against the sharp books.**
  - The Odds API's pricing page confirms START 20K at $30 a month and Pinnacle's coverage. The page doesn't
    show that one call also returns Kalshi and Polymarket prices: not verified.
  - Our data agrees that Claude adds nothing on real-priced sports markets (+0.011 ± 0.005 Brier).
- **10 Fees and liquidity.** Kalshi's API, read today:
  - KXMLBGAME has `fee_multiplier` 0.5 (`quadratic_with_maker_fees`); KXNFLGAME has 1.
  - So MLB games cost half the fee our model charges. Fixing it is part of phase 1 of the plan.
- **11 Fill simulation.** No source check. Its direction (resting orders fill on adverse moves) agrees with our
  −16% to −31% test.
- **12 Bet sizing.** Its λ, the share of a forecast's distance from the price that comes true, measured on
  first looks with a real price (95% event-clustered ranges):

  | Forecaster | Markets | λ |
  |---|---|---|
  | Claude direct | 330 | −0.05 [−0.25, +0.18] |
  | Jev + research | 608 | −0.03 [−0.17, +0.10] |
  | Jev alone | 1,006 | −0.06 [−0.14, +0.01] |

  All are about zero, so by its rule every Kelly stake we place over-bets.
- **13 Judging skill.** `rules_history.jsonl` holds 18 rule changes in about 11 days. The median rules version
  with settled bets was judged on 8 of them. The report's "tuning on noise" holds.
- **14 Jev's harness.** TypeSafe's documentation (llms.txt and model-jaggedness/jev-1.13.md, read today):
  - System One is for routing, ranking, extraction, verification, classification and moderation; forecasting
    isn't mentioned.
  - jev-1.13's documented weak spots: dates read as text, "Jev is not a calculator", multi-hop indirection,
    first-option bias, and score levels "weak in numerical calibration".
  - Our "will it resolve YES by the deadline?" question leans on every one of them.

## 04, test T2: calibrating our forecasters on their own record (run 2026-10-09)

A Platt map, z = a·logit(p) + b, fitted on the older half of each forecaster's finished markets with a real
price and scored on the newer half (the fit's prior was negligible, so it is close to a plain fit):

| Forecaster | Test markets | Map | Brier raw → calibrated |
|---|---|---|---|
| Claude direct | 281 | a 0.81, b +0.10 | 0.2079 → 0.2088 |
| Jev + research | 422 | a 1.07, b +0.14 | 0.2186 → 0.2229 |
| Jev alone | 513 | a 0.66, b −0.04 | 0.2278 → 0.2289 |

The market scored 0.1785–0.1845 on the same test markets. Calibration doesn't carry over from older to newer
markets here, so plan item 2C (B29) is dropped.

## Favourites as a small-edge strategy (run 2026-10-10, for Joey's "it's a formula" question)

The favourite bought at the ask with real fees plus 1¢, at the first look, on 1,026 finished markets with a real
price (95% ranges resample whole events):

| Slice | Markets | Return |
|---|---|---|
| All | 1,026 | −2.8% [−6.7, +0.9] |
| 50–70¢ | 423 | −6.0% |
| 70–85¢ | 224 | −3.1% |
| 85–95¢ | 279 | +0.6% [−3.0, +3.7] |
| 95–99¢ | 100 | +2.2% [−0.8, +3.4] |
| Under 1 day left | 451 | −0.8% |
| 1–7 days left | 503 | −6.2% [−11.5, −1.5] |
| Over 7 days left | 72 | +8.3% [−4.3, +21.5] |

The over-7-days slice matches the published finding that prices sit too close to 50% far from resolution (report
01, F8), but 72 markets can't confirm it. Re-run it once 300 or more long-dated markets judged after 2026-10-10 have
finished. The trader's `market_filters.max_price` of 0.95 keeps it out of the 95–99¢ band.

## 15 Who makes the money (checked 2026-10-10)

Written by a research agent from this session (six parallel researchers plus a writer). The agent checked seven
load-bearing sources itself: the Akey et al. CEPR paper, Becker's 72-million-trade study, two arbitrage papers,
Prediction Arena, Polymarket's rebate page, and Théo's figures. All matched. Its headline: about four wallets ever
made $10M+ on Polymarket. The money flows from takers to makers and from YES and long-shot buyers to NO and
favourite buyers. AI agents trading every 15–45 minutes lost 16–31% on Kalshi.

- **Corrections it found in earlier reports:**
  - Report 10 called the 2026-07-10 Polymarket sports fee rise (0.03 → 0.05) refuted. Polymarket's changelog has it,
    along with a cut in the sports maker rebate from 25% to 15%.
  - Report 02's "about 16 seconds" leaves out 58.7% of observed gaps, which lasted the whole sampled hour. Nobody has
    shown those longer gaps pay after fees.
- **Its test T1 on our data (run 2026-10-10).**
  - Our history holds no Kalshi mention markets: the trader loads only the 100 highest-volume markets per venue.
  - Buying at the ask with real fees plus 1¢, first look, on every real-priced finished market:

    | Side | Purchases | Return | Priced 30–70¢ |
    |---|---|---|---|
    | YES | 1,022 | −20.8% [−28.4, −13.1] | −12.1% [−20.5, −3.9] (453) |
    | NO | 1,001 | −7.6% [−13.7, −0.3] | −2.1% [−11.3, +7.5] (450) |

    That is the YES-optimism pattern the literature describes; NO still doesn't clearly beat costs here.
- **Its main lead held on fresh data (run 2026-10-10, scratchpad `mention_test.py`).** Method: the 90 most
  recently updated Kalshi "Mentions" series, their settled markets with volume of 200 or more, and in each the
  first real taker purchase of each side within the first quarter of the market's life (at most 48 hours, so
  before the event). Kalshi's taker fee at the series' multiplier; the 95% ranges resample whole events. That gave
  639 markets in 55 events.

  | Side and price paid | Purchases | Won | Price implied | Return after fee |
  |---|---|---|---|---|
  | NO 30–50¢ | 122 | 50.8% | 41.3% | +19.4% [−6.6, +42.3] |
  | NO 50–70¢ | 118 | 72.9% | 57.6% | **+22.6% [+7.5, +38.3]** |
  | **NO 30–70¢** | **240** | **61.7%** | **49.3%** | **+21.0% [+6.1, +35.5]** |
  | NO 70–90¢ | 71 | 78.9% | 80.2% | −3.0% [−14.8, +8.0] |
  | YES 50–70¢ | 136 | 48.5% | 59.9% | −21.8% [−37.9, −4.3] |
  | YES 70–90¢ | 182 | 68.1% | 77.9% | −13.7% [−22.6, −4.1] |

  This is the first edge in this project to clear costs on real data, and it matches the published finding.
  Limits: it was found on history (so it must pass a forward test), 55 events is few, and early order books can be
  thin. Mention markets are under a CFTC review. Built as the `mention_no` strategy (decision
  2026-10-10-mention-markets-no-side-strategy-37e6).

## The honest maker test (run 2026-10-10, scratchpad `maker_test.py`)

Reports 01, 11 and 15 say the money flows from takers to makers. Our earlier resting-order test counted a fill
whenever a later snapshot's ask reached our price, which is too harsh. This one uses Kalshi's public trade
records, on 628 finished Kalshi markets with a real price and a favourite at 50–95¢:
- a bid on the favourite side one cent above the best bid, so first in the queue;
- filled only when real trades sold into it, enough to cover a $250 order;
- Kalshi's maker fee charged on every fill (0.0175·p·(1−p)).

| Order life | Filled | Maker return | Same markets at the ask | Win rate, filled vs never filled |
|---|---|---|---|---|
| Never cancelled, 50–95¢ | 549/628 (87%) | −2.8% [−9.1, +3.5] | −7.3% [−13.2, −1.2] | 68% vs 97% |
| Never cancelled, 70–95¢ | 247/295 | +0.4% [−5.1, +6.2] | −3.0% [−8.3, +2.7] | 84% vs 100% |
| Cancelled after 6 h, 50–95¢ | 215/628 (34%) | −1.3% [−10.3, +6.8] | −5.7% [−14.2, +1.8] | 71% vs 71% |
| Cancelled after 6 h, 70–95¢ | 120/295 | +0.5% [−9.4, +7.2] | −3.1% [−12.5, +3.5] | 84% vs 89% |

Making instead of taking saves about 4–5 points, the spread plus the fee gap. A slow maker still only breaks even,
and the never-cancelled orders show adverse selection plainly: the orders that never filled would have won 97%.
Not built as a strategy. It may later lower the cost of a strategy that has an edge (for example `mention_no`).


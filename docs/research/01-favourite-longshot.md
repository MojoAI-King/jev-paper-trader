# 01: How mispriced are cheap and expensive contracts?

Researched 2026-10-09 for `docs/research/briefs/01-favourite-longshot.md`.

## Answer in five lines

1. Cheap contracts lose a lot and expensive ones gain a little. On Kalshi (2021 to April 2025, about 314,000 contract prices), takers lost about 72% at 1–10¢, 29% at 10–30¢, 9% at 30–50¢ and 2% at 50–70¢ after fees, and made roughly 0 to +1% at 70–99¢. Makers did 10 to 40 points better at the cheap end and made about +4% to +6% at 50–90¢.
2. Polymarket shows the same direction but much smaller numbers: about −4% at 1–10¢ and +0.6% to +1.2% at 70–100¢, before fees, averaged over trades. The result swings with how trades are weighted (cheap contracts lose anywhere from 19% to gaining 4%), and in sports the pattern disappears.
3. For a taker, buying favourites (or NO on cheap YES, which is the same trade) is at best break-even after Kalshi's fee curve: roughly +0.5% to +1% at 85–99¢ and about zero at 70–80¢ on 2021–25 data, and the bias weakened in 2025. Only makers earn it reliably, and makers who post orders on long shots get picked off.
4. Why it happens: people overrate small chances; traders with the most extreme beliefs take liquidity and pay a spread and fee that are proportionally biggest on cheap contracts; at long horizons, tying up money pushes prices toward 50¢. The bias is strongest in politics, crypto and long-dated markets and weakest in sports and finance. It has shrunk slightly on Kalshi, there are no trend numbers for Polymarket, and on racetracks it has lasted 50+ years.
5. Our own numbers match the literature closely. Keep the 30¢ floor, treat favourites as break-even rather than an edge, test betting only on the favourite's side, and don't expect resting orders to rescue us.

## Findings

### F1. On Kalshi, return rises steadily with price, and takers do much worse than makers

**The claim.** Buyers of cheap contracts lose most of their money, and buyers above about 70¢ make a small positive return. Takers lose more than makers at every price.

**The evidence.** Bürgi, Deng & Whelan, "Makers and Takers: The Economics of the Kalshi Prediction Market":
- Source: [January 2026 version](https://www.karlwhelan.com/Papers/Kalshi.pdf), also GWU CER WP 2026-001 and [CEPR DP20631](https://cepr.org/publications/dp20631).
- Sample: Kalshi from launch in 2021 to April 2025. 46,282 YES contracts in 12,403 events, giving 156,986 YES prices and 313,972 YES+NO prices.
- Filters: contracts needed at least $1,000 volume, at least 24 hours open and a final spread of 20¢ or less. Hourly crypto and index markets were excluded.
- Which prices count: the last trade on the closing day, plus the last trade at each 24-hour mark up to 10 days before close. Each snapshot counts equally, whatever its volume.
- Taker or maker: comes from Kalshi's own flag on each trade.
- Fees: takers paid 0.07·P·(1−P) per contract, rounded up. Makers paid nothing during this period.

The paper's headline averages are takers −31.46% and makers −9.64% ([p. 27](https://www.karlwhelan.com/Papers/Kalshi.pdf)). Makers who bought at 50¢ and above earned +2.6%, which is statistically significant but has a 33% standard deviation per contract (p. 40).

The paper prints no table of returns by price, only charts. The numbers below were read off its Figures 5 and 6 to about ±1 percentage point. Regrouped into our buckets, weighted by the paper's own counts, they reproduce its stated averages: −31.0% for takers against −31.46% stated, and −9.4% for makers against −9.64%.

**Table 1. Kalshi, return per dollar by price paid (best available source)**

| Bucket (paper's bins) | All buyers, taker fee only | Takers, after fee | Makers, no fee | Prices in bucket (all / takers / makers) |
|---|---|---|---|---|
| 1–10¢ | −55.8% | **−71.5%** | −33.9% | 106,209 / 60,024 / 46,185 |
| 10–30¢ (11–30) | −19.5% | **−29.0%** | −8.8% | 32,953 / 17,290 / 15,663 |
| 30–50¢ (31–50) | −5.2% | **−9.1%** | −1.0% | 17,248 / 8,884 / 8,364 |
| 50–70¢ (50–69) | +0.5% | **−2.4%** | +3.6% | 18,400 / 8,940 / 9,460 |
| 70–90¢ (70–89) | +3.0% | **+0.4%** | +5.6% | 32,953 / 15,663 / 17,290 |
| 90–99¢ | +1.1% | **+0.6%** | +1.8% | 106,209 / 46,185 / 60,024 |

How to read the table:
- Venue and period: Kalshi, 2021 to April 2025.
- Sample: counts are contract-price snapshots, not trades or dollars.
- Precision: values are read from the charts (±1 point) and regrouped by the researcher; the paper does not print them.
- Fees: maker returns exclude the maker fee Kalshi introduced after April 2025. The September 2025 version of the paper charged makers a fee too, which pulled maker returns at 70–89¢ down to about +4%. The rate it used was not verified.
- Significance: the paper calls post-fee returns above 70¢ "statistically significant, though small" (p. 17).
- An unresolved discrepancy: the text says contracts at 10¢ and under lose "over 60%", but the all-buyers chart shows about −56%. Only the takers' bar is clearly over 60%.

**Strength: strong.** It is a large sample, the taker/maker flag comes from the exchange, and fees are handled explicitly. It is still a working paper, and its sample stops before Kalshi's 2025 sports boom and before maker fees.

### F2. A 72-million-trade study of Kalshi finds the same pattern, but much smaller average losses

**The claim.** Weighting by trade instead of by daily snapshot keeps the shape (cheap contracts lose, takers lose to makers) but shrinks the averages about tenfold.

**The evidence.** Becker, "The Microstructure of Wealth Transfer in Prediction Markets" ([jbecker.dev, 18 Jan 2026](https://www.jbecker.dev/research/prediction-market-microstructure); an SSRN version is dated 1 Aug 2026).
- Sample: Kalshi from June 2021 to 25 Nov 2025. 72.1 million trades, $18.26 billion, resolved markets only. Returns are before fees.
- Calibration: 5¢ contracts won 4.18% of the time and 95¢ contracts won 95.83%. Every price below 20¢ underperformed and every price above 80¢ outperformed.
- Takers vs makers: takers averaged −1.12% per trade and makers +1.12%. At 1¢, takers won 0.43% of the time (−57%) and makers 1.57%. At 50¢, takers made −2.65% and makers +2.66%. Takers lost money at 80 of the 99 price levels.
- YES vs NO: a 1¢ YES had an expected value of −41%, against +23% for a 1¢ NO. NO beat YES at 69 of 99 prices.

The difference from F1 is mostly weighting. Bürgi gives each daily price equal weight, and a third of those prices are under 10¢. Becker's trades are dominated by 2025 sports at mid-range prices.

Our own "flat $100 on every finished market" test also weights each market equally, so **Bürgi is the closer comparison for our numbers.**

**Strength: moderate.** The sample is huge, but the author is an independent researcher, the work is not peer reviewed, and whether the averages are weighted by trade or by dollar is not verified.

### F3. On Polymarket the bias points the same way but is far smaller, and fragile

**The claim.** Cheap Polymarket contracts lose a few percent, and those above 70¢ gain about 1%, before fees. The long-shot loss depends heavily on weighting and is concentrated in a few large events. The small gain on favourites holds up better.

**The evidence.** Qin & Yang, "Polymarket-v1 Database" ([arXiv 2606.04217, June 2026](https://arxiv.org/html/2606.04217v1)).
- Sample: the full on-chain archive of Polymarket's first-generation exchange, 21 Nov 2022 to 28 Apr 2026. 1.20 billion trades, 1.3 million markets, $60.9 billion.
- Method: the mean return per trade by price decile (their Table 3), with no fees deducted.

**Table 2. Polymarket, return per dollar by price paid (comparison)**

| Bucket | Before fees (trade-weighted) | After today's taker fee, 4% rate (politics) | After today's taker fee, 7% rate (crypto) | Trades |
|---|---|---|---|---|
| 0–10¢ (avg 5.2¢) | −4.4% | −8.2% | −11.1% | 34.9M |
| 10–20¢ | −1.3% | −4.6% | −7.2% | 17.7M |
| 20–30¢ | −1.3% | −4.3% | −6.5% | 19.5M |
| 30–40¢ | −0.1% | −2.7% | −4.7% | 24.4M |
| 40–50¢ | +0.6% | −1.6% | −3.3% | 35.4M |
| 50–60¢ | +0.3% | −1.5% | −2.9% | 27.8M |
| 60–70¢ | +0.7% | −0.7% | −1.7% | 19.9M |
| 70–80¢ | +1.0% | 0.0% | −0.7% | 17.2M |
| 80–90¢ | +1.2% | +0.6% | +0.1% | 14.4M |
| 90–100¢ (avg 95.2¢) | +0.6% | +0.4% | +0.3% | 27.2M |

How the columns were built:
- The before-fee column is the paper's dollars-per-contract figure divided by the bucket's average price (researcher's arithmetic).
- The after-fee columns subtract the current taker fee, feeRate × (1−p), at the bucket's average price. That is my arithmetic, and it treats every trade as a taker, which overstates the cost for maker trades.
- Almost all of these trades happened before Polymarket charged fees (crypto from January 2026, sports from February, most other categories from March, per the paper's Table 7).
- No confidence intervals are given.

Cardozo & Rivero-Wildemauwe, "The Favorite-Longshot Bias in Prediction Markets: Evidence from Polymarket" ([arXiv 2609.12878, Sept 2026](https://arxiv.org/html/2609.12878v1)).
- Sample: 560.9 million purchases, $22.49 billion, in 591,187 markets resolved between Nov 2022 and Mar 2026. Returns are before fees.
- Long shots (below 10¢) lose −6.30% [95% CI −8.38, −4.22] with equal weight per market and −19.35% [−46.99, +8.30] pooled by dollar, but *gain* +4.09% when weighted by event.
- The pooled long-shot loss is not statistically robust (p = 0.184), and dropping the ten largest events cuts it to −10.6%.
- Favourites (90¢ and up) gain +0.28% [0.24, 0.31] per market, +0.83% pooled and +0.39% per event, and that gain is robust (p = 0.001).
- Buyers who posted a resting order: long shots −3.50%, favourites +0.64%.
- Buyers who accepted someone else's offer (roughly takers): long shots −31.17%, and favourites **−0.46% [−0.52, −0.41]** per market, but +0.88% pooled.

**Strength: moderate.** The data are large, but the papers are recent working papers, cover mostly the fee-free era, and their conclusions depend on weighting. A smaller study of 2,946 high-volume markets, snapshotted 1–30 days before resolution, found no long-shot overpricing at all ([honest-odds, GitHub, data to Sept 2026](https://github.com/CH4RL3I/honest-odds); anecdotal).

### F4. Kalshi's fee curve makes long shots expensive and favourites cheap, but small orders pay a minimum

**The claim.** The Kalshi taker fee is 0.07 × contracts × P × (1−P), rounded up to the next cent per order. Per dollar staked that is about 0.07 × (1−P), so it ranges from about 6–7% of the stake at 5–10¢ down to 0.36% at 95¢. The round-up costs a 1-contract order 1–2¢ whatever the price, which on a 98¢ contract is half the possible profit.

**The evidence.**
- Formula: [Kalshi fee schedule PDF](https://kalshi.com/docs/kalshi-fee-schedule.pdf), as extracted by a search engine; direct fetches were blocked on 2026-10-09.
- Taker-only fees before April 2025: [Bürgi et al., p. 6](https://www.karlwhelan.com/Papers/Kalshi.pdf).
- A maker fee of 0.0175 × C × P × (1−P) applies on "certain markets" since 2025. Which markets is not verified.
- Kalshi's help page (dated 19 Apr 2026) confirms maker fees exist "in some cases" ([help.kalshi.com](https://help.kalshi.com/trading/fees)).
- S&P 500 and Nasdaq-100 series use 0.035, per a [2022 CFTC filing](https://www.cftc.gov/sites/default/files/filings/orgrules/22/09/rule091222kexdcm003.pdf); whether that is still current is not verified.
- Polymarket's live docs, read 2026-10-09: the taker fee is C × feeRate × p × (1−p), with feeRate 0.04–0.07 depending on category (0 for geopolitics). Makers pay nothing and get a 15–25% rebate ([docs.polymarket.com](https://docs.polymarket.com/trading/fees)).

**Table 3. Fee as % of stake, and the win rate needed to break even (my arithmetic from the formulas above)**

| Price | Kalshi taker, 1 contract | Kalshi taker, 100 contracts | Kalshi maker, 100 contracts | Break-even win rate, taker 100-lot | Break-even, taker 1-lot | Our trader's own cost model (fee + 1¢ slippage), break-even | Polymarket taker, 4% / 7% rate |
|---|---|---|---|---|---|---|---|
| 5¢ | 20.0% | 6.80% | 1.80% | 5.34% | 6.0% | 6.33% | 3.80% / 6.65% |
| 10¢ | 10.0% | 6.30% | 1.60% | 10.63% | 11.0% | 11.63% | 3.60% / 6.30% |
| 20¢ | 10.0% | 5.60% | 1.40% | 21.12% | 22.0% | 22.12% | 3.20% / 5.60% |
| 30¢ | 6.67% | 4.90% | 1.23% | 31.47% | 32.0% | 32.47% | 2.80% / 4.90% |
| 50¢ | 4.00% | 3.50% | 0.88% | 51.75% | 52.0% | 52.75% | 2.00% / 3.50% |
| 70¢ | 2.86% | 2.10% | 0.53% | 71.47% | 72.0% | 72.47% | 1.20% / 2.10% |
| 80¢ | 2.50% | 1.40% | 0.35% | 81.12% | 82.0% | 82.12% | 0.80% / 1.40% |
| 90¢ | 1.11% | 0.70% | 0.18% | 90.63% | 91.0% | 91.63% | 0.40% / 0.70% |
| 95¢ | 1.05% | 0.36% | 0.09% | 95.34% | 96.0% | 96.33% | 0.20% / 0.35% |
| 98¢ | 1.02% | 0.14% | 0.04% | 98.14% | 99.0% | 99.14% | 0.08% / 0.14% |

The "own cost model" column follows `papertrade/engine.py`, where cost = ask + 0.07·P·(1−P) + $0.01 slippage on Kalshi. On Polymarket the code charges a fee of 0 (`policy.json` `fees.polymarket_per_contract`), which has been out of date since Polymarket's January–March 2026 fee rollout.

The fee is not the whole cost. A taker pays the spread on top, and the returns in Tables 1 and 2 already include it because they are measured at real trade prices.

**Strength: strong for the formulas, moderate for the current coefficients.** The live Kalshi schedule (a reported 7 July 2026 version) could not be read.

### F5. Buying favourites, or NO on cheap YES, is thin for takers and reliable only for makers

**The claim.** Buying NO on a 5¢ YES is a 95¢ purchase. The fee is identical, and Table 1's 90–99¢ row is that trade.

On Kalshi's 2021–April 2025 data, a taker after fees made about +0.6% at 90–99¢ and +0.4% at 70–89¢ (Table 1). The paper's fitted line gives after-fee taker returns of:

| Price | After-fee taker return (fitted line) |
|---|---|
| 75¢ | −0.66% |
| 85¢ | +0.30% |
| 90¢ | +0.77% |
| 95¢ | +1.21% |

These come from the researcher's arithmetic on [Bürgi et al., Table 4](https://www.karlwhelan.com/Papers/Kalshi.pdf): profit = −1.736 + 0.034 × price, in cents, with a 100-lot fee. A straight line overstates the edge near 99¢.

Makers made +3.6% to +6.2% at 50–89¢. On Polymarket before fees, takers' favourite purchases were −0.46% per market and makers' +0.64% (F3).

**What makes it fragile.** At entry price P, one loss costs as much as P/(1−P) wins: 19 wins at 95¢, 49 at 98¢. An edge of +0.3% to +1.7% disappears if the true win rate is 0.3 to 1.5 points lower than measured, which a single disputed resolution can do (researcher's arithmetic).

The traders on Polymarket most inclined to buy favourites "earn less than others" ([Cardozo & Rivero-Wildemauwe](https://arxiv.org/html/2609.12878v1)). No practitioner "bond strategy" (buying at 95–99¢) has a published track record with sample, dates and net returns; the guides that promote it are anecdotal ([startpolymarket.com](https://startpolymarket.com/strategies/bonding/), affiliate links).

**Strength: moderate.** Taker-only returns at 90–99¢ exist only in a chart (±1 point), and nothing covers Kalshi after April 2025.

### F6. Makers beat takers on every venue studied, but makers posting on long shots get picked off

**The claim.** The bias shows up mostly as a transfer from takers to makers, and that transfer is concentrated in takers buying long shots. The exception is makers who post bids on long shots: they lose heavily, because their orders fill just as news turns against them.

**The evidence.**
- **Kalshi:** makers −9.64% against takers −31.46%. Makers' purchases at 10¢ or less still lost money with statistical significance on 5 of 6 days shown, and on the closing day their losses on cheap contracts matched takers' ([Bürgi et al., pp. 27–30](https://www.karlwhelan.com/Papers/Kalshi.pdf)).
- **Betfair soccer, 2022–24:** 152,102 matches and 902,568 bets. Takers made −2.5% after commission and makers +0.6% (t = 11.8). The maker figure has a 198% standard deviation ([Whelan, Jan 2026](https://www.karlwhelan.com/Papers/Betfair.pdf)).
- **Polymarket:** long shots bought with a resting order were *up* 4.85% after 5 minutes, 6.96% after an hour and 6.62% after a day, then **−36.27%** at resolution. Favourites bought with a resting order made +1.94% at resolution ([Cardozo & Rivero-Wildemauwe, Table 18](https://arxiv.org/html/2609.12878v1)).
- **Old TradeSports:** limit orders "often execute against traders who exploit the well-known favorite-longshot bias" ([Tetlock 2008](https://drupalgsb-test.paas.cc.columbia.edu/sites/default/files-efs/pubfiles/3098/Tetlock_SSRN_Liquidity_and_Efficiency.pdf)).
- Bürgi et al. note that makers "must also be willing to cancel those orders if new evidence emerges" (p. 27).

**Strength: strong** for makers beating takers. **Moderate** for the adverse-selection pattern on long shots. No study measures how often resting bids at 90–99¢ get picked off.

### F7. The bias differs by market type: strongest in politics and crypto, weakest in sports and finance

**The claim.** Every category on Kalshi is biased, but by different amounts. Polymarket sports shows no favourite-longshot pattern.

**The evidence.**
- **Kalshi, Bürgi et al., Table 8.** This is a regression of profit on price, before fees, on closing and earlier prices from 2021 to April 2025. A larger slope means a steeper bias.

| Category | Slope | Significance |
|---|---|---|
| Crypto | 0.058 | significant (n = 8,150) |
| Other | 0.053 | significant |
| Economics | 0.034 | significant |
| Financials | 0.032 | significant |
| Climate & weather | 0.031 | significant |
| Politics | 0.022 | **not** significant (n = 26,819) |
| Entertainment | 0.020 | **not** significant |

  The sample has no separate sports column, because Kalshi only added sports in January 2025 ([p. 24](https://www.karlwhelan.com/Papers/Kalshi.pdf)).
- **Kalshi, Becker** (to Nov 2025, before fees). The maker-minus-taker gap ([jbecker.dev](https://www.jbecker.dev/research/prediction-market-microstructure)):

| Category | Maker-minus-taker gap | Trades |
|---|---|---|
| Finance | 0.17 points | 4.4M |
| Politics | 1.02 points | 4.9M |
| Sports | 2.23 points | 43.6M |
| Weather | 2.57 points | 4.4M |
| Crypto | 2.69 points | 6.7M |
| Entertainment | 4.79 points | 1.5M |
| Media | 7.28 points | 0.6M |
| World events | 7.32 points | 0.2M |

- **Polymarket, Cardozo & Rivero-Wildemauwe** (before fees, equal weight per market):

| Category | Long shots under 10¢ | Favourites 90¢+ |
|---|---|---|
| Crypto | −14.8% | +0.64% |
| Politics | −16.3% | +1.04% |
| Sports | **+2.4%** | **−0.23%** |
| Weather | −25.2% | +0.50% |
| Finance | −2.6% | +0.09% |

  Pooled by dollar, the sports long shots made +18.1% ([arXiv](https://arxiv.org/html/2609.12878v1)).
- **Calibration slopes** (above 1 means prices are too close to 50%):
  - Le ([arXiv 2602.19520, Aug 2026](https://arxiv.org/pdf/2602.19520)): 64.7M Kalshi trades from Jul 2021 to Dec 2025, and 135.6M Polymarket trades. Polymarket's average slopes are politics 1.45, sports 1.06 and crypto 1.06. On Kalshi, politics is the most compressed: a 70¢ political contract a week out maps to about 83%.
  - Walker (Princeton senior thesis, 188,509 Polymarket markets, Nov 2022 to Dec 2025): overall slope 1.112, with the bias present in every domain ([thesis page](https://theses-dissertations.princeton.edu/entities/publication/d5708372-5ea3-4252-b669-7f9cee07387c)).

There is a conflict on politics. In Bürgi's return regression its slope is the weakest; in Le's calibration slopes it is the most compressed. The two use different periods, methods and price ranges, and the conflict is not resolved.

**Strength: moderate.** The direction is consistent across sources, but no study gives returns by price bucket within each category.

### F8. Time to resolution matters in two opposite ways

**The claim.** Far from resolution, prices are more compressed toward 50¢ (long shots too expensive, favourites too cheap). Very close to the end of live sports, long shots are badly overpriced (the "Yogi Berra" effect, named for "it ain't over till it's over"). Short-dated weather prices are too *extreme*, the reverse of the usual bias.

**The evidence.**
- **Le, Kalshi Table 4.** Slopes by domain and time left ([arXiv](https://arxiv.org/pdf/2602.19520)). The average slope rises from 0.99 at 0–1 hours to 1.32 at a month or more.

| Domain | 0–1 hours left | A month or more left |
|---|---|---|
| Politics | 1.34 | 1.73 |
| Sports | 1.10 | 1.74 |
| Weather | **0.69** (too extreme) | 1.37 |

- **Bürgi et al., Table 5.** The bias is significant at every horizon from 0 to 10 days. Losses on cheap contracts are, if anything, largest on the closing day ([p. 22](https://www.karlwhelan.com/Papers/Kalshi.pdf)).
- **Polymarket, Cardozo.** Long shots bought within a day of the scheduled close lose 13.1% with equal weight per market ([Appendix Table 14](https://arxiv.org/html/2609.12878v1)).
- **Older markets:**
  - Intrade, 1,787 markets from 2002–07: a 20¢ price won 15.3% of the time and an 80¢ price won 87.4%. The bias was stronger beyond 100 days and close to calibrated near expiry ([Page & Clemen 2013](https://people.duke.edu/~clemen/bio/Published%20Papers/45.PredictionMarkets-Page&Clemen-EJ-2013.pdf)).
  - Iowa Electronic Markets: no bias except at long horizons ([Berg & Rietz 2019](https://iemweb.biz.uiowa.edu/?p=397)).
  - Betfair in-play soccer: takers backing bottom-decile long shots late in the match lose "about 70%" ([Whelan 2026](https://www.karlwhelan.com/Papers/Betfair.pdf)).
  - Kalshi sports moneylines, Mar–May 2026, about 23M trades: well calibrated 30–240 minutes before expiry, but 10–40¢ contracts in the last ten minutes "resolve favorably almost never" ([Moshrefi, arXiv 2607.14430](https://arxiv.org/pdf/2607.14430)).

**Strength: moderate.**

### F9. The venues rank roughly PredictIt ≥ Kalshi > Polymarket, and exchanges show the least bias before events

**The claim.** Fee-heavy, capped or thin markets show more bias. Deep exchanges with no house margin show almost none before the event.

**The evidence.**
- **PredictIt (2016–22, $850 cap):** "much larger pricing biases than in previously studied prediction markets" ([Zitzewitz, NBER w35845, Oct 2026](https://www.nber.org/papers/w35845); abstract only, no bucket numbers).
- **Betfair:** last pre-kick-off soccer prices are unbiased across 200,622 matches in 2022–24 ([Whelan 2026](https://www.karlwhelan.com/Papers/Betfair.pdf)). Betfair odds showed no bias across 799 UK races, while bookmaker odds did ([Smith, Paton & Vaughan Williams 2006](https://ideas.repec.org/a/bla/econom/v73y2006i292p673-689.html)).
- **Iowa Electronic Markets:** no bias ([Berg & Rietz 2019](https://iemweb.biz.uiowa.edu/?p=397)).
- **Kalshi vs Polymarket:** Kalshi's −56% for all buyers at 1–10¢ against Polymarket's −4% to −6% is partly real and partly the weighting difference between snapshots and trades.

**Strength: weak to moderate.** The studies are not measured the same way.

### F10. Older betting markets: the same shape for 75 years, and heavy favourites still don't pay

**The claim.** On racetracks, return falls steadily as odds lengthen. Backing every favourite loses only a little, and nothing simple is profitable.

**The evidence.** Snowberg & Wolfers (JPE 2010; [NBER w15923](https://www.nber.org/system/files/working_papers/w15923/w15923.pdf)) studied all 6.4 million US horse starts from 1992–2001:

| Bet | Return per dollar |
|---|---|
| Always the favourite | −5.5% |
| 4/1 to 9/1 shots | about −18% |
| Random bet | −23% |
| 100/1 or longer | about −61% |

- The same pattern holds in Australia (2.7M starts) and Britain (380,000 starts).
- The bias "has been stable since first noted in Griffith (1949)", whose sample was 1,386 races in 1947.
- The authors say the claim that extreme favourites earn positive returns (Thaler & Ziemba 1988) "is not true in any of our datasets".
- The exceptions are Hong Kong and Japan: no bias in about 7,000 races (Busche & Hall 1988; Busche 1994).
- Two-outcome sports markets are less consistent. Baseball moneylines once showed a reversed bias that later corrections weakened ([Woodland & Woodland 1994](https://ideas.repec.org/a/bla/jfinan/v49y1994i1p269-79.html)).

**Strength: strong.** Racing is the most-studied case. The −5.5% for favourites is after a track take of roughly 15–20%; that take figure is not verified.

### F11. Why the bias exists: people overweight small chances, and costs and slow money keep it alive

**The claim.** The best-supported cause is that people overestimate small probabilities. On exchanges this works through traders with extreme beliefs sorting into taker roles and paying a spread and fee that are proportionally largest on cheap contracts. At long horizons, the cost of tying up money also pushes prices toward 50¢. Risk-loving bettors and insider trading have weaker support.

**The evidence.**
- **Misperception vs risk-love.** Snowberg & Wolfers separate the two using exotic bets (exactas, quinellas and trifectas). Misperception fits better in 54–71% of cases, and "the misperceptions class strongly dominates" ([NBER w15923](https://www.nber.org/system/files/working_papers/w15923/w15923.pdf)).
- **Kalshi model.** Bürgi et al. fit a model of disagreeing traders choosing between taker and maker roles. It fits Kalshi only if people overestimate small probabilities by a modest amount (β ≈ 0.09, range 0.06–0.12). "None of the calibrations with β = 0 fit well", and unbiased-but-disagreeing traders predict the opposite pattern. The paper also cites the fee formula and the spread both being "larger as a fraction of price for cheap contracts" ([pp. 35–41](https://www.karlwhelan.com/Papers/Kalshi.pdf)).
- **Why it isn't traded away (the authors' untested views):** thin books (the top tenth of markets averaged $526,245 in volume), high risk per bet, and traders not knowing about the pattern.
- **Takers' preference for YES.** Becker attributes makers' gains to takers preferring YES long shots (an "optimism tax"), not to makers forecasting better. This is the author's interpretation ([jbecker.dev](https://www.jbecker.dev/research/prediction-market-microstructure)).
- **Discounting.** Page & Clemen model time discounting as the cause of long-horizon compression on Intrade ([Economic Journal 2013](https://people.duke.edu/~clemen/bio/Published%20Papers/45.PredictionMarkets-Page&Clemen-EJ-2013.pdf)).

**Strength: strong** for racing, **moderate** for Kalshi (one model calibration), and **weak** for "attention" and entertainment explanations, for which no direct test was found.

### F12. Has it shrunk as volume grew? A little on Kalshi, unknown on Polymarket

**The claim.** On Kalshi the price bias weakened in early 2025, but the transfer from takers to makers grew after the 2024 election. No numbers by year exist for Polymarket.

**The evidence.**
- **Bürgi et al., Table 9** (slope by year; [p. 25](https://www.karlwhelan.com/Papers/Kalshi.pdf)). The authors call this "some evidence of a weakening".

| Year | Slope | Prices |
|---|---|---|
| 2021 | 0.041 | 3,855 |
| 2022 | 0.023 | 24,913 |
| 2023 | 0.036 | 23,559 |
| 2024 | 0.048 | 53,338 |
| 2025 (Jan–Apr) | **0.021** (significant only at 10%) | 51,321 |

- **Becker:** takers averaged +2.0% per trade from 2021 to 2023. After the 2024 election the gap flipped to +2.5 points in makers' favour, while quarterly volume went from $30M (Q3 2024) to $820M (Q4 2024) ([jbecker.dev](https://www.jbecker.dev/research/prediction-market-microstructure)).
- **Polymarket:** quarterly returns appear only in a chart (Cardozo, Figure 6).
- **Racing:** stable from 1947 to 2004 (Snowberg & Wolfers). UK bookmaker bias fell after 2000, when betting exchanges arrived ([Smith & Vaughan Williams 2010](https://ideas.repec.org/a/eee/intfor/v26yi3p543-550.html)).
- **Liquidity:** more liquidity did not reduce price errors on TradeSports ([Tetlock 2008](https://drupalgsb-test.paas.cc.columbia.edu/sites/default/files-efs/pubfiles/3098/Tetlock_SSRN_Liquidity_and_Efficiency.pdf)).

**Strength: weak.** There is one shortened 2025 data point, and nothing on Kalshi after November 2025 except sports moneylines.

## What it means for our trader

### Our numbers against the literature

| Our measurement (2026-10-09) | Closest published figure | Verdict |
|---|---|---|
| Our bets under 30¢: 4 won of 78 when the prices implied 9.3, a **−78%** return | Kalshi takers: −71.5% at 1–10¢, −29.0% at 11–30¢. Polymarket before fees: −4.4% / −1.3% | Same direction. Ours is worse than Kalshi's 11–30¢ takers, which fits our forecasts picking the long shot exactly when they disagreed with a price that was right. 78 bets is a small sample. |
| Our bets at 30–50¢: **−7.0%** (73 bets) | Kalshi takers −9.1%, makers −1.0%. Polymarket about 0 before fees, −2% to −5% after today's taker fee | Matches the Kalshi taker figure. |
| Our bets at 50–70¢: **−0.4%** (81 bets) | Kalshi takers −2.4%, makers +3.6% | Matches. |
| Our bets at 70¢ and up: **−21.6%** (19 bets) | Kalshi takers +0.4% (70–89¢), +0.6% (90–99¢) | Doesn't match, but 19 bets can't tell us anything: at these prices a single loss costs a whole stake. |
| Every favourite at the ask: **−2.8% ± 1.7%** (1,133 markets) | Kalshi takers, weighted like ours (each price snapshot counts equally, not each trade): −2.4% at 50–70¢, about +0.5% above 70¢ | Matches. A taker buying favourites loses about what trading costs. |
| Favourites at 70–95¢: **−1.5% ± 1.8%** (544 markets) | Kalshi takers +0.4% to +0.6% after fees. Polymarket after today's fee about 0% to +0.6% | The literature sits at or just above the top of our range. Break-even is the honest reading. |
| Every underdog at the ask: **−31.9% ± 4.6%** | Kalshi takers −72% to −9% depending on price | Matches in direction and size. |
| Weight of 1.35 on the market's log-odds | Polymarket overall 1.06–1.11; politics 1.45. Kalshi from 0.99 (under an hour left) to 1.32 (a month or more), and up to 1.83 for politics a week to a month out | At the high end of the published range, like politics or month-ahead markets. Two caveats follow below the table. |
| Resting orders with a strict fill rule: **−16% to −31%** | Makers who actually got filled: Kalshi +3.6% to +6.2% at 50–89¢. But Polymarket long-shot bids were −36% at resolution after early gains | Our result matches the adverse-selection half of the literature. See change 6. |

Two caveats on the 1.35 weight:
- In `docs/REBUILD_SCOPE.md` it comes from the blend fit, estimated alongside our forecasts, so it is not a clean measure of the price alone.
- Taken literally, it says an 80¢ favourite wins about 86.7% of the time. That would be roughly +8% before costs, yet we measure −1.5% at the ask for 70–95¢ (my arithmetic, assuming no intercept). Either the 1.35 overstates the bias in our sample, or the spread and fees eat it. Test T3 below settles which.

### Changes, ranked

1. **Keep `min_ask` at 0.30 on every strategy, and never let the loop lower it.**
   - Every source agrees takers lose 29% to 72% below 30¢ on Kalshi, and we lost 78% there.
   - Expected effect: avoids the single worst bucket.
   - Confidence: high.
   - How: it is a rule (`min_ask`), already set, and the coach prompt already warns against lowering it. No code change.

2. **Test raising `min_ask` to about 0.50, so a strategy only buys the side the market already favours.**
   - Our 30–50¢ bets lost 7.0%, and our bets *against* the market's favourite at 30–50¢ lost 35% (55 bets). Kalshi takers lost 9.1% at 31–50¢ and 2.4% at 50–70¢.
   - Expected effect: losses shrink from about −7% toward −2% to 0% on those bets. This cuts losses; it does not create profit.
   - Confidence: moderate.
   - How: it is a rule the loop can set. Run it as a challenger with a row in `docs/EXPERIMENTS.md` first, not as a change to `main`.

3. **Treat buying favourites as break-even at best for a taker, and don't build a "buy every favourite" or 95–99¢ "bond" strategy expecting profit.**
   - The evidence: +0.4% to +1.2% after fees on Kalshi in 2021–25, with the bias weakening in 2025; Polymarket takers −0.46% even before fees; our own −1.5% ± 1.8%; and one loss at 95¢ wipes out 19 wins.
   - Expected effect: avoids wasting a strategy slot.
   - Confidence: moderate to high.
   - If anything, run it as a yardstick, labelled as such. `market_filters.max_price` 0.95 already keeps the trader out of the 95–99¢ range.

4. **Use the market price, corrected for this bias, as the baseline forecast, and bet only where a specific, checkable reason says that baseline is wrong.**
   - The correction is a calibration slope fitted on our history by category and time to resolution. The literature says it should be largest for politics and long horizons, about 1.0 for sports and finance, and below 1 for short-dated weather.
   - Expected effect: a small improvement in Brier score over the raw price. A low chance of profit on its own, because the correction is a few points and our costs are about 8.4%.
   - Confidence: moderate on the Brier gain, low on profit.
   - How: a code change, so it needs Joey's OK. It overlaps with brief 05.

5. **Filter by category and horizon only after our own data confirms the literature.**
   - The literature says the favourite edge, where it exists, is biggest in politics, crypto and month-ahead markets.
   - It says there is no favourite edge in Polymarket sports, and that short-dated weather leans the other way: there the cheap side is, if anything, *under*priced.
   - Expected effect: unknown until tested, probably a few points either way.
   - Confidence: low.
   - How: `skip_categories` is a rule the loop can set. `days_ahead` is in `policy.json` for Joey to change.

6. **Re-test resting orders only in a narrow form, if at all.**
   - The form: bids on the *favourite* side at 70–95¢ (the same as offering to sell the long shot), never on long shots, scored with the strict fill rule and with how the price moved after each fill.
   - The literature's maker profits are real but go to makers who cancel when news breaks. An hourly cycle can't do that, so our −16% to −31% is what the literature predicts for a slow maker.
   - Expected effect: probably still negative. Worth one honest backtest, not a live strategy.
   - Confidence: low.
   - How: a code change (fill simulation, brief 11), which needs Joey's OK.

7. **Pass this to brief 10: the trader's Polymarket fee is set to zero.**
   - `fees.polymarket_per_contract` is 0.0, but Polymarket has charged takers 0.04–0.07 × p × (1−p) since January–March 2026: 2.0–3.5% of the stake at 50¢. The Kalshi fee in the code also skips the per-order round-up.
   - Expected effect: every Polymarket backtest and paper result is flattered by 1 to 3.5 points at mid prices.
   - Confidence: high that the fee exists.
   - How: changing the formula is a code change, which needs Joey's OK.

None of this points toward real-money trading. The best documented edge (makers at 50–90¢, +2.6% on average with a 33% standard deviation per bet) is too thin and too fragile for an hourly paper trader to capture.

## How to test it on our history

All of these use the roughly 1,133 finished markets. The common rules:
- Score only real-priced snapshots (spread 10¢ or less).
- Treat each market as two possible purchases (YES at the YES ask, NO at the NO ask), so cheap and expensive sides are mirror images.
- Charge the actual fee curve: Kalshi 0.07 × C × P × (1−P), rounded up per order at our real order size. On Polymarket, charge today's category rate on markets traded after that category's fee started, and zero before.
- Report n, wins, the wins the price implied, the return, and a ± range from a bootstrap that resamples whole events, because markets in the same event share an outcome.
- No conclusion from a bucket with fewer than about 200 purchases.

**T1. Return by price bucket at the ask, at first look.**
- What to compute: the buckets 1–10, 10–30, 30–50, 50–70, 70–90 and 90–99¢, before and after fees, for all markets and separately for our actual bets. Then repeat at the snapshots nearest 24 hours, 6 hours and 1 hour before close.
- Confirms the literature: returns rise with price, and 1–30¢ is strongly negative at every snapshot.
- Kills "favourites are break-even": 70–90¢ or 90–99¢ comes out positive by more than twice its ± after fees. That would justify pre-registering a favourite strategy.
- Kills "the bias grows with horizon" for our markets: the first-look snapshot is no more compressed than the 1-hour snapshot.

**T2. The same table by category (sports, crypto, politics, weather, economics/finance, other), by time to resolution (under 1 day, 1–7 days, 7–30 days) and by venue.**
- Confirms: the long-shot loss is biggest in politics and crypto and at 7–30 days; sports is about flat; short-dated weather is reversed.
- Kills change 5: no category differs from the pooled result by more than its ±.

**T3. The calibration slope from the price alone.**
- What to compute: a logistic regression of outcome on the log-odds of the mid price, and separately of the ask, with an intercept and confidence intervals that resample events. Overall, then by category, horizon and venue.
- Then check whether the slope's implied return in each bucket matches the realized return in T1.
- Confirms the 1.35: the overall slope's interval stays above 1, and the politics or long-horizon slopes are the largest.
- Kills it: the interval includes 1, or the implied favourite returns don't show up at the ask. That would mean the spread eats the bias, and change 4 is about forecasting accuracy only, not profit.

**T4. Favourite-buying net of the real fee curve.**
- What to compute: the flat-$100 "always the favourite" and "favourites 70–95¢" tests from REBUILD_SCOPE, repeated with the corrected fees (rounded-up Kalshi fees, real Polymarket fees) and split by venue.
- Confirms change 3: the result stays at or below zero within its ±.
- Changes the conclusion: the Kalshi 85–95¢ subset is positive by more than twice its ±. Pre-register that subset as a challenger, nothing more.

**T5. Our bets against the market's own baseline in the same bucket.**
- What to compute: for each settled bet, its return minus the T1 all-market return in the same bucket and venue. This separates the price bias from how well our forecasts pick bets within a bucket.
- Confirms "our forecasts subtract value": negative within buckets, especially at 30–50¢ against the favourite.
- Kills it: within-bucket differences are zero or positive.

**T6. Testing a `min_ask` of 0.50 on past bets.**
- What to compute: re-run each strategy's settled bets keeping only those at 50¢ or more, and report the return with its ±.
- Confirms change 2: losses are clearly smaller than with the 0.30 floor, measured in standard errors.
- Kills it: no difference within the ±.

**T7. Resting orders, narrow form.**
- What to compute: simulated resting bids on the favourite side at 70–95¢ only, with the strict fill rule. Report the price move 1, 6 and 24 hours after each fill and the return at resolution, next to the taker return in the same bucket.
- Confirms change 6 is worth building: filled orders beat the taker by more than their ±.
- Kills it: they are at or below the taker figure, or the price usually moves against us right after a fill (the same adverse selection as before).

Our history cannot test whether the bias is shrinking over time. Two weeks is too short.

## Data sources

- **Kalshi trade data (Becker's dataset):** [github.com/jon-becker/prediction-market-analysis](https://github.com/jon-becker/prediction-market-analysis). Free. Kalshi trades June 2021 to Nov 2025, 72.1M trades, said to include which side was the taker. Size and exact fields not verified.
- **Le's calibration code:** github.com/namanhzz/prediction-market-calibration, as stated in [arXiv 2602.19520](https://arxiv.org/pdf/2602.19520). Free. Code for calibration slopes by domain, horizon and trade size on Kalshi and Polymarket. Not opened.
- **Polymarket-v1 database:** [Qin & Yang, arXiv 2606.04217](https://arxiv.org/html/2606.04217v1). The full on-chain trade archive from Nov 2022 to Apr 2026, 1.2 billion trades. Whether and how it can be downloaded is not verified.
- **honest-odds:** [github.com/CH4RL3I/honest-odds](https://github.com/CH4RL3I/honest-odds). Free. A snapshot calibration of 2,946 high-volume Polymarket markets, with code. Anecdotal quality.
- **Polymarket fee docs:** [docs.polymarket.com/trading/fees](https://docs.polymarket.com/trading/fees). Free. The current category fee rates. The page carries no date stamp.
- **Kalshi fee schedule:** [kalshi.com/docs/kalshi-fee-schedule.pdf](https://kalshi.com/docs/kalshi-fee-schedule.pdf). Free, but it blocked automated fetches on 2026-10-09. The authoritative taker and maker coefficients, and which series carry maker fees.

## Not verified

- **Kalshi's current fees (as of Oct 2026):** the coefficients (0.07 taker, 0.0175 maker, 0.035 for S&P/Nasdaq series), which series carry maker fees, whether event contracts now have volume tiers, and the contents of a reported 7 July 2026 schedule. The live schedule could not be fetched.
- **Kalshi returns after April 2025, by price bucket:** none found, for makers or takers, and none net of maker fees.
- **Bürgi et al.:**
  - All bucket figures were read from charts (±1 point), not printed.
  - The "over 60%" text and the −56% chart value are not reconciled.
  - The July 2025 UCD version was not read.
  - The VoxEU column summarising the paper was not read.
- **Becker:** whether the ±1.12% averages are weighted by trade or by dollar, and how fees were treated in the category table.
- **Polymarket:**
  - The effective dates of fees by category beyond the month level, and the date today's rates took effect.
  - No yearly or before/after-2024 bias estimates exist in readable text.
  - No returns by price bucket within each category.
- **Papers seen only second-hand or not at all:**
  - Reichenbach & Walther (SSRN, blocked).
  - Gómez-Cram et al.: only a news summary was read.
  - Bartlett & O'Hara on adverse selection on Kalshi.
  - Akey et al.
  - Yurchyna on composition shift.
  - Zitzewitz's PredictIt numbers by price: abstract only.
- **Older studies:** the Thaler & Ziemba (1988) table by odds band, the racetrack take, sample periods for Ali (1977) and Jullien & Salanié (2000), and the authorship of the TradeSports NFL point-spread study.
- **Kalshi's current interest rate on balances** (3.25% or 4.05% in different help pages). It matters for whether locking up money in long-dated favourites costs anything.
- **Anecdotal claims not checked:** Hacking the Markets' "+2.5% makers", SimpleFunctions' "bias is reversed", and the claims on sportsgameodds.com of no bias in Fed and rate markets.
- **Our own 1.35 weight:** whether it comes from a price-only fit or the blend fit with our forecasts (REBUILD_SCOPE presents it alongside the blend weights), and whether our "±" figures are one standard error or a 95% interval.

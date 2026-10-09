# 08: Pricing economic-data and Fed markets

Researched 2026-10-09 for `docs/research/briefs/08-economic-release-markets.md`.

## Answer in five lines

1. **Kalshi's prices for these markets are already as good as the professional benchmarks, or slightly better.** Over 2022 to mid-2025, the Federal Reserve Board's own study found Kalshi's prices beat the Bloomberg consensus on headline CPI on release day (error 0.063–0.069 against 0.081 points) and tied it on core CPI and unemployment. On Fed decisions they tied or beat fed funds futures; the only difference was one meeting. Studies from 2002–2005 of a market on data releases found the same, and they found its probabilities for each outcome bin well calibrated.
2. **The free inputs a model would use don't beat the consensus forecast.** The Atlanta Fed says its GDPNow is not shown to beat professional forecasters (its error is 1.17 points, typical size measured as RMSE, over 56 quarters). The Cleveland Fed inflation nowcast beats surveys on headline inflation but not on core. Correcting the consensus for its known biases doesn't work in real time. FedWatch is a market price, so it is only a check on Kalshi, not an edge over it.
3. **To price a bin, centre a fat-tailed curve on the consensus or nowcast, then account for Kalshi's rounding.** Kalshi settles CPI, unemployment and GDP on the first one-decimal figure the agency publishes, and ignores revisions. Bloomberg consensus errors since 2022 have a typical size (RMSE) of about 0.10 point for headline and core CPI month on month, and 0.13 for unemployment. Payroll surprises had a standard deviation of about 110k jobs through 2009; the post-2020 figure is not verified.
4. **No general edge is plausible.** One narrow lead is worth an offline backtest on Kalshi's free public price history, which covers hundreds of events: cheap long-shot bins are overpriced in economics markets as everywhere else on Kalshi. A second lead is weaker: one 45-release study found Kalshi's CPI distribution sits slightly too low. Either has to clear Kalshi's fee of 0.07 × p × (1 − p) per contract plus the spread.
5. **For our trader:** stop the AI forecasters from pricing these markets, and don't build a consensus-based pricer that bets. Our price screen strips the consensus and nowcast figures out of their research by design, so their poor score here (Claude direct Brier 0.306 against the market's 0.087, on 6 markets) is what you'd expect. If anything is built, it is an offline backtest of the long-shot lead.

## Findings

### How the markets resolve (read from Kalshi's live API and its CFTC filings, 2026-10-09)

**F1. All of these settle on the first published figure. Later revisions are ignored.**
- **The rule text.** Each contract filing with the CFTC says "Revisions to the Underlying made after Expiration will not be accounted for":
  - CPI: [CPI.pdf](https://assets.kalshi.com/regulatory/product-certifications/CPI.pdf), 2021-06-28. It names the first sentence of the BLS release, e.g. "increased 0.8 percent in April".
  - Payrolls: [PAYROLLS.pdf](https://assets.kalshi.com/regulatory/product-certifications/PAYROLLS.pdf), 2022-03-08.
  - Unemployment: [U3.pdf](https://assets.kalshi.com/regulatory/product-certifications/U3.pdf), 2021-07-01.
  - GDP: [GDP.pdf](https://assets.kalshi.com/regulatory/product-certifications/GDP.pdf), 2021-06-28. It settles on the Advance Estimate.
  - Fed decision: [FEDDECISION.pdf](https://assets.kalshi.com/regulatory/product-certifications/FEDDECISION.pdf), 2023-04-05.
- **The live rules agree.** The `rules_primary`/`rules_secondary` text on today's markets says the value is "the single-decimal value published at the Source Agency" (CPI) and "the one-decimal value published by the BEA" (GDP) ([Kalshi API, series KXCPI, KXGDP](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXCPI&status=settled)).
- **Strength:** strong.

**F2. Each series and what it settles on.**

| Series | Settles on | Trading closes (ET, release day) | Settled, in our sample |
|---|---|---|---|
| KXCPI, KXCPICORE | BLS seasonally adjusted month-on-month % change, one decimal, "more than X" | 8:25 | about 1 to 2 hours after the 8:30 release (13:28Z, 14:41Z) |
| KXCPIYOY | 12-month % change (not seasonally adjusted), one decimal | 8:29 | about 1 hour after |
| KXPAYROLLS | first-print change in nonfarm payrolls, whole number | 8:29 | about 30 to 75 minutes after |
| KXU3 | seasonally adjusted U-3 rate, one decimal, "above X%" | 8:29 | about 30 to 95 minutes after |
| KXGDP | BEA advance estimate, real GDP growth at an annual rate (SAAR), one decimal | 8:29 | next listed event is 2026-10-30 (Q3) |
| KXFED | upper bound of the target range after the meeting, "greater than X%" | 1:55 PM | within about 25 minutes of the 2:00 PM statement |
| KXFEDDECISION | the size of the move; the outcomes are mutually exclusive, and a cancelled meeting settles as "maintains" | 1:59 PM | within about 10 minutes of the statement |

- **Evidence:** live and settled markets from the [Kalshi API](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXU3&status=settled), read 2026-10-09. Settled values in the last few months, which are after my training data, so as Kalshi reports them:
  - CPI month on month: +0.1 (Jul 2026), +0.4 (Aug)
  - Payrolls: −23k (Jul), +162k (Aug), +29k (Sep)
  - Unemployment: 4.1 (Jul), 4.1 (Aug), 4.2% (Sep)
  - Fed: a 25bp **hike** on 2026-09-16, to an upper bound of 4.00%
- **Data quirks:**
  - The `expiration_value` field isn't consistent: "0.4", "Above 0.2%", "29,000" and "4.2%" all appear. Any parser has to cope with every form.
  - Kalshi's series record for KXPAYROLLS lists the BLS **PPI** page as its settlement source, which looks like a metadata error. The rules text names the Employment Situation report.
- **Strength:** strong (primary, live).

**F3. If a government shutdown delays the data, the contract waits rather than settling No. But the October 2025 CPI market settled on a value BLS never published for that month.**
- **The rule:** Kalshi's filing with the CFTC on 2023-11-06 extends the latest expiration to "the sooner of the release of the Underlying or six months after the end of the government shutdown". It covers BLS, BEA and Census contracts, not the Fed contracts ([CFTC filing](https://www.cftc.gov/filings/orgrules/rules1106238217.pdf)). The same sentence is in today's CPI rules.
- **What happened in October 2025:** KXCPI-25OCT closed 2025-11-13 and settled 2025-11-22 at "0.2", although BLS did not publish an October 2025 month-on-month CPI change. KXCPI-25NOV settled 2025-12-18, eight days after its scheduled date ([Kalshi API, historical markets](https://api.elections.kalshi.com/trade-api/v2/historical/markets?series_ticker=KXCPI)).
- **What we don't know:** where the 0.2 came from. Kalshi evidently ruled outside the written text.
- **Strength:** strong for the rule. The October 2025 outcome is a fact, but its basis is not verified.

**F4. The headline-CPI series charge both takers and makers. Core CPI charges takers only.**
- **The formulas:** taker fee = round_up(0.07 × contracts × p × (1 − p)), so about 1.75¢ per contract at 50¢, and 1¢ (about 10% of the stake) on a 10¢ contract bought singly. The maker fee is 0.0175 × contracts × p × (1 − p), on series that charge it ([Kalshi fee schedule](https://kalshi.com/docs/kalshi-fee-schedule.pdf), seen through search excerpts; [Kalshi help, 2026-04-19](https://help.kalshi.com/en/articles/13823805-fees)).
- **Which series charge what:** the live series records show `fee_type` "quadratic_with_maker_fees" for KXCPI, KXCPIYOY, KXPAYROLLS, KXU3, KXGDP, KXFED and KXFEDDECISION. KXCPICORE and KXCPICOREYOY show "quadratic" (takers only). Every multiplier is 1 ([Kalshi API, series](https://api.elections.kalshi.com/trade-api/v2/series/KXCPI)).
- **Strength:** strong for the fee types; moderate for the formula, which I didn't fetch directly (brief 10 covers costs in full).

**F5. Volume is concentrated in the nearest release and the next Fed meeting. Far-dated Fed markets are not real prices.**
- **Contracts traded per event** (API `volume_fp`), read 2026-10-09:
  - The September 2026 Fed decision: about 103 million. October's: 8.7 million so far.
  - The September CPI event: about 1.2 million.
  - Payroll and unemployment events: 0.36 to 0.68 million each.
- **Spreads on near events:** mostly 1¢ (September CPI, October unemployment, the October GDP release), and 2–6¢ for October payrolls.
- **Spreads on far events:** KXFED for 2027–2028 shows 11–40¢. Those mids are not forecasts, the same flaw as point 7 in `REBUILD_SCOPE.md` ([Kalshi API](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXFED&status=open)).
- **Strength:** strong (a snapshot on one day).

### Are Kalshi's prices as good as the benchmarks?

**F6. Kalshi beats or ties the Bloomberg consensus, and ties or beats fed funds futures.**
- **The study:** Diercks (Fed Board), Katz and Wright, "Kalshi and the Rise of Macro Markets", FEDS 2026-010 / NBER w34702, January–February 2026, Table 3 ([FEDS PDF](https://www.federalreserve.gov/econres/feds/files/2026010pap.pdf), [NBER](https://www.nber.org/papers/w34702)).
- **Headline CPI on release day:** mean absolute error (MAE) 0.081 for Bloomberg; 0.069 for Kalshi's mean and 0.063 for its median and mode (p<0.10). The Kalshi mean also has a lower RMSE, 0.080 against 0.100 (p<0.05).
- **Core CPI:** Bloomberg MAE 0.070, Kalshi's mean also 0.070. **Unemployment:** 0.109 against 0.107–0.117. "In no case is Kalshi significantly worse."
- **The Fed:** Kalshi's median and mode missed by 0.000 on the day; futures missed by 0.010 (p<0.05). The whole gap is **one meeting**, September 2024, when Kalshi put more weight on the 50bp cut that happened. At longer horizons Kalshi roughly matches the NY Fed's Survey of Market Expectations.
- **Other results:** the realized outcomes fall roughly evenly across Kalshi's predicted range (a PIT check), with some sign that the market overprices high-inflation and high-unemployment outcomes.
- **Sample:** releases and meetings since 2022, roughly 40 CPI releases and roughly 30 meetings; the paper doesn't state exact counts.
- **What it doesn't cover:** payrolls and GDP. It compares point forecasts, not whether the bin probabilities are calibrated.
- **Bias risk:** Kalshi's CEO promoted the paper. It is a staff working paper, not peer reviewed.
- **Strength:** moderate (primary, but a small sample, and the Fed result rests on one meeting).

**F7. Kalshi's own claim of a much larger edge is marketing.** "Crisis Alpha" (Kalshi Research, December 2025) claims 40.1% lower CPI error than consensus from February 2023 to mid-2025, and that Kalshi was right 75% of the time when it disagreed with consensus. It gives no count of releases, and it is about twice the gap the Fed study found ([casino.org summary, 2025-12-23](https://www.casino.org/news/want-an-accurate-inflation-forecast-kalshi-says-it-beats-wall-street/)). **Strength:** anecdotal (vendor).

**F8. Markets on data releases were already as good as consensus in 2002–2005.**
- **The study:** Gürkaynak and Wolfers, NBER w11929 (2006), on the Economic Derivatives auctions, October 2002 to April 2005 ([NBER](https://www.nber.org/papers/w11929)).
- **Accuracy:** the market's central forecasts were somewhat more accurate than the MMS consensus. Payrolls, n=33: the market's error SD was 100.7k against the survey's 103.7k.
- **Calibration:** the probabilities across bins were "remarkably well calibrated", and the survey's known anomalies were absent.
- **Limits:** the samples are small (33 payroll, 30 ISM, 26 retail-sales and 64 jobless-claims auctions). The series don't include CPI, GDP or the Fed. The market traded on release morning, after the survey was taken.
- **Strength:** moderate.

**F9. Kalshi's economics markets have the same favourite–long-shot bias as the rest of Kalshi.**
- **The study:** Bürgi, Deng and Whelan, "Makers and Takers: The Economics of the Kalshi Prediction Market", UCD, January 2026 ([karlwhelan.com](https://www.karlwhelan.com/Papers/Kalshi.pdf); also GWU Research Program on Forecasting WP 2026-001, February 2026, [PDF](https://www2.gwu.edu/~forcpgm/2026-001.pdf)).
- **Sample:** every Kalshi contract from 2021 to April 2025 with at least $1,000 of volume and a final spread of 20¢ or less. That is 46,282 contracts and 156,986 daily prices.
- **Results:**
  - Contracts at 10¢ or less lose over 60% after fees. Those above 70¢ earn small, significant positive returns.
  - Takers average −31.5% and makers −9.6%.
  - The economics category has 24,405 price observations, and its bias has the same slope as the full sample (Table 8). CPI and the Fed are not split out.
  - The bias is weaker in 2025.
- **Strength:** moderate (one working paper, but a large sample). It matches our own data in report 01.

**F10. One study finds Kalshi's CPI distribution sits slightly too low. Its tail result did not survive checking.**
- **The study:** Goel, *International Review of Economics and Finance* 110 (2026) 105577, peer reviewed ([PDF](https://eprints.gla.ac.uk/390184/1/390184.pdf)).
- **Sample:** 45 headline CPI month-on-month releases, 2022–2026. 45 of 66 candidate releases passed its liquidity filters.
- **Result:** actual prints landed in the upper part of Kalshi's implied distribution. The mean of where each print fell (the PIT) was 0.599 against an ideal 0.5 (p=0.022).
- **Weak points:**
  - The implied median called the direction of the surprise against consensus on only 16 of 28 releases.
  - The p-value is uncorrected for multiple tests.
  - The paper's claim that the tails are too thin (66.7% coverage of the 10–90 band) was **refuted 1–2** by our verifiers.
- **Strength:** weak. It is a lead to backtest, not an edge.

### The inputs a model would use

**F11. The Cleveland Fed Inflation Nowcast: free, updated every business day at about 10:00 a.m. ET.**
- **What it covers:** headline and core CPI and PCE, month on month (seasonally adjusted) and year on year (CPI not seasonally adjusted), unrounded ([Cleveland Fed](https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting), read 2026-10-09).
- **How accurate it is:** against the Survey of Professional Forecasters (SPF), headline CPI error was lower by 0.41 point on average (1999Q2–2022Q4, quarterly annualized rates) and by 0.74 point in 2020Q1–2022Q4. The gains on **core** are not statistically significant, and the advantage reversed in late 2022 ([Knotek & Zaman, Economic Commentary 2023-06](https://www.clevelandfed.org/publications/economic-commentary/2023/ec-202306-real-time-assessment-inflation-nowcasting-cleveland-fed)).
- **Limits:** the authors built the model. The comparison is against quarterly surveys, not the monthly consensus, and no comparison with Kalshi exists.
- **Strength:** high on the facts, moderate on what they mean for us.

**F12. Atlanta Fed GDPNow: free, updated several times a month after major data releases.**
- **Accuracy:** its last nowcast missed BEA's first estimate by 0.77 point on average, RMSE 1.17 (2011Q3–2025Q2, 56 quarters).
- **The Atlanta Fed's own verdict:** this does "not give compelling evidence that the model is more accurate than professional forecasters" ([Atlanta Fed GDPNow](https://www.atlantafed.org/cqer/research/gdpnow), read 2026-10-09).
- **The error shape:** RMSE divided by mean absolute error is about 1.52, against 1.25 for a bell curve, so the errors are fat-tailed (the 2020 quarters).
- **An older comparison:** MAE 0.56 against 0.60 for the WSJ survey over 19 quarters in 2011–2016 ([Atlanta Fed Macroblog, 2016-05-16](https://fraser.stlouisfed.org/files/docs/historical/frbatl/publications/macroblog/frbatl_macroblog_20160516.pdf)).
- **The NY Fed Staff Nowcast:** relaunched 2023-09-08 with a new model, published about 11:45 ET on Fridays, not during the FOMC blackout ([NY Fed](https://www.newyorkfed.org/newsevents/news/research/2023/20230908)).
- **Strength:** strong for GDPNow; moderate for the NY Fed schedule.

**F13. CME FedWatch reads probabilities off 30-day fed funds futures using a two-outcome tree.**
- **How it works:** each futures contract settles at 100 minus the month's average effective fed funds rate. The tool assumes 25bp steps, an effective rate that moves one-for-one with the target, and month-end equals next month's start ([CME methodology, 2023](https://www.cmegroup.com/articles/2023/understanding-the-cme-group-fedwatch-tool-methodology.html); seen through search excerpts, because the page timed out).
- **Its weakness:** two outcomes per meeting is "problematic in times of high uncertainty or when looking beyond the next meeting" (FEDS 2026-010, p.11).
- **Cost:** the web tool is viewable without paying. The API's end-of-day tier starts at $25 a month, updated at 01:45 UTC; an intraday tier updates every 60 seconds ([CME FedWatch API](https://www.cmegroup.com/market-data/market-data-api/fedwatch-api.html)).
- **A free alternative:** the Atlanta Fed Market Probability Tracker uses SOFR options and updates daily with the previous day's data ([Atlanta Fed](https://www.atlantafed.org/cenfis/market-probability-tracker)).
- **No rigorous study** of whether Kalshi's Fed prices lead or lag the futures within the day was found. The one student thesis comparing them (26 meetings, 2023–2026) could not be read.
- **Strength:** moderate.

**F14. Free consensus forecasts.**
- **Trading Economics calendar:** shows a "Consensus" column and its own "Forecast" for CPI, core CPI, payrolls, unemployment and GDP. The page loaded without a login, but whether it stays free and whether its history is free are not verified ([calendar](https://tradingeconomics.com/united-states/calendar)).
- **Briefing.com, Investing.com, MarketWatch:** show a consensus column, but none could be fetched (not verified).
- **Paid only:** Bloomberg, Reuters polls and Blue Chip.
- **Philadelphia Fed SPF:** free and quarterly, with **probability bins** for annual GDP growth, unemployment and core PCE. Its horizons are too long for monthly bins ([SPF](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/spf-faqs)).
- **Strength:** moderate.

### How big the surprises are (actual minus consensus)

**F15. Surprise sizes by release.** "Typical size" is the root-mean-square error (RMSE); "SD" is standard deviation.

| Release | Since 2022, Bloomberg consensus (FEDS 2026-010) | Long history (Hess & Orbe 2013, MMS survey to 2009) | Kalshi bin width |
|---|---|---|---|
| CPI m/m | MAE 0.081, typical size 0.100 | SD 0.151 (1980–2009, n=358) | 0.1 |
| Core CPI m/m | MAE 0.070, typical size 0.100 | SD 0.116 (1989–2009, n=244) | 0.1 |
| Unemployment rate | MAE 0.109, typical size 0.132 | SD 0.164 (1980–2009, n=359) | 0.1 |
| Payrolls | not in the study | SD 109.9k (1985–2009, n=299); 111.0k in Campbell & Sharpe FEDS 2007-12 (about 180 months) | 25k–50k |
| GDP advance | not found | GDPNow typical size 1.17 (2011–2025, n=56) as a stand-in | 0.5–1.0 |

- **Sources:** [Hess & Orbe, CFR WP 11-13 / Review of Finance 2013](https://www.cfr-cologne.de/download/workingpaper/cfr-11-13.pdf); [Campbell & Sharpe, FEDS 2007-12](https://www.federalreserve.gov/pubs/feds/2007/200712/200712pap.pdf); FEDS 2026-010 Table 3.
- **What it means:** a typical CPI or unemployment surprise is about one bin wide. So where the unrounded forecast sits inside a tenth (0.25 against 0.34) moves the probabilities a lot.
- **BLS's own noise:** the 90% interval on the monthly payroll change is about ±122k ([BLS technical note, Sep 2026 report](https://www.bls.gov/news.release/empsit.tn.htm)). The first print's mean absolute revision is 51k (2003 onward); revisions averaged −58k in 2025, i.e. downward ([BLS revisions](https://www.bls.gov/web/empsit/cesnaicsrev.htm)).
- **Strength:** strong for the pre-2010 and since-2022 figures. The post-2020 standard deviation for payrolls is **not found**.

**F16. The consensus is hard to improve on in real time.**
- MMS medians beat ARIMA time-series models on all 23 US series tested.
- Correcting for their known anchoring bias in real time improved only 2 of 23 series, and made payrolls significantly **worse** (Hess & Orbe 2013; samples CPI n=358, payrolls n=299).
- A claim that the anchoring bias is tradeable (from a FEDS paper) was **refuted 0–3**.
- **Strength:** moderate (the data end in 2009).

**F17. You can rebuild the unrounded CPI change.**
- **How:** since January 2007, BLS publishes CPI indexes to three decimals and computes the one-decimal % change from them. Before then, published monthly rounding differed from the full-precision change about 25% of the time ([Williams, BLS WP-397, 2006](https://www.bls.gov/osmr/research-papers/2006/ec060090.htm)).
- **Use:** the unrounded month-on-month change can be rebuilt from FRED or ALFRED index levels.
- **Unemployment:** the unrounded rate can be computed from the published counts of unemployed people and the labour force.
- **Strength:** strong.

### Our own pipeline

**F18. Our price screen removes most of what would make an AI forecast of these markets good.** It does this by design, and two of its rules do it:
- **"Makes a prediction."** The screen drops any fact containing "forecast(s)", "projection", "predicted" and similar ([`papertrade/news.py:271-274`](../../papertrade/news.py)). So "economists forecast CPI rose 0.3%" never reaches Jev or Claude direct. The research prompt also forbids "forecasts from models or forecasters" (`news.py:58-61`). FedWatch probabilities are blocked as market odds (`news.py:254-266`, `_PROB_WORDS`).
- **"A figure within 1 point of this market's price."** Every percentage is compared with every bin's price, plus 100 minus that price, across the whole event ladder (`engine.py:575`, `news.py:282-306`). Kalshi ladders almost always have bins at 1–5¢ or 95–99¢. So a fact like "unemployment was 4.2%" or "CPI rose 0.3%" can be dropped as a price leak.
- **Consequence:** the forecasters price these markets from general knowledge plus whatever survives. That is a plausible cause of Claude direct's 0.306 Brier.
- **What changing it would take:** loosening either rule needs Joey's OK (`CLAUDE.md`). And given F6, loosening it would at best bring them *up to* the market, not past it.
- **Strength:** strong for what the code does. The effect on our scores is untested (see the tests below).

## What it means for our trader

Ranked by expected effect.

1. **Stop the AI forecasters from betting economics and Fed markets** (exclude the category, as report 07 proposes for weather).
   - *Why:* the evidence says the market already beats every input we could add (F6, F8, F11, F12). Our forecasters can't even see those inputs (F18), and our only measurement is in line with that (Brier 0.306 against 0.087, n=6).
   - *Effect:* removes a small source of loss. Economics is about 4.5% of finished markets (51 of 1,133).
   - *Sure:* high that there is no edge; low on the size of the saving, given the tiny sample.
2. **Don't loosen the screen for economics.** It would need Joey's OK, and the best case (F6) is matching the market, which still loses the cost of trading (about 8.4% per bet per `REBUILD_SCOPE.md`).
   - *Sure:* high.
3. **Don't build a consensus- or nowcast-based pricer that bets.** Build it only as an offline benchmark, if the backtest below is run at all.
   - *Expected effect:* nothing positive. Consensus ties Kalshi, and nowcasts don't beat consensus.
   - *Sure:* moderate to high.
4. **If anything is backtested, test long-shot bins first.**
   - *Idea:* sell the overpriced cheap bins in economics ladders, i.e. buy No at 90–99¢ (F9, report 01).
   - *Expected effect:* small, a few cents per $1 at best before the spread, and taker fees bite hardest near 50¢, not here.
   - *Sure:* low to moderate.
   - The CPI "sits too low" lead (F10) is second. The Cleveland headline nowcast against Kalshi's month-on-month CPI bins on the eve of release is third.
5. **Handle the settlement details if economics markets stay in at all.**
   - Value strings come in many forms (F2).
   - Markets close at 8:25 or 8:29 ET on release day.
   - A shutdown delay can leave a position open for weeks (F3).
   - Kalshi may rule outside the text (F3).
   - Far-dated Fed markets with 11–40¢ spreads are not real prices (F5) and should be excluded by the existing spread rule (B25).
   - *Sure:* high.

### The model for each release (if built as a benchmark)

| Release | Centre | Spread around it | Rounding and settlement | Free data |
|---|---|---|---|---|
| CPI m/m (headline) | Cleveland nowcast on the eve of release, blended with free consensus | Student-t with σ≈0.10 (since 2022), fitted to past nowcast errors | P(BLS one-decimal > k) = P(unrounded ≥ k + 0.05) | Cleveland nowcast; FRED CPIAUCSL to 3 decimals |
| Core CPI m/m | Consensus; the Cleveland core nowcast adds little (F11) | σ≈0.10; consensus is often exactly 0.2 or 0.3, so model where it sits inside the tenth | same | FRED CPILFESL |
| CPI y/y | (last year's not-seasonally-adjusted index) × (1 + this month's not-seasonally-adjusted m/m forecast); only this month is unknown | same σ as m/m | one decimal; computed from the not-seasonally-adjusted index | FRED CPIAUCNS |
| Payrolls | Free consensus | t-distribution, σ about 110k (pre-2010) until refitted on 2015–2026 | whole number; first print only | ALFRED vintages of PAYEMS (first prints) |
| Unemployment | Consensus, usually equal to last month | Discrete: the empirical distribution of monthly changes of −0.2 to +0.2, conditioned on last month's unrounded rate | one decimal | BLS levels, ALFRED UNRATE vintages |
| GDP advance | GDPNow's last value before release, or consensus | t-distribution, σ≈1.0–1.2, fitted without 2020 | one decimal; advance estimate only | GDPNow history; ALFRED GDPC1 first releases |
| Fed (KXFED, KXFEDDECISION) | FedWatch or the Atlanta Fed tracker, **as a check only**. It is a market price, which the AI path can't use, and Kalshi already ties or beats it (F6) | n/a | upper bound of the target range | CME FedWatch (web), Atlanta Fed MPT |

## How to test it on our history

**On our own data (the main session runs these; I did not open `papertrade_data/`):**

1. **The economics scorecard.** For all economics markets (about 51), at first look, compute Brier for the market and for each forecaster that covered them, with the ± range. Split real prices (spread ≤10¢) from fake ones.
   - *Confirms:* the market is better on real-priced economics markets, with a difference above 2 standard errors.
   - *Kills the "stop betting" idea:* any forecaster within 1 standard error of the market or better. That is unlikely at this n, and n≈51 can't settle it either way; the Kalshi backtest below can.
2. **The screen's effect on economics research.** For economics events, count researched facts by screen reason, especially "makes a prediction" and "a figure within 1 point of this market's price", against all other categories.
   - *Confirms F18:* economics events lose a clearly larger share of facts to those two reasons.
   - *Kills it:* drop rates no higher than other categories.
3. **The settled bets.** Did we bet economics markets? With what return, and with or against the favourite? Check the brief's example (U-3 above 3.9% for September at about 9.5¢) against Kalshi's settled value: KXU3-26SEP settled at 4.2%, so "above 3.9%" resolved **Yes**.
   - A Yes contract at 9.5¢ on that line would have been far off the market, since unemployment had printed 4.1% for two months. Check which side and which market the bet was.

**On Kalshi's public history (the real test; free, no account):**

- **The data.** The `/historical/markets?series_ticker=KXCPI` endpoint returns every event back to 2024 (older ones under `CPI-…`), with settled values. `/series/{s}/markets/{t}/candlesticks` gives hourly bid, ask and last prices. I confirmed both on 2026-10-09 (233 hourly candles for KXCPI-26AUG-T0.3). The same exists for KXPAYROLLS, KXU3, KXGDP and KXFED.
- **The sample.** Expect about 40–50 events per monthly series for 2022–2026, times 10–20 bins each.
- **Test A (long-shot bins).**
  - *Trade:* at 24 hours and 1 hour before close, buy No on every bin whose Yes ask is 3–10¢. Pay the ask plus the taker fee, using `expiration_value` for outcomes.
  - *Confirms:* an after-fee return above zero with a 95% interval that excludes zero, clustered by event, on the 2022–2024 events and again on 2025–2026.
  - *Kills it:* an interval that includes zero in either period.
- **Test B (a benchmark pricer).**
  - *Pricer:* the model table above, frozen on 2015–2021 data (nowcast and consensus errors) and scored on 2022–2026.
  - *Score:* log loss and Brier on every bin, against Kalshi's mid at the same moment.
  - *Kills it:* the pricer's loss is worse than or equal to Kalshi's (the expected result, given F6).
  - *Only if it beats Kalshi by more than 2 standard errors:* simulate trading where |pricer − ask| > fee + 2¢. The after-fee return must be positive on each half of the test period.
- **Test C (Goel's lead).** Compute the PIT of headline CPI against Kalshi's implied distribution on the eve of release for events after Goel's sample (2026 onward).
  - *Confirms:* the mean PIT is still above 0.55.
- **One known problem.** Free *historical* consensus is the weak link. If Trading Economics' history is paid, use the Cleveland nowcast (its history is published) and GDPNow (its history is published) as the centres, and the BLS or BEA prior value as a naive benchmark.

## Data sources

| Name | URL | Cost | Provides | Limits |
|---|---|---|---|---|
| Kalshi public market data | `https://api.elections.kalshi.com/trade-api/v2/` (`/series`, `/markets`, `/historical/markets`, `/candlesticks`) | free, no key | rules, settled values, hourly prices, volume | rate-limited (HTTP 429 seen); settlements before 2026-08-10 are only on `/historical` |
| Kalshi contract filings | `https://assets.kalshi.com/regulatory/product-certifications/{CPI,PAYROLLS,U3,GDP,FED,FEDDECISION}.pdf` | free | legal settlement terms | from 2021–2023; the live rules text wins |
| Cleveland Fed Inflation Nowcast | https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting | free | daily CPI and PCE nowcasts, about 10:00 ET | strong on headline only |
| Atlanta Fed GDPNow | https://www.atlantafed.org/cqer/research/gdpnow | free | GDP nowcast and its history | not better than consensus |
| NY Fed Staff Nowcast | https://www.newyorkfed.org/research/policy/nowcast | free | weekly GDP nowcast, Fridays about 11:45 ET | paused in the FOMC blackout |
| CME FedWatch | https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html | web free; API from $25/mo | meeting probabilities from fed funds futures | a market price, which the AI path can't use; two-outcome assumption |
| Atlanta Fed Market Probability Tracker | https://www.atlantafed.org/cenfis/market-probability-tracker | free | rate probabilities from SOFR options | daily, one day behind |
| Trading Economics calendar | https://tradingeconomics.com/united-states/calendar | web viewable; API paid | consensus and its own forecast per release | free history not verified |
| Philadelphia Fed SPF | https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters | free | quarterly forecasts and probability bins | horizons too long for monthly bins |
| FRED / ALFRED | https://fred.stlouisfed.org, https://alfred.stlouisfed.org | free (key for API) | 3-decimal CPI indexes; first-print vintages for payrolls, unemployment and GDP | none relevant |

## Not verified

- The post-2020 standard deviation of payroll surprises, and the release-eve consensus surprise size for advance GDP: no primary source found.
- How Kalshi arrived at 0.2 for KXCPI-25OCT, given BLS published no October 2025 month-on-month change.
- The Kalshi fee formula was read from search excerpts and the help page, not the fee-schedule PDF (HTTP 429). Allium reports per-series rounding to $0.0001, which conflicts with whole-cent rounding up.
- How CME FedWatch handles a meeting late in the month, and whether its web tool is officially free. The CME pages timed out.
- Whether Trading Economics' consensus history is free, and whether Briefing.com, Investing.com and MarketWatch consensus pages are reachable without a login.
- Exact sample counts in FEDS 2026-010 (about 40 releases and about 30 meetings, estimated).
- A June 2026 arXiv preprint (Angelini, "The Shape of Macroeconomic Beliefs", 2606.30040) reportedly finds Kalshi's implied mean CPI error at RMSE 0.169 over 268 snapshots at various horizons, and a median implied σ of about 0.10. It came to us through one research agent and was not checked further.
- Any intraday lead-lag between Kalshi's Fed markets and futures. A Gothenburg thesis (26 meetings, 2023–2026) could not be read.
- The Bloomberg analysis said to find no Kalshi edge on payrolls over 33 months (both errors above 60k): secondhand only.
- Whether the brief's example bet (U-3 above 3.9%, about 9.5¢) was a Yes or a No, and on which venue: for the main session to check.

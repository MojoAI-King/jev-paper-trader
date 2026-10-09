# 07: Pricing daily weather markets from forecast models

Researched 2026-10-09 for `docs/research/briefs/07-weather-markets.md`.

## Answer in five lines

1. **Kalshi** daily high/low markets settle on the official daily maximum (or minimum) at one named NWS climate station, now published by The Weather Company (TWC) for events dated 2026-08-14 onward. The value is a whole °F, the day is midnight to midnight *standard* time, and NYC means Central Park and Chicago means Midway. **Polymarket** settles on the highest *hourly reading* on NOAA's weather.gov time-series page for an airport (NYC means LaGuardia, Chicago means O'Hare): whole °F with 2°F bins in the US, whole °C with 1°C bins abroad, for events dated about 2026-08-23 onward.
2. The defensible way to price a bin is to take the National Blend of Models (NBM) forecast high, plus LAMP on the day itself, and correct it for each station's recent bias. Then put a bell curve around it whose width (σ) depends on station, season and lead time: about 2.1°F on the morning of the day, 2.5–2.7°F the day before, and roughly 3.0–3.5°F at 2–3 days (the 2–3-day figures are extrapolated). Add up the curve over each bin with ±0.5° edges, and cut it off below the highest temperature already observed that day. Before the day starts, no 2°F bin can honestly get more than about 29–37%, and no 1°C bin more than about 26–33%.
3. The markets are hard to beat. In the one study that compares them directly (a single-author, not peer-reviewed arXiv paper, 7,590 city-days), Kalshi's price-implied forecast beat every public forecast: an error of 2.44°F against the NBM's 2.70°F the morning before. Prices are close to calibrated on average. The one documented, systematic bias is that cheap long-shot contracts are overpriced.
4. The two candid 2026 paper-trading bots that report numbers found no edge, or losses roughly equal to their fees. The big Polymarket weather profits are anecdotes from crypto news, with heavy survivorship bias.
5. For us: stop the AI forecasters from pricing temperature bins directly. Do not widen weather coverage on current evidence. If anything is built, it should first be an offline backtest of a non-LLM pricer aimed at the few places where a structural edge could exist: Polymarket's same-day observed maximum, the gap between Polymarket's hourly-reading rule and the official maximum, and the No side of overpriced long-shot bins.

## Findings

### How the markets resolve

**F1. Kalshi switched settlement source from the NWS Daily Climate Report to The Weather Company for events dated 2026-08-14 onward. In practice TWC still relays the NWS number.**
- **Evidence, the rules:** live `rules_primary` text on every daily-high series reads "...greater than X° fahrenheit according to The Weather Company", still keyed to the NWS climate-report code, e.g. "New York City (CLINYC)" ([Kalshi API, KXHIGHNY open markets, read 2026-10-09](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXHIGHNY&status=open)). Settled KXHIGHNY events up to 26AUG13 name the NWS "Climatological Report (Daily)"; 26AUG14 onward name TWC ([Kalshi API, settled](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXHIGHNY&status=settled)). The partnership was announced on 2026-08-27, about two weeks *after* the rules changed ([Artemis](https://artemis.bm/news/prediction-market-kalshi-partners-with-the-weather-company-for-weather-hedge-settlements)).
- **Evidence, the numbers:** our researcher compared Kalshi's settled values with NWS climate-report values archived by the Iowa Environmental Mesonet (IEM) for 8 series (NY, CHI, AUS, LAX, DEN, PHIL and MIA highs, plus the NYC low), 2026-08-02 to 2026-10-08. In the TWC era the two agreed on **447 of 448 series-days**. The one exception was Miami on 2026-08-29: Kalshi settled at 90, IEM shows 85, cause unknown ([IEM CLI JSON](https://mesonet.agron.iastate.edu/json/cli.py?station=KMIA&year=2026)).
- **Conflict:** Kalshi's own help centre (last updated 2026-07-22) still says daily markets settle on "the final NWS Daily Climate Report" ([Kalshi Help](https://help.kalshi.com/en/articles/13823837-weather-markets)). So does a trader site updated 2026-08-28 ([wethr.net](https://wethr.net/market-resolution)). The live market rules win.
- **Strength:** strong (primary rules text plus a measured 448-day check).

**F2. Kalshi rules: whole °F; the first non-preliminary TWC publication counts; later revisions are ignored; settlement comes the next morning.**
- **Evidence:** `rules_secondary` says only the first non-preliminary TWC publication counts, and that expiry may be held if that publication has a "material error" ([Kalshi API](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXHIGHCHI&status=open)). Settled values are integers (e.g. "73.00"). Expiry is the first 7 or 8 AM ET after the data is released; KXHIGHNY-26OCT07 and -26OCT08 settled at 11:19Z and 11:18Z ([Kalshi API, settled](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXHIGHNY&status=settled)).
- **Rulebook amendments:** Kalshi filed amendments to seven weather rulebooks on 2026-09-02 adding this material-error delay. The only source is secondary ([nextpredict.io, 2026-09-03](https://nextpredict.io/market-news/industry/kalshi-reins-weather-market-rules-manipulation-concerns/)).
- **Strength:** strong for the rules; moderate for the amendment history.

**F3. Kalshi's "day" is midnight to midnight local standard time all year.**
- **What that means:** during daylight saving time the day runs 1:00 AM to 12:59 AM local clock time. Trading closes at local-standard midnight, which is 05:00Z for New York in October.
- **Evidence:** NWS Instruction 10-1004 (2025-06-05) defines the climate-report day as midnight to midnight local standard time, issued between 12:30 and 5:00 AM ([NWSI 10-1004](https://www.weather.gov/media/directives/010_pdfs/pd01010004curr.pdf)). The API `close_time` for 2026-10-10 events is 05:00/06:00/07:00/08:00Z for the Eastern, Central, Mountain and Pacific zones ([Kalshi API](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXHIGHLAX&status=open)).
- **Conflict:** the same market's text says trading ends at "11:59 PM local time".
- **Strength:** strong.

**F4. The official daily maximum is not the maximum of the hourly reports. It can be higher than every hourly reading.**
- **Why:** the ASOS station keeps its own running daily high from 1-minute sampling. Hourly METAR reports carry tenths of °C. The public 5-minute reports are whole °C converted to °F, so they "might be a 1 degree or 2 off". The official high "could also occur in between" observations.
- **Evidence:** [NWS Los Angeles ASOS page](https://www.weather.gov/lox/asostemperature); [IEM, "Wagering on ASOS Temperatures", 2024-12-04](https://mesonet.agron.iastate.edu/onsite/news.phtml?id=1469). A trader site says the official report "will occasionally report a high temperature that is 1°F (or sometimes more)" above Weather Underground's hourly-based value; this is anecdotal ([wethr.net, 2026-08-28](https://wethr.net/market-resolution)).
- **Not found:** any measured frequency of this gap.
- **Strength:** strong for the mechanism; no data on its size.

**F5. Kalshi market structure.**
- **Bins:** each daily high or low event has 6 markets: four inclusive 2°F bins ("73° to 74°") and two open tails.
- **Listing:** events open at 14:00Z the day before, so two days trade at once.
- **Coverage on 2026-10-09:** 24 US cities had both high and low series open.
- **Evidence:** [Kalshi API, read 2026-10-09](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXHIGHNY&status=open). Station codes include Central Park (CLINYC), Midway (CLIMDW), DFW (CLIDFW), Hobby (CLIHOU) and Reagan National (CLIDCA). The airport behind 7 of the codes is confirmed by exact settlement matches; the other 17 follow standard NWS codes but were not checked.
- **International series:** 20 international daily series (London, Tokyo and others) exist in the metadata but had no open markets ([Kalshi series list](https://api.elections.kalshi.com/trade-api/v2/series?category=Climate%20and%20Weather)).
- **Strength:** strong.

**F6. Kalshi rain: "Will it rain" is one yes/no market per city.**
- **Rule:** Yes means more than 0 inches at the climate station on the standard-time day, per TWC. A trace counts as 0, and so does a missing value. The market closes early once rain occurs.
- **Coverage:** KXRAIN-26OCT10 had 33 markets ([Kalshi API](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXRAIN&status=open)).
- **Station trap:** monthly Chicago rain settles at O'Hare (CLIORD), while Chicago temperature settles at Midway ([Kalshi API](https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXRAINCHIM&status=open)).
- **Strength:** strong.

**F7. Polymarket temperature markets resolve on the highest reading in the "Temp" column of NOAA's weather.gov/wrh/timeseries page for one airport.**
- **Rule text:** "highest temperature recorded by NOAA at the LaGuardia Airport Station... resolve off of the Hourly Data" ([Gamma API, NYC 2026-10-10](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-nyc-on-october-10-2026)). The Amsterdam rule specifies whole °C ([Gamma API, Amsterdam 2026-10-10](https://gamma-api.polymarket.com/events?slug=highest-temperature-in-amsterdam-on-october-10-2026)). Revisions count until the next day's first data point is published.
- **Units and bins:** US cities use whole °F and 2°F bins; international cities use whole °C and 1°C bins. Each event has 11 outcomes: 9 bins plus 2 tails.
- **Coverage:** 51 cities on 2026-10-09.
- **History of the rules:**
  - Weather Underground was the source until events dated 2026-08-22 for NYC. A third-party code review counted 2,195 of 2,596 active markets reworded around 2026-08-22 ([simmer-sdk PR #341](https://github.com/SpartanLabsXyz/simmer-sdk/pull/341)).
  - London switched from °F to °C for events from 2025-12-11.
  - Paris moved from CDG to Le Bourget for events from 2026-04-19.
- **Exceptions:** Taipei, Jinan and Zhengzhou still use Weather Underground. Hong Kong uses the Hong Kong Observatory's 0.1°C daily maximum, and how that is rounded into whole-degree bins is not stated.
- **Conflict:** an earlier data-source note and third-party rule mirrors still describe Weather Underground as the source ([polyguana mirror](https://polyguana.com/market/1779728)). The live Gamma API rules win.
- **Strength:** strong (primary rules text).

**F8. The same city name often means a different station on each venue.**
- **Differences:**

  | City | Kalshi | Polymarket |
  |---|---|---|
  | NYC | Central Park | LaGuardia |
  | Chicago | Midway | O'Hare |
  | Dallas | DFW | Love Field |
  | Denver | DEN | Buckley SFB (KBKF) |
  | Houston | Hobby | Hobby (the same) |

- **Measurement also differs:** Kalshi uses the official continuous maximum; Polymarket uses the maximum hourly reading.
- **Day may differ:** Polymarket's rules do not define "this day". The page shows local clock time, so it is probably midnight to midnight *daylight* time, unlike Kalshi's standard-time day. This is not verified.
- **Evidence:** the Kalshi API and Polymarket Gamma API rules cited in F5 and F7.
- **Strength:** strong for stations; weak for Polymarket's day definition.

**F9. Polymarket rain markets resolve on the NWS climate report.**
- **Rule:** at least 0.01 in on the standard-time climate day; a trace does not count.
- **Timing:** the last report published by 2:00 PM ET the next day governs, and if none has been published the market resolves No.
- **Evidence:** [Gamma API, "Where will it rain on October 9, 2026"](https://gamma-api.polymarket.com/events?slug=where-will-it-rain-on-october-9-2026).
- **Strength:** strong.

**F10. Single-station settlement carries tampering and odd-reading risk.**
- **What happened:** Météo-France filed a complaint over possible tampering with its Paris-CDG temperature sensor after evening spikes on 2026-04-06 and 2026-04-15 coincided with winning long-shot Polymarket bets. The "hair dryer" explanation is unproven.
- **Evidence:** [NPR via KPBS, 2026-04-23](https://www.kpbs.org/news/science-technology/2026/04/23/french-police-probe-suspected-weather-device-tampering-after-odd-polymarket-bet); [Euronews, 2026-04-23](https://fr.euronews.com/business/2026/04/23/astuce-au-seche-cheveux-derriere-25-000-la-france-enquete-sur-une-fraude-meteo-polymarket).
- **Strength:** moderate (news reports of an official complaint; the cause is unproven).

### Forecast error and method

**F11. The best public forecast of tomorrow's high errs by about 2.7°F the morning before, 2.45°F that evening and 2.1°F on the morning of the day. The market's implied forecast does better at each time.**
- **Source:** Crosier, "Prediction Markets Beat the Weather Forecast on Tomorrow's High Temperature", arXiv 2609.23969, September 2026. It is a **single-author working paper, not peer reviewed**. It covers 7 Kalshi cities and 7,590 city-days through 2026-08-12, measured against the NWS climate-report high ([PDF](https://arxiv.org/pdf/2609.23969)).
- **Root-mean-square error (°F) at three times:** 11:00 ET the day before, 19:00 local the day before, and 13Z on the day.

  | Forecast | 11:00 ET, day before | 19:00 local, day before | 13Z, the day itself |
  |---|---|---|---|
  | NBM | 2.70 | 2.45 | 2.12 |
  | LAMP (bias-corrected) | 2.83 | 2.63 | 2.19 |
  | Official NWS forecast | 2.83 | 2.66 | 2.33 |
  | GFS MOS | 3.17 | 2.95 | 2.69 |
  | HRRR / ECMWF (bias-corrected) | 3.31–3.32 | 3.07–3.16 | 2.63–2.68 |
  | **Kalshi implied mean** | **2.44** | **2.21** | **1.88** |
  | Best combination of all public products (fitted out of sample) | 2.45 | 2.25 | 1.90 |

- **City and season:** errors vary widely. Miami's NBM error is about 1.6°F; the other six cities range 2.6–3.5°F. November–June is worse (3°F or more); July–October is better (about 2°F).
- **Strength:** moderate. The paper uses exactly the right stations and a large sample, but it has one author and no review. No day-2 or day-3 table for current models was found.

**F12. Raw model and hourly-based highs run cold at settlement stations.**
- **Size:** HRRR runs cold by up to about 2°F, ECMWF by 1–5°F and LAMP by 1–2°F when the daily high is taken as the maximum of hourly values.
- **Why:** the true peak falls between hours, a model grid cell averages over an area, and the highest of several average hourly values sits below the average daily peak (a statistical effect called Jensen's inequality).
- **Daytime window:** on 4.6% of days the calendar-day high fell outside the "daytime" window that NBM and MOS forecast.
- **Evidence:** [Crosier 2026](https://arxiv.org/pdf/2609.23969).
- **Strength:** moderate (same single paper).

**F13. Raw ensembles are far too confident. Calibrated post-processing (EMOS, also called NGR) fixes this.**
- **The method:** take a normal distribution with mean a + b·forecast and variance c + d·spread², fitted over a sliding window of about 30–40 days.
- **Evidence on spread:** in the original studies the 5-member ensemble's range contained only **29% of outcomes against a nominal 66.7%**. After calibration, coverage was 68.6% and the error score (CRPS) fell 15% ([Gneiting et al. 2005, MWR 133:1098](https://sites.stat.washington.edu/raftery/Research/PDF/gneiting2005.pdf); [Raftery et al. 2005, MWR 133:1155](https://w2w.meteo.physik.lmu.de/publications/previous_publications/gneiting_2005b.pdf)). Both studies use the Pacific Northwest in spring 2000, with a test period of about 39 days.
- **Evidence on training window:** windows under about 30 days produced over-confident output; 30–60 days was about right.
- **Strength:** strong for the method (peer reviewed and widely replicated). The specific numbers are old and regional.

**F14. NBM v5.0 now publishes a ready-made distribution for each station's maximum temperature.**
- **What it publishes:**
  - the NBS/NBE bulletins: max temperature `TXN` plus its standard deviation `XND`, and 6/12-hour rain probabilities;
  - the NBP bulletin: mean, standard deviation and 10/25/50/75/90th percentiles for max temperature.
- **When it changed:** v5.0 was scheduled for 2026-04-21 ([NWS Service Change Notice 26-24](https://www.weather.gov/media/notification/pdf_2026/scn26-24NBM_V5(1).0_aaa.pdf); [NBM v5.0 text card](https://vlab.noaa.gov/web/mdl/nbm-textcard-v5.0)). IEM's archive shows a cycle change on 2026-05-05, so the exact go-live date is not verified.
- **What it means for us:** history spans two NBM versions, so treat the change as a structural break.
- **Calibration:** no study measuring how well-calibrated the NBM percentiles are was found.
- **Strength:** strong for availability; no evidence yet on calibration.

**F15. The maximum honest probability on one bin is small.**
- **The arithmetic:** with a calibrated bell curve, the most any 2°F bin can get is 2Φ(1/σ)−1, and for a 1°C bin (1.8°F) it is 2Φ(0.9/σ)−1, where Φ is the standard normal cumulative distribution.

  | Situation | σ (°F) | Max for a 2°F bin | Max for a 1°C bin |
  |---|---|---|---|
  | Miami-like | 1.6 | 47% | 43% |
  | Morning of the day | 2.1 | 37% | 33% |
  | Evening before | 2.45 | 32% | 29% |
  | Morning before | 2.7 | 29% | 26% |
  | 2 days out | 3.0 | 26% | 24% |

- **The Wuhan bet:** Jev's 76% on Wuhan landing in one 1°C bin would need σ ≈ 0.43°C (0.77°F). That is about a third of the best public day-before error at US stations.
- **Caveats:** the arithmetic is our own, using σ inputs from [Crosier 2026](https://arxiv.org/pdf/2609.23969). No error statistics were found for Wuhan specifically. A forecast made late in the day with the running maximum already known could legitimately be that confident; I do not know when that forecast was made.
- **Strength:** strong as arithmetic; moderate as applied to non-US stations.

**F16. Rain probability forecasts are useful but run slightly dry.**
- **Evidence:** Bickel, Floehr and Kim (2011, MWR 139:3304) checked about 13 million forecasts at 734 US stations, November 2008 to October 2010 ([PDF](https://utw10181.utweb.utexas.edu/Papers/NWS_Calibration.pdf)).
- **Skill:** NWS 12-hour rain probabilities beat climatology by:
  - 0.47, 0.41 and 0.33 at days 1, 2 and 3 in the cool season;
  - 0.36, 0.30 and 0.22 in the warm season.
- **Bias:** the NWS under-forecast slightly, by 0.02 to 0.05.
- **Strength:** strong, but the data are old and cover 12-hour windows, not the full-day question the markets ask.

### Efficiency and bots

**F17. Kalshi weather prices show a favourite–long-shot bias: cheap contracts are overpriced.**
- **Source:** Bürgi, Deng and Whelan, "Makers and Takers", University College Dublin, January 2026. It is an academic working paper.
- **Data:** 46,282 contracts from 2021 to April 2025, of which 29,924 price observations are in Climate & Weather ([PDF](https://www.karlwhelan.com/Papers/Kalshi.pdf)).
- **The bias:** contracts at 10¢ and under lose over 60% on average after fees, across all categories. The bias appears in every volume band, but it was weaker in the 2025 data.
- **What the Climate & Weather fit implies** (our arithmetic, a linear fit that assumes the coefficients are in cents):
  - about −17% before fees at 5¢;
  - about −7% at 10¢;
  - break-even near 32¢;
  - about +2% at 90¢.
- **Strength:** moderate. The paper is rigorous, but its data ended before the 2025–26 weather boom and the fee changes.

**F18. Prices are close to calibrated on average.**
- **Evidence:** an independent notebook of 8,494 settled NYC daily-high markets found an average calibration error of 0.016, i.e. about 1.6 points; the date range is not stated ([Zerve "CalibShi", 2026-03-22](https://www.zerve.ai/gallery/85cce830-f612-4b23-8b78-34d7da65a2c6)). Kalshi's own calibration pages could not be read (HTTP 429).
- **Strength:** weak to moderate (a non-peer-reviewed notebook; the company material is unread).

**F19. The candid 2026 paper bots found no edge.**
- **Phan-Vincent/kalshi-weather-trader** (NBM plus Open-Meteo) labels itself "PAPER-ONLY, no proven edge"; its Brier comparison "shows no edge vs. market" (status note 2026-06-02) ([GitHub](https://github.com/Phan-Vincent/kalshi-weather-trader)).
- **rohilkanwar/dual-market-trader** (Polymarket, Open-Meteo plus METAR) ran on paper on 2026-10-02 with 69 fills. P&L was −$74.26, against fees of $74.67, so fees roughly equal the whole loss. Its evaluation reads "venue-settled FAIL n=117" ([PR #28](https://github.com/rohilkanwar/dual-market-trader/pull/28)).
- **Strength:** weak (two small self-reported repos). The direction is consistent.

**F20. Claimed weather-trading profits are anecdotal.**
- **The claims:**
  - Polymarket wallets reported as earning ">$2M" or "$24.88 → $12,398" ([KuCoin](https://www.kucoin.com/news/flash/traders-on-polymarket-earn-millions-by-predicting-weather); [X post](https://x.com/de1lymoon/status/2053110330956321249));
  - returns of "up to 49,000%" on international cities ([Phemex, 2026-04-27](https://phemex.com/news/article/polymarket-traders-reap-huge-profits-from-weather-bets-amid-controversy-76567));
  - vendor claims such as an "~88% win rate" from a "METAR lock" after about 2 PM ([kalshiweatheredge.com](https://www.kalshiweatheredge.com/)).
- **Against them:** a Medium analysis of a viral "$88K" strategy found its latest 2,000 closed positions summed to only about $6,095 ([Medium](https://medium.com/mountain-movers/inside-the-data-behind-polymarkets-viral-88k-weather-prediction-trading-strategy-and-results-2e65a8389f37); seen via search summary only).
- **Strength:** anecdotal. The large wins are long-shot payoffs, which F17 says lose money on average.

**F21. Fees on weather markets rose in 2025–26.**
- **Kalshi:** the taker fee is 0.07 × contracts × P × (1−P), rounded up to the next cent per order ([Whelan et al.](https://www.karlwhelan.com/Papers/Kalshi.pdf)). Maker fees were added after April 2025, reportedly at 25% of the taker rate ([pm.wiki](https://pm.wiki/uk/learn/kalshi-fees-explained)). One open-source bot instead assumes a maker *rebate*, so the maker terms conflict and are not verified.
- **Polymarket:** taker fees reached weather markets on 2026-03-30, reportedly at 0.05 × P × (1−P) ([Pine Analytics](https://pineanalytics.substack.com/p/polymarket-fee-rollout)).
- **Strength:** moderate for Kalshi's taker fee; weak for the rest.

## What it means for our trader

Ranked by expected value to us. All code changes below are **proposals that need Joey's approval**.

1. **Stop the AI forecasters from pricing temperature bins directly.**
   - *Why:* Claude direct scored a Brier of 0.304 against the market's 0.185 on 19 weather markets. Jev's 76% on one 1°C bin needed a forecast about three times sharper than the best public model achieves (F15). This is a task where an LLM reading research has no information advantage over the NBM, and where the market already beats the NBM (F11).
   - *Expected effect:* it removes a demonstrated loss source on a small slice (36 of 1,133 finished markets).
   - *How sure:* fairly sure of the direction; the 19-market sample is far too small to size the effect.
   - *The cheapest form:* a market-filter rule excluding temperature-bin markets from LLM forecasting, which the daily review may be able to set itself within `learning.bounds`. Whether the current filters can express "temperature bin" is not verified.
   - *Fallback:* a small code proposal that caps any single-bin forecast at the F15 ceiling for its lead time.
2. **Do not target more weather markets on the current evidence.**
   - *Why:* to profit, a public-model pricer has to beat a market whose implied forecast already beats the NBM by about 10% in error (2.44 vs 2.70°F; F11). The best combination of public products only *ties* the market (2.45 vs 2.44). The pricer would then also have to clear our ~8.4% trading cost. The two honest 2026 bots found nothing (F19).
   - *Expected effect:* it avoids adding cost-negative volume.
   - *How sure:* moderately sure. The key study is a single non-peer-reviewed paper, but nothing contradicts it.
3. **If weather is pursued, build a non-LLM pricer offline first and test it only where a structural edge could exist.** All three ideas below take live observations, never prices, so they fit the price screen.
   - **Polymarket same-day truncation.** Polymarket settles on the same hourly readings anyone can see live (F7). Once today's hourly maximum is X, every bin below X is worth exactly zero, barring revisions. That rule is exact on Polymarket, but only a lower bound on Kalshi (F4). *Expected effect:* small, frequent, low-risk edges if prices lag. *How sure:* weak; paid "lock" feeds suggest the trade is contested (F20).
   - **The gap between the hourly reading and the official maximum.** Polymarket's US value is a maximum hourly reading, which runs at or below the official maximum (F4, F12). Forecasts such as the NBM target the official maximum. Traders who anchor on the forecast high would overprice the upper bins at LaGuardia, O'Hare, Love Field and Buckley. *How sure:* a hypothesis with no measurement found.
   - **The No side of long-shot bins.** Cheap bins are overpriced (F17). *How sure:* moderate on the bias, weak on profitability after costs. Our own result for always buying the underdog (−31.9% ± 4.6%) is the mirror image and fits this. Note this is a price-based betting rule, not a forecaster; it belongs in strategy gates, not in a model.
4. **Never treat Kalshi and Polymarket "same city" markets as one quantity** (F8). This matters for any model and for any comparison across venues. Our forecasters may not see prices from either venue anyway.

### What would have to be true for an edge

For the pricer to beat the price, at least one of these must hold, measured on our data:
- (a) prices lag observations on the day by more than the cost of crossing the spread;
- (b) Polymarket US prices are centred on the official-maximum forecast rather than on the hourly-reading maximum;
- (c) long-shot bins win less often than their price, by more than fees plus spread.

The pricer's core forecast cannot be the edge on its own: by F11 it at best matches the market.

### 3.1 The algorithm, from forecast to bin probability

1. **Inputs, refreshed each cycle:**
   - US: the NBM NBS/NBE `TXN` and `XND`, and the NBP percentiles when present. On the day itself, also LAMP and the latest hourly NBM or HRRR temperatures for the remaining hours.
   - International: Open-Meteo multi-model hourly forecasts (ECMWF IFS, ICON, JMA, KMA, CMA, UKMO, GEM) and the spread of an ensemble.
   - Observations: latest METARs, including the 6-hourly max/min group, from IEM or the NWS API.
   - Rain: NBM 6- and 12-hour rain probabilities.
2. **Map each station, every event.**
   - Read the station and source from each event's own rules text (Kalshi `rules_primary`; Polymarket `description`), never from a fixed table. Both venues changed stations, sources and units mid-2026 without changing tickers (F1, F7).
   - Keep a lookup from climate-report code to ICAO code (CLINYC→KNYC, CLIMDW→KMDW, and so on).
   - Record which measurement the event uses: `official_max` (Kalshi, Polymarket Hong Kong) or `max_hourly_reading` (other Polymarket events).
3. **Mean (μ).**
   - US: μ = NBM `TXN`, plus a station bias equal to the mean (observed − forecast) over the last ~40 days at the same lead time. The literature's best window is 30–40 days (F13).
   - Day 0: blend in LAMP with weights refit from history. Crosier found LAMP drives most of the same-day improvement (F11).
   - Take the larger of the daytime-maximum forecast and the overnight hours' forecast temperatures, to cover the 4.6% of days with an off-window high (F12).
   - Re-window everything to the settlement day: standard time for Kalshi, probably local clock time for Polymarket (not verified).
   - International: μ = a weighted blend of model hourly maxima plus a station offset. Raw hourly maxima run 1–5°F cold (F12).
4. **Width (σ) by station × season × lead time.**
   - Estimate it from 90–365 days of past errors (a longer window than the bias, because σ from 40 points has about ±11% sampling error).
   - Optionally use the calibration form σ² = c + d·XND² (or c + d·ensemble spread²), fitted by maximum likelihood.
   - Starting values before fitting: 2.1°F on the morning of the day, 2.45–2.7°F the day before, about 3.0°F at 2 days and about 3.3–3.5°F at 3 days (the last two extrapolated, not verified). Use about 60% of these for Miami-like stations, and more for Denver and Chicago in winter.
   - Consider a Student-t instead of a normal curve for fatter tails (not verified from literature).
   - **Never use raw ensemble member counts as probabilities** (29% coverage against 66.7%; F13).
5. **Integrate over the bins, °F (Kalshi, Polymarket US).**
   - With F the predictive cumulative distribution of the continuous maximum:
     - a bin "a° to b°" gets F(b+0.5) − F(a−0.5);
     - "≤ a" gets F(a+0.5);
     - "≥ b" gets 1 − F(b−0.5).
   - For Polymarket US events, F is the distribution of the **maximum hourly reading**. That is the official-maximum distribution shifted down by a station-specific gap δ, estimated from IEM history as official max minus max hourly METAR (F4).
6. **Integrate over the bins, 1°C (Polymarket international).**
   - Work in °C, with σ_C = σ_F / 1.8. A bin "k°C" gets F_C(k+0.5) − F_C(k−0.5).
   - F_C is the distribution of the maximum of the reported METARs, which are often whole °C and sometimes half-hourly. It sits below the true maximum.
   - How METARs round half-degrees, and how Hong Kong's 0.1°C value maps into bins, are not verified, so skip edge cases there.
7. **Cut off at the running observed maximum (day 0).**
   - Final high = max(M_obs, R), where R is the forecast maximum over the remaining hours. Then P(high ≤ x) = 0 for x < M_obs, and F_R(x) for x ≥ M_obs.
   - Polymarket: M_obs is the running maximum on the resolution page itself, so the cutoff is exact.
   - Kalshi: M_obs is only a lower bound. Use the METAR 6-hour maximum group and allow for the official value coming in 1°F or more higher.
   - After the usual peak hour (about 3–5 PM local), most probability collapses onto M_obs's bin.
8. **Rain.**
   - Target: P(at least 0.01 in at the climate station on the standard-time day).
   - Combine the two 12-hour rain probabilities with logistic regression fitted per station and season; they are not independent, so do not just multiply. Their overlap bounds the answer: max(p1, p2) ≤ P ≤ min(1, p1 + p2).
   - Expect the raw NWS values to be 0.02–0.05 low (F16). A trace counts as No on both venues.
   - On the day: if no rain has fallen yet, use only the remaining hours. Kalshi closes the market as soon as rain is reported.
9. **Calibration check, monthly and pooled across stations.**
   - The most likely bin's probability must stay under the F15 ceilings.
   - Bin-level reliability by decile; a PIT histogram (the share of outcomes falling at each percentile of the forecast) should be flat.
   - The mean's error must be ≤ the NBM's, otherwise no σ tuning can save the bins.
   - Brier and log score against the market at the same timestamps.
   - Per-station checks are noisy (±2.4 points on the modal-bin hit rate with a year of data), so pool.
10. **The venue switch in one place.**

    | | Kalshi | Polymarket (most cities) |
    |---|---|---|
    | Measurement | Official maximum | Max hourly reading |
    | Day | Standard-time day | Probably local-clock day |
    | Units and bins | Whole °F, 6 markets with 2°F bins | US: whole °F, 2°F bins; abroad: whole °C, 1°C bins; 11 outcomes |
    | Station | Climate-report station (Central Park, Midway, DFW...) | Airport (LaGuardia, O'Hare, Love Field, Buckley) |
    | Revisions | Ignored after first non-preliminary TWC value | Count until the next day's first reading |

## How to test it on our history

All of this is offline and read-only: no `cycle`, `scan` or `settle` runs, and nothing writes to `papertrade_data/`.

**Step 1. Our own 36 weather markets: diagnosis, not proof.** For each of Claude's and Jev's weather forecasts, compute:
- the bin width and the lead time at the forecast;
- whether the probability exceeded the F15 ceiling, and the hit rate of those forecasts;
- Brier against the market at the same snapshot.

*Supports the bin ban:* most over-ceiling forecasts lose, and the Brier gap stays positive. *At 36 markets* nothing can be concluded about size; report every number with its ±.

**Step 2. Rebuild the truth labels.** For 2024-10 to 2026-10:
- **Kalshi:** take the settled `expiration_value` from the Kalshi API, cross-checked against the IEM climate-report JSON.
- **Polymarket US:** take the maximum routine hourly METAR at KLGA, KORD, KDAL, KBKF and the others (IEM ASOS), converted from tenths of °C, rounded to whole °F, over the local day.
- **Polymarket international:** take the maximum METAR in whole °C. IEM's coverage of international stations is not verified; Ogimet is the alternative.
- **Validation gate:** check the rebuilt labels against at least 50 actually resolved events per venue. If more than 2% disagree, fix the day window or rounding before going further.

**Step 3. Rebuild the forecasts as they were known at each time.**
- Sources: IEM's NBS (from 2018-11), NBE (from 2020-07) and LAMP/MOS archives; Open-Meteo **Previous Runs** (most models from 2024-01) for international cities and HRRR/ECMWF.
- Use only runs issued before each timestamp.
- Do **not** use Open-Meteo's Historical Forecast API for leads beyond today. It stitches together each run's first hours, so it overstates the skill available a day ahead.
- *Sanity gate:* the rebuilt NBM must reproduce Crosier's 2.70 / 2.45 / 2.12°F within about ±0.15°F at his 7 stations. A bigger miss means a pipeline bug.

**Step 4. Fit and score the model out of sample.**
- Walk forward: refit the bias daily from the last 40 days and σ from the last 90–365.
- Report RMSE by lead time, bin Brier, log score and reliability.
- Treat 2026-04/05 (NBM v5.0) as a break.

**Step 5. Compare with the market.**
- Use our own price snapshots (every ~30 min) where we have them, which are only the markets the cycle sampled.
- Use Kalshi or Polymarket price history for the rest. Whether either public API serves historical intraday prices was not verified in these notes, though Crosier and the CalibShi notebook show Kalshi prices can be recovered.
- **Kill** if, over at least 300 event-days, the model's Brier is not lower than the market's by more than the ± range, **or** if a gated paper simulation's after-cost return (our 8.4%, or the cost measured by price band) has a range that touches zero.

**Step 6. The three structural hypotheses.**
- **Truncation (Polymarket):** count the snapshots where a bin already ruled out by the day's hourly maximum still priced above our cost per bet, and how long that lasted. *Confirm:* this happens regularly at prices we could actually trade. *Kill:* it rarely happens, or only inside the spread.
- **Hourly-vs-official gap:**
  - First, from IEM alone, compute the distribution of δ (official max − max hourly METAR) per station, including P(δ ≥ 1°F).
  - Then check whether Polymarket US prices are calibrated to the hourly-reading outcome, or sit too high compared with it.
  - *Confirm:* the upper bins win less often than their price, by more than costs. *Kill:* they are calibrated.
- **Long-shot bins:** in Kalshi settled markets, compare the win rate of bins priced at 10¢ or less with their price, by month.
  - *Confirm:* buying No has an after-fee return above zero with its ± range clear of zero.
  - *Kill:* the bias has faded since the 2025 data, as F17 hints it may.

## Data sources

| Name | URL | Cost / free tier | Limits | Provides |
|---|---|---|---|---|
| Kalshi trade API (public market data) | https://api.elections.kalshi.com/trade-api/v2/ | Free to read; no key needed for the calls used here | Rate limits not verified | Series, markets, rules text, settled values, close times |
| Polymarket Gamma API | https://gamma-api.polymarket.com/events | Free | Not verified | Event rules (station, source, units), bins, dates |
| NWS API | https://api.weather.gov | Free; User-Agent with contact details required | Limit not published ("generous"); 7-day horizon; **no forecast archive** | Grid forecasts, rain probability, station observations |
| NBM v5.0 (GRIB2 and text bulletins) | https://nomads.ncep.noaa.gov/pub/data/nccf/com/blend/prod/ ; AWS `noaa-nbm-grib2-pds` | Free (NOAA open data) | Hourly runs to 264 h; NBP fully populated at 01/07/13/19Z | Max/min mean and SD, percentiles, 6/12-hour rain probability, rainfall amounts |
| IEM MOS/NBM/LAMP archive | https://mesonet.agron.iastate.edu/mos/ | Free | GFS MOS from 2003; NBS 2018-11; NBE 2020-07; LAMP 2020-07 (00/06/12/18Z only) | Station forecasts as they were issued, CSV/JSON |
| IEM climate reports, ASOS/METAR, 1-minute data | https://mesonet.agron.iastate.edu/json/ | Free | International coverage not verified | Truth labels: official daily max/rain, hourly METAR, 6-hour max groups |
| NOAA time series (Polymarket's resolution page) | https://www.weather.gov/wrh/timeseries?site=klga | Free | Web page; no archive depth verified | The exact readings Polymarket settles on |
| weather.com/kalshi | https://weather.com/kalshi | Free page | Rendered in the browser; method not readable | Kalshi's legal settlement values |
| Open-Meteo Forecast / Ensemble | https://open-meteo.com/en/docs/ensemble-api | Free for **non-commercial** use; paid plans unpriced publicly | 600/min, 5,000/hour, 10,000/day | ~30 models; ensembles: ECMWF IFS/AIFS 51, GEFS 31, ICON-EPS 40, GEM 21, WeatherNext 2 64 members; global |
| Open-Meteo Previous Runs | https://open-meteo.com/en/docs/previous-runs-api | Same as above | Hourly variables only; most models from 2024-01 (GFS 2021-03) | "What was forecast 1–7 days earlier": the backtest backbone abroad |
| Open-Meteo Historical Forecast | https://open-meteo.com/en/docs/historical-forecast-api | Same as above | Stitched first hours (overstates lead skill) | Long model history (ECMWF from 2017, NBM from 2024-10-08) |
| ECMWF open data | https://www.ecmwf.int/en/forecasts/datasets/open-data | Free, CC BY 4.0 since 2025-10-01 | Portal keeps ~12 runs; 0.25°; AIFS has no max/min temperature field | IFS HRES/ENS (51), AIFS single/ENS |
| Herbie (Python) | https://github.com/blaylockbk/Herbie | Free | — | Downloader for NBM, GEFS, HRRR, ECMWF |
| Met Office DataHub (site-specific) | https://datahub.metoffice.gov.uk/pricing/site-specific | Free 360 calls/day; £8/month for 900/day | Undated pricing snippet | UK point forecasts |
| Meteostat | https://dev.meteostat.net/terms | Free, CC BY-NC 4.0 | No commercial redistribution; may block | Station history |
| Weather Underground / TWC | https://developer.weather.com/docs/history-on-demand-package | No free API (retired 2018); history is paid enterprise | — | Fallback source for Polymarket; Taipei/Jinan/Zhengzhou resolution |

## Not verified

- **Kalshi:**
  - the ICAO station behind 17 of the 24 climate-report codes (e.g. CLIHOU = Hobby, CLIDFW = DFW);
  - whether the international KXHIGHT* series are paused or seasonal;
  - TWC's own method and what "preliminary" means on weather.com/kalshi;
  - the cause of the Miami 2026-08-29 mismatch;
  - whether the material-error hold has ever been used;
  - the content of the 2026-09-02 rule amendments (secondary source only).
- **Polymarket:**
  - the time zone that defines "this day";
  - how Hong Kong's 0.1°C value maps into whole-degree bins;
  - the meaning of `customLiveness` 900, against the help page's 2-hour challenge period and $750 bond (the API shows a bond of 250);
  - whether SPECI special reports count alongside hourly data (a trader site says yes; the US rules say "Hourly Data").
- **Fees:** the current official Kalshi maker fee (a 25% maker fee vs a claimed maker rebate); Polymarket's maker rebate share (20% vs 25%).
- **Forecast skill:**
  - day-2 and day-3 error for current NBM at these stations (the σ priors are extrapolated);
  - the NBM v5.0 go-live date (2026-04-21 vs 2026-05-05);
  - how well-calibrated the NBM percentiles are;
  - the shape of the error tails;
  - how often the official maximum exceeds the maximum hourly METAR.
- **Markets:**
  - Kalshi's own weather calibration charts (HTTP 429);
  - any measurement of how fast prices react to observations;
  - historical intraday prices from either API;
  - on-chain P&L for any named weather wallet.
- **Data access:**
  - Open-Meteo's view of whether paper trading counts as non-commercial;
  - IEM's coverage of international METARs;
  - KMA, JMA, CMA and Environment Canada access terms;
  - the depth of the AWS NBM and ECMWF-mirror archives.
- **The 76% Wuhan forecast:** whether it was made before or during the day, which decides whether it was impossible or merely aggressive.

# 06: Pricing crypto, oil, gold and stock-index thresholds

Researched 2026-10-09 for `docs/research/briefs/06-price-threshold-markets.md`.

Method: a multi-agent deep-research run (23 sources fetched, 25 claims put to a 3-vote adversarial check, 22
survived), then direct checks by this session: the settlement rules of every relevant Kalshi series and
Polymarket event read from the venues' public APIs today, the four efficiency studies read in their own text,
the worked example recomputed and checked by simulation, and one live snapshot of model vs market. The trader's
`papertrade_data/` was not analyzed; the tests for it are described below.

## Answer in five lines

1. These markets are options. "Above $K at time T" is a European digital worth N(d2); "reach $B by T" is a
   one-touch barrier worth about twice that. Both can be computed from the current price and one volatility
   number, with no AI judgement needed.
2. The volatility input matters more than the formula. For a one-day market, use option implied volatility for
   that same expiry (Deribit, free and live). The 30-day indices (DVOL, VIX, OVX, GVZ) run high over short
   horizons: on 2026-10-09 DVOL said 36% and next-day BTC options said 16–18%.
3. The settlement reference matters more still. Each venue settles on a different price, sampled a different
   way: a 60-second BRTI average, a Binance 1-minute close or high, a Pyth 1-minute high on the *active-month*
   WTI future, the ICE daily settle, or the official S&P close. The WTI miss is consistent with forecasting
   spot when the market paid on the active-month future.
4. The liquid markets already agree with options. In one live snapshot, Kalshi's BTC ladder sat within 1.6
   points of a term-matched lognormal model, and Polymarket's monthly touch ladder within 2.3 points. Published
   studies (n = 255 to 46,282) agree, apart from overpriced tails and some slow touch markets.
5. So a model should replace the AI forecast in these categories (it should at least match the market, where
   Claude direct is worse), but don't expect it to find bets that beat our ~8.4% trading cost. The remaining
   gaps are cheap-tail overpricing and occasional multi-hour lags, both smaller than that cost on most strikes.

## Findings

### F1. The formulas (strong: textbook, checked by simulation)

Notation: S is the current price of the settlement reference, K the strike, B the barrier, T the years to
expiry, σ the annual volatility, N() the standard normal CDF. Rates are ignored: under a day to a few months,
and with 1–4% rates, the effect is a fraction of a point. The price is treated as a martingale (no drift), so
the log-price drifts at −σ²/2.

**Close above K at T (European digital):**

    d2 = [ ln(S/K) − ½σ²T ] / (σ√T)
    P(close above K) = N(d2)            P(close below K) = N(−d2)

**Touch B at any time before T (one-touch, continuous monitoring).** Let y = |ln(B/S)|/σ and let μ be the
log-drift per unit σ, taken in the direction of the barrier (μ = −σ/2 for an up-barrier, +σ/2 for a down-barrier):

    P(touch) = N( (−y + μT)/√T ) + e^(2μy) · N( (−y − μT)/√T )

With μ = 0 this is exactly 2·N(−y/√T), the reflection-principle shortcut: touch = 2 × close-beyond. With the
−σ²/2 drift, the shortcut slightly overstates an up-touch and understates a down-touch.
Sources: [Kou & Wang 2003](https://www.dam.brown.edu/people/huiwang/research/kou_wang_jump.pdf);
[YorkU barrier note 2012](https://hku.info.yorku.ca/files/2021/11/2012_Cross-a-barrier.pdf?x20453);
[Langnau 2010, arXiv 1002.2573](https://arxiv.org/pdf/1002.2573). A verifier's Monte Carlo agreed with the
formula to within discrete-step bias (0.4505 vs 0.4540).

**Discrete monitoring.** If the market checks only at set times (daily settles, 1-minute candles), the touch
probability is lower. The usual fix (Broadie-Glasserman-Kou) moves the barrier away from spot by a factor of
e^(0.5826·σ·√(T/n)), for n checks. The deep-research run refuted the exact error bound (0-3), so treat the
shift as an approximation and check it by simulation. One-minute checks over a month barely matter; daily
checks over a month matter a lot.

**Worked example (computed this session).** BTC at $100,000, target $110,000, 30 days, σ = 40%:

| Quantity | Value |
|---|---|
| σ√T = 0.40 × √(30/365) | 0.1147 |
| d2 = (ln(100/110) − ½·0.16·0.0822)/0.1147 = (−0.0953 − 0.0066)/0.1147 | −0.888 |
| P(close above $110k on day 30) = N(−0.888) | **18.7%** |
| P(touch $110k, continuous), formula above | **38.7%** |
| Reflection shortcut 2·N(−y/√T) | 40.6% |
| Touch with 720 hourly checks (BGK shift) / Monte Carlo, 20,000 paths | 37.5% / 37.6% |
| Touch with 30 daily checks (BGK shift) | 33.0% |

Two lessons for forecasting: a touch is about twice as likely as a close-above at the same level, and a
"reach $X this month" market at 30–40% can be fair even when the target is 10% away.

**What makes this model wrong.** All three come from the same sources as above.
- **Skew.** A digital's true price adds a skew term: digital call ≈ N(d2) − vega·∂σ/∂K. In Langnau's
  equity example, ignoring skew gives 50.5% where the skew-aware price is 44.7%. The size is equity-specific
  (strong as an identity, weak as a size estimate for BTC or oil). The model-free alternative is a tight call
  spread, (C(K−h) − C(K+h))/2h, which carries the whole smile.
- **Jumps.** A jump can overshoot the barrier, which breaks the reflection shortcut. Kou's jump model is
  solvable but heavy to compute (Laplace inversion at 30–80 digits). Monte Carlo is the practical route.
- **When the simple model is good enough.** For short horizons and strikes within about 2σ√T of spot, it
  is enough provided σ matches the horizon (F4, F7). Far tails are where skew and jumps matter, and where
  the markets misprice anyway (F9).

### F2. Exactly what each market settles on (strong: venue rules read today, 2026-10-09)

| Venue / series | Reference price | Sampling | Type | Time |
|---|---|---|---|---|
| Kalshi KXBTCD, KXBTC (BTC above / range) | CF Benchmarks BRTI (USD) | simple average of the 60 seconds before the time | close-above or range | hourly and daily; e.g. "before 4 PM EDT"; strikes end .99 (e.g. 91799.99) |
| Kalshi KXETHD | CF Benchmarks ETHUSD_RTI (ERTI) | same 60-second average | close-above | same |
| Kalshi BTC "how high/low" (KXBTCMAXY etc., terms BTCMINMAX.pdf) | BRTI | "simple average of the BRTI values for any minute … ignoring the top 20% and bottom 20% of values" | touch on minute averages (wording ambiguous; see Not verified) | annual and other periods |
| Kalshi KXWTI (WTI on a day) | ICE WTI futures **daily settlement price**, nearest contract (e.g. the Nov 2026 contract on Oct 8) | one daily settle | close-above | rolls to the next contract 2 business days before last trade; market closes 14:30 ET |
| Kalshi KXWTIMAX / KXWTIMIN | ICE WTI front-month settle prices | maximum (or minimum) of the daily settles since issuance | touch, monitored daily | through the period end |
| Kalshi KXGOLDD | Pyth gold 1-oz/USD | close of the 1-minute candle ending at 5:00 PM EDT, rounded to 2 decimals | close-above | daily |
| Kalshi KXINX, KXNASDAQ100 | "end-of-day" S&P 500 / Nasdaq-100 value (settlement-source link: Google Finance) | official close | close-above or range | 4 PM EDT; the rules note that Kalshi has changed the source agency and underlying for index markets |
| Polymarket "Bitcoin above ___ on [date]" | Binance BTC/**USDT** | final close of the 12:00 noon ET 1-minute candle, strictly above the strike; precision as published | close-above | daily ladders, e.g. 7-day |
| Polymarket "What price will Bitcoin hit in [month]" | Binance BTC/USDT | any 1-minute candle **High** ≥ the strike, 00:00 ET first day to 23:59 ET last day | touch, 1-minute checks | monthly, weekly, daily ladders |
| Polymarket 15-minute "BTC Up or Down" | Chainlink BTC/USD data stream | end of window ≥ start (a tie resolves Up) | close-above at the opening price | 15-minute ET windows |
| Polymarket "What price will WTI hit in [month]" | Pyth 1-minute candles for the **Active Month of ICE WTI futures** ("CLL") | any 1-minute High/Low beyond the strike, **only after market creation** and only in ICE sessions | touch | the Active Month rolls at the open of the contract's third-to-last session |
| Polymarket "What price will Gold (XAUUSD) hit" | Pyth XAUUSD 1-minute candles | any 1-minute High/Low beyond the strike, after creation, Sun 18:00 to Fri 17:00 ET sessions | touch | monthly, weekly |
| Polymarket S&P 500 "close over / close at" | official SPX close via Yahoo Finance ^GSPC history | last trading day of the month | close-above or range | an exact tie with a bracket edge resolves to the higher bracket |

Sources: Kalshi public API `GET /trade-api/v2/markets?series_ticker=…` (`rules_primary`, `rules_secondary`) and
`/series/…` (settlement sources, contract-terms links); the contract terms
[BTC.pdf](https://assets.kalshi.com/contract_terms/BTC.pdf),
[BTCMINMAX.pdf](https://assets.kalshi.com/contract_terms/BTCMINMAX.pdf) and
[COMMODITIES.pdf](https://assets.kalshi.com/contract_terms/COMMODITIES.pdf); Kalshi's CFTC filings
([crypto, 2024-11](https://www.cftc.gov/filings/orgrules/rules1112248605.pdf),
[WTI, 2024-03](https://www.cftc.gov/filings/orgrules/rules03042412315.pdf)); Polymarket Gamma API
`GET /events?slug=…` (`description`). Rules change through amendments, so re-read each series before relying
on it.

What it means for a model:
- **The reference is often not the price a news article quotes.** Polymarket BTC uses USDT on Binance, not
  USD. Oil uses the active-month future, not spot. Gold uses Pyth XAUUSD.
- **Touch markets only count after creation.** Polymarket's "from September 28"-style re-listings start their
  window at creation.
- **Averaging lowers volatility slightly.** A 60-second average has less noise than a single print, but the
  effect is negligible except within the last few minutes.

### F3. The WTI miss is consistent with forecasting the wrong reference (moderate; matching it to our trade is not verified)

The Polymarket September 2026 WTI ladder has five separate "↑ $95" markets, re-listed as the price moved.
Four resolved Yes. The one created 2026-09-28 16:45Z resolved **No**.

Its price history, from the public `clob.polymarket.com/prices-history`:
- about 62¢ at 09-29 00Z;
- 22.5¢ at 09-29 12Z;
- 2.5–3.2¢ on 09-30;
- 0.05¢ at the close.

Over the same days FRED's daily spot WTI ([DCOILWTICO](https://fred.stlouisfed.org/series/DCOILWTICO)) was
$99.37, $96.16 and $97.18 (09-28 to 09-30), all above $95. The market paid only if the Pyth 1-minute high of
the ICE active-month future reached $95 after creation. It didn't, so that future must have stayed below $95
while spot was above it.

A forecaster reading "oil at $97" in the news would say 81–93%; the market's 7¢ was pricing the right
contract. If this is our market, the lesson is that knowing what pays, and its current price, beats any
volatility model.

Strength: moderate for the mechanism, because the price and rule facts are primary. Our market id and the
basis between the active-month future and spot are not verified.

Correction: the deep-research run's illustrative "WTI at $65 → $95" example used a wrong starting price. WTI
traded $84–107 in August and September 2026 (FRED). Don't reuse that example.

### F4. Volatility inputs (strong for the feeds, moderate for which forecasts best)

- **BTC/ETH live implied vol is free.**
  - The Deribit DVOL index: `public/get_volatility_index_data`, no key, candles from 1 second to 1 day.
    Verified live on 2026-10-09; BTC DVOL was 36.4.
    [docs](https://docs.deribit.com/api-reference/market-data/public-get_volatility_index_data.md)
  - Per-option `mark_iv` for every expiry: `public/get_book_summary_by_currency?currency=BTC&kind=option`,
    no key, 950 BTC options returned today.
  - DVOL is a 30-day measure. The at-the-money implied vol by expiry today, read this session:

    | Expiry | Implied vol |
    |---|---|
    | 10 Oct | 18.5% |
    | 11 Oct | 15.8% |
    | 12 Oct | 20.9% |
    | 13 Oct | 25.3% |
    | 16 Oct | 30.8% |
    | 23 Oct | 31.3% |
    | 30 Oct | 32.5% |

    The weekend curve is far below DVOL, so **use the implied vol for the matching expiry, not DVOL, for
    markets under about a week.**
- **Equity, oil and gold implied vol is free but daily and one day stale.**
  - FRED series [VIXCLS](https://fred.stlouisfed.org/series/VIXCLS),
    [OVXCLS](https://fred.stlouisfed.org/series/OVXCLS) and GVZCLS (all three fetched this session; latest
    values are the 10-08 closes: VIX 15.41, OVX 48.40, GVZ 22.68).
  - Cboe CSVs with no key: `cdn-api.cboe.com/api/global/us_indices/daily_prices/{VIX,VIX9D,VXN,OVX,GVZ}_History.csv`.
    VIX goes back to 1990, OVX and GVZ to September 2009. VIX9D (9-day) and VXN both returned 10-08 values today.
  - Caveats:
    - OVX and GVZ come from options on the USO and GLD ETFs, so they are proxies for WTI-futures and gold vol.
    - All of these are 30-day measures except VIX9D.
    - VIX is variance-swap style and sits above at-the-money vol because of skew.
- **Implied vs realized as a forecast.** Giot (2002 working paper; S&P 100 1989–2002, Nasdaq-100 1996–2002):
  - VIX- and VXN-based forecasts had the most information about realized vol at 5, 10 and 22 days, ahead of
    RiskMetrics and GJR-GARCH.
  - But unbiasedness was rejected in almost every case, and VXN ran *above* realized vol (variance risk premium).
  - Strength: moderate; old data, and one sub-claim voted 2-1.
  - Crypto: Dutta 2024 (CME BTC futures; out of sample Apr 2021 to Mar 2022) found that a HAR model with a
    jump-volatility term beat standard HAR. Strength: weak; one study, read from its abstract and published version.
  - Practical reading: implied vol is the best single input but too high on average; realized vol shows what
    the crowd actually prices (F8).

### F5. Free price feeds (moderate; checked live today unless marked)

| Feed | Endpoint | Notes |
|---|---|---|
| Coinbase spot BTC-USD | `api.coinbase.com/v2/prices/BTC-USD/spot`; candles at `api.exchange.coinbase.com/products/BTC-USD/candles?granularity=60…86400` | no key; 300 candles per call. One of BRTI's constituent exchanges (background knowledge, not verified this session) |
| Kraken | `api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1` | no key; 1-minute OHLC (about 720 most recent) |
| Binance BTCUSDT (Polymarket's reference) | `api.binance.com/api/v3/klines` is **geo-blocked from the US** ("restricted location"); `data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m` works | the mirror returned a live 1-minute candle today |
| Deribit | F4 | also gives `underlying_price` per option |
| FRED | `fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>` | no key for CSV; daily; DCOILWTICO is **spot** WTI, not the settlement future |
| Kalshi / Polymarket history | Kalshi `trade-api/v2` markets (settled, with rules); Polymarket Gamma events and `clob.polymarket.com/prices-history` | public; used in F3 and F8 |

CF Benchmarks BRTI itself, the ICE WTI settle history, and Pyth's CLL and XAUUSD candles are the true
settlement series. No free historical source for them was verified (see Not verified).

### F6. Polymarket BTC prices track options well for "above" bets and less well for touch bets; tails are overpriced (moderate)

Fabi, Marfè, Ruffo & Schönleber, "Are Decentralized Prediction Markets Efficient? Evidence from Bitcoin
Options", a talk paper at FC'26 DeFi
([pdf](https://fc26.ifca.ai/defi/papers/market-efficiency-prediction-markets.pdf), read in full).
- **Sample:** 255 Polymarket BTC bets, March 2024 to May 2025.
- **Benchmark:** hourly Deribit implied-vol surfaces (via Amberdata) turned into risk-neutral densities;
  touch bets were priced with the reflection principle.
- **Alignment:** mean correlation with the option-implied price was 0.97 for Above bets, 0.83 for Range,
  0.79 for Reach and 0.73 for Dip.
- **Tail events** (BTC to $200k or below $40k) were "persistently" priced above near-zero option-implied
  probabilities.
- **Mispricing** was largest at inception, near expiry for touch bets (a U-shape), on weekends and after
  macro shocks.
- Strength: moderate. It is a short talk paper with no gap sizes, standard errors or costs, and the full
  paper is not out.

### F7. A measured gap of 6–11 points against options, half-life about 4 hours, arbitrage marginal after costs (weak to moderate)

Portnaya, "Do Prediction Markets Match Option Prices? Bitcoin Threshold Evidence from Binance and Polymarket",
[arXiv 2606.19517](https://arxiv.org/abs/2606.19517), 2026-06-17 (abstract read).
- **Main contract:** a September 2023 BTC contract, 214 hourly observations, mean gap 5.6 points (t = 6.46).
- **Pooled across three markets:** 287 observations, 6.3 points against Binance options and about 11 points
  against Deribit options.
- **Pattern:** the gap is largest at low implied probabilities and long maturities.
- **Persistence:** it mean-reverts with a half-life of about 4 hours.
- **Arbitrage:** a delta-hedged proxy stays profitable after "conservative" costs, but only with marginal
  statistical precision.
- The direction of the gap is not stated in the abstract.
- Strength: weak to moderate. The sample is tiny (3 contracts, mostly 2023), it is an unrefereed single-author
  preprint, and the market was thinner then than now.

### F8. Polymarket monthly BTC touch prices are calibrated and sit nearer a realized-vol model than an implied-vol one (moderate)

Olsen, "The informational content of prediction markets: evidence from Polymarket Bitcoin contracts", MSc
thesis, Aalborg University, 2026-05-31
([record](https://projekter.aau.dk/the-informational-content-of-prediction-markets-evidence-from-polymarket-bitcoin-contracts-628468cf.html),
abstract read).
- **Sample:** 258 monthly barrier contracts, October 2024 to March 2026 (plus 252 ETH contracts).
- **Calibration:** a Mincer-Zarnowitz test cannot reject that prices are unbiased forecasts.
- **Against barrier models:** prices "track" a closed-form barrier model run on realized vol and sit below
  the same model run on implied vol (variance risk premium).
- **Information:** they add little beyond spot and options.
- Strength: moderate. A thesis, not peer-reviewed, but the sample covers our period.

### F9. Kalshi's favourite-longshot bias holds in its crypto and financial markets (strong for the pattern, moderate for today's size)

Bürgi, Deng & Whelan, "Makers and Takers: The Economics of the Kalshi Prediction Market", UCD, January 2026
([pdf](https://www.karlwhelan.com/Papers/Kalshi.pdf), read in full).
- **Sample:** 46,282 Kalshi contracts with at least $1,000 volume, 2021 to April 2025. Kalshi's hourly
  crypto and stock-index markets are **excluded**.
- **Cheap contracts:** those at 10¢ or less lose over 60% after fees.
- **Expensive contracts:** those above 70¢ earn small, statistically significant positive post-fee returns.
- **The bias is strongest in crypto:**

  | Category | Price coefficient | Prices (n) |
  |---|---|---|
  | Crypto | 0.058 | 8,150 |
  | All categories | 0.034 | not given |
  | Financials | 0.032 | 27,123 |

- **Fees during the sample:** taker fee 0.07·P·(1−P) per contract, rounded up; makers paid nothing.
- **Trend:** the bias was weaker in 2025 (coefficient 0.021).
- Strength: strong for the pattern; moderate for today's size, since current fees are brief 10's question.

### F10. Live snapshot: the liquid ladders agree with a term-matched model (anecdotal: one moment, strikes correlated)

Taken 2026-10-09 21:42Z: BTC $82,494 (Coinbase), DVOL 36.4.
- **Kalshi KXBTCD-26OCT1017** (above $K at 5 PM EDT Oct 10, about 23 hours; 12 strikes with mids between
  3¢ and 97¢ and spreads of 10¢ or less):
  - With DVOL (36%), the model differs from the mid by 14.2 points on average. The market's ladder is much
    steeper.
  - Backing out implied vol from the Kalshi mids gives 15–17%.
  - That matches Deribit's 10 Oct (18.5%) and 11 Oct (15.8%) at-the-money options.
  - With σ = 17%, the mean absolute gap is **1.6 points** and the mean gap +0.5. The largest are +3.3 to
    +3.4 points at $82,000–82,250, about the size of the 1¢ spread plus the fee.
  - Realized vol from hourly Coinbase candles was 27% (24 h), 38% (72 h) and 32% (about 14 days). A
    realized-vol model would also have been wrong here.
- **Polymarket "What price will Bitcoin hit in October 2026"** (22.3 days, 18 strikes; continuous-touch
  model at DVOL 36%):
  - mean absolute gap 2.3 points, mean −1.1;
  - mid-range strikes sit 2–8 points *below* the model (consistent with F8);
  - the far tails ($60k–67.5k down, $100k–105k up) sit 0.3–2 points *above* it, at 1.4–4.5¢ against model
    values of 0–3% (consistent with F6).

Script and output are in this session's scratchpad, not the repo.

## What it means for our trader

Ranked. Each item is a code or policy change, so each waits for Joey's yes. None touches the price screen,
because the model reads the underlying (BTC, oil, gold, index) and its options, never the prediction market's
own price.

1. **Stop using AI judgement as the forecast in these markets; compute it.**
   - Parse each market's rules into: reference, threshold, direction, close-above vs touch, window, monitoring.
   - Price it with F1, using the reference price from F2 and expiry-matched vol from F4.
   - Expected effect: Brier close to the market's (0.146 on our 61 crypto markets) instead of Claude direct's
     0.186.
   - Confidence: high that it beats Claude direct (the market is already about this model, per F6, F8 and
     F10); low that it beats the market.
2. **Until that exists, skip these categories, or use the model as a veto.**
   - The veto: refuse any bet where the AI forecast and a crude model (spot from a free feed, vol from
     DVOL/VIX/OVX/GVZ) disagree by more than about 20 points.
   - That alone would have flagged an 81–93% forecast on a touch market priced at 7¢.
   - Expected effect: removes the worst misses. Confidence: moderate, because a crude model with the wrong
     reference also errs (F3).
3. **Expect few or no bets that clear costs.**
   - The liquid ladders are within about 2 points of the model (F10).
   - The documented gaps total a few points and decay with a half-life of about 4 hours (F7), against our
     roughly 8.4% trading cost.
   - The only systematic pattern is that cheap tails are overpriced (F6, F9). Exploiting it means buying NO
     on 95–99¢ contracts for 1–3% gross, before fees and capital lock-up; that conflicts with the current
     `min_ask` floor logic and needs brief 10's fee answer.
   - Confidence: moderate.
4. **Never price a market off a news quote of "the price".**
   - Oil: settles on the active-month future (Polymarket) or the front-month settle (Kalshi).
   - BTC on Polymarket: USDT on Binance.
   - Touch windows: count only after creation.
   - Expected effect: avoids misses like F3. Confidence: high on the mechanism.
5. **Treat ladder strikes as one bet, not many.**
   - Every strike on a ladder moves with one price.
   - Exposure and sample-size counts should group by event, or ten correlated strikes will look like ten
     independent edges.
   - Confidence: high.

## How to test it on our history

For the main session. Our crypto set is 147 finished markets, probably only a few dozen independent events.
That is enough to compare forecasters, not to prove a betting edge. Add the venues' own public history (step 6)
before concluding anything about edge.

1. **Select and parse.** Take finished markets tagged crypto by `learn.category`, plus oil, gold and index
   markets by regex on question or rules (`WTI|crude|gold|XAU|S&P|SPX|INX|Nasdaq|NDX`).
   - From `rules`, extract: reference, threshold, direction, type (close-above, range or touch), window start
     (creation time for Polymarket touch markets) and end, and monitoring (60-second average, 1-minute
     candle, daily settle).
   - Report how many parse cleanly. A parse failure rate above 10% means the parser, not the model, is the
     first job.
2. **Rebuild the inputs at first-look time** (and at every snapshot for the time-series test). Inputs:
   - **Price:** Coinbase or Kraken 1-minute BTC-USD as a BRTI proxy; `data-api.binance.vision` for
     BTCUSDT. For oil, gold and indices, record which proxy was used and how far it is from the settlement
     contract.
   - **Vol:** three variants: DVOL (or prior-day VIX, VIX9D, OVX, GVZ), trailing realized vol (24 h, 7 d),
     and a blend.
   - Per-expiry Deribit implied-vol history is not free (Amberdata or Tardis), so expiry-matched vol can only
     be tested going forward. Start logging Deribit `mark_iv` per expiry at each cycle if Joey approves that
     code change.
3. **Score**, on the same markets, with a first-look spread of 10¢ or less:
   - Brier for the model (each vol variant), the market mid, Claude direct, Jev + research, and a
     model–market blend.
   - Paired differences, with bootstrap confidence intervals **clustered by event**. Split by asset, by
     touch vs close-above, and by horizon (under 1 day, 1–7 days, more than 7 days).
4. **Decision rules.**
   - *Confirms #1:* model Brier better than Claude direct by more than 2 clustered standard errors, and
     within ±0.01 of the market.
   - *Kills #1:* model no better than Claude direct, or parse failures above 20%.
   - *Edge (#3):* model minus ask, after the measured 8.4% cost, positive at 95% confidence on clustered
     resamples. Expect this to fail on our sample, and don't size bets on a pass from fewer than several
     hundred events.
5. **The WTI case (F3).**
   - Confirm which market our 81–93% forecast was on (venue, id, creation time, the price at our first look).
   - Compare the forecast to the model run on the right reference (the active-month future) vs on spot.
   - If our market is not the Polymarket "from September 28" one, re-check F3.
6. **Widen the sample with public data, without trading.**
   - Pull settled Kalshi KXBTCD/KXETHD events: rules and settlement value from `trade-api/v2/markets`, price
     history from Kalshi's candlestick endpoint (not verified this session).
   - Pull resolved Polymarket BTC ladders: Gamma events plus `prices-history`.
   - Score market mid vs model on thousands of strikes across hundreds of events. This tests the market,
     not our forecasters, and it decides whether any tail or lag edge is worth building.
   - Confirm an edge only if it survives the ask, the fees and event clustering.

## Data sources

| Name | URL | Cost / limits | Provides |
|---|---|---|---|
| Deribit public API | `https://www.deribit.com/api/v2/public/get_volatility_index_data`, `…/get_book_summary_by_currency` | free, no key; general per-IP rate limits | live and historical DVOL (BTC, ETH); live per-option `mark_iv` and underlying price (option history is not free) |
| FRED | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS` (also OVXCLS, GVZCLS, DCOILWTICO) | free; daily, posted next morning | VIX, OVX and GVZ closes; spot WTI (not the settlement future) |
| Cboe index history | `https://cdn-api.cboe.com/api/global/us_indices/daily_prices/{VIX,VIX9D,VXN,OVX,GVZ}_History.csv` | free, no key; daily | full daily OHLC history of the vol indices |
| Coinbase Exchange | `https://api.exchange.coinbase.com/products/BTC-USD/candles` | free, no key; 300 candles per call | BTC-USD 1-minute to daily candles (BRTI proxy) |
| Kraken | `https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1` | free; recent window only | 1-minute OHLC |
| Binance market-data mirror | `https://data-api.binance.vision/api/v3/klines?symbol=BTCUSDT&interval=1m` | free; `api.binance.com` is geo-blocked from the US | BTCUSDT candles, Polymarket's BTC settlement source |
| Kalshi trade API | `https://api.elections.kalshi.com/trade-api/v2/markets`, `/series/{ticker}` | free, public reads | rules, strikes, settlement sources, contract-terms links, settled results |
| Kalshi contract terms | `https://assets.kalshi.com/contract_terms/{BTC,ETH,BTCMINMAX,COMMODITIES,INX,NASDAQ100,GOLD}.pdf` | free | formal definitions of the underlying |
| Polymarket Gamma and CLOB | `https://gamma-api.polymarket.com/events?slug=…`, `https://clob.polymarket.com/prices-history?market=<token>` | free, public | rules text, outcomes, price history |

## Not verified

- **Which market the WTI 81–93% forecast was on, and the price gap behind it.** Whether it was Polymarket's
  "↑ $95 from September 28" (F3). The spot-vs-active-month gap that would explain the No was inferred from the
  outcome and FRED spot, not measured on ICE or Pyth data.
- **Kalshi's BTC "how high/low" terms.** Whether the trimming applies within each minute or across all
  minutes. The wording ("simple average … for any minute after Issuance … ignoring the top 20% and bottom 20%")
  is ambiguous; ask Kalshi or read a settled market's value.
- **The source and close time for Kalshi index markets** after the "modified Source Agency and Underlying"
  change. The series page links Google Finance; INX.pdf was not read.
- **The direction of the gap in the Portnaya preprint (F7),** and the size of any gap in the Fabi et al. talk
  (F6). Neither text gives them.
- **Free historical sources** for BRTI, ICE WTI settles, Pyth CLL and XAUUSD 1-minute candles, and Deribit
  per-option implied vol. Pyth has a public benchmarks API, but its history depth and symbols were not checked.
- **Kalshi's candlestick or price-history endpoint** for settled markets.
- **Kalshi's current fees,** including maker fees introduced after April 2025. That is brief 10's question.
- **How often the trader actually sees hourly and daily BTC ladders.** Both venue scans require markets to
  close 12 hours or more ahead (`papertrade/markets.py`), so same-day "5 pm" markets reach the trader only the
  day before. Count them in our data.

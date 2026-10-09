# 09: Sports prices against the sharp sportsbooks

Researched 2026-10-09 for `docs/research/briefs/09-sports-vs-sharp-books.md`.

## Answer in five lines

1. **Nobody has published a measurement of Kalshi or Polymarket sports prices against Pinnacle, Circa or Betfair.** That covers gaps by league, gaps by market type, and the lag after news. The only recent head-to-head (285 NFL games, 2025-26) set Kalshi against DraftKings, a retail book, and found Kalshi slightly *more* accurate. So whether a profitable gap exists is untested, and our own history plus a month of bought odds history can answer it.
2. **Kalshi's liquid game markets are already priced like a sharp book.** On 2026-10-09 the two sides of NFL, ATP, EPL and college-football games with real volume added up to only 1–2¢ over $1, a tighter margin than any sportsbook. A developer who watched Kalshi against Polymarket for a day saw 870 gaps with a median life of about 9 seconds. Our trader runs once an hour, so it cannot chase lags. The only version it can run is "buy when the ask, after fees, is below the de-vigged Pinnacle price", tested on prices that last.
3. **Costs set the bar at about 2.5–3¢ at a 50¢ price.** Kalshi's taker fee is 0.07·p·(1−p) per contract (1.75¢ at 50¢), and MLB has been at half that since 2026-08-07. **Polymarket sports markets now charge a taker fee of 0.05·p·(1−p) (1.25¢ at 50¢), but `policy.json` models Polymarket fees as 0.** Our Polymarket sports bets have been costed too cheaply. Add our 1¢ slippage and a bet needs the fair price to sit about 2.5–3¢ (5–6% of stake) above the ask before it breaks even.
4. **De-vig with the power method, and use Shin as a check.** Both beat the plain "divide by the sum" method in published comparisons, but only by about 0.004 in probability. On a low-margin Pinnacle line the choice barely matters.
5. **Score the strategy by closing-line value (CLV), not by profit.** CLV is the de-vigged closing price over the price we paid. A profit test at 50¢ prices needs thousands of bets to show a 3% edge; CLV needs tens to low hundreds. The data costs **$30 a month** (The Odds API 20K plan; one call returns Pinnacle, Kalshi and Polymarket together for 1 credit). Expect the edge to be **zero or below our costs on liquid markets** until a backtest says otherwise.

## Findings

### Do prediction-market sports prices differ from sharp books?

**F1. No published study compares Kalshi or Polymarket sports prices with a sharp book. The nearest one compares Kalshi with a retail book and finds Kalshi slightly better.**
- **Evidence:** The research harness ran five search angles, read 22 sources and checked 25 claims by adversarial vote, and found no source measuring gaps against Pinnacle, Circa, Betfair, Novig or ProphetX by league, market type or timing. The one head-to-head is a Claremont McKenna undergraduate thesis (April 2026): on **285 NFL games in 2025-26**, Kalshi's win probabilities had a slightly lower Brier score than DraftKings', a difference that was only marginally significant. The abstract says the gap shrinks once you control for how each platform spreads its probabilities, and that both platforms get *less* accurate close to kickoff ([CMC thesis 4214](https://scholarship.claremont.edu/cmc_theses/4214)). The full PDF returned 403, so the Brier values are not verified.
- **Strength:** weak. It is an undergraduate thesis, read from the abstract only, and it uses a retail book as the yardstick.

**F2. On 2026-10-09, Kalshi's liquid game markets carried a two-sided margin of 1–2¢, below any sportsbook's margin.**
- **Evidence:** I measured this from the public Kalshi API (`/markets?series_ticker=…&status=open`, read 2026-10-09 21:55 UTC). Margin here is the yes-asks of every outcome in an event added up, minus $1.

  | Series | Events with a bid on every side | Median margin | Events where each side traded ≥1,000 contracts | Their median margin |
  |---|---|---|---|---|
  | NFL games | 28 | 2¢ | 23 | **1¢** |
  | MLB games | 5 | 2¢ | 5 | 2¢ |
  | EPL games (3-way) | 21 | 2¢ | 8 | 1.5¢ |
  | ATP matches | 19 | 1¢ | 9 | 1¢ |
  | NHL games | 53 | 4¢ | 8 | 1¢ |
  | College football | 212 | 3¢ | 65 | 1¢ |

  Median bid-ask spreads tell the same story: 1¢ on NFL, MLB, EPL, ATP and WNBA, but 3–3.5¢ on NHL and NBA (before the season) and 42¢ on the first 200 open college-football markets, most of them weeks away with no volume. On 2026-10-02 a news piece measured Kalshi's NFL straight-bet margin at 4.28%, against 4.41% at FanDuel and 4.47% at DraftKings, over 28 Week-4 data points. That figure *includes* Kalshi's fee, and the piece does not mention Pinnacle ([RotoWire](https://www.rotowire.com/article/kalshi-beats-draftkings-fanduel-on-nfl-week-1-pricing-134248)).
- **What it means:** the big Kalshi sports markets are made by professionals quoting tighter than the books. Susquehanna is widely reported to be Kalshi's largest market maker; it has been a committed market maker since 2024 and took its biggest sports loss in June 2026 ([BusinessWire 2024-04-03](https://www.businesswire.com/news/home/20240403664852/en/Kalshi-Onboards-Its-First-Dedicated-Institutional-Market-Maker); [InGame](https://ingame.com/susquehanna-biggest-sports-kalshi-volume-knicks), secondary). Whether those makers price off sportsbook feeds is **not verified**. Large, lasting gaps against Pinnacle are unlikely on these markets.
- **Strength:** strong as a snapshot (primary data, one evening). It is one point in time, so it says nothing about how the margin moves over a game week.

**F3. Gaps between two fast venues close within seconds.**
- **Evidence:** A developer built a matcher for Kalshi against Polymarket sports and e-sports covering about 98% of markets. Over one 24-hour window it logged **870 cross-venue gaps**: median life about 9 seconds, 96% closed within 30 seconds. Across a whole high-volume football match, the total opportunity after fees was $439 ([dev.to, July 2026](https://dev.to/michaelmustopo/built-a-prediction-market-arbitrage-no-sizable-arbitrage-found-36cf)).
- **Strength:** anecdotal (one developer, one day, no published code or data). It agrees with F2, though.

**F4. Older peer-reviewed work shows the mechanism works when the sharp price is compared with *slower* books: the bigger the gap, the bigger the return.**
- **Evidence:** Franck, Verbeek & Nüesch, *International Journal of Forecasting* 26 (2010). The sample is 5,478 Big-5 European football matches, 2004/05–2006/07. Betfair was slightly more accurate than the average of eight soft bookmakers (home-win Brier 0.2221 against 0.2235). Betting at a bookmaker whenever Betfair's implied probability was higher returned **+1.4% on 8,234 bets**, against −7.2% for betting everything. On the largest 5% of gaps (821 bets) it returned **+10%** ([PDF](https://unifr.ch/tim/en/assets/public/uploads/Publication%20list/2010/IJoF_Franck_Verbeek_Nuesch.pdf)).
- **Caveats:** the odds were Friday/Tuesday snapshots rather than closing prices, and the cut-offs were chosen in-sample with no significance test (by our verifier's estimate, +10% on 821 bets is about 2 standard errors at best). The bets went to soft bookmakers, with no limits or costs. The venue we would bet on (Kalshi, Polymarket) is now the *tight* one, the reverse of this setup.
- **Strength:** moderate for the mechanism, weak as evidence of an edge today.

**F5. Kalshi as a whole shows a favourite-longshot bias, but there is no sports-only estimate, and it was fading in 2025.**
- **Evidence:** Bürgi, Deng & Whelan, UCD working paper WP25/19 (July 2025). The sample is 313,972 Kalshi contract prices, 2021 to April 2025, limited to contracts with at least $1,000 volume and a final spread of 20¢ or less. Contracts under 10¢ lost over 60% after fees. Contracts above 50¢ earned small positive returns, significant above 70¢. The bias measure fell from 0.048 (2024) to 0.021 (2025, significant only at 10%) ([UCD PDF](https://www.ucd.ie/economics/t4media/WP2025_19.pdf)). The authors' February 2026 revision says the result holds without the category that contains sports, but the paper gives no sports estimate. The data end about four months after Kalshi's sports volume took off.
- **Against it, our own data:** buying the sports favourite at the ask lost 1.6% ± 2.6% over 606 markets (`docs/REBUILD_SCOPE.md`). That fits a fair price minus our costs. Brief 01 covers this bias in depth.
- **Strength:** moderate for Kalshi overall, weak for sports.

**F6. A sharp closing price is close to calibrated, which is what we need to use it as the fair-value yardstick.**
- **Evidence:** Hubáček & Šír, *International Journal of Forecasting* 39(2), 2023 ([arXiv 2010.12508](https://arxiv.org/abs/2010.12508v1)). It covers NBA moneylines, with Pinnacle closing odds for 2010–2014 pooled with mixed bookmakers for 2000–2010. Smoothed implied probabilities tracked outcomes closely, and the apparent miscalibration at long odds was put down to small samples. The check is visual, with no formal test, and Pinnacle is not tested on its own.
- **Strength:** moderate.

### Removing the bookmaker's margin

**F7. The plain method (divide each 1/odds by their sum) ignores how books load their margin. The power and Shin methods correct for it and are slightly more accurate.**
- **Definitions** ([CRAN `implied` package](https://search.r-project.org/CRAN/refmans/implied/html/implied_probabilities.html), primary):
  - **multiplicative (plain):** pᵢ = (1/oᵢ) / Σ(1/oⱼ);
  - **power:** pᵢ = (1/oᵢ)^k, with k solved so the pᵢ add up to 1;
  - **Shin:** models a share z of insider money and solves for the pᵢ and z together.

  The plain method spreads the margin in proportion to probability, so it leaves favourites slightly too low and long shots slightly too high.
- **Evidence on accuracy:**
  - Clarke, Kovalchik & Ingram (2017), on three datasets from three sports: the power method "universally outperforms the multiplicative method and outperforms or is comparable to the Shin method" ([AJSS](https://www.sciencepublishinggroup.com/article/10.11648/j.ajss.20170506.12)).
  - On out-of-sample football in four leagues in 2016-17, Shin put more probability on the actual result than the plain method in every league, for example Premier League 0.4516 against 0.4480 ([arXiv 1802.08848](https://arxiv.org/pdf/1802.08848)).
  - On bet365 Premier League home wins over 6,840 matches (2002/03–2019/20), Shin was unbiased and the plain method was not (p = 0.015). In La Liga both underrated favourites ([Annals of OR, 2022](https://link.springer.com/article/10.1007/s10479-022-04722-3)).
- **Size:** the gains are 0.0035–0.0047 in mean probability on the result. Every dataset comes from soft books, whose margins (5–10%) are much bigger than Pinnacle's.
- **Strength:** strong that power and Shin beat the plain method; weak that the difference matters on a low-margin sharp line.

### Data

**F8. One The Odds API call can return Pinnacle, Kalshi and Polymarket prices for the same games, but its Pinnacle prices are scraped and may lag.**
- **Coverage (vendor pages, read 2026-10-09):** the `us_ex` region holds Kalshi, Polymarket, Novig, ProphetX and BetOpenly. Pinnacle is only in `eu`, marked "Odds are from public website which may incur a delay". Betfair Exchange is available as `betfair_ex_uk`, `betfair_ex_eu` and `betfair_ex_au`. Circa is not listed ([bookmaker list](https://the-odds-api.com/sports-odds-data/bookmaker-apis.html)).
- **Cost rules ([v4 guide](https://the-odds-api.com/liveapi/guides/v4/)):**
  - a live odds call costs "1 per region per market";
  - "every group of 10 bookmakers is the equivalent of 1 region", so `bookmakers=pinnacle,kalshi,polymarket&markets=h2h` costs **1 credit**;
  - the events list is free;
  - the bookmaker-level `last_update` field is deprecated in favour of the market-level one, which we would use to drop stale Pinnacle quotes.
- **Not verified:** how long the Pinnacle delay is (one competitor says about 60 seconds), and which sports and market types the Kalshi and Polymarket keys actually carry. Pinnacle reportedly closed its own public API in July 2025; the only source is a secondary blog.
- **Strength:** strong (vendor documentation), apart from the delay.

**F9. The Odds API costs $30–59 a month, and its history starts in June 2020.**
- **Plans:** Starter is free (500 credits a month); 20K credits is $30 a month; 100K is $59; 5M is $119; 15M is $249. History is on paid plans only.
- **History:** moneylines, spreads and totals start on 2020-06-06, in 10-minute snapshots, every 5 minutes from September 2022. Props start on 2023-05-03.
- **Historical cost:** a historical call costs 10 credits per region per market, and an empty response is free ([pricing](https://the-odds-api.com/), [historical](https://the-odds-api.com/historical-odds-data/)).
- **Not verified:** how far back the Kalshi and Polymarket keys go in the history.
- **Strength:** strong (vendor pages, read 2026-10-09; prices can change).

**F10. Free or one-off alternatives fit a backtest, not a live feed.**
- **Betfair Exchange API:** a free "delayed" key gives prices 1–180 seconds late, 3 price levels and no traded volume. A live key costs a one-off £299 activation fee, and Betfair is generally closed to US residents ([Betfair developer docs](https://betfair-developer-docs.atlassian.net/wiki/x/URAp); confirmed through search snippets, the page didn't render).
- **football-data.co.uk:** CSVs with Pinnacle pre-closing odds (`PSH/PSD/PSA`) and closing odds (the same with a `C`, e.g. `PSCH`), plus Betfair Exchange odds, for European football ([notes](https://www.football-data.co.uk/notes.txt)). This only checks the de-vig method and the soccer side; it has no Kalshi or Polymarket prices. From which season closing odds start, and the terms of use, are not verified.
- **Not checked:** OddsJam, OpticOdds, SportsGameOdds and OddsPortal scraping.
- **Strength:** moderate.

### Fees on sports markets

**F11. Kalshi charges sports takers 0.07·p·(1−p) per contract (scaled by each series' multiplier). It charges makers a quarter of that, and MLB has been at half rate since 2026-08-07.**
- **Evidence (primary, Kalshi API, read 2026-10-09):** `GET /series/{ticker}` returns `fee_type: quadratic_with_maker_fees` for NFL, NBA, MLB, NHL, college football, EPL and ATP. `fee_multiplier` is 1 for all of them except **MLB at 0.5**. The fee-change log (`/series/fee_changes?series_ticker=KXMLBGAME`) shows MLB moving to 0.5 on **2026-08-07**, from 1 since 2025-10-04. NFL has been at 1 since 2026-01-01.
- **Formula (secondary):** taker fee = M × 0.07 × C × p × (1−p), maker fee = M × 0.0175 × C × p × (1−p) ([Allium docs](https://docs.allium.so/historical-data/predictions/kalshi/series-fee-changes)). Sources disagree on rounding (up to $0.0001 or up to the cent). Kalshi's own fee schedule PDF returned a bot challenge, so the exact wording is **not verified** from Kalshi.
- **For us:** `engine.fee_per_contract` applies 0.07 to every Kalshi market, so it overcharges MLB by 2× (0.875¢ too much at 50¢). The engine is right not to apply maker fees because it only takes.
- **Strength:** strong for the multipliers (primary); moderate for the coefficients.

**F12. Polymarket sports markets now charge takers 0.05·p·(1−p). Our policy models Polymarket fees as zero.**
- **Evidence:** Polymarket's fee page gives "fee = C × feeRate × p × (1 − p)", with Sports at a taker rate of **0.05**, no maker fee and a 15% maker rebate ([docs.polymarket.com/trading/fees](https://docs.polymarket.com/trading/fees), no date on the page). The Gamma API agrees. On 2026-10-09, all 100 of the top open moneyline markets by 24-hour volume showed `feesEnabled: true`, `feeType: sports_fees_v3` and `feeSchedule {rate: 0.05, exponent: 1, takerOnly: true}`.
- **For us:** `policy.json` has `polymarket_per_contract: 0.0`, so every Polymarket sports bet has been costed up to 1.25¢ too cheaply. When the fee started is **not verified**, so how many of our past bets it affects is unknown. Brief 10 covers fees in general; this one changes the sports break-even, so it is reported here.
- **Strength:** strong (primary docs plus live API).

**F13. Fees at the prices we bet:**

| Price | Kalshi (×1) | Kalshi MLB (×0.5) | Polymarket sports |
|---|---|---|---|
| 30¢ / 70¢ | 1.47¢ | 0.74¢ | 1.05¢ |
| 50¢ | 1.75¢ | 0.88¢ | 1.25¢ |
| 85¢ | 0.89¢ | 0.45¢ | 0.64¢ |

Add the 1¢ slippage our engine charges. At 50¢, a Kalshi NFL bet needs the fair price **2.75¢ above the ask** to break even (5.5% of stake), MLB 1.9¢ and Polymarket 2.25¢. A 1–2¢ gap of the size F2 suggests for liquid markets would not survive these costs.

### Closing-line value

**F14. CLV is the standard skill measure, and its evidence is mostly practitioner work. One careful 2026 analysis warns that CLV only pays when it exceeds the margin.**
- **Evidence:** the economist Karl Whelan, writing on his blog on 2026-08-12, used 3,670 NBA games (2022/23–2024/25) with The Odds API quotes from about ten books. Only the top tenth of bets ranked by CLV made meaningful profit (+11.4%). The next tenth averaged 5% CLV but only +0.2% profit. His point: you must beat the close by more than the margin ([karlwhelan.com](https://www.karlwhelan.com/?p=2595)). His "close" is the median across books, not Pinnacle. Pinnacle's own articles on CLV did not render when fetched, so their content is **not verified**.
- **Strength:** moderate that CLV tracks profit; anecdotal on the exact size.

**F15. How many bets each test needs (derived here; the arithmetic is standard, the inputs are assumptions).**
- **Profit test.** A $1 stake at price p has a profit standard deviation of about √((1−p)/p): 1.0 at 50¢, 0.65 at 70¢. To show a +3% edge at 2 standard errors at 50¢ takes n ≈ (2 × 1.0 / 0.03)² ≈ **4,400 bets**. Our own ±2.6% on 606 favourites matches this formula.
- **CLV test.** Per bet, CLV = (de-vigged closing probability ÷ cost paid) − 1. Its noise is only how much the price moves between our entry and the start. If that move has a standard deviation of about 3¢ at 50¢ (an assumption to measure from our snapshots, **not verified**), CLV has an SD of about 6%. A +3% mean then shows at 2 standard errors in about **16–100 bets**, depending on the true SD.
- **Strength:** strong arithmetic; the CLV input is assumed.

## What it means for our trader

Ranked by expected value to us.

1. **Fix the sports fees before trusting any sports result.**
   - Charge Polymarket sports 0.05·p·(1−p) and read Kalshi's `fee_multiplier` per series, or store it in `policy.json` per series prefix.
   - Effect: Polymarket sports costs rise by 1–1.25¢ a contract, and MLB costs on Kalshi fall by about 0.9¢. Every past and future sports P&L number moves. This is a code change, so it needs Joey's yes.
   - Confidence: high (primary sources, F11–F12).
2. **Add CLV to how every sports bet is scored, using data we already have.**
   - Use the venue's own mid at the last snapshot before start as the "close". It costs nothing and doesn't need Pinnacle.
   - A forecaster with negative CLV against the venue's own close is losing to the market before costs, whatever its lucky P&L.
   - Effect: much faster answers (F15). Confidence: high that it is a better measure; medium that the venue's close stands in well for Pinnacle's (F2 suggests it does on liquid markets).
3. **Test, then perhaps run, a "sharp-price" strategy.**
   - What it is: it buys when the ask plus fee plus slippage is at least 3¢ below de-vigged Pinnacle (step-by-step below).
   - Why separate code: it bets on a *price* (the books'), not a forecast, so it must sit outside the Jev/Claude pipeline. The price screen in `news.py` stays as it is, and no Pinnacle number may ever reach Jev or Claude.
   - What it needs from Joey: his yes on a code change and a data subscription, a `DECISIONS.md` entry, and a row in `docs/EXPERIMENTS.md` before results come in.
   - Expected effect: small. On liquid Kalshi and Polymarket markets the gap is probably under our 2.5–3¢ cost (F2, F3, F13). Any lasting edge is likelier on thin markets (NHL, college, smaller soccer leagues, tennis early in the week), whose wide spreads usually eat it.
   - Confidence that it makes money: **low**. Confidence that the backtest settles it for about $30: high.
4. **Stop the AI forecasters from pricing liquid sports markets.**
   - Claude was worse than the market on 205 real-priced sports markets (+0.011 ± 0.005 Brier). Kalshi's sports prices are made by professionals at a 1–2¢ margin.
   - A filter on that category saves research budget for areas where an AI might add something. The loop can already set `skip_categories` itself, within its bounds.
   - Confidence: medium-high.
5. **Never trade these sports markets:**
   - Polymarket "Completed Match" markets with no bid;
   - any market with no bid or a spread over 3¢;
   - Kalshi combos and parlays (a 26.5% implied margin, F2's source);
   - props;
   - season-long futures (sharp lines there carry big margins, and money is locked up for months; not verified with data here);
   - anything within an hour of the start (`min_hours_before_start` already does this).

   Confidence: high for the first three, medium for the rest.

### The strategy, step by step (for the backtest first, then a paper shadow)

1. **Universe.** Pre-game moneylines only:
   - Kalshi `KXNFLGAME`, `KXNBAGAME`, `KXMLBGAME`, `KXNHLGAME`, `KXEPLGAME` (and other top soccer leagues), `KXATPMATCH`/WTA;
   - Polymarket markets with `sportsMarketType == "moneyline"`;
   - from 48 hours down to 1 hour before start.
2. **Data.**
   - Each hourly cycle, call The Odds API `GET /v4/sports/{sport}/odds?bookmakers=pinnacle,kalshi,polymarket&markets=h2h&oddsFormat=decimal` once per in-season league with a game in the window. That is 1 credit per call: about 6 leagues × 24 × 30 ≈ 4,300 credits a month, inside the **$30 20K plan**.
   - Use the free `/events` endpoint to find which leagues have games.
   - Take our own venue prices and depth from our feeds, as now. The Odds API's Kalshi and Polymarket prices serve only to check the event matching.
3. **Match events.** Match on league, the two team names (a hand-kept alias table) and start time within 3 hours. For soccer, match all three outcomes (home, draw, away).
4. **Fair value.**
   - De-vig Pinnacle with the **power method**: solve Σ(1/oᵢ)^k = 1 by bisection, pᵢ = (1/oᵢ)^k. Log the Shin and plain versions alongside.
   - Skip if Pinnacle's market-level `last_update` is older than 15 minutes, or its margin is above 5%.
5. **Cost.** cost = ask + fee + slippage:
   - fee = 0.07·M·p·(1−p) on Kalshi, with M = the series' `fee_multiplier`;
   - fee = 0.05·p·(1−p) on Polymarket sports;
   - slippage is our 1¢.
6. **Entry rule.** Buy the side where fair − cost ≥ **3¢** (pre-registered; the backtest also reports 2, 4 and 5¢), only when all of these hold:
   - ask between 20¢ and 85¢;
   - a bid exists and the spread is ≤ 3¢;
   - the depth at the ask covers the stake;
   - no position is already open on that game;
   - at least 1 hour before the start.
7. **Size.** A flat small stake (for example 0.5% of the strategy bankroll). No Kelly sizing until CLV is proven; brief 12 owns sizing.
8. **Score.**
   - Per bet: CLV against de-vigged Pinnacle at the last snapshot before the start, CLV against the venue's own last mid, and P&L.
   - **Kill rule:** after 150 bets, stop if the upper end of the 95% range of mean Pinnacle-CLV, after costs, is below +1%.
   - **Keep rule:** the lower end is above 0 at 300 bets.

**Expected edge, honestly:** unknown, and most likely zero or negative after costs on liquid markets.
- The evidence for a lasting gap is indirect and old (F4), and points the wrong way: the soft venue then was the bookmaker, while today the prediction market is the tight one.
- The current evidence (F2, F3) says Kalshi's liquid sports prices are as sharp as the books and cross-venue gaps die in seconds.
- An hourly bot only catches gaps that last an hour.
- Write the strategy's row in `docs/EXPERIMENTS.md` expecting 0% ± a few percent, not a profit.

## How to test it on our history

These run on the main session's side, on the ~606 finished sports markets with snapshots about every 30 minutes.

1. **Re-cost every sports bet and first look with the real fees** (F11–F12): Polymarket sports at 0.05·p·(1−p), Kalshi MLB at half rate. Report sports P&L before and after, by venue. *Confirms the fix matters* if the Polymarket sports result moves by more than its ± range.
2. **CLV against the venue's own close, free.**
   - For each finished sports market, take the mid at the first look and at the last snapshot at least 1 hour before start, on the real-priced (spread ≤ 10¢) subset only.
   - Compute the SD of the move: this is the input F15 needs.
   - For every sports bet we placed, compute CLV = close mid ÷ (ask + fee + slippage) − 1, with mean and ±, by forecaster and league.
   - *Kills the AI forecasters for sports* if mean CLV is negative beyond 2 standard errors. *Interesting* if one forecaster has positive CLV on 100+ bets.
3. **Sharp-price backtest (needs one month of The Odds API at $30–59).**
   - For each of the ~606 games, pull a historical Pinnacle h2h snapshot at our first-look time and at the last snapshot before start. That is 2 × 10 credits × 606 ≈ 12K credits, inside the 20K plan. Alternatively take hourly per-league snapshots over the whole period: about 43K credits, the 100K plan.
   - De-vig with power (Shin and plain as checks). Then:
     - **(a)** Brier of de-vigged Pinnacle against our venue's mid at the same time, on the same real-priced games, with ±;
     - **(b)** the distribution of (Pinnacle fair − venue ask − fee − slippage), by league and venue;
     - **(c)** apply the step-6 entry rule and report the number of bets, mean CLV against Pinnacle's close, and ROI, each with ±, for the 2/3/4/5¢ thresholds.
   - *Confirms* if the 3¢ rule produces at least 100 bets with mean Pinnacle-CLV above +1% at 2 standard errors. *Kills* if (b) has almost no mass beyond 3¢ on two-sided books, or if CLV is ≤ 0.
   - Also report how often a ≥3¢ gap one snapshot was still there 30 minutes later, which tests whether an hourly bot can catch it at all.
4. **Leave-one-league-out.** Check that the threshold and any league filter chosen in step 3 hold on the league left out, so the in-sample cut-off mistake in F4 isn't repeated.

## Data sources

| Name | URL | Cost / free tier | Limits | Provides |
|---|---|---|---|---|
| The Odds API | https://the-odds-api.com | Free 500 credits/month; $30 (20K), $59 (100K), $119 (5M), $249 (15M) per month | Live: 1 credit per region per market, and up to 10 named bookmakers count as one region. Historical: 10 per region per market, paid plans only. Pinnacle scraped "may incur a delay" | Pinnacle (`eu`), Betfair Exchange, Kalshi, Polymarket, Novig and ProphetX (`us_ex`); history from 2020-06-06 in 5–10-minute snapshots |
| Kalshi public API | https://api.elections.kalshi.com/trade-api/v2 | Free, no key for reads | Rate-limited (our feed already pauses between pages) | Markets, order books, per-series `fee_type`/`fee_multiplier`, fee-change log |
| Polymarket Gamma API | https://gamma-api.polymarket.com | Free | Rate-limited | Markets with `sportsMarketType`, bid/ask, `feeSchedule` |
| Betfair Exchange API | https://developer.betfair.com | Delayed key free; live key £299 one-off | Delayed 1–180 s, 3 price levels; generally unavailable to US residents | Exchange prices, a sharp benchmark for soccer and tennis |
| football-data.co.uk | https://www.football-data.co.uk | Free download (terms not verified) | European football only | Pinnacle pre-closing and closing odds, Betfair Exchange odds, results |

## Not verified

- Any measured gap between Kalshi or Polymarket sports prices and Pinnacle, Circa, Betfair, Novig or ProphetX, by league, market type, or timing (open against close, the lag after news). No source found.
- Whether Kalshi's sports market makers (Susquehanna and others) price off sportsbook feeds.
- How long Pinnacle's delay is inside The Odds API, and which sports and markets its Kalshi and Polymarket keys carry, now and in the history.
- Whether Pinnacle closed its public API in July 2025 (secondary source only).
- Kalshi's own fee-schedule wording, the coefficients 0.07 and 0.0175 as stated by Kalshi, and its rounding rule. The multipliers themselves are verified from the API.
- When Polymarket began charging sports taker fees, and so how many of our past bets were mis-costed.
- The Brier numbers in the CMC thesis (abstract only).
- Pinnacle's own CLV articles (pages did not render), and any study tying CLV to long-run profit on a sharp book.
- The 3¢ standard deviation of the price move used in F15; it is an assumption for our data to replace.
- OddsJam, OpticOdds, SportsGameOdds and OddsPortal: not checked.
- A claim that Kalshi makers averaged −9.64% against takers' −31.46% was **refuted** 1–2 in verification. Do not rely on "post limit orders instead of taking" as a sourced finding here.

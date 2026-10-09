# 03: Markets that keep trading after the answer is known

Researched 2026-10-09 for `docs/research/briefs/03-stale-markets.md`.

## Answer in five lines

1. No source measures the thing the brief asks about: how often a decided market still trades below 95–99¢,
   and for how long. Every number below is either the average return on expensive contracts in general
   (not only decided ones), or one month of NBA games on Polymarket.
2. The structure of both venues leaves very little room. On Kalshi, trading stops when a market closes, and
   sports game-winner contracts are closed early once a winner is reported. On Polymarket, market makers pull
   out after the game and the winning side drifts toward 99.9¢ while the oracle runs, which takes about 2
   hours when nobody disputes.
3. Buying at 97–99¢ only pays if we are wrong less than 1–3% of the time, counting rule traps (overtime,
   postponements, which source is official) and oracle disputes. UMA disputes run about 1.3–1.7% of all
   requests, which is the same size as the whole margin at 99¢.
4. Outcome sources are free and fast (BLS posts at exactly 8:30 a.m. ET, league score feeds, CF Benchmarks).
   Where the outcome becomes known at the same moment trading stops (crypto, economic releases), there is no
   window at all. Weather settles on a report published the next morning, which can differ from live readings.
5. A 30-minute cycle can't catch a window measured in minutes. Even where the window lasts hours (Polymarket
   between game end and resolution), there is no evidence the price sits low enough to pay. Don't build it.
   Measure it first if Joey wants the question settled (test below).

## Findings

**1. Expensive contracts earn a thin average edge, but nobody has measured it on decided markets alone.**
- Polymarket, all trades in resolved markets, 2022-11-21 to 2026-04-28, 27,179,635 trades at 90–100¢
  (average price 95.2¢): +0.56¢ per $1, before fees. The 80–90¢ band earned more (+0.98¢), so the edge does
  not grow toward 99¢. There are no standard errors, and trades within a market are correlated.
  [Qin & Yang, arXiv 2606.04217, June 2026](https://arxiv.org/html/2606.04217v1), Table 3.
- Polymarket, 588M trades and 2.48M accounts (period not given in the abstract): buying at 90¢ or more earns
  about +0.83¢ per dollar, and buying under 10¢ loses 19.3¢. The paper says the pattern is absent in Sports.
  [Cardozo & Rivero-Wildemauwe, arXiv 2609.12878, Sept 2026](https://arxiv.org/abs/2609.12878), abstract only.
- Kalshi, 2021 to April 2025, 313,972 prices from 46,282 contracts: contracts above 70¢ show small but
  statistically significant returns after fees, under the old fee rules (takers only). The paper's own worked
  example is a 95¢ contract that wins 98% of the time, returning about 3.1% before fees; one loss costs 95¢,
  about 30 wins. [Bürgi, Deng & Whelan, "Makers and Takers", UCD working paper, Jan 2026](https://www.karlwhelan.com/Papers/Kalshi.pdf).
- Strength: **strong** that the edge exists and is thin; **not measured** on decided markets. These are
  preprints and working papers. This overlaps brief 01.

**2. On Polymarket, the book empties out after a game ends.**
- 173 NBA games, 2026-02-04 to 2026-03-04, 75,088,497 order-book snapshots taken every 3.6–5.5 seconds.
- The median spread was 392 bps before the game, 1,031 bps during it and 7,533 bps after it, while the
  market waited for the oracle.
- 30 of 37 apparent single-market arbitrage episodes (81%) fell after the game ended. The authors judged them
  not executable: stale orders made the book look crossed, but no live liquidity stood behind them.
- The paper did not measure whether fillable asks below 99¢ existed on the winning side, or how long the gap
  between game end and resolution lasted.
- Source: [Cheng, Yang & Zou, arXiv 2605.00864, May 2026](https://arxiv.org/pdf/2605.00864), §3.2,
  Table 2, App. A.3.
- Strength: **moderate** (one sport, one month, a preprint; "not executable" is the authors' inference, never
  tested by trading).

**3. Polymarket has a post-event "bonding" window where specialists buy decided outcomes at about 99.9¢.**
- Gebele & Matthes study every Polymarket market through 2025-12-31: 323,342 markets, of which a
  near-certainty sample of 36,349 markets and 1,181,226 market-days.
- They define a post-event window in which the outcome is decided economically but the oracle hasn't
  finalized. In it, bids sit near 99.9¢ and no ask is below $1.
- The ten most profitable makers in that window made 6,000–35,000 trades each, with median holds of 0.78 to
  2.0 hours. For example, one wallet made $23,616 on 34,994 trades.
- Separately, the authors find long-dated near-certain contracts carry a settlement discount of about 3–7% a
  year, the cost of capital locked until settlement.
- Source: [arXiv 2605.31431, May 2026](https://arxiv.org/html/2605.31431), Table 3, Table 6, App. 9.3.
- Strength: **weak** as an answer to this brief. The 99.9¢ price is how the paper *selects* these markets,
  so it is not a measured "typical price once decided". Our verification pass rejected (0–3 and 1–2) the
  stronger readings, that decided markets generally trade at 99.9¢ and that wallets cover this window at
  scale. What it does show is that people already harvest this window for fractions of a cent, with holds
  of about an hour.

**4. On Kalshi, a decided market is tradable only while it is "active", and sports winners close early.**
- After `close_time` passes, every order operation is rejected with `MARKET_INACTIVE`, and resting orders are
  cancelled.
- `closed` means no new orders and a result pending. `determined` means the result is known and a settlement
  timer is running (it can still go to disputed or amended). Only `finalized` is terminal. All three arrive
  after trading has stopped, so they tell a bot the window is over, never that one is open.
  [Kalshi market lifecycle docs, read 2026-10-09, undated](https://docs.kalshi.com/getting_started/market_lifecycle).
- Markets with `can_close_early` can have their close moved earlier, which emits a `close_date_updated`
  event.
- The football game-winner contract (FOOTBALLGAMEWIN, amended 2026-09-18) is listed to expire up to a week
  after the game. Its expiration is moved earlier under Rule 7.2 once a winner is reported, and its last
  trading time equals its expiration. [CFTC filing, 2026-09-18](https://www.cftc.gov/filings/orgrules/rules09182627969.pdf).
- So a stale window can exist only between the result and Kalshi's early close. How long that gap is, is
  documented nowhere I found.
- Strength: **strong** on the mechanism (the exchange's own documents); the length of the gap is **not
  verified**.

**5. Polymarket's API flags lag reality in both directions.**
- A market is tradable when `active=true`, `closed=false` and `acceptingOrders=true`
  ([Polymarket docs, read 2026-10-09](https://docs.polymarket.com/market-data/market-details.md)).
- A GitHub issue reports games that had ended still showing as active and accepting orders
  ([rs-clob-client #199](https://github.com/Polymarket/rs-clob-client/issues/199), seen only in search
  results).
- A bot has to read the order book itself, and needs an outside source to know the game has ended.
- Strength: **moderate** for the flag definitions; **anecdotal** for the lag.

**6. Polymarket resolution takes about 2 hours undisputed and 4–6 days disputed. Disputes happen to about
1.3–1.7% of requests.**
- A proposer posts a bond (typically $750), followed by a 2-hour challenge period. The first dispute starts a
  new proposal round. A second dispute goes to a UMA token-holder vote after 24–48 hours of debate; the vote
  takes about 48 hours. Possible outcomes include "Too Early" and a 50-50 split (each token pays 50¢).
  Clarifications can be added after trading starts.
  [Polymarket resolution docs, read 2026-10-09, undated](https://docs.polymarket.com/concepts/resolution).
- UMA's own figures: a 1.67% dispute rate over 22,000+ assertions
  ([UMA, 2024-09-06](https://blog.uma.xyz/articles/what-is-a-prediction-market-dispute)), and about 1.3% for
  the whole oracle ([UMA, 2025-08-12](https://blog.uma.xyz/articles/managed-proposers)).
- Since 2025, only whitelisted "managed proposers" may propose on Polymarket. They made 96% of proposals,
  with 99.7% accuracy, against 85.8% for proposers outside the whitelist.
- A secondary report says Polymarket had more than 1,150 disputed markets in the first five months of 2026,
  more than in all of 2025 ([crypto.news](https://crypto.news/how-prediction-markets-resolve-uma-optimistic-oracle/),
  **not verified**).
- A dispute is not a reversal; how often the final result differs from the apparent one is **not verified**.
- Strength: **moderate** (mechanism from the venue; rates from UMA's own blog, which is interested and
  undated as to period).

**7. Rule traps are real, and the wording differs from contract to contract.**
- Polymarket sports (from mirrored market pages, **anecdotal** until checked on the venue):
  - a postponed game keeps the market open until the game is completed;
  - a game cancelled with no make-up resolves 50-50;
  - some MLB markets name a winner for a tie and others resolve a tie 50-50;
  - the official league stats are the source, with a fallback to "consensus of credible reporting" after
    24 hours.
- Kalshi changed its rules in 2026 filings to CFTC:
  - hockey (certified 2026-07-08) and soccer (filed 2026-07-06) cut their postponement and delay windows to
    48 hours and resolve on the league's declared official result;
  - lacrosse (September 2026) clarified whether overtime counts in "time period" contracts;
  - a Kalshi NHL game-winner summary counts overtime and shootouts.
  ([CFTC product filings](https://www.cftc.gov/IndustryOversight/IndustryFilings/PTCDCMRules/61338))
- Strength: **moderate**. The lesson is that "the game ended 3–2" is not always "the market resolves YES".

**8. Outcome sources: fast where trading stops anyway, and slow or revisable where it doesn't.**
- *Economic data:* BLS commits to posting CPI and jobs data on its site at the 8:30 a.m. ET release time
  ([BLS blog, 2020-01-23](https://www.bls.gov/blog/2020/ensuring-security-and-fairness-in-the-release-of-economic-statistics.htm)).
  JOLTS is at 10:00. Shutdowns moved dates in late 2025 and early 2026. A DOL Inspector General audit found
  CPI posted 31 minutes early once in May 2024. Nothing found shows these markets still trading after the
  release. Strength **moderate**.
- *Crypto:* most Kalshi crypto markets settle on a CF Benchmarks index averaged over the 60 seconds before
  the named time, which is also when trading stops, so the window is about zero. The exceptions are "touch"
  (high/low) markets, which are decided when a level is hit; whether they stay open afterwards is **not
  verified**. [Kalshi help, read 2026-10-09](https://help.kalshi.com/en/articles/13823838-crypto-markets).
  Strength **moderate**.
- *Weather:* Kalshi settles daily highs on the final NWS Daily Climate Report, issued 12:30–5:00 a.m. local
  time the next day, for the day measured in standard time. Kalshi may delay settlement if the report
  disagrees with METAR highs. ([NWS Instruction 10-1004](https://www.weather.gov/media/directives/010_pdfs/pd01010004curr.pdf);
  [Kalshi weather help, 2026-07-22](https://help.kalshi.com/en/articles/13823837-weather-markets).)
  Two claims were rejected in verification: that live readings reveal the answer hours before settlement,
  and that the afternoon report gives a same-day window. Strength **strong** on the rule; the window itself
  is **not established**.
- *Sports scores:* ESPN's unofficial API and the official MLB/NHL/NBA stats APIs are free, but their delays
  are documented only in blogs ([e.g.](https://zuplo.com/learning-center/espn-hidden-api-guide)).
  **Anecdotal**; delays **not verified**.

**9. Our own data, re-read.**
- The "already decided?" question rated 11 of 939 finished markets above 0.6, and on those the market
  favourite was right as often as Jev (`docs/REBUILD_SCOPE.md`).
- The Polymarket "Completed Match" tennis books (asks at 97–99¢ and 91–92¢, no bids) were seen *before* the
  matches started. They show an empty book, not a decided market selling cheap, so they are not evidence of a
  stale window.

## What it means for our trader

The trader is built so that it never looks at a market after its event:

- both venue fetches skip markets closing within 12 hours ([markets.py:123](../../papertrade/markets.py#L123),
  [markets.py:213](../../papertrade/markets.py#L213));
- Polymarket sports are dropped from an hour before the start ([policy.json:16](../../policy.json#L16)).

Changing that is a code change and needs Joey. Ranked:

1. **Don't build a stale-market strategy.**
   - *Expected effect:* avoids a strategy whose total edge (about 0.5–1¢ per $1 on expensive contracts in
     general) is smaller than one rule-trap loss per 30–100 bets.
   - *Why:* where a window can exist, it is short (Kalshi early close) or already priced at about 99.9¢ by
     specialists (Polymarket bonding).
   - *Confidence:* moderate. It rests on mechanism and indirect evidence; no measurement exists either way.
2. **Stop treating `already_decided` as a possible betting signal.**
   - *Expected effect:* frees one question per market for something useful (brief 14).
   - *Confidence:* high, from our own 939 markets, though 11 positives is far too few to show a skill either
     way.
   - Removing or rewording it means bumping `QUESTION_SET_VERSION` in `papertrade/judge.py`, and it is a
     design change for Joey.
3. **If Joey wants the question settled, measure before building.**
   - *What:* a read-only logger (a code change, so his approval first) that watches a sample of Kalshi game
     markets and Polymarket sports markets every 1–5 minutes from the scheduled end until close or
     resolution.
   - *What it records:* status flags, best ask on each side and its size.
   - *How long:* two to four weeks gets roughly 300–600 games.
   - *Kill criterion:* if fewer than 5% of decided markets show a fillable ask of $5 or more at 98¢ or less
     on the winning side for at least 30 minutes, the idea is dead at our cadence.
   - *Confidence that it will come back negative:* moderate.
4. **The cadence each window would need** (see the table). None fits a 30-minute cycle, except possibly the
   Polymarket post-game wait, where the price is unlikely to pay.

| Market type | Signal that it's decided | Venue behaviour after that | Window | Cadence needed | Worth watching? |
|---|---|---|---|---|---|
| Kalshi sports game winner | league final score (official stats API, ESPN) | early close once a winner is reported (FOOTBALLGAMEWIN Rule 7.2) | minutes? not documented | seconds to 1 min | no, unless the logger finds a long gap |
| Polymarket sports / esports / tennis | final score; then a UMA proposal on chain | makers leave; winner drifts to ~99.9¢; about 2 h of challenge after the proposal | hours, but priced near 99.9¢ | 5 min to catch it before the proposal; 30 min only sees the tail | only to measure (logger) |
| Kalshi / Polymarket economic data (CPI, jobs, Fed) | BLS / Fed website at the release time | markets normally stop at or before the release (not verified for every series) | about 0 | sub-second; out of reach | no |
| Kalshi crypto price at a time | CF Benchmarks 60 s average | stops trading at the fixing time | about 0 | out of reach | no |
| Kalshi crypto "touch" (high/low) | index crosses the level | not verified whether it stays open | unknown | 1–5 min | maybe; check the rules first |
| Kalshi weather daily high | final NWS CLI, next morning | settles on the CLI; preliminary data can differ | not established | hourly would do, but the signal isn't final | no |
| Mention / speech markets | transcript | not researched (no verified source) | unknown | unknown | not verified |

## How to test it on our history

All of this is for the main session; this report did not analyze `papertrade_data/`.

1. **Do we hold any post-event snapshots at all?**
   - *Compute:* for each finished market, count the price snapshots taken after the event time and before
     settlement. The event time is `expected_expiration` on Kalshi, and start + 3 h for Polymarket sports.
   - *Expected:* probably near zero, given the 12-hour and pre-start filters. If so, history can't answer
     this question, and only the logger (recommendation 3) can.
2. **If there are post-event snapshots:**
   - *Compute:* for each one, the eventual winner's ask, its size and the time since the event. Report the
     share of markets with a winner's ask of 98¢ or less (with ±), the median time that lasts, and the loser
     rate among tokens priced 95–99¢ in that window.
   - *Confirms the idea:* at least 10% of decided markets have a fillable ask of 98¢ or less for 30 minutes or
     more, *and* the loser rate is under 1% on at least 300 markets.
   - *Kills it:* anything less.
3. **The "already decided" signal at every threshold:**
   - *Compute:* across all 939+ judged markets, plot the favourite's win rate and Jev's accuracy against the
     `already_decided` score in bands (0.2, 0.4, 0.6, 0.8), with the count and ± in each band.
   - *Kills the question for good:* no band above 0.4 holds 50 or more markets where Jev beats the favourite.
4. **Favourite at 95–99¢ by category:**
   - *Compute:* on every finished market whose first look had the favourite's ask between 95¢ and 99¢, the
     return after the real taker fee, split by category, with ±.
   - This checks finding 1 on our own markets: is any category positive after fees?

## Data sources

| Source | URL | Cost | Limits | Provides |
|---|---|---|---|---|
| Kalshi market lifecycle and websocket | https://docs.kalshi.com/getting_started/market_lifecycle | free | public market data; rate limits apply | status (`active`/`closed`/`determined`/`finalized`), `close_date_updated` events, `can_close_early` |
| Polymarket Gamma + CLOB | https://docs.polymarket.com/market-data/market-details.md | free | public | `active`/`closed`/`acceptingOrders` flags, order book |
| UMA Optimistic Oracle (Polygon) | https://docs.polymarket.com/concepts/resolution | free (chain reads) | needs an RPC | proposal and dispute events, the 2 h liveness period |
| BLS release calendar and site | https://www.bls.gov/schedule/ | free | posted at release time | CPI, jobs and others at 8:30 a.m. ET |
| NWS Daily Climate Report (CLI) | https://www.weather.gov/media/directives/010_pdfs/pd01010004curr.pdf | free | final report next morning | Kalshi's weather settlement value |
| CF Benchmarks (BRTI etc.) | https://help.kalshi.com/en/articles/13823838-crypto-markets | free display; data licensing varies | 60 s average | Kalshi crypto settlement |
| League stats APIs / ESPN unofficial API | https://zuplo.com/learning-center/espn-hidden-api-guide | free, unofficial | undocumented; may change or block | live and final scores; delay not verified |

## Not verified

- How often decided markets trade below 95–99¢, and for how long, on either venue. This is the core question,
  and no source measures it.
- How long after a reported winner Kalshi actually triggers an early close, and the text of Rule 7.2.
- Whether Kalshi's `can_close_early` and `early_close_condition` fields exist in its own API reference
  (seen only in third-party schema catalogues).
- How often a disputed Polymarket market resolves against the apparent result, and the 2026 dispute rate as a
  share of markets (only a count of 1,150+ for January–May, from a secondary source).
- How fast competing bots are in post-decision windows on either venue.
- Score feed delays (ESPN, league APIs), and mention or speech market rules and transcript timing.
- Whether Kalshi economic-data markets ever trade after the release, whether crypto "touch" markets stay open
  after the level is hit, and whether weather markets stay active between midnight and the CLI.
- Whether the favourite edge in finding 1 survives today's fees on each venue (brief 10 covers fees).

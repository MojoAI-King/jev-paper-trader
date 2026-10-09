# 11: Simulating fills honestly

Researched 2026-10-09 for `docs/research/briefs/11-paper-fill-simulation.md`.

Method: the deep-research workflow (5 search angles, 22 sources fetched, 83 claims extracted, 25 checked by three
independent verifiers each; 23 survived, 2 were refuted) plus a read of `papertrade/engine.py`,
`papertrade/markets.py` and `policy.json` to fit the model to the code. Every API fact below was read from the
venue's own docs on 2026-10-09. Those pages carry no dates and change often. No `papertrade_data/` analysis was
done; the tests are described for the main session.

## Answer in five lines

1. Both venues give a free, public full order book for each market *now*, and trade prints that can be downloaded
   *later*. Neither one lets you download past order-book depth, so depth exists only if we record it live.
2. Market orders: replace "fill everything at best ask + 1¢" with a walk up the ask ladder, re-fetched at the
   moment of the bet and capped at the worst price where the bet still clears its edge gate. Thin books then give
   partial fills or no bet.
3. Resting (limit) orders: count a fill only when a later real trade prints *through* our price, or when enough
   volume trades *at* our price to clear the queue ahead of us. Never count a touch, and never assume we were at the
   front of the queue.
4. The literature agrees with our own −16% to −31% result: resting orders fill mostly when the price moves against
   them. The evidence is strong on direction but measured on crypto and futures, so it doesn't tell us the size on
   prediction markets. Until a test says otherwise, the trader should keep taking.
5. Store the book only for the markets we bet on, at the moment we bet (kilobytes a day). Don't store trades,
   because they can be downloaded afterwards. Full-depth snapshots of every scanned market every cycle cost about
   1 GB a year raw, my estimate. That is only worth it if the bet-time test shows stakes regularly outgrow the top
   of the book.

## Findings

**F1. Kalshi's public order book shows bids only. The ask ladder has to be built by inverting the opposite side.**
`GET /markets/{ticker}/orderbook` returns YES bids and NO bids, never asks. A NO bid at price z is a YES ask at
1.00 − z with the same size (and a YES bid is a NO ask the same way). The response field is `orderbook_fp`, with
`yes_dollars` and `no_dollars` arrays of [price string in dollars, fixed-point count]. A `depth` parameter takes 0
(all levels, the default) or 1–100.
Evidence: docs.kalshi.com/api-reference/market/get-market-orderbook.md, read 2026-10-09. Three verifiers agreed
(3-0). A separate claim that the levels come back sorted best to worst was refuted 0-3, so sort them in code. The
page declares no security scheme yet documents a 401 response, so whether it always works without a key is not
settled by the docs alone. Strength: **strong** for the structure; **not verified** for whether `depth=0` is ever
truncated.

**F2. Kalshi publishes every trade, with price, size, time and aggressor side, live and as a downloadable history.**
`GET /markets/trades` (no authentication declared) filters by ticker and by `min_ts`/`max_ts`, returns up to 1,000
records per page with a cursor, and each record carries `yes_price_dollars`, `no_price_dollars`, `count_fp`,
`created_time`, the taker side and `is_block_trade`. Data older than a moving cutoff (`GET /historical/cutoff`,
which gives a separate timestamp for each data type) moves to `/historical/trades` and
`/historical/markets/{ticker}/candlesticks`. The candlesticks come in 1, 60 and 1,440-minute bars and carry YES
bid/ask open-high-low-close, trade-price open-high-low-close and volume. There is no historical order-book endpoint.
Evidence: get-trades.md and getting_started/historical_data, read 2026-10-09, 3-0. Strength: **strong**. Caveats:
block trades are matched off the book and must be excluded from any fill rule. A backfill has to query both sides of
the cutoff. Retention and rate limits for the historical endpoints are not documented.

**F3. Kalshi's rate limits are generous for authenticated users and undocumented for public reads.** The limits
are token buckets, and most requests cost 10 tokens. The Basic tier (every account) gets 200 read tokens a second,
about 20 ordinary reads a second. Limits for the unauthenticated reads the trader makes are not stated anywhere I
found.
Evidence: docs.kalshi.com/getting_started/rate_limits, read 2026-10-09, 3-0. Strength: **strong** for the
authenticated tiers, **not verified** for public reads. (The repo's paper-only rule forbids exchange credentials,
so the authenticated tier isn't an option.)

**F4. Polymarket's public `/book` returns the whole resting book for one outcome token, with generous limits.**
`GET /book` on the CLOB (Polymarket's order book) gives bids and asks for one token. The guide says bids come in
ascending order and asks in descending order, so the best prices are the last entries. The OpenAPI reference says
the opposite, so sort in code. Each response also carries a hash that changes whenever the book changes, plus
`tick_size`, `min_order_size` and `last_trade_price`. Limits are per IP: 1,500 requests per 10 s for `/book` and 500
per 10 s for the batch `/books` (up to 500 tokens per call). Requests over the limit are slowed down, not rejected.
Evidence: docs.polymarket.com/market-data/prices-order-books.md and api-reference/rate-limits.md, read 2026-10-09,
3-0. One verifier made a live, unauthenticated call that returned 28 bid levels and 133 ask levels spanning the
whole price range. Strength: **strong**. Full depth was observed in that call, not promised by the docs.

**F5. Polymarket has no historical depth anywhere in its own APIs. It has trade history, and price history only in
coarse, expiring buckets.** `/v2/prices-history` is a price-only series. An explicit range is capped at 15 days,
and retention is tiered: 1-minute data kept at least 7 days, 5-minute at least 60, 30-minute at least 90, and only
3-hour and 12-hour buckets kept permanently. Trades are available from the Data API (`/trades`, 200 requests per
10 s; `/v2/trades`, 300 per 10 s) and from the Polygon chain, where every matched trade and its initiator is
recorded. Resting orders and cancellations never reach the chain.
Evidence: Polymarket docs (above), read 2026-10-09. The prices-history part was voted 2-1, the rest 3-0. The chain
point rests on Tsang & Yang (arXiv 2603.03136, working paper), who identified the initiator in all 2,348,771 matched
transactions of one market. Strength: **strong** that no depth history exists, **moderate** on the retention tiers.
How far back the Data API `/trades` goes is not verified.

**F6. Goldsky streams Polymarket's on-chain fills (price, side, amounts, maker or taker, block time, token id),
history included. It is a paid pipeline into your own database, not a download.** It has no depth, cancellations or
queue data. Each match produces a row for both sides, so the data has to be deduplicated, and times are only as
precise as the block. Polymarket moved to v2 contracts on 2026-04-28, and the history may cover v2 only.
Evidence: docs.goldsky.com/chains/polymarket.md, read 2026-10-09, 3-0, but rated moderate by the verifiers.
Strength: **moderate**. For this project the free Data API `/trades` is the simpler source.

**F7. Limit orders fill mainly when the price is moving against them. Simulators that fill on a touch, against the
latest snapshot, or regardless of the price path overstate profit.** This is the mechanism behind our own resting-
order result.
Evidence (all read 2026-10-09):
- Albers et al. (arXiv 2502.18625): 232,897 live minimum-size maker orders on the Binance BTC perpetual (127,051
  filled). How likely an order was to fill was negatively correlated with the return after the fill. The mean
  markout (the price move after the fill) was about −0.8 basis points (bp), or −0.3 bp after the maker rebate. A
  naive strategy resting at the best price lost about 60% in roughly 3 days.
- Lalor & Swishchuk (arXiv 2409.12721, using the Trading Technologies simulator on CME futures): 66–89% of 1-lot
  fills were adverse (ES 767 of 941, NQ 1,269 of 1,929, CL 518 of 625, ZN 199 of 224). Across 330 CL price paths, a
  market maker that looked fine in the benchmark simulator did much worse once adverse fills were enforced (that
  sub-claim was voted 2-1).
- Albers et al. 2025, Quantitative Finance (ora.ox.ac.uk record; abstract only, the full text returned 403): real
  fills of millions of market orders on Bybit and Binance came out worse than the order-book snapshot predicted,
  and the gap was correlated with volatility, latency and liquidity.

Strength: **strong** on direction (independent datasets, mechanism well understood), **weak** on size for us. None
of it is from Kalshi or Polymarket, and the horizons run from sub-second to one day, not our 30 minutes to weeks.

**F8. Queue position matters, and the standard conservative way to model it uses only trades.** The hftbacktest
docs (a backtesting library) describe a queue model in which an order starts at the back of the displayed queue at
its price and moves forward only when trades print at that price. Cancellations are ignored, and the docs call this
possibly too pessimistic. Their less pessimistic variant lets each drop in displayed size, beyond what trades
explain, count as cancellations ahead of us with probability f(back)/(f(back)+f(front)), where f(x)=xⁿ, n≈1–3. The
Trading Technologies simulator gives each paper order an imaginary place in the queue and fills it only after enough
real volume has traded through that place, which its authors call realistic only for orders too small to move
prices. On the Binance data, front-of-queue fills averaged −0.296 bp against −1.157 bp for back-of-queue fills, so
assuming a good queue position flatters results.
Evidence: mintlify.com/nkaz001/hftbacktest/concepts/queue-position (secondary, library docs), arXiv 2409.12721,
arXiv 2502.18625, read 2026-10-09. These were extracted from the sources but not separately voted on.
Strength: **moderate**.

**F9. On Polymarket the best price level usually holds a small part of the displayed depth, so a stake bigger than
the best level will often walk several levels.** At the median market, the best level holds about 13.6% of the depth
in the top 10 levels (both sides counted together). The range across markets is wide: the 10th percentile is 2.4%
and the 90th is 44.8%.
Evidence: Dubach 2026 (arXiv 2604.24366), a single-author preprint with a replication package: 600 pre-registered
markets and 52 days of tick-level book data. Voted 3-0. Strength: **moderate** (one unrefereed paper, and the share
of depth says nothing about how far apart the price levels are). The same paper's spread-by-price figures were
refuted 0-3 (it mixes half-spread and full-spread numbers) and are not used here.

**F10. Price impact varies a great deal between markets. For a single bet placed at once, walking the displayed
book is the right model, and volume-based impact formulas are only a fallback.** Across 212 Polymarket 2024
election markets, Kyle's lambda (price impact per dollar traded) fell with market activity at an elasticity of about
−0.92 (R² 0.59). For orders worked over time, impact roughly follows a square-root law,
I ≈ Y·σ·√(Q/V): Y is a constant near 1, σ the price volatility, Q the size of the order and V the market's traded
volume. The verifiers warned against using that formula as the price of an instant sweep.
Evidence: arXiv 2603.03136 (working paper, election markets only, lambda measured against lifetime activity, which a
live trader can't know in advance), ar5iv 1412.0141 (Donier, Bonart, Mastromatteo & Bouchaud), read 2026-10-09,
3-0. Strength: **moderate**.

**F11. On Kalshi, resting orders in single-name markets lose more to informed traders.** (This finding was
extracted from its source but not run through the three-vote check.) A Stanford Law working paper (2026-04-21),
using 41.6 million Kalshi trades, finds more informed price impact in single-name markets than in broad-based
ones. A one-sided-order-flow measure predicts losses for makers in single-name markets only, and makers are still
paid on average because takers overbet YES in markets that mostly settle NO.
Evidence: law.stanford.edu/?p=564919, read 2026-10-09. Strength: **weak** until checked. It is the only source
found that measures adverse selection on a prediction-market venue itself.

**F12. Full tick-level depth is expensive to store. Snapshots taken now and then are cheap.** One 52-day archive of
Polymarket's public WebSocket feed came to about 30.3 billion events and 623.8 GB (Parquet), and full book
snapshots were only 0.8% of those events (Dubach 2026, as F9). Our own estimate for periodic snapshots is in the
storage section below. Strength: **moderate** for the archive figure, an **estimate** for ours.

## What it means for our trader

Today (`engine.py` around line 230, `policy.json` `fees.slippage: 0.01`) the trader prices every bet at the
listing's best ask + 1¢ and fills the whole stake, up to 2% of the $100,000 bankroll ($2,000), however little is
offered at that ask. The ask comes from the market listing (Polymarket `bestAsk`, Kalshi `yes_ask`/`no_ask`), fetched
at the start of the cycle, before research runs.

### The fill model to implement

**Notation.** `S` = the stake the sizing rules want (brief 12). `side` = yes or no. A ladder `L = [(p₁,q₁),
(p₂,q₂), …]` lists price per contract in dollars and contracts on offer, sorted by price ascending in code (never
trust the API's order, F1 and F4). `t₀` = the moment the bet is booked. `p_cap` = the worst price at which this bet
still passes its edge gate: the highest p where `q_side − (p + fee(p)) ≥ min_edge`, with `fee` from brief 10.

**Rule M1: build the ladder for the side being bought.**
- Kalshi, buying YES: `L = sort[(1 − z, n) for each NO bid (z, n)]`. Buying NO: `L = sort[(1 − y, n) for each YES
  bid (y, n)]` (F1).
- Polymarket, buying YES: the YES token's own asks. Buying NO: the NO token's own asks (F4).
- *Assumption A1:* on Polymarket, use one token's own book and don't merge in the other token's inverted bids.
  Polymarket's matching engine can also match against the complementary token, so the real fillable depth may be
  larger. Ignoring it can only understate liquidity, so the error is on the safe side. Not verified.

**Rule M2: re-fetch the book at the moment of the bet.** Before booking, fetch the ladder again (Kalshi: one
`/orderbook` call; Polymarket: `/books` for both tokens in one call). Compute the edge gate against the re-fetched
price, not the price from the start of the cycle.
- *Assumption A2:* the minutes between the start-of-cycle fetch and the bet (research runs in between) are the
  latency that matters for us. Sub-second latency doesn't. Snapshot-based fills are known to be optimistic (F7,
  Albers 2025), and re-fetching removes the part of that error that comes from a stale price.
- The ladder data stays in the engine. It must never reach research or any forecaster (the price screen,
  `news.screen_facts()`).

**Rule M3: walk the ladder.** Fill level by level, in ascending price, while `pᵢ ≤ p_cap` and budget remains:

```
nᵢ   = min( α · qᵢ ,  remaining_budget / (pᵢ + fee(pᵢ)) )      # contracts taken at level i
cost = Σ nᵢ · (pᵢ + fee(pᵢ))
N    = Σ nᵢ                                                     # contracts filled
VWAP = Σ nᵢ · pᵢ / N                                            # average price, before fees
```

Round `N` down to the venue's step: whole contracts on Kalshi (not verified, `count_fp` hints at fractions), and at
least `min_order_size` from `/book` on Polymarket. Prices must sit on the venue's `tick_size`.
- *Assumption A3:* `α = 0.5`, meaning we take at most half of each displayed level. This is a haircut for depth that
  may be cancelled between our fetch and a real order arriving, and for the snapshot optimism in F7. It is a guess
  with no prediction-market measurement behind it. Keep it a code constant (fill realism, like `slippage`, is not a
  rule the loop may tune) and calibrate it with test T3 below.
- *Assumption A4:* the fee is charged per level at that level's price, because Polymarket's fee depends on
  p·(1 − p) (brief 10, BACKLOG B26).
- The walk replaces the flat +1¢. Walking the book *is* the slippage, and keeping the 1¢ on top would count it
  twice.

**Rule M4: partial fills and no fill.** Keep a partial fill. This is how an immediate-or-cancel order capped at
`p_cap` behaves on a real venue. If `N` is below the venue minimum, or `cost < f_min · S` with `f_min = 0.10`, book
no bet and log the reason "book too thin".
- *Assumption A5:* `f_min = 0.10`, so we don't open positions too small to be worth tracking. This is arbitrary and
  only affects bookkeeping.
- Record `N`, `VWAP`, `S − cost` (the unfilled part), the levels used and the book hash or a timestamp on the bet,
  so every fill can be audited.

**Rule M5: fallback when no book is available.** If the book fetch fails, or (in a backtest on old data) no book was
stored, fill at `ask + 1¢`, but cap the stake at `β · V₂₄` dollars, where `V₂₄` is traded dollar volume over the
trailing 24 hours from the trades endpoints (F2, F5). Flag every such fill as "no depth".
- *Assumption A6:* `β = 0.05`. A stake above 5% of a day's volume would plausibly move the price. This is a
  heuristic, not calibrated; F10 says impact varies widely between markets. Report flagged fills separately so they
  can't hide inside the headline numbers.

**Rule L1: resting limit orders, if ever simulated again.** An order to buy `side` at `p_L` with size `n_L` rests
from `t₀ + δ` until its expiry `T`. Using non-block trades (`is_block_trade = false`) from `/markets/trades` on
Kalshi or the Data API `/trades` on Polymarket, between `t₀ + δ` and `T`:
1. **Queue ahead.** `Q₀` = the displayed size already bid at `p_L` on our side at `t₀`. It is 0 if `p_L` improves on
   the best bid. If no book was stored at `t₀`, `Q₀ = ∞`, meaning only rule 3 can fill the order.
2. **Trades at our price.** Let `V_at` be the cumulative volume of trades at exactly `p_L` where the taker sold into
   our side. Filled so far: `min(n_L, max(0, V_at − Q₀))`. Cancellations ahead of us earn no credit (F8, the
   conservative model).
3. **Trade-through.** Any trade at a price worse than `p_L` for the seller (YES traded below `p_L` when we are
   buying YES) fills the whole remaining order at `p_L`, because the level must have been cleared.
4. **A touch is never a fill.** A later snapshot showing the ask reaching `p_L` gives no fill without trades that
   satisfy rule 2 or 3. (That touch rule is what our earlier test used, so it ignored the queue.)
5. **Fill price** is `p_L` (makers get their own price). The fee is the maker fee from brief 10.
- *Assumption A7:* `δ = 0`, with trades counted from the booking timestamp. Seconds don't matter at our horizon.
- *Assumption A8:* when backtesting with settled outcomes, add **no** extra penalty for adverse selection. Because
  the fill depends on the price path (rules 2 and 3), the bad fills land on the markets whose news turned against
  us, and settlement scores them. A penalty on top would count it twice. The simulators F7 criticizes go wrong
  because their fills ignore the price path, not because they lack a penalty term.

### Ranked changes

1. **Walk a re-fetched book for every bet (rules M1–M5).** It replaces `ask + 1¢`, fills everything (BACKLOG B15).
   Expected effect: on deep markets with small stakes, close to today's numbers. It could even come out slightly
   better, because the 1¢ allowance goes and the walk often stays at the ask. On thin markets (low-volume Kalshi
   strikes, niche Polymarket markets), smaller fills, worse average prices and some bets dropped. The size of the
   net change is unknown until test T1. **High** confidence that it is more honest. **Unknown** whether it moves
   headline returns by more than about 1%.
2. **Store the ladder at bet time, for bets only (a few KB per bet).** This is what makes every fill auditable and
   what calibrates `α`. **High** confidence it's worth it, at negligible cost (storage section below).
3. **Don't store trades.** Both venues let us download trades after the fact (F2, F5), so storing them each cycle
   adds nothing a backtest can't fetch later. One exception: Polymarket's 1-minute *price* history expires after
   7 days (F5), so if minute bars are ever wanted, they have to be pulled within a week. **High** confidence.
4. **Keep taking, and keep resting orders out of live strategies.** Our own test (−16% to −31% against about −13%)
   and F7 agree. Re-run the earlier resting-order test under rule L1 (test T2) before any strategy rests orders.
   **High** confidence on direction.
5. **Full-depth snapshots of every scanned market each cycle: only if T1 says so.** That is the case if stakes
   exceed half the top of the book on 20% or more of bets, or the walk's price differs from `ask + 1¢` by 1¢ or
   more on average. Store them truncated (rule below) and preferably outside git. **Moderate** confidence that it
   won't be needed at today's stake sizes. Not verified.

### What storing depth would cost (estimate, not measured)

Inputs: about 200 markets per cycle (`markets_per_source: 100` × 2 venues), hourly cycles. Book sizes: about
150 levels per Polymarket token (one live call saw 28 + 133, F4), and about 30 per side on Kalshi (a guess). About
30 bytes per level as JSON. `papertrade_data/` is committed to git by every cycle, and the repo's `.git` is 263 MB
today (`du`, 2026-10-09).

| What is stored | Raw per day | Raw per year | In git (assume 5–10× compression) |
|---|---|---|---|
| Full books, all scanned markets, every cycle | ≈ 30 MB | ≈ 11 GB | ≈ 1–2 GB/yr, which would swamp the repo |
| Books truncated to levels within 10¢ of best, or enough to fill 2 × max stake, all markets, every cycle | ≈ 3 MB | ≈ 1 GB | ≈ 100–200 MB/yr, which roughly doubles the repo each year |
| Book at bet time, bets only (20–35 bets/day × ≈ 5 KB) | ≈ 0.15 MB | ≈ 55 MB | ≈ 5–10 MB/yr, negligible |

Rate limits are not the constraint. Polymarket's batch `/books` covers 200 tokens in one call (500 allowed), and
Kalshi needs one `/orderbook` call per market, so about 100 calls per cycle with the public read limit undocumented
(F3). Pace those calls (for example 5 per second). Bet-time fetches add 20–35 calls a day.

## How to test it on our history

**T1. How often does the stake outgrow the book, and what does the walk change?** No past depth exists (F1, F5),
so this is mostly a forward test.
- *Retro proxy, now:* for every settled bet since the 30¢ floor (137 so far; more is better), pull trades for that
  market from the bet time to +24 h (Kalshi `/markets/trades` or `/historical/trades`; Polymarket Data API
  `/trades`). Compute the stake as a share of the next 24 hours' traded dollars. Report the distribution, and the
  return of bets above and below 5% (with ±1 SE).
  - Confirms the concern: bets above 5% of next-day volume make up 10% or more of bets, or return worse than the
    rest by more than 2 SE.
  - Kills it: under 5% of bets are above that line.
- *Forward test:* log the bet-time ladder (change 2) and compute the M3 walk alongside today's fill, for at least
  200 bets (about 1–2 weeks at 20–35 a day). Report the mean of `(VWAP − (ask + 0.01))` with ±1 SE, the share of
  bets where `S > α·q₁`, and the share that M4 would partly fill or drop.
  - Confirms change 1 matters: mean difference of 1¢ or more, or 10% or more of bets partly filled or dropped.
  - Kills the need for full-universe depth (change 5): mean |difference| under 0.3¢ and under 5% of bets affected.

**T2. Re-run the resting-order test under rule L1.** Take the same candidate orders as the earlier test (resting at
the mid). Pull their trades and apply rules 2–3 with `Q₀ = ∞` (no stored book, so only trade-throughs fill).
- Report the fill rate, the return on filled orders and the overall return, each with n and ±1 SE, next to the
  touch rule's −16% to −31%.
- Report the markout: the change in mid 1 h, 6 h and 24 h after each fill, for resting fills compared with taker
  fills on the same markets.
- Confirms adverse selection on our venues: the resting-fill markout is negative and more than 2 SE below the taker
  markout.
- Kills it: no significant difference across 200 or more fills. If so, resting orders deserve a pre-registered
  experiment (a row in `docs/EXPERIMENTS.md`).
- Split Kalshi single-name markets from the rest, to check F11.

**T3. Calibrate α.** Once bet-time ladders are being logged, re-fetch the same market's book about 60 seconds and
about 5 minutes after each bet. For each level we would have used, measure the share of its displayed size that is
still there.
- The median surviving share at 60 s is the evidence-based `α`.
- If it is 0.9 or more, raise `α` towards 1. If it is under 0.5, lower it.
- Needs at least 200 bets. Check-only: no bet depends on it.

**T4. How stale is the start-of-cycle price?** For bets already placed, compare the ask used in the bet with the
ask at the next snapshot, by minutes elapsed between the cycle's market fetch and the bet's `opened` time.
- If the median move against us is 0.5¢ or more, rule M2 (re-fetch) is worth more than the walk itself.

## Data sources

| Name | URL | Cost / limits | What it provides |
|---|---|---|---|
| Kalshi order book | `GET /markets/{ticker}/orderbook` (docs.kalshi.com/api-reference/market/get-market-orderbook.md) | Free; public read limit undocumented; authenticated Basic tier is 200 read tokens/s, about 10 tokens per call | YES and NO bids, all levels with `depth=0`. Asks come from inverting the other side |
| Kalshi trades | `GET /markets/trades` (docs.kalshi.com/api-reference/market/get-trades.md) | Free; 1,000 per page with cursor | Price, size, time, taker side, block flag |
| Kalshi history | `/historical/cutoff`, `/historical/trades`, `/historical/markets/{ticker}/candlesticks` (docs.kalshi.com/getting_started/historical_data) | Free; retention and limits undocumented | Old trades; 1/60/1440-minute bars with bid/ask and trade open-high-low-close plus volume. No depth |
| Polymarket CLOB book | `GET /book`, `POST /books` (docs.polymarket.com/market-data/prices-order-books.md) | Free; per IP 1,500/10 s (`/book`), 500/10 s (`/books`, ≤500 tokens per call), throttled not rejected | Full book per token, `tick_size`, `min_order_size`, `last_trade_price`, book hash |
| Polymarket price history | `/v2/prices-history` | Free; 15-day range cap; 1-min data kept ≥7 days, 5-min ≥60, 30-min ≥90; 3-h and 12-h kept permanently | Prices only |
| Polymarket trades | Data API `/trades` (200/10 s), `/v2/trades` (300/10 s) | Free; how far back it goes is not verified | Trade prints |
| Goldsky Polymarket | docs.goldsky.com/chains/polymarket.md | Paid, price not published; you supply the database | On-chain fills with maker/taker flag; possibly v2 (from 2026-04-28) only |
| Third-party depth archives | pmxt archive (archive.pmxt.dev), Telonex, Tardis, Oddpool; a Hugging Face Kalshi L2 dataset (naratron33/fable5-kalshi-l2) | Not checked | Recorded Polymarket and Kalshi depth, per the verifiers. **Anecdotal** until their pages are read |

## Not verified

- Kalshi's rate limits for unauthenticated public reads, and whether `/orderbook` ever needs a key (the spec
  declares no security scheme but lists a 401 response).
- Whether Kalshi's `depth=0` ever truncates, and whether contract counts can be fractional (`count_fp`).
- Whether Polymarket's matching against the complementary token adds fillable depth that one token's `/book` doesn't
  show (assumption A1 takes the conservative side).
- How far back Polymarket's Data API `/trades` reaches, and whether Goldsky's history goes back before v2.
- Every assumed constant: `α = 0.5`, `β = 0.05`, `f_min = 0.10`, and the 30 bytes per level and about 30 Kalshi
  levels per side behind the storage table.
- F11 (Kalshi adverse selection in single-name markets): extracted from the source, not checked by the three
  verifiers.
- The third-party depth archives and datasets listed above. None of their pages were read.
- Any size estimate of adverse selection on Kalshi or Polymarket at our horizons. The strong evidence (F7) is all
  crypto and CME futures.
- Refuted, not used: that Kalshi returns its book sorted best to worst with full depth (0-3); Dubach 2026's spread
  figures by price level (0-3).

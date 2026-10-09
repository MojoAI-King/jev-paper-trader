# 10: What trading actually costs on each venue

Researched 2026-10-09 for `docs/research/briefs/10-fees-and-liquidity.md`.

## Answer in five lines

1. **Kalshi:** the taker fee is `m × 0.07 × C × P × (1−P)`. The multiplier `m` is set per series, and per event as an override, and both are published in the public API. Most series use `m = 1`. MLB props and MLB games use 0.5. 14 long-dated series use 0 and are free. The old S&P/Nasdaq half rate (0.035) appears to have ended on 2026-07-03, when the API set every index series to `quadratic` × 1.
2. **Kalshi makers** pay `0.25 × 0.07 = 0.0175 × C × P × (1−P)`, and only on series flagged `quadratic_with_maker_fees`: 160 of 14,869, mostly sports and economic data. Combo series charge makers 0.5 × 0.07. The "round up to the next cent" rule in the fee PDF is out of date. Fees are now kept to $0.000001, and each order's balance is aligned to $0.0001 (direct members) or $0.01 (members trading through a broker).
3. **Polymarket (international, the venue we read):** takers pay `C × rate × p × (1−p)` and makers pay nothing. The rate belongs to each market, in its `feeSchedule.rate` field on Gamma. It is not a fixed category table: live sports markets show both 0.03 and 0.05, and about 9% of the top 1,547 markets charge no fee at all. Fees were phased in from 2026-01-05 (15-minute crypto) to 2026-03-30 (every category except geopolitics), so all of our own history falls under fees.
4. **Spreads** in a snapshot taken on 2026-10-09: on Polymarket the median spread is 1¢ (69% of markets at 1¢ or less), 3¢ on weather. On Kalshi the median is 3¢ (23% at 1¢ or less), 1¢ on politics, 3¢ on sports, 5¢ on economics, 9¢ on weather. As a share of the price, the spread is largest on cheap contracts: a median 20% of the ask below 10¢ on Polymarket and 41% on Kalshi.
5. **What's wrong with our model** at `c5f54c2`: Kalshi ignores the per-series and per-event multipliers (free series, MLB at half rate). Polymarket bets saved before 2026-10-09 fall back to a flat 0.05, which overcharges free and 0.03 markets and undercharges crypto (0.07). Minimum order size (5 on Polymarket) and tick size are never checked.

## Findings

### F1. Kalshi's taker fee formula, and where each market's multiplier comes from

**The claim.** Taker fee = `fee_multiplier × 0.07 × C × P × (1−P)`, charged only on orders that match immediately. `C` is the number of contracts and `P` is the trade price in dollars. Each series publishes `fee_type` and `fee_multiplier`. An event can override both (`fee_type_override`, `fee_multiplier_override`), and changes are scheduled in advance with a timestamp.

**Evidence.**
- Formula and coefficient: the [Kalshi fee schedule PDF](https://kalshi.com/docs/kalshi-fee-schedule.pdf), version "Last updated and effective: Feb 5, 2026", read from a Wayback capture of 2026-06-12. Fetching the live PDF returned HTTP 429 on 2026-10-09. Three of three verifiers agreed on the 0.07 rate.
- Fields: [Get Series](https://docs.kalshi.com/api-reference/market/get-series) documents `fee_type` (`quadratic`, `quadratic_with_maker_fees`, `quadratic_with_combo_maker_fees`, `flat`) and `fee_multiplier`, "a floating point multiplier applied to the fee calculations". `flat` means "Specific Trading Fees Table"; no current series uses it.
- Overrides and history: [Get Series Fee Changes](https://docs.kalshi.com/api-reference/exchange/get-series-fee-changes.md) (`GET /series/fee_changes?show_historical=true`) and [Get Event Fee Changes](https://docs.kalshi.com/api-reference/events/get-event-fee-changes.md) (`GET /events/fee_changes`). The event page says: "Event fees are an override layered on top of the parent series' fee structure."
- Live values on 2026-10-09: `GET /trade-api/v2/series` (no auth) returned 14,869 series.

| fee_type | multiplier | Series | Examples |
|---|---|---|---|
| quadratic | 1 | 14,674 | almost everything, including KXINX, KXNASDAQ100, KXHIGHNY, KXBTCD |
| quadratic_with_maker_fees | 1 | 159 | KXNBAGAME, KXNFLGAME, KXFED, KXCPI, KXPAYROLLS, KXINXY, KXNASDAQ100Y |
| quadratic | 0.5 | 18 | MLB props: KXMLBTOTAL, KXMLBSPREAD, KXMLBHR, KXMLBF5 … |
| quadratic_with_maker_fees | 0.5 | 1 | KXMLBGAME |
| quadratic | 0 (free) | 14 | KXTRUMPOUT, KXGREENLAND, KXBTCY, KXETHY, KXGDPYEAR, KXNEXTIRANLEADER … |
| quadratic_with_combo_maker_fees | 1 | 3 | KXMVECROSSCATEGORY and the other combo series |

- Event overrides: 44 historical rows, all multiplier 1 or a switch to maker fees. The latest ones put the Dodgers–Brewers MLB playoff events (12–16 Oct 2026) back to multiplier 1, which overrides MLB's 0.5.

**Strength: strong** for the formula and the API fields: primary docs plus live API reads. **Moderate** on whether `fee_multiplier` also scales the maker fee. The docs say "the fee calculations", which is ambiguous, so treat it as not verified.

### F2. Kalshi's index half-rate (0.035) appears to have ended on 2026-07-03

**The claim.** The Feb 2026 PDF says: "The INX and NASDAQ100 market fees are given by … round up(0.035 x C x P x (1-P))." The API's fee-change log shows every S&P 500 and Nasdaq-100 series set to `quadratic` with multiplier 1 at 2026-07-03T17:00Z: KXINX, KXINXU, KXNASDAQ100, KXNASDAQ100U, KXINXPOS, KXINXMINY and KXINXMAXY, with KXINXY and KXNASDAQ100Y moved to `quadratic_with_maker_fees` × 1. Today all of them read multiplier 1.

**Evidence.** The PDF as above. Live `GET /series/fee_changes?show_historical=true` returned 107 rows, and the log starts in October 2025. There is no earlier index entry, so the value before July is not shown.

**Strength: moderate.** The plain reading is that index markets now pay the full 0.07. That the API multiplier is how Kalshi applied the PDF's index rule is my inference, not verified. A later fee PDF could not be read.

### F3. Kalshi maker fees: 0.0175, only on flagged series

**The claim.** Maker fee = `0.0175 × C × P × (1−P)`, on resting orders that later fill, only in series whose `fee_type` is `quadratic_with_maker_fees`. 0.0175 = 0.07 × 0.25, matching the API doc's "0.25 maker multiplier". Combo series use a 0.5 maker multiplier. Cancelling is free. Overpayments from maker-fee rounding above $10 a month are refunded the next month.

**Evidence.** The [fee schedule PDF](https://kalshi.com/docs/kalshi-fee-schedule.pdf) (Feb 5, 2026; 3 of 3 verifiers agreed). [Get Series](https://docs.kalshi.com/api-reference/market/get-series) for the 0.25 and 0.5 multipliers. The fee-change log dates the switches:
- 2025-10-04: WNBA and MLB.
- 2025-11-15: about 25 sports series.
- 2026-01-01: NFL and college football.
- 2026-06-05: World Cup games.
- 2026-07-03: the yearly index ranges.
- 2026-09-03: about 25 GPU-price series.

**Strength: strong.**

### F4. Kalshi fee rounding is now per order, at $0.0001 or $0.01, not per trade to the cent

**The claim.**
- Each fill's model fee is rounded up to $0.000001.
- A rounding fee then aligns the balance change to the member's precision: $0.0001 for direct members, $0.01 for non-direct members (cleared through a futures broker).
- A per-order accumulator rebates the overpayment, "so that the total fee converges to what a single equivalent fill would cost".
- Net fee = trade fee + rounding fee − rebate, never below 0.

**Evidence.** [Fee Rounding](https://docs.kalshi.com/getting_started/fee_rounding.md), read 2026-10-09; the page has no date. Its worked example has the balance moving −$0.06 on a −$0.055 fill with a model fee of $0.00363825. The PDF's "round up to the next cent" and the third-party blogs repeating it look out of date: a claim built on per-trade cent rounding was refuted 1 to 2 by the verifiers.

**Strength: strong** for the mechanism. Whether an ordinary kalshi.com account is a direct member ($0.0001) is not stated anywhere I found. It is likely, because accounts opened through brokers are the FCM case, but not verified.

**So what.** The 1–2¢ minimum on a 1-contract order that report 01 (F4) describes no longer applies for a direct member. At our order sizes, rounding costs less than 0.01¢ per contract.

### F5. Polymarket international: taker formula, per-market rate, and how to read it

**The claim.**
- The taker fee is `C × rate × p × (1−p)`, where `C` is shares and `p` is the trade price.
- Makers pay 0. The fee is charged in collateral (pUSD), added to a buy's cost, and rounded to 5 decimals (smallest fee 0.00001).
- The rate is the market's own `feeSchedule.rate` on Gamma. A market with `feesEnabled: false` charges nothing.
- The category table on the docs page is a guide: crypto 0.07; sports, economics, culture, weather and other 0.05; politics, finance, tech and mentions 0.04; geopolitics 0. Live markets differ from it.

**Evidence.**
- [docs.polymarket.com/trading/fees](https://docs.polymarket.com/trading/fees), read 2026-10-09 (3 of 3 verifiers agreed). [Market details](https://docs.polymarket.com/market-data/market-details) for `feeSchedule` `{rate, exponent, takerOnly, rebateRate}`, `feesEnabled` and `feeType`.
- Older Polymarket docs collected fees in shares and used a formula with an exponent and a crypto rate of 0.25, so the schedule has changed before.
- Live Gamma, top 2,000 active markets by 24-hour volume, 2026-10-09. Of the 1,547 that traded in 24 hours with both sides quoted:

| feeType | rate | Markets |
|---|---|---|
| sports_fees_v3 | 0.05 | 338 |
| sports_fees_v2 and sports_fees_nfl_cfb_oct26 | 0.03 | 225 |
| politics_fees | 0.04 | 251 |
| crypto_fees_v2 | 0.07 | 166 |
| weather_fees | 0.05 | 158 |
| culture_fees | 0.05 | 107 |
| tech | 0.04 | 71 |
| finance_prices | 0.04 | 50 |
| economics | 0.05 | 33 |
| no fee (`feesEnabled: false`) | 0 | 138 |

- The fee-free markets were Iran, Israel, Taiwan and Russia questions, which is the geopolitics exemption.
- NFL and college-football spreads created in late September 2026 sit at 0.03 under their own fee type, so a rate is set per market and can't be inferred from category plus date.
- `exponent` was 1 on every market seen. The docs don't say how it enters the formula.
- Closed markets keep their `feeSchedule`: the 20 most recently closed on 2026-10-09 all showed it. Old bets can therefore be priced again from `GET /markets/{id}`.
- Don't use CLOB `GET /fee-rate` or the legacy Gamma fields `makerBaseFee`/`takerBaseFee` as the rate. A live politics market showed `takerBaseFee: 1000` while its `feeSchedule.rate` was 0.04, and the claim that `/fee-rate` can serve as a lookup was refuted 0 to 3.

**Strength: strong.**

### F6. When Polymarket's fees started

**The claim.**
- 2026-01-05: 15-minute crypto only.
- 2026-02-12: 5-minute crypto.
- 2026-02-18: NCAAB and Serie A.
- 2026-03-06: all crypto, for markets created after that date.
- 2026-03-30 (Fee Structure V2): crypto, sports, finance, politics, economics, culture, weather, tech, mentions and other. Geopolitics and world events stay free.
- 2026-04-28: CLOB V2 went live. Orders no longer carry `feeRateBps`; the fee is set at match time from the market's schedule.

**Evidence.** The [Polymarket predictions changelog](https://docs.polymarket.com/changelog/predictions.md), read 2026-10-09; each date matches an entry (3 of 3). This agrees with report 01's dating from its paper's Table 7: crypto January, sports February, the rest March. A claim that sports moved from 0.03 to 0.05 on 2026-07-10 was refuted 0 to 3. The live mix of 0.03 and 0.05 sports markets shows both rates in force today, but when each started is not verified.

**Strength: strong** on the start dates. Weak on the history of sports rates.

**So what.** Our trader has only run since late September 2026, so every one of our bets falls under fees. The start dates only matter when we use outside data from early 2026, such as the papers in report 01.

### F7. Polymarket rebates don't change our cost

**The claim.** Makers receive a daily share of taker fees: crypto 20%, sports 15%, most others 25%, which is the `rebateRate` field. A Taker Rebate Program, launched about 2026-05-28, pays 0% below $2,000 of 30-day weighted volume, then 3% from $2,000 up to 50% at $10M and above.

**Evidence.** [Maker rebates](https://docs.polymarket.com/market-makers/maker-rebates) and [Taker rebates](https://docs.polymarket.com/trading/taker-rebates), read 2026-10-09 (3 of 3). Polymarket can change these without notice.

**Strength: strong.** A small taker gets nothing.

### F8. Polymarket US is a different exchange with a different fee

**The claim.** Polymarket US (QCX LLC, regulated by the CFTC) charges every market the same `Θ × C × p × (1−p)`. Θ was 0.05, then 0.06 from 2026-07-01, and has been 0.0695 since 2026-09-17. Makers get a rebate of Θ = −0.0125 at trade time. Combo contracts have used a separate formula since 2026-09-25.

**Evidence.** CFTC self-certification filings of [2026-07-07](https://www.cftc.gov/filings/orgrules/rules0707269057.pdf), [2026-09-21](https://www.cftc.gov/filings/orgrules/rules09212628660.pdf) and [2026-09-29](https://www.cftc.gov/filings/orgrules/rules09292630356.pdf). A secondary article (River Markets, 2026-08-09) says the US venue uses category rates; the primary filings contradict it.

**Strength: strong.**

**So what.** It doesn't apply to us. `papertrade/markets.py` reads `gamma-api.polymarket.com`, the international venue.

### F9. Typical spreads and displayed depth

**The claim.** Polymarket's liquid markets usually quote a 1¢ spread. Kalshi's median is wider, at about 3¢. On both venues the spread as a share of the price balloons on cheap contracts.

**Evidence, own snapshot.** These are public API reads on 2026-10-09 around 22:00 UTC, one snapshot, not a time series.

*Polymarket*: the top 2,000 active markets by 24-hour volume; 1,547 traded in the last 24 hours with both sides quoted.

| | n | Median spread | 90th percentile | Share at 1¢ or less | Median spread as % of ask |
|---|---|---|---|---|---|
| Sports | 563 | 1.0¢ | 2.0¢ | 82% | 2.6% |
| Politics | 251 | 1.0¢ | 2.1¢ | 77% | 5.6% |
| Crypto | 166 | 1.0¢ | 2.8¢ | 73% | 8.5% |
| Weather | 158 | 3.0¢ | 5.0¢ | 26% | 9.2% |
| Culture | 107 | 1.0¢ | 4.0¢ | 63% | 8.6% |
| Mid below 10¢ | 567 | 0.3¢ | 2.0¢ | 81% | 20.0% |
| Mid 30–70¢ | 513 | 1.0¢ | 4.0¢ | 67% | 2.3% |
| Mid above 90¢ | 68 | 1.0¢ | 4.5¢ | 60% | 1.0% |

*Kalshi*: the first 8,000 open markets returned by `GET /markets?status=open`, combos excluded, which skews toward sports; 372 traded in the last 24 hours with both sides quoted.

| | n | Median spread | Share at 1¢ or less | Median ask size (contracts) |
|---|---|---|---|---|
| All | 372 | 3.0¢ | 23% | 526 |
| Sports | 300 | 3.0¢ | 19% | 428 |
| Politics | 29 | 1.0¢ | 76% | 1,995 |
| Economics | 29 | 5.0¢ | 17% | 262 |
| Weather | 8 | 9.0¢ | 12% | 338 |
| Mid below 10¢ | 60 | 2.0¢ (41% of the ask) | 43% | 2,075 |
| Mid 30–70¢ | 173 | 3.0¢ (6.8% of the ask) | 20% | 357 |

**Evidence, published.**
- Dubach, [arXiv:2604.24366](https://philippdubach.com/posts/the-anatomy-of-a-decentralized-prediction-market-notes-from-the-polymarket-order-book/), May 2026, updated Aug 2026. It uses a Polymarket WebSocket archive from 2026-02-21 to 2026-04-15 covering 385,198 market ids.
  - The median full spread is about 400 bps of the mid in the 0.4–0.6 range, and 1,300–1,800 bps below 0.10.
  - The best level holds a median 13.7% of top-10 depth (n = 546), so most displayed size sits behind the best price.
  - Depth is about 6% lower per 10× less time to close (n = 322).
- Cheng, Yang and Zou, [arXiv:2605.00864](https://arxiv.org/html/2605.00864), Apr 2026, on Polymarket NBA markets: 173 games from 2026-02-04 to 2026-03-04, 3,042 markets.
  - Median spreads were 392 bps before games, 1,031 bps in-game and 7,533 bps after them, with bps not defined.
  - Resting liquidity absorbed a $100 order in 6 of 7 single-market episodes.
- FalconX, [2026-02-17](https://www.falconx.io/newsroom/from-opinions-to-odds-emerging-trends-in-the-prediction-market-landscape), on the top 100 Kalshi events of Jan 2026: spreads fall toward the 1¢ tick as markets mature (7 days or more). The charts are images with no numbers I could read; vendor research.
- Bürgi, Deng and Whelan [filtered to final spreads of 20¢ or less](https://www.karlwhelan.com/Papers/Kalshi.pdf) and find taker losses largest on cheap contracts, partly because spreads are a larger fraction of the price there.

**Strength: moderate.** The snapshot is large but taken once and skewed toward liquid markets; the papers are recent working papers. The spreads are consistent with our own measured 3.8% of each bet lost to crossing the spread.

### F10. Reading the order book through each public API

- **Kalshi.** [`GET /markets/{ticker}/orderbook`](https://docs.kalshi.com/getting_started/orderbook_responses) needs no auth.
  - It returns `orderbook_fp.yes_dollars` and `orderbook_fp.no_dollars`, bids only, as `[price_dollars, count_fp]` sorted ascending, so the best bid is last.
  - Best YES ask = $1 − best NO bid. There is no depth parameter.
  - "Get Multiple Market Orderbooks" takes up to 100 tickers.
  - The cheaper route is the `GET /markets` list we already call. On 2026-10-09 it also carried `yes_ask_size_fp` and `yes_bid_size_fp` (size at the best price), `price_level_structure` and `price_ranges`.
  - Authenticated Basic-tier reads refill 200 tokens a second at 10 tokens a request, about 20 requests a second ([rate limits](https://docs.kalshi.com/getting_started/rate_limits.md)). Limits for requests without auth aren't documented.
- **Polymarket.** CLOB [`GET /book?token_id=`](https://docs.polymarket.com/market-data/prices-order-books.md) (and `POST /books`, up to 500 tokens) returns `bids`, `asks`, `tick_size`, `min_order_size`, `neg_risk` and `last_trade_price`.
  - On one live book (2026-10-09) bids were sorted ascending and asks descending, so the best price is last on both sides.
  - `GET /price`, `/midpoint` and `/spread` give single numbers.
  - Gamma's market record already has `bestBid`, `bestAsk`, `spread`, `orderPriceMinTickSize` and `orderMinSize`.
  - Polymarket's site shows the mid, or the last trade when the spread is over 10¢. The fetched docs page didn't contain this rule; it is a claim from the workflow's sources.

**Strength: strong** (primary docs plus live reads).

### F11. Minimum sizes, ticks and limits

- **Polymarket minimum order:** `orderMinSize` was 5 on all 2,000 markets checked. Newer docs call it "USDC"; older docs and the CLOB's `min_order_size` treat it as shares. The CLOB rejects smaller orders. Which unit applies is not verified.
- **Polymarket tick:** 0.001 on 53% of the 2,000 markets, 0.01 on the rest. The allowed values are 0.1, 0.01, 0.005, 0.0025 (World Cup markets since 2026-07-02), 0.001 and 0.0001. The docs say "always read the active value from the market."
- **Polymarket size limits:** "no trading size limits" ([docs](https://docs.polymarket.com/concepts/prices-orderbook)).
- **Kalshi ticks:** set per market by `price_ranges` `{start, end, step}` bands; off-grid orders are rejected ([fixed-point migration](https://docs.kalshi.com/getting_started/fixed_point_migration.md), updated 2026-08-20).
  - Of 8,000 open markets on 2026-10-09: 7,980 `linear_cent` (1¢), 18 `center_centi_edge_centi_cent` (0.01¢) and 2 `tapered_deci_cent` (0.1¢ below 10¢ and above 90¢).
  - Contracts can be fractional, down to 0.01.
- **Kalshi position limits:** set per contract in its terms, and defined as a maximum dollar loss. The global $25,000 limit was removed in 2023 ([CFTC filing](https://www.cftc.gov/filings/orgrules/rule022123kexdcm002.pdf)). Today's values are not verified, and they are far above our stakes.

**Strength: strong** for ticks and API fields. Weak on the units of the minimum size and on position limits.

## What it means for our trader

This is ranked by how much it moves our cost estimate. Code changes need Joey's OK.

1. **Price Polymarket bets saved before 2026-10-09 at their real rate, not the 0.05 default.** `markets._poly_fee_rate` (commit c5f54c2) already reads `feeSchedule` for new snapshots. The fallback `fees.polymarket_default_rate = 0.05` gets three groups wrong:
   - geopolitics markets, which are free, and sports v2/NFL markets at 0.03: overcharged;
   - crypto at 0.07: undercharged.
   - The fix is to fetch `GET /markets/{id}` for each old market, since closed markets keep `feeSchedule` (F5).
   - Effect: up to ±2.5% of stake per bet at p = 0.5 on the affected markets. Confidence: high.
2. **Use Kalshi's per-series and per-event multipliers.**
   - Read `fee_type` and `fee_multiplier` from `GET /series/{ticker}`, cached daily. The series is the `event_ticker` prefix before the first "-".
   - Apply `GET /events/fee_changes` overrides.
   - Then charge `m × 0.07 × P(1−P)`.
   - Effect: removes a 1.75%-of-stake overcharge at p = 0.5 on MLB (m = 0.5) and the whole fee on free series (m = 0). It changes nothing on most series, including index markets since 2026-07-03 (F2). Confidence: high on the fields, moderate on the size of the effect, which depends on how many of our Kalshi bets are MLB or free series.
3. **Don't model the 0.035 index rate, and drop cent rounding.** The current Kalshi code (`0.07 × P × (1−P)` per contract, unrounded) is already right for index markets and close enough on rounding for a direct member (F4). If the main session wants extra caution, round each order's fee up to $0.0001. Confidence: moderate.
4. **Check the minimum order size and the tick before counting a paper bet.**
   - A Polymarket bet under `orderMinSize` (5) would be rejected for real.
   - Snap prices to `orderPriceMinTickSize` on Polymarket and to `price_ranges` on Kalshi.
   - Effect: small, but it removes bets that could not exist. Confidence: high.
5. **Store the size at the best ask with each snapshot.** Kalshi's `yes_ask_size_fp`/`no_ask_size_fp` is already in the `/markets` response; Polymarket needs `/book`. Today's median ask sizes (hundreds to thousands of contracts) look large next to our stakes, so the flat 1¢ slippage is probably too high for small orders. Testing that belongs to brief 11. Confidence: moderate.

**Exact fee functions to put in code** (taker unless noted; `C` contracts or shares, `p` trade price in dollars):

```python
# Kalshi. Source: kalshi.com/docs/kalshi-fee-schedule.pdf (Feb 5, 2026); docs.kalshi.com Get Series,
# Get Series/Event Fee Changes, Fee Rounding (read 2026-10-09).
def kalshi_fee(C, p, fee_type, multiplier, maker=False):
    if maker:
        k = {"quadratic_with_maker_fees": 0.25, "quadratic_with_combo_maker_fees": 0.5}.get(fee_type, 0.0)
        # whether `multiplier` also scales maker fees is not verified; assume it does not
        return k * 0.07 * C * p * (1 - p)
    return multiplier * 0.07 * C * p * (1 - p)   # event override > series value; 'flat' unused today
# Rounding: ceil to $0.000001 per fill, balance aligned per order to $0.0001 (direct) or $0.01 (broker-cleared).

# Polymarket international. Source: docs.polymarket.com/trading/fees and market-details (read 2026-10-09).
def polymarket_fee(C, p, market):
    if market.get("feesEnabled") is False:
        return 0.0
    s = market.get("feeSchedule") or {}
    return round(C * s["rate"] * p * (1 - p), 5)   # exponent = 1 on every market seen; makers pay 0

# Polymarket US (QCX) — not our venue. Source: CFTC filing 2026-09-21. Theta = 0.0695 taker, -0.0125 maker.
```

**What's wrong with the current model** (`fee_per_contract` in `papertrade/engine.py`, `fees` in `policy.json`, at `c5f54c2`):
- Kalshi uses one coefficient (0.07) for every market. That overcharges free series (m = 0) and MLB (m = 0.5), and ignores event overrides.
- Polymarket snapshots without a `fee_rate` pay a flat 0.05: geopolitics and 0.03 sports markets are overcharged, crypto undercharged.
- Neither venue checks the minimum order size or the tick.
- Before c5f54c2, Polymarket bets were charged 0. So the measured "fees and slippage 4.6%" understates what Polymarket bets cost from now on, by about rate × (1 − p): 2–3% of stake at mid prices.

## How to test it on our history

1. **Reprice every settled bet.**
   - Kalshi: the series and event multiplier in force at bet time, from `/series/fee_changes` and `/events/fee_changes` with `show_historical=true`.
   - Polymarket: each market's `feeSchedule.rate` from Gamma.
   - Recompute the 8.4% cost split and each strategy's return.
   - Confirms: the cost share moves by more than about 0.5 point, or a strategy's return changes sign. Kills: everything moves by less than 0.3 point, in which case this is bookkeeping, not a lever.
2. **Count exposure to non-standard Kalshi multipliers.** Count our Kalshi bets and first looks by `fee_multiplier` (0, 0.5, 1). If under 5% are on 0 or 0.5, item 2 above is low priority.
3. **Polymarket rate mix.** Count our Polymarket bets by actual rate (0, 0.03, 0.04, 0.05, 0.07) against the 0.05 default. The default is fine if more than 80% are at 0.05; otherwise backfill.
4. **Spreads on our own markets.**
   - Compute the spread at first look by venue × category × price bucket (as in F9) on the ~1,100 finished markets, with ±.
   - If our Kalshi markets are much wider than the 3¢ median here, the market filter is choosing thin books.
   - If our Polymarket sports first looks are wider than about 2¢, the "Completed Match" tennis problem (REBUILD_SCOPE item 6) is still getting in.
5. **Minimum size.** Count Polymarket bets whose shares (or dollars) fall under 5. Any such bet should be dropped from results.

## Data sources

- **Kalshi trade API** (`api.elections.kalshi.com/trade-api/v2`), free, no auth for market data.
  - `/series`: about 19 MB for all 14,869.
  - `/series/{t}`, `/series/fee_changes`, `/events/fee_changes`, `/markets` (top-of-book price and size, `price_ranges`), `/markets/{t}/orderbook`.
  - No historical depth beyond what we record ourselves. Allium sells Kalshi order-book history; the price is not verified.
- **Polymarket Gamma** (`gamma-api.polymarket.com/markets`), free, no auth: `feeSchedule`, `feesEnabled`, `feeType`, `bestBid`/`bestAsk`/`spread`, `orderPriceMinTickSize`, `orderMinSize`. Closed markets keep these.
- **Polymarket CLOB** (`clob.polymarket.com`), free reads: `/book`, `/books` (500 per request), `/price`, `/midpoint`, `/spread`, `/tick-size`.

## Not verified

- Whether a newer Kalshi fee PDF exists after Feb 5, 2026: the live file returned HTTP 429, and Wayback captures from July to October 2026 also show 429s.
- Whether Kalshi's `fee_multiplier` encoded the PDF's index half-rate before 2026-07-03, and whether it scales maker fees.
- Whether a retail kalshi.com account is a direct member ($0.0001 balance precision) or not ($0.01).
- When Polymarket sports moved between 0.03 and 0.05, and how `feeSchedule.exponent` enters the formula when it isn't 1.
- The unit of Polymarket's `orderMinSize` (USDC or shares).
- Polymarket's site rule of showing the last trade when the spread is over 10¢: the docs page fetched didn't contain it.
- Kalshi's per-contract position limits today, and rate limits for requests without auth.
- How spreads vary over time: the F9 tables are one snapshot on 2026-10-09, skewed toward the liquid end. Dubach's bps figures assume a mid-price base, and the NBA paper doesn't define its bps.

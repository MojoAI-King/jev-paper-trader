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

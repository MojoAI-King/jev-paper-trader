# 02: Prices that don't add up

Researched 2026-10-09 for `docs/research/briefs/02-prices-that-dont-add-up.md`.

## Answer in five lines

1. Prices that can't all be right are common on Polymarket. In a year of its data (Apr 2024 to Apr 2025), 662 of 1,578 multi-outcome markets were at some moment priced more than 2¢ away from adding up. But a 2026 order-book study finds these gaps last about **16 seconds** (median), and fast bots take almost all of the profit.
2. Across venues, only about 2–8% of non-sports markets have a twin on the other venue. Where a twin exists, Kalshi and Polymarket can stay 2–4% apart for long stretches. Most of that persistent gap comes from small differences in the rules (who calls the result, the deadline, what happens if someone dies), not free money. Sports gaps close in seconds.
3. Under today's fees on both legs (Kalshi about 1.75¢ per contract at 50¢, plus Polymarket's per-market fee), most gaps a 30-minute snapshot can see are too small to capture. No source measured what's left after both venues' 2026 fees. That is not verified.
4. For this trader, arbitrage is not a strategy: we sample every 30 minutes, store no order-book depth, and can't fill two legs at once. A paper "arbitrage" profit from our snapshots would almost certainly be fiction.
5. The useful part is cheaper. (a) Make our own forecasts consistent within an event (BACKLOG B3): no two-way race at 38% + 23%, no ladder that rises with the strike. (b) Use a matched market on the other venue as a check in the betting rules. Both need Joey's approval as code changes, and each comes with a test below.

## Findings

**F1. Within one Polymarket event, prices that don't add up are frequent, and they existed both above and below 100%.**
Polymarket markets resolved between 1 Apr 2024 and 1 Apr 2025 cover 8,659 single-condition markets and 1,578 multi-outcome ("NegRisk") markets, 17,218 conditions in all. Of these, 7,051 conditions had at least one moment where the outcome prices summed more than 0.02 away from $1. A moment only counted when it allowed at least 5¢ profit per dollar and no outcome was above 95¢. 662 of the 1,578 multi-outcome markets had such a moment, about 100 each on average, with sports as outliers. Opportunities showed up on both sides, with sums above and below $1.
Caveat: prices are volume-weighted trade prices carried forward for up to 2.5 hours, not order-book asks. So these are inconsistencies seen after the fact, not proven fills at size. The period had no Polymarket trading fee and was dominated by the 2024 election.
Evidence: Saguillo, Ghafouri, Kiffer & Suarez-Tangil, "Unravelling the Probabilistic Forest: Arbitrage in Prediction Markets", AFT 2025 (peer-reviewed), §4.1, §6. https://arxiv.org/abs/2508.03474 and https://drops.dagstuhl.de/storage/00lipics/lipics-vol354-aft2025/LIPIcs.AFT.2025.27/LIPIcs.AFT.2025.27.pdf
Strength: **strong** that inconsistencies occurred; **weak** as a measure of what could be traded.

**F2. Someone took about $40M from these gaps on Polymarket in that year, almost all of it inside single events. That is a gross upper bound before fees.**
The authors' total is $39,587,585, and most of it came from multi-outcome markets:

| Trade | Profit |
|---|---|
| Buy every NO in a multi-outcome market | $17.3M |
| Buy every YES in a multi-outcome market | $11.1M |
| Buy YES + NO under $1 in a single-condition market | $5.9M |
| Sell YES + NO above $1 in a single-condition market | $4.7M |

The top account made $2.0M over 4,049 trades. Only about 1% of the estimated US-election opportunities were taken.
The totals are inferred from on-chain patterns (a wallet's bids within about an hour grouped together), fees are not deducted, and the lead author calls it "an upper bound on extractable profit, not what was actually pocketed". Profit was concentrated in the 2024 election and the August 2024 Democratic-nominee markets.
Evidence: same paper, §7.4. Flashbots post by the lead author: https://collective.flashbots.net/t/arbitrage-in-prediction-markets-strategies-impact-and-open-questions/5198
Strength: **moderate** (one study, one venue, before fees).

**F3. In 2026 order-book data, Polymarket's multi-outcome gaps last seconds and nearly all the profit goes to bots that use Polymarket's conversion contract.**
The order-book panel runs from 14 Apr 2026 to 19 May 2026. Gaps were counted only when they were positive after fees, assuming taker fills.
- **Gaps where the YES prices summed to less than $1:** 2,098 episodes. Among the 253 episodes whose duration could be measured exactly, the median was **16.15 seconds**.
- **Gaps on the NO side:** 36 episodes, with a median of 7.99 seconds over 5 measurable episodes.

The authors reconstruct about $1.12M of profit. About $1.086M came from strategies that convert NO shares through Polymarket's NegRisk adapter, and only $32k from buying a basket and waiting for settlement. The adapter converts NO into YES before settlement, but not the other way. So a NO-side basket can be recycled at once, while a YES-side basket ties money up until the market resolves.
Evidence: Gebele, Mutzel & Matthes, "Executable Arbitrage and Market Efficiency in Prediction Markets", arXiv 2608.00666, 1 Aug 2026 (preprint, not peer reviewed). Episode counts and durations were read from the full text: https://arxiv.org/html/2608.00666. The share of profit going to the top ten addresses is truncated in the text I could read; a blog reports it as about 75%.
Strength: **moderate** (primary, recent, but a preprint, and only about five weeks of order-book data).

**F4. Polymarket's own docs say the "sum of YES prices" test is not clean on augmented multi-outcome events.**
In a negative-risk event, one NO share in any outcome can be converted into one YES share in every other outcome. In *augmented* neg-risk events, outcomes can be added after trading starts. These events also carry placeholder outcomes and an "Other" outcome whose meaning changes as placeholders are named, and Polymarket says to "only trade on named outcomes". A detector must therefore read the neg-risk and augmented flags and drop placeholders and "Other" before summing.
Evidence: Polymarket docs, "Negative risk" (current, read 2026-10-09). https://docs.polymarket.com/advanced/neg-risk
Strength: **strong** (primary documentation).

**F5. Kalshi marks events where only one market can resolve YES, and returns collateral on NO positions in them, but only for users who switch it on.**
Kalshi's event object has a `mutually_exclusive` flag: true means only one market in the event can resolve YES. Nested markets come back with `with_nested_markets=true`. The help center describes "collateral return". Its example: buying NO on two candidates at 60¢ and 70¢ costs $1.30, but only $0.30 is held, because one of the NOs must pay $1. The feature is off by default, is fixed per event once you trade, and "may make you unable to sell positions for which you've already had collateral returned."
Evidence: Kalshi Python SDK EventData model (https://docs.kalshi.com/python-sdk/models/EventData); Kalshi help center "Collateral return" (https://help.kalshi.com/en/articles/13823816-collateral-return), both read 2026-10-09. The raw REST field name was not seen in a live response.
Strength: **moderate** for the field, **strong** for the collateral rule.
I found no study measuring how often Kalshi's mutually exclusive events add up to more or less than 100%.

**F6. Few markets have a twin on the other venue.**
The dataset covers 102,275 non-sports events on ten venues, from 2018 to Aug 2025.
- **Events:** about 6% were listed on more than one venue at the same time (as an identical market, or one contained in another). Because these events are long-lived, they make up about 10% of event-days.
- **Markets:** about 8% of Polymarket's markets had an identical market somewhere else, against about 2% of Kalshi's. The 8% counts a match on any of the ten venues, not only Kalshi.

Sports are excluded, and overlap rose sharply from 2024.
Evidence: Gebele & Matthes, "Semantic Non-Fungibility and Violations of the Law of One Price in Prediction Markets", arXiv 2601.01706, Jan 2026 (preprint), §5.1–5.2. https://arxiv.org/abs/2601.01706
Strength: **moderate**.

**F7. Where twins exist, prices stay apart for long stretches, mostly because one venue prices the event consistently higher.**
- **Size:** at the median, even the most liquid twins stay "2–4% away from execution-adjusted parity". The study counted fees and typical spreads, but assumed spreads rather than measuring them, and assumed zero fees on Kalshi and Polymarket for the markets studied, which is out of date for 2026.
- **Who sits there:** many pairs have a risk-free gap open for nearly their whole shared life, "driven primarily by directional disagreement, with one platform pricing the event consistently higher". Others sit at zero because fees absorb the visible gap.
- **2024 presidential case:**
  - **Gap size:** the execution-adjusted gap between Kalshi and Polymarket averaged about 3¢ and reached 7¢.
  - **Cause:** the two contracts were not the same bet. Polymarket resolved on network calls, Kalshi on inauguration.
- **What drives the high returns:** they come from a short time to resolution, not from large mispricing.

Evidence: same paper, §5.4, Figs 6–7.
Strength: **moderate** (one preprint pooling ten venues; out-of-date fee assumption).

**F8. In the 2024 election, Polymarket moved first and Kalshi followed.**
Identical contracts on Polymarket, Kalshi, PredictIt and Robinhood showed "significant price disparities across platforms". Polymarket led Kalshi in price discovery, most strongly when trading was heavy, and large-trade order imbalance predicted later moves. The authors call the gaps "economically meaningful arbitrage opportunities". The abstract gives no gap size in cents, no duration, and no figure after fees.
Evidence: Ng, Peng, Tao & Zhou, SSRN 5331995 (working paper, first posted Jul 2025, revised Apr 2026). Only the abstract was read; SSRN returned 403. https://papers.ssrn.com/abstract=5331995
Strength: **moderate** for "Polymarket leads"; **weak** for "capturable after fees".

**F9. Live sports gaps between the venues close in seconds, and what's left after fees is tiny.**
A developer's Kalshi–Polymarket sports matcher logged 870 cross-venue gaps in one 24-hour window. The median gap stayed open about 9 seconds and 96% closed within 30 seconds. Across one big match (Argentina vs Egypt), the total net of fees was $439, against $20.8M traded on Polymarket and $13.8M of Kalshi open interest. The matcher covered about 98% of sports and e-sports markets; the author says economics, bitcoin and weather markets are harder to match. No method is given for fees or matching.
Evidence: dev.to post, Jul 8 (year likely 2026). https://dev.to/michaelmustopo/built-a-prediction-market-arbitrage-no-sizable-arbitrage-found-36cf
Strength: **anecdotal**.
The workflow's verifiers refuted (0–3) a second-hand claim that *political* cross-venue gaps "last only seconds to minutes". F7 says political gaps from wording differences persist. Both can be true: noise gaps close fast, rule-difference gaps don't.

**F10. Different rules break cross-venue hedges, sometimes badly.**
- **Khamenei, Feb–Mar 2026:** Kalshi's "leaves office" contract had a death carve-out: it settles at the last traded price before the death, not as YES. Kalshi halted trading under rule 13.1 and settled the "before Mar 1" contract at $0.02 and the "before Apr 1" contract at $0.29. Polymarket's contract had no carve-out and was proposed YES, disputed twice, and still open on 1 Mar. A trader long YES on one venue and NO on the other would have lost on both counts: paid on neither, and with money stuck.
- **New York temperature:** Kalshi uses NOAA Central Park and Polymarket uses LaGuardia. The markets look identical, and both the paper's human annotator and its matching pipeline called them equivalent.
- **2024 election:** network calls vs inauguration (F7).
- **Fed rates (anecdotal):** "any cut" on one venue vs "at least 25bp at a scheduled meeting" on the other.

Evidence:
- DeFi Rate, 1 Mar 2026 (secondary): https://defirate.com/news/kalshi-halts-khamenei-market-polymarkets-contract-enters-second-dispute/
- Gebele & Matthes 2026 (F6).
- Fed example from practitioner guides via the verifiers.

Strength: **moderate** (documented cases, no count of how often).

**F11. Automatic matching of *related* markets gives mostly false positives, and the profit in related-market arbitrage was small.**
Saguillo et al. ran an LLM (DeepSeek-R1-Distill-Qwen-32B, with markets grouped by topic using embeddings) over 46,360 pairs of US-election markets.

| Stage | Pairs kept |
|---|---|
| Flagged as dependent by the LLM | 1,576 |
| Kept by an automated check | 374 |
| Genuine after manual review | 13 |
| Profit actually taken | 5 |

The five pairs made about $95k in total, the largest about $60k, mostly at thin moments with an average maximum profit of about $100. Outside elections, 2,267 pairs gave one flagged pair, and it failed the strict test.
For matching *identical* events across venues, Gebele & Matthes report a three-step pipeline:
1. a structural filter (same category, overlapping dates);
2. retrieval of the 20 nearest neighbours by text embedding;
3. a two-pass LLM check of what each market counts as YES.

The paper claims 99.9% recall and under 2% false positives. Our verifiers did not confirm those accuracy figures (1–2), so treat them as the authors' own claims.
Evidence: arXiv 2508.03474 §5.2, §6.3, §7.3; arXiv 2601.01706.
Strength: **strong** for "related-market matching is mostly false positives"; **weak** for the cross-venue accuracy figures.

**F12. Bots that hunt these gaps are simple and usually ignore fees. Their authors report little real profit.**
- **realfishsam (GitHub):** fuzzy title matching (Jaccard + Levenshtein, threshold 0.7). It buys YES on one venue and NO on the other when they cost 1¢ under $1, ignoring fees and slippage, polling every 30 s. Dry-run by default.
- **ImMike (GitHub):** text-similarity matching (0.6), a "1% after fees" gate with both fees set to 0 by default. The author: "Arbitrage opportunities are rare and fleeting". Profit figures come from simulation.
- **predictionmarketspicks scanner:** a scanner page that matches on title tokens (≥60% coverage), and on team, ET game date and opponent for sports. It uses Kalshi's 0.07·p·(1−p) fee and flags a gap only at ≥2¢ net with two-sided books. It drops gaps over 12 points as stale, and drops Polymarket legs with under $500 of 24h volume. It says "most days the two venues agree within 0–2pp, which does NOT clear the cost line".
- **A Polymarket bot template on clawhub:** checks crypto threshold ladders for prices out of order. It gates on a 4-point violation, an 8¢ maximum spread and $5k of volume, with no fee in the gate.

Evidence:
- https://github.com/realfishsam/prediction-market-arbitrage-bot
- https://github.com/ImMike/polymarket-arbitrage
- https://predictionmarketspicks.com/tools/arb-scanner (page read 2026-10-09)
- https://clawhub.ai/diagnostikon/polymarket-24h-price-curve-arb-trader

Strength: **anecdotal**. These are useful only as design references.

**F13. Ladders priced out of order: no measurement found on either venue.**
I found no study counting how often a higher strike (P(BTC > $110k)) is priced above a lower one on Kalshi or Polymarket. The closest work compares Polymarket bitcoin thresholds with Binance options, not with each other. Polymarket YES ran 5.6–6.3 points above the options-implied probability, on 287 hourly observations from 2023 (arXiv 2606.19517). A DeFi Rate dashboard (2026-10-09, last trades, not asks) showed two Kalshi contracts settling on the same October rate hike at 15.5% and 17.5%.
Strength: **none** for ladder frequency. This part of the brief needs our own data (test T2).

## What it means for our trader

Ranked by expected value for the effort. All of them are code changes, so each one waits for Joey's yes.

1. **Make our own forecasts fit together within an event (B3).** This is cheap, needs no fills, and goes straight at a flaw we already saw: Jev at 38% + 23% on a two-way race.
   - **Mutually exclusive outcomes:** where the market's event is mutually exclusive (Kalshi `mutually_exclusive`, Polymarket negRisk with named outcomes only), rescale each forecaster's YES probabilities to sum to 1.
   - **Ladders:** where it's a ladder of "above $X" markets on one event, force the forecasts to fall as X rises (isotonic fit).
   - **Expected effect:** a small Brier improvement on multi-leg events, and fewer bets on both sides of an incoherent pair. It won't close the 0.035–0.073 gap to the market by itself.
   - **Confidence:** moderate that it helps a little. It is mathematically safe for truly exclusive and exhaustive sets, and the size is unknown (test T3).
2. **Never treat a cross-venue gap or within-event gap as a bet on its own.**
   - **Why:** our snapshots are about 30 minutes apart. Within one cycle, the two venues are fetched one after the other: the Kalshi walk took 65 s when measured and may run up to 300 s (`KALSHI_DEADLINE`). We store no depth. Gaps that pay last 9–16 seconds (F3, F9). So any "arbitrage" our data shows is most likely a timing artefact, a rule mismatch (F10), or a fake price.
   - **The fake price:** `normalize_polymarket` falls back to the mid when there is no best ask, and sets `no_ask` from `1 − best_bid`.
   - **Effect:** avoids a fictional strategy.
   - **Confidence:** high.
3. **Use a matched twin on the other venue as a check in the betting rules, not in forecasting.**
   - **The rule:** where a verified twin exists, don't bet against the side that both venues' asks agree on. When the venues disagree, treat the Kalshi price as the stale one, since Polymarket leads (F8).
   - **The screen:** prices may enter only the code that makes the bet, never Jev's or Claude's inputs (`news.screen_facts` and its tests stay as they are).
   - **Effect:** small. It might trim the losing "bet against the favourite" group (REBUILD_SCOPE finding 4), but at most about 2–8% of non-sports markets will have a twin.
   - **Confidence:** low until T4 runs.
4. **If arbitrage is ever wanted, it's a different system.** It would need:
   - order-book polling every few seconds;
   - both legs filled at once;
   - real accounts on both venues;
   - money tied up until resolution.

   That conflicts with this repo's paper-only rule, and the evidence (F3, F9, F12) says the gaps that survive fees go to fast bots. **Not recommended.**

**Frequency to expect in our cycles.** These are estimates, not verified; T1, T2 and T4 measure them.

| Kind | Expected in our 100 + 100 markets per cycle |
|---|---|
| Cross-venue twins (non-sports) | about 2–8 pairs (F6). More if both venues' top-volume lists hold the same sports games, which is unmeasured. |
| Cross-venue gaps clearing both fees, seen in two consecutive snapshots | rare: 0 to a few per week, mostly rule mismatches when checked |
| Within-event sums off by more than fees, at a 30-minute snapshot | near zero (16-second median life, F3) |
| Kalshi ladders out of order by more than fees | not known (F13); expected near zero for liquid crypto ladders |

## Recipe for automatic detection

Use `engine.fee_per_contract(source, price, policy)` for each leg's taker fee and `policy.fees.slippage` per leg. In the formulas below, write

- a(·) for the best ask,
- f(·) for the fee at that ask,
- s for slippage per leg,
- m for a safety margin of at least the cost of tied-up money: about 0.05 × days to resolution ÷ 365, so roughly 0.4¢ for 30 days.

**A. Within one event, on one venue**
- **Which events count:**
  - Kalshi: `mutually_exclusive == true` (`GET /events?with_nested_markets=true`).
  - Polymarket: `negRisk == true` events from the Gamma `/events` endpoint, dropping placeholder and "Other" outcomes in augmented events (F4). The exact field names for "augmented" and "placeholder" are not verified.
- **Buy every NO.** This is safe with any subset of k legs, because at most one leg can resolve YES:
  flag when Σ(a(NO_i) + f(NO_i) + s) ≤ (k − 1) − m.
- **Buy every YES.** This is only safe when the set is also *exhaustive* (one outcome must happen). Mutually exclusive alone isn't enough, so require every leg and a rule that something resolves YES:
  flag when Σ(a(YES_i) + f(YES_i) + s) ≤ 1 − m.
- **Never flag YES + NO on the same market.** Both venues' books make yes_ask + no_ask = 1 + spread ≥ 1. A flag there is a data error.

**B. Ladders, on one event and one venue**
- Group "above X" markets by event ticker, which keeps the index, time and source the same. Sort by strike.
- For each pair L < H, buying YES(>L) and NO(>H) pays at least $1 whatever happens.
  Flag when a(YES_L) + f + s + a(NO_H) + f + s ≤ 1 − m.
- "Between" ranges are buckets: test them as in A.

**C. Across venues**
1. **Candidates:**
   - same category;
   - close times within 2 days of each other;
   - then either title-token overlap ≥ 0.6 or the top 20 embedding neighbours.
   - Sports: match on teams, ET game date and market type.
2. **Check the rules:** an LLM or a person compares the two `rules` texts on these points:
   - resolution source and station;
   - deadline and timezone;
   - whether a threshold includes the boundary or not;
   - what happens on death, cancellation or postponement;
   - who decides the result.

   Keep only "same YES-region" pairs, and store each verdict. This step sees question and rules text only, never prices, so it stays inside the price screen.
3. **Trade test,** in both directions:
   a_K(YES) + f_K + s + a_P(NO) + f_P + s ≤ 1 − m, and the mirror image.
4. **Freshness and persistence:**
   - both quotes fetched within 60 s of each other (store a fetch timestamp per market);
   - two-sided books on both legs;
   - gap ≤ 12 points (larger means a stale book);
   - the flag holds in two consecutive snapshots.

## How to test it on our history

The main session runs these on `papertrade_data/` (about 1,100 finished markets, snapshots every ~30 minutes). Report each count with n and ± (or a 95% interval).

**T1. Within-event sums at our snapshots.**
1. From `judgments.jsonl`, group rows by (cycle `ts`, `event`).
2. For groups with 2 or more legs from events that are mutually exclusive by their wording, compute the buy-every-NO test from A with k = the legs we have. For groups that hold every leg of an exhaustive set, also compute the buy-every-YES test.
3. Count flags, then check each flag against the next snapshot for that event.

Mutual exclusivity has to be judged from the wording, because we don't store Kalshi's flag. The full list of an event's legs is not verified to be in our data, because we only keep top-volume markets.
- **Kills the idea:** under 1% of groups flag after fees, or flags don't survive to the next snapshot.
- **Worth a second look:** flags that persist in 2 or more snapshots, each checked for a fake Polymarket ask (missing bestAsk).

**T2. Ladders out of order.**
1. For Kalshi events with 2 or more "above X" strikes in one snapshot (crypto, indexes, rates), sort by strike.
2. Count pairs where the higher strike's YES ask exceeds the lower strike's YES ask (gross).
3. Count the pairs that clear test B after fees.

- **Kills it:** zero net flags.
- **Also worth knowing:** whether Jev's, Jev + research's or Claude direct's forecasts ever rise with the strike on the same event. Count the share of ladders where that happens.

**T3. Coherence repair (B3).**
1. On finished markets that share an event with at least one other judged market, measure how often each forecaster's YES probabilities on mutually exclusive legs sum outside 0.9–1.1. Include the Lula/Bolsonaro case.
2. Rescale them to sum to 1. On ladders, apply an isotonic fit.
3. Compare Brier on the same markets: paired difference ± one standard error.

- **Confirms:** improvement over 2 SE on at least a few hundred markets (REBUILD_SCOPE finding 8).
- **Kills:** no improvement, or fewer than 200 markets in multi-leg events. The second outcome is a likely risk, since we fetch top-volume markets, not whole events.

**T4. Cross-venue twins.**
1. Match the Kalshi and Polymarket markets judged in the same cycle with C1 (tokens plus close-date window).
2. Hand-check 50 candidate pairs to measure the false-positive rate, and record how many twins per cycle survive.
3. For the true twins:
   - count gaps clearing C3 after both fees;
   - count how many consecutive snapshots each gap lasts;
   - compare the Brier score of each venue's mid with the outcome.

- **The twin signal is worth building only if:** the other venue's price beats this venue's price by more than 2 SE, on at least 200 twins.
- **Expected:** few twins; gaps that clear fees are rare and mostly turn out to be rule differences.

## Data sources

| Name | URL | Cost | What it gives, and limits |
|---|---|---|---|
| Kalshi Trade API v2, events | `GET /trade-api/v2/events?with_nested_markets=true`, docs at https://docs.kalshi.com | free, public read without auth | `mutually_exclusive` flag, nested markets, asks and bids. The rate limit is what our fetch already respects (1 s between pages). |
| Polymarket Gamma API, events | https://gamma-api.polymarket.com/events | free | negRisk flag and the outcome markets of an event. We use `/markets` today, which loses the grouping into one event except via `events[0].id`. |
| Polymarket CLOB order book | https://docs.polymarket.com | free | Depth at each price. This is the only way to know if a gap had size behind it. |
| Gebele & Matthes relation dataset | arXiv 2601.01706 | unknown | About 1,500 human-validated cross-venue twin classes. Whether it is public was not verified. |
| Commercial arbitrage scanners (predictionmarketspicks, defirate dashboards) | see F12 | free pages | Last-trade comparisons only. Anecdotal; not a data feed. |

## Not verified

- **What survives 2026 fees on both legs, across venues.** No source measured it. The 2–4% figure (F7) assumed zero fees on Kalshi and Polymarket.
- **How often Kalshi's mutually exclusive events add up to more or less than 100%.** No source found for Kalshi.
- **How often ladders are out of order** on either venue (F13).
- **How many of our cycle's markets have a twin once sports are included.** F6 excludes sports, and F9's 98% sports coverage comes from an anecdotal source.
- **How much depth sat at the best ask when gaps appeared.** No study measured it, and we don't store depth.
- **The top-ten addresses' share of converter profit (about 75%) in arXiv 2608.00666.** It is truncated in the text I could read.
- **Gebele & Matthes's matching accuracy (99.9% recall, under 2% false positives after the LLM step).** These are the authors' claims; our verifiers voted 1–2 against confirming them.
- **Refuted by the verifiers and left out of the findings:**
  - "On 62 of 65 days before the 2024 election, Harris + Trump didn't sum to $1 on at least one venue" (second-hand from Clinton & Huang, refuted 1–2);
  - "every Polymarket rebalancing opportunity summed below 1" (0–3; F1 says both directions);
  - "political cross-venue gaps last only seconds to minutes" (0–3).
- **The exact Polymarket field names for augmented neg-risk events and placeholders,** and the raw Kalshi REST field name. The Kalshi name was seen only in the SDK docs.

# Task: Fixes from research feedback: real Polymarket fees, real-price scoring, weather

Kind: Living. Task record.

- **ID:** 2026-10-09-fixes-from-research-feedback-real-polyma-6946
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-09T21:53:37.344Z

## Request

not yet written

## Acceptance criteria

- [ ] Polymarket bets pay Polymarket's real taker fee by category (B26); the Forecasters panel and paired scores use only markets with a real price and say how many were left out (B25); AI strategies stop betting weather markets (report 07); tests cover each; offline tests pass; page redeployed and checked live

## Decisions

not yet written

## Checkpoints

### 2026-10-09T21:53:37.344Z

- **State:** B26 (each Polymarket market pays its own published taker fee; 0.05 default) and B25 (head-to-head scores only on real-priced markets, left-out count shown) committed at c5f54c2, pushed, page deployed (Worker 996e8d0c). Live check pending: edge cache still served the old page at 21:53Z; the next cycle must write paired.left_out and fee_rate. Reports 01, 05, 06, 07 in and checked; no category skips (losses since the floor are sports and other, not weather or price thresholds)
- **Evidence:** 125 offline tests OK (FeeTests, updated paired test); live paired preview 562 markets, 101 left out; Polymarket API feeSchedule seen live (politics 0.04, geopolitics off)
- **Next:** Confirm the live page and the 22:04Z cycle (paired.left_out in summary.json, fee_rate on new Polymarket judgments), then archive B25 and B26 and close the task; keep checking reports as Joey calls them done
- **Git:** master @ c5f54c2, 2 uncommitted

## Handoff

- **State:** B26 (each Polymarket market pays its own published taker fee; 0.05 default) and B25 (head-to-head scores only on real-priced markets, left-out count shown) committed at c5f54c2, pushed, page deployed (Worker 996e8d0c). Live check pending: edge cache still served the old page at 21:53Z; the next cycle must write paired.left_out and fee_rate. Reports 01, 05, 06, 07 in and checked; no category skips (losses since the floor are sports and other, not weather or price thresholds). Evidence: 125 offline tests OK (FeeTests, updated paired test); live paired preview 562 markets, 101 left out; Polymarket API feeSchedule seen live (politics 0.04, geopolitics off).
- **Next:** Confirm the live page and the 22:04Z cycle (paired.left_out in summary.json, fee_rate on new Polymarket judgments), then archive B25 and B26 and close the task; keep checking reports as Joey calls them done
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: add report files by name; past Polymarket bets keep their old zero-fee cost (not rewritten)

# Task: Edge scan: every Kalshi market family for steady mispricing (B33)

Kind: Living. Task record.

- **ID:** 2026-10-10-edge-scan-every-kalshi-market-family-for-2725
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-10T23:31:07.293Z

## Request

out of all your research on how to be the 11th 8 figure player thats what you came up with

## Acceptance criteria

- [ ] docs/research/scripts/edge_scan.py runs over the active non-mention Kalshi series and its results (category table and leads with event-resampled ranges and both halves) are recorded in docs/research/CHECKS.md
- [ ] Each lead that survives gets a series-level history test with the exact rule a live strategy would follow before anything is built

## Decisions

not yet written

## Checkpoints

### 2026-10-10T23:07:49.493Z

- **State:** Edge scan running locally (docs/research/scripts/edge_scan.py, 41cdc5e) over 4,552 active non-mention Kalshi series: real bid/ask 24 h and 72 h before close, after fees, split by close date; 469 markets scored so far. B32 closed as verified. Joey: paid tools and data yes, real money only after a strategy is proven (decision 2026-10-10-paid-tools-and-data-yes-real-money-only-6f1a).
- **Evidence:** edge scan smoke test: 8 series, 41 markets scored; 151 offline tests OK; maintenance recorded
- **Next:** When the scan finishes (about 3 h from 22:00Z): python3 -I docs/research/scripts/edge_scan.py --summarize; record the category table and leads in docs/research/CHECKS.md; deepen surviving leads with a series-level history test
- **Git:** master @ 7925c69, 2 uncommitted

### 2026-10-10T23:31:07.293Z

- **State:** Edge scan running (4354 markets scored). Analysis plan fixed before results: separate markets that closed early because their event happened (a price 24 h before an unscheduled close is look-ahead) from scheduled-event markets, using expiration and expected-expiration times from the cached listings; then put each surviving lead through an adversarial check (look-ahead, quote quality, deeper resampling, capacity) before anything is built.
- **Evidence:** scan progress read from research_data/edge_scan_rows.jsonl; no trader code changed since 151 offline tests passed
- **Next:** When the scan finishes (about 02:00Z): summarize, enrich rows with scheduled-vs-early close, run the adversarial verification of leads, record results in docs/research/CHECKS.md
- **Git:** master @ 313dff6, 2 uncommitted

## Handoff

- **State:** Edge scan running (4354 markets scored). Analysis plan fixed before results: separate markets that closed early because their event happened (a price 24 h before an unscheduled close is look-ahead) from scheduled-event markets, using expiration and expected-expiration times from the cached listings; then put each surviving lead through an adversarial check (look-ahead, quote quality, deeper resampling, capacity) before anything is built. Evidence: scan progress read from research_data/edge_scan_rows.jsonl; no trader code changed since 151 offline tests passed.
- **Next:** When the scan finishes (about 02:00Z): summarize, enrich rows with scheduled-vs-early close, run the adversarial verification of leads, record results in docs/research/CHECKS.md
- **Blocked:** nothing
- **Watch out:** The scan runs on this Mac (research_data/ is gitignored); a rerun skips markets already scored. With 15-minute cycles the bot alone makes ~4 commits an hour, so Skilliton's 15-commit maintenance nudge comes every few hours

# Task: Edge scan: every Kalshi market family for steady mispricing (B33)

Kind: Living. Task record.

- **ID:** 2026-10-10-edge-scan-every-kalshi-market-family-for-2725
- **State:** done-local
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-11T03:54:55.124Z

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

### 2026-10-11T01:16:26.531Z

- **State:** Edge scan v1 done (20,747 markets): all 10 leads were a look-ahead artifact (markets chosen by final volume pick the winners; the clock was anchored to outcome-dependent closes); the unbiased subset (7,494, mostly sports games) has no cut above zero. v2 (7abb0c6) picks without hindsight and decides 24/72 h before the scheduled occurrence time; running in the background since ~01:40Z (about 3 h).
- **Evidence:** v1 summary and the complete-event check (sports YES 2-15c: +46.4% all vs -47.0% unbiased); occurrence identical across markets in 29,297 of 29,482 events; v2 smoke test 33 rows
- **Next:** When v2 finishes: python3 -I docs/research/scripts/edge_scan.py --summarize; put each lead through an adversarial check (look-ahead and selection, quote quality and capacity, fresh-data replication, mechanism); record in docs/research/CHECKS.md
- **Git:** master @ 7abb0c6, 2 uncommitted

### 2026-10-11T03:13:13.614Z

- **State:** Edge scan v2 (no hindsight) complete: 19,960 markets in 1,373 series; 1 lead in 57 cuts (weather YES at 50-70c, 24 h before occurrence: +29.0% [+8.7, +44.0], 52 events, both halves positive; ~1 expected by chance). Adversarial workflow wf_b31c17a4-a6a running: lookahead, replication, quotes, mechanism lenses on the lead, plus a recheck of the mention finding without final-volume selection.
- **Evidence:** edge_scan.py --summarize on research_data/edge_scan_rows_v2.jsonl (19,960 rows)
- **Next:** Read the workflow verdicts, record results in docs/research/CHECKS.md, report to Joey
- **Git:** master @ a0071b8, 2 uncommitted

## Handoff

- **State:** Edge scan v2 (no hindsight) complete: 19,960 markets in 1,373 series; 1 lead in 57 cuts (weather YES at 50-70c, 24 h before occurrence: +29.0% [+8.7, +44.0], 52 events, both halves positive; ~1 expected by chance). Adversarial workflow wf_b31c17a4-a6a running: lookahead, replication, quotes, mechanism lenses on the lead, plus a recheck of the mention finding without final-volume selection. Evidence: edge_scan.py --summarize on research_data/edge_scan_rows_v2.jsonl (19,960 rows).
- **Next:** Read the workflow verdicts, record results in docs/research/CHECKS.md, report to Joey
- **Blocked:** nothing
- **Watch out:** v1 rows (research_data/edge_scan_rows.jsonl) are look-ahead biased: never use them for leads; v2 rows are research_data/edge_scan_rows_v2.jsonl

# Task: Mention NO strategy: live forward test

Kind: Living. Task record.

- **ID:** 2026-10-10-mention-no-strategy-live-forward-test-aaec
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-10T05:22:33.449Z

## Request

not yet written

## Acceptance criteria

- [ ] The live walk collects Kalshi mention markets; the mention pass logs them and places NO probes at 30-70c before the event within the ask size; settle scores them; after 150 settled bets the keep/kill rule in docs/EXPERIMENTS.md is applied and reported to Joey

## Decisions

not yet written

## Checkpoints

### 2026-10-10T05:22:33.449Z

- **State:** mention_no built and pushed (cfff32a): Kalshi walk keeps mention markets, scan looks once per 6h with no Jev call, logs to mentions.jsonl, NO probes at 30-70c before the event capped at the ask size. Replication: +21.0% after fees [+6.1, +35.5] on 639 settled markets. Maker test: makers save 4-5 pts but break even. Sharp line verified live (no qualifying gaps yet). Jev alone and Jev alone, bold retired
- **Evidence:** 141 offline tests OK; CHECKS.md has the replication and maker tables; gh run 04:34Z green on the sharp code
- **Next:** Confirm the next CI cycle runs green on cfff32a and shows stats.mentions; watch for mention markets to appear (earnings season next week) and the first NO probes
- **Git:** master @ cfff32a, 5 uncommitted

## Handoff

- **State:** mention_no built and pushed (cfff32a): Kalshi walk keeps mention markets, scan looks once per 6h with no Jev call, logs to mentions.jsonl, NO probes at 30-70c before the event capped at the ask size. Replication: +21.0% after fees [+6.1, +35.5] on 639 settled markets. Maker test: makers save 4-5 pts but break even. Sharp line verified live (no qualifying gaps yet). Jev alone and Jev alone, bold retired. Evidence: 141 offline tests OK; CHECKS.md has the replication and maker tables; gh run 04:34Z green on the sharp code.
- **Next:** Confirm the next CI cycle runs green on cfff32a and shows stats.mentions; watch for mention markets to appear (earnings season next week) and the first NO probes
- **Blocked:** nothing
- **Watch out:** Stage by explicit path; tests must never reach The Odds API (DataDirTest guards it) or write real mentions.jsonl (DataDirTest covers MENTIONS)

# Task: Rebuild research: fourteen narrow briefs and their reports

Kind: Living. Task record.

- **ID:** 2026-10-09-rebuild-research-fourteen-narrow-briefs-96f9
- **State:** verified
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-09T23:11:12.098Z

## Request

not yet written

## Acceptance criteria

- [ ] Fourteen narrow briefs in docs/research/briefs/ (done); each research tab writes its report to docs/research/NN-<slug>.md; the main session commits every report, checks its claims against our data, and writes the rebuild plan for Joey

## Decisions

not yet written

## Checkpoints

### 2026-10-09T21:16:29.810Z

- **State:** Fourteen narrow research briefs ready in docs/research/briefs/ (run sheet docs/research/README.md; page https://claude.ai/artifact/2USu1tPk31NdbK2p1vj5ta). Joey runs each as its own Claude Code tab, all at once; each tab writes only docs/research/NN-<slug>.md and does not commit. No reports yet
- **Evidence:** briefs committed at 8d23ab7; 122 offline tests OK; run-sheet page checked once by screenshot
- **Next:** When the tabs finish: commit the reports, mark them done in the run sheet, check each report's claims against papertrade_data, then write the plan (strategies, backtests to pass, code changes for Joey to approve)
- **Git:** master @ 8d23ab7, 2 uncommitted

### 2026-10-09T21:17:50.289Z

- **State:** Fourteen narrow research briefs ready; Joey asked for one paste-ready prompt at a time and runs each as its own Claude Code tab with the deep-research skill on Opus 5.5 high. Order given: 01, 05, 06, 07, 09, 10, 14, then 02, 03, 04, 08, 11, 12, 13. Prompts are built from the brief files (scratchpad paste.py). No reports yet
- **Evidence:** briefs committed; README rule fixed so a tab carries on after declining a hook reminder
- **Next:** Hand Joey the next prompt when he asks; when tabs finish, commit the reports, mark them in the run sheet, check claims against papertrade_data, write the plan
- **Git:** master @ 87b85c3, 2 uncommitted

### 2026-10-09T21:45:20.490Z

- **State:** Reports 01, 05, 07 in and checked (docs/research/CHECKS.md): on real-priced markets the price is about calibrated and none of our forecasters adds information; cheap contracts lose ~60%, favourites break even; weather markets are hard to beat. 06 running; 09, 10, 14, 02, 03, 04, 08, 11, 12, 13 handed out by a dispatcher tab from docs/research/prompts/. New: B26 (Polymarket taker fees, trader charges 0)
- **Evidence:** event-clustered bootstrap refits on 1,006 real-priced first looks; price-bucket returns by venue; WebFetch of AIA (2511.07678), Kim (2602.21229), Crosier (2609.23969), docs.polymarket.com/trading/fees and Kalshi KXHIGHNY rules; 122 tests OK
- **Next:** Process each report as Joey says it's done: commit only that file, check it into CHECKS.md, mark the run sheet; then the plan. Joey decides B25 and B26
- **Git:** master @ 8bf4adf, 2 uncommitted

## Handoff

- **State:** Reports 01, 05, 07 in and checked (docs/research/CHECKS.md): on real-priced markets the price is about calibrated and none of our forecasters adds information; cheap contracts lose ~60%, favourites break even; weather markets are hard to beat. 06 running; 09, 10, 14, 02, 03, 04, 08, 11, 12, 13 handed out by a dispatcher tab from docs/research/prompts/. New: B26 (Polymarket taker fees, trader charges 0). Evidence: event-clustered bootstrap refits on 1,006 real-priced first looks; price-bucket returns by venue; WebFetch of AIA (2511.07678), Kim (2602.21229), Crosier (2609.23969), docs.polymarket.com/trading/fees and Kalshi KXHIGHNY rules; 122 tests OK.
- **Next:** Process each report as Joey says it's done: commit only that file, check it into CHECKS.md, mark the run sheet; then the plan. Joey decides B25 and B26
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: add report files by name, never git add -A; don't commit a report Joey hasn't called done; all tabs draw on Joey's Claude plan

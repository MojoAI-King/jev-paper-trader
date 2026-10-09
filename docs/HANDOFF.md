# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-09 18:50 EDT

- **State:** Phase 1 shipped at 04b8c2a (sizing by measured skill with probes, one stake per event, real price required, Kalshi per-series fees, slower capped review); page deployed (Worker ee378ff7); live check of the 23:04Z cycle running. B29 tested offline and dropped. Maintenance run. Evidence: 131 offline tests OK; B29 split test in docs/research/CHECKS.md.
- **Next:** Confirm the 23:04Z cycle (green run, skill in scans, probes for all but original, Kalshi fee_multiplier on judgments); then report to Joey. Phase 2: B27 needs Joey's $30; B28 and B30 next
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)
- **Git:** master @ 7bd74c0, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 22:50 UTC)

## Earlier

### 2026-10-09 18:49 EDT
- **State:** Rebuild phase 1 shipped at 04b8c2a under Joey's blessing (he is away for Shabbat): every strategy but original sizes by measured skill (lambda ~0 for all, so 0.25% probe bets, max 5/day), one stake per event, real price required, Kalshi per-series fee multipliers, review changes at most every 7 days within caps (Kelly 0.5, 3%/bet, 50% open), calibration needs 300. Page deployed (Worker ee378ff7). Live check pending on the 23:04Z cycle. All 14 research reports checked; plan in docs/REBUILD_PLAN.md. Evidence: 131 offline tests OK (SkillSizingTests, Kalshi multiplier test, tuning tests moved to the new limits).
- **Next:** Confirm the 23:04Z cycle: workflow green, scans carry skill, new bets probe for all but original, Kalshi judgments carry fee_multiplier; then report to Joey when he is back. Phase 2 waits: B27 needs his $30 decision; B28-B30 next
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)
- **Git:** master @ 04b8c2a, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 22:49 UTC)

### 2026-10-09 18:09 EDT
- **State:** B25 and B26 done and verified live: page matched build at 21:53Z; cycle 22:09Z published paired n 562, left_out 101; new Polymarket judgments carry fee_rate (0.04, 0.05). No bet since the fix yet, so a fee-charged bet isn't seen live (FeeTests cover it). Archived both. Evidence: background check output (page cmp, origin summary.json, judgments tail); 125 offline tests OK.
- **Next:** Check research reports as Joey calls them done (09, 10, 14, 02, 03, 04, 08, 11, 12, 13 via the helper tab), then write the rebuild plan
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: add report files by name; past Polymarket bets keep their old zero-fee cost (not rewritten)
- **Git:** master @ e4bae17, 14 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 22:09 UTC)

### 2026-10-09 17:53 EDT
- **State:** B26 (each Polymarket market pays its own published taker fee; 0.05 default) and B25 (head-to-head scores only on real-priced markets, left-out count shown) committed at c5f54c2, pushed, page deployed (Worker 996e8d0c). Live check pending: edge cache still served the old page at 21:53Z; the next cycle must write paired.left_out and fee_rate. Reports 01, 05, 06, 07 in and checked; no category skips (losses since the floor are sports and other, not weather or price thresholds). Evidence: 125 offline tests OK (FeeTests, updated paired test); live paired preview 562 markets, 101 left out; Polymarket API feeSchedule seen live (politics 0.04, geopolitics off).
- **Next:** Confirm the live page and the 22:04Z cycle (paired.left_out in summary.json, fee_rate on new Polymarket judgments), then archive B25 and B26 and close the task; keep checking reports as Joey calls them done
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: add report files by name; past Polymarket bets keep their old zero-fee cost (not rewritten)
- **Git:** master @ c5f54c2, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:53 UTC)

### 2026-10-09 17:45 EDT
- **State:** Reports 01, 05, 07 in and checked (docs/research/CHECKS.md): on real-priced markets the price is about calibrated and none of our forecasters adds information; cheap contracts lose ~60%, favourites break even; weather markets are hard to beat. 06 running; 09, 10, 14, 02, 03, 04, 08, 11, 12, 13 handed out by a dispatcher tab from docs/research/prompts/. New: B26 (Polymarket taker fees, trader charges 0). Evidence: event-clustered bootstrap refits on 1,006 real-priced first looks; price-bucket returns by venue; WebFetch of AIA (2511.07678), Kim (2602.21229), Crosier (2609.23969), docs.polymarket.com/trading/fees and Kalshi KXHIGHNY rules; 122 tests OK.
- **Next:** Process each report as Joey says it's done: commit only that file, check it into CHECKS.md, mark the run sheet; then the plan. Joey decides B25 and B26
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: add report files by name, never git add -A; don't commit a report Joey hasn't called done; all tabs draw on Joey's Claude plan
- **Git:** master @ 8bf4adf, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:45 UTC)

### 2026-10-09 17:17 EDT
- **State:** Fourteen narrow research briefs ready; Joey asked for one paste-ready prompt at a time and runs each as its own Claude Code tab with the deep-research skill on Opus 5.5 high. Order given: 01, 05, 06, 07, 09, 10, 14, then 02, 03, 04, 08, 11, 12, 13. Prompts are built from the brief files (scratchpad paste.py). No reports yet. Evidence: briefs committed; README rule fixed so a tab carries on after declining a hook reminder.
- **Next:** Hand Joey the next prompt when he asks; when tabs finish, commit the reports, mark them in the run sheet, check claims against papertrade_data, write the plan
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: never git add -A or commit their half-written reports mid-run; they must not run cycle/scan/settle/review or skilliton; all of them draw on Joey's Claude plan (week 47%, resets Mon 2026-10-12 08:00Z)
- **Git:** master @ 87b85c3, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:17 UTC)

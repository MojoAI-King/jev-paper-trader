# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-09 19:40 EDT

- **State:** Phase 1 verified live: cycle 23:09Z green on 04b8c2a with lambda 0 for all sources; first bet after it was a probe (bold, $175.20, 0.25% of equity, 23:35Z). Task closed. Joey is away for Shabbat; plan and results are in docs/REBUILD_PLAN.md. Evidence: portfolio bold.json open bet at 2026-10-09T23:35:08Z with sizing probe, lambda 0.0; peak_equity recorded on every book.
- **Next:** When Joey is back: summarize phase 1 and the research verdict; ask about B27 ($30/month sports odds). Phase 2 candidates B28 (math pricer) and B30 (Jev jobs) wait for his go-ahead on scope
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)
- **Git:** master @ e6b2e8f, 5 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 23:40 UTC)

## Earlier

### 2026-10-09 19:11 EDT
- **State:** Phase 1 live: cycle 2026-10-09T23:09Z ran green on 04b8c2a; skill computed in the scan (lambda 0 for all four sources: raw -0.06/-0.03/-0.02/-0.03 on 1,025/843/562/774 markets); Kalshi judgments carry fee_multiplier. No bet in that cycle, so a probe bet isn't seen yet; a background check is waiting for the first one. Research task closed (14 of 14 reports checked). Evidence: gh run 2026-10-09T23:04:45Z success; scans.jsonl 23:05Z skill field; judgments since 23:00Z.
- **Next:** Confirm the first new bet is a probe (original at the old size), then summarize for Joey when he's back
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)
- **Git:** master @ ee51a75, 6 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 23:11 UTC)

### 2026-10-09 18:50 EDT
- **State:** Phase 1 shipped at 04b8c2a (sizing by measured skill with probes, one stake per event, real price required, Kalshi per-series fees, slower capped review); page deployed (Worker ee378ff7); live check of the 23:04Z cycle running. B29 tested offline and dropped. Maintenance run. Evidence: 131 offline tests OK; B29 split test in docs/research/CHECKS.md.
- **Next:** Confirm the 23:04Z cycle (green run, skill in scans, probes for all but original, Kalshi fee_multiplier on judgments); then report to Joey. Phase 2: B27 needs Joey's $30; B28 and B30 next
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)
- **Git:** master @ 7bd74c0, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 22:50 UTC)

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

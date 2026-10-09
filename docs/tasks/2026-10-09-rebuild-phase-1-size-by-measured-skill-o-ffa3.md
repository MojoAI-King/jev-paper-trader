# Task: Rebuild phase 1: size by measured skill, one stake per event, real Kalshi fees, slower review

Kind: Living. Task record.

- **ID:** 2026-10-09-rebuild-phase-1-size-by-measured-skill-o-ffa3
- **State:** verified
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-09T23:40:50.725Z

## Request

not yet written

## Acceptance criteria

- [ ] Strategies other than original place probe stakes while their forecaster's measured lambda is 0, and Kelly stakes on a market-shrunk forecast once it is positive; one stake budget per event and no opposite sides; Kalshi fees use each series' published multiplier; the daily review changes a strategy at most every 7 days within capped bounds; tests cover each; offline tests pass; deployed and seen working on a live cycle

## Decisions

not yet written

## Checkpoints

### 2026-10-09T22:49:28.335Z

- **State:** Rebuild phase 1 shipped at 04b8c2a under Joey's blessing (he is away for Shabbat): every strategy but original sizes by measured skill (lambda ~0 for all, so 0.25% probe bets, max 5/day), one stake per event, real price required, Kalshi per-series fee multipliers, review changes at most every 7 days within caps (Kelly 0.5, 3%/bet, 50% open), calibration needs 300. Page deployed (Worker ee378ff7). Live check pending on the 23:04Z cycle. All 14 research reports checked; plan in docs/REBUILD_PLAN.md
- **Evidence:** 131 offline tests OK (SkillSizingTests, Kalshi multiplier test, tuning tests moved to the new limits)
- **Next:** Confirm the 23:04Z cycle: workflow green, scans carry skill, new bets probe for all but original, Kalshi judgments carry fee_multiplier; then report to Joey when he is back. Phase 2 waits: B27 needs his $30 decision; B28-B30 next
- **Git:** master @ 04b8c2a, 2 uncommitted

### 2026-10-09T22:50:41.372Z

- **State:** Phase 1 shipped at 04b8c2a (sizing by measured skill with probes, one stake per event, real price required, Kalshi per-series fees, slower capped review); page deployed (Worker ee378ff7); live check of the 23:04Z cycle running. B29 tested offline and dropped. Maintenance run
- **Evidence:** 131 offline tests OK; B29 split test in docs/research/CHECKS.md
- **Next:** Confirm the 23:04Z cycle (green run, skill in scans, probes for all but original, Kalshi fee_multiplier on judgments); then report to Joey. Phase 2: B27 needs Joey's $30; B28 and B30 next
- **Git:** master @ 7bd74c0, 2 uncommitted

### 2026-10-09T23:11:15.110Z

- **State:** Phase 1 live: cycle 2026-10-09T23:09Z ran green on 04b8c2a; skill computed in the scan (lambda 0 for all four sources: raw -0.06/-0.03/-0.02/-0.03 on 1,025/843/562/774 markets); Kalshi judgments carry fee_multiplier. No bet in that cycle, so a probe bet isn't seen yet; a background check is waiting for the first one. Research task closed (14 of 14 reports checked)
- **Evidence:** gh run 2026-10-09T23:04:45Z success; scans.jsonl 23:05Z skill field; judgments since 23:00Z
- **Next:** Confirm the first new bet is a probe (original at the old size), then summarize for Joey when he's back
- **Git:** master @ ee51a75, 6 uncommitted

### 2026-10-09T23:40:50.725Z

- **State:** Phase 1 verified live: cycle 23:09Z green on 04b8c2a with lambda 0 for all sources; first bet after it was a probe (bold, $175.20, 0.25% of equity, 23:35Z). Task closed. Joey is away for Shabbat; plan and results are in docs/REBUILD_PLAN.md
- **Evidence:** portfolio bold.json open bet at 2026-10-09T23:35:08Z with sizing probe, lambda 0.0; peak_equity recorded on every book
- **Next:** When Joey is back: summarize phase 1 and the research verdict; ask about B27 ($30/month sports odds). Phase 2 candidates B28 (math pricer) and B30 (Jev jobs) wait for his go-ahead on scope
- **Git:** master @ e6b2e8f, 5 uncommitted

## Handoff

- **State:** Phase 1 verified live: cycle 23:09Z green on 04b8c2a with lambda 0 for all sources; first bet after it was a probe (bold, $175.20, 0.25% of equity, 23:35Z). Task closed. Joey is away for Shabbat; plan and results are in docs/REBUILD_PLAN.md. Evidence: portfolio bold.json open bet at 2026-10-09T23:35:08Z with sizing probe, lambda 0.0; peak_equity recorded on every book.
- **Next:** When Joey is back: summarize phase 1 and the research verdict; ask about B27 ($30/month sports odds). Phase 2 candidates B28 (math pricer) and B30 (Jev jobs) wait for his go-ahead on scope
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)

# Task: Rebuild phase 1: size by measured skill, one stake per event, real Kalshi fees, slower review

Kind: Living. Task record.

- **ID:** 2026-10-09-rebuild-phase-1-size-by-measured-skill-o-ffa3
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-09T22:49:28.335Z

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

## Handoff

- **State:** Rebuild phase 1 shipped at 04b8c2a under Joey's blessing (he is away for Shabbat): every strategy but original sizes by measured skill (lambda ~0 for all, so 0.25% probe bets, max 5/day), one stake per event, real price required, Kalshi per-series fee multipliers, review changes at most every 7 days within caps (Kelly 0.5, 3%/bet, 50% open), calibration needs 300. Page deployed (Worker ee378ff7). Live check pending on the 23:04Z cycle. All 14 research reports checked; plan in docs/REBUILD_PLAN.md. Evidence: 131 offline tests OK (SkillSizingTests, Kalshi multiplier test, tuning tests moved to the new limits).
- **Next:** Confirm the 23:04Z cycle: workflow green, scans carry skill, new bets probe for all but original, Kalshi judgments carry fee_multiplier; then report to Joey when he is back. Phase 2 waits: B27 needs his $30 decision; B28-B30 next
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)

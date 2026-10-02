# Task: Forecaster scoreboard on the page (p7)

Kind: Living. Task record.

- **ID:** 2026-10-01-forecaster-scoreboard-on-the-page-p7-91a5
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-02T02:22:41.021Z

## Request

not yet written

## Acceptance criteria

- [ ] The page shows Jev alone, Jev + research, Claude direct and the market scored on the same resolved markets, with counts, updated each cycle; Joey approved p7; tests cover it; offline tests pass; deployed and checked live

## Decisions

not yet written

## Checkpoints

### 2026-10-02T02:22:41.021Z

- **State:** Forecasters panel built (engine.paired, page panel under the feed, report lines), p7 approved, committed 3a605d0 and pushed; page shell deployed (Worker version 1e638bb3), live HTML equals the build. Not yet verified: the live panel's numbers, which appear once a cycle on the new code writes summary.json
- **Evidence:** 122 offline tests OK incl. test_forecasters_are_scored_head_to_head_on_the_same_markets; screenshots at 1600, 1280 and a true 400px frame; local paired scores on 111 markets: market 0.119, Jev + research 0.184, Claude direct 0.195, Jev alone 0.241
- **Next:** Confirm summary.json on origin carries calibration.paired and the live page shows the panel filled; then close the task as verified. Watch the post-floor bets settle (8 close 2026-10-06)
- **Git:** master @ 3a605d0, 6 uncommitted

## Handoff

- **State:** Forecasters panel built (engine.paired, page panel under the feed, report lines), p7 approved, committed 3a605d0 and pushed; page shell deployed (Worker version 1e638bb3), live HTML equals the build. Not yet verified: the live panel's numbers, which appear once a cycle on the new code writes summary.json. Evidence: 122 offline tests OK incl. test_forecasters_are_scored_head_to_head_on_the_same_markets; screenshots at 1600, 1280 and a true 400px frame; local paired scores on 111 markets: market 0.119, Jev + research 0.184, Claude direct 0.195, Jev alone 0.241.
- **Next:** Confirm summary.json on origin carries calibration.paired and the live page shows the panel filled; then close the task as verified. Watch the post-floor bets settle (8 close 2026-10-06)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the week meter rose 68 to 82% while the trader made 0-1 calls, so other use on that account is filling it (not verified); never build an unattended job that edits or ships code

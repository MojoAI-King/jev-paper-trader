# Task: Dependable trading trigger and mission-control dashboard

Kind: Living. Task record.

- **ID:** 2026-09-27-dependable-trading-trigger-and-mission-c-d56e
- **State:** verified
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-09-27T18:36:06.411Z

## Request

As long as it's automatically trading and I don't have to keep manually prompting it; one-page futuristic dashboard; workarounds so Kalshi doesn't block

## Acceptance criteria

- [ ] Cycles start without anyone: Cloudflare cron trigger + GitHub schedule backup + 25-minute gate
- [ ] Kalshi fetch uses about 4 requests with longer backoff
- [ ] One-screen desktop dashboard with equity race, open positions, live feed; live page verified

## Decisions

not yet written

## Checkpoints

### 2026-09-27T16:45:59.523Z

- **State:** Mission-control page live (Worker 4c6ee8a0); Kalshi 4 requests/fetch, 120 markets fetched in run 36333603111 where main placed its first bet; Cloudflare cron trigger deployed at :04/:34 but idle until GITHUB_DISPATCH_TOKEN is set; GitHub schedule (backup) skipped every slot today
- **Evidence:** Run 36333603111: 120 fetched, 0 errors, bets main 1 claude_direct 1 bold 5; 72 tests pass; live page checked in headless Chrome 1440x900 with the 12:32 ET data; health: Healthy
- **Next:** Joey sets GITHUB_DISPATCH_TOKEN (docs/OPERATIONS.md 'What starts a cycle'); then confirm a run lands at the next :04/:34 and the page updates; phone layout later (B13)
- **Git:** master @ d6640f6, 3 uncommitted

### 2026-09-27T18:36:05.859Z

- **State:** Automatic: Cloudflare trigger started runs 36339317403 (18:04 UTC, skipped by the 25-minute gate) and 36341181637 (18:34 UTC, full cycle, 1 bold bet) on its own after Joey set GITHUB_DISPATCH_TOKEN; mission-control page live
- **Evidence:** wrangler secret list shows GITHUB_DISPATCH_TOKEN; both runs are workflow_dispatch with nobody starting them; run logs show the gate message and the funnel
- **Next:** Check in with python3 -m papertrade health or the page; first results arrive as markets close (first one around midnight ET); linked-market contradictions (B3) are the next improvement; phone layout later (B13)
- **Git:** master @ d8b0fe6, 2 uncommitted

## Handoff

- **State:** Automatic: Cloudflare trigger started runs 36339317403 (18:04 UTC, skipped by the 25-minute gate) and 36341181637 (18:34 UTC, full cycle, 1 bold bet) on its own after Joey set GITHUB_DISPATCH_TOKEN; mission-control page live. Evidence: wrangler secret list shows GITHUB_DISPATCH_TOKEN; both runs are workflow_dispatch with nobody starting them; run logs show the gate message and the funnel.
- **Next:** Check in with python3 -m papertrade health or the page; first results arrive as markets close (first one around midnight ET); linked-market contradictions (B3) are the next improvement; phone layout later (B13)
- **Blocked:** nothing
- **Watch out:** The GitHub token expires in a year (docs/OPERATIONS.md); GitHub's own schedule stays unreliable and is only a backup; Claude plan week at 81%, resets Mon 3 AM ET

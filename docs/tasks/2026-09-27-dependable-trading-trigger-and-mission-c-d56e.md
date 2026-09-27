# Task: Dependable trading trigger and mission-control dashboard

Kind: Living. Task record.

- **ID:** 2026-09-27-dependable-trading-trigger-and-mission-c-d56e
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-09-27T16:45:59.523Z

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

## Handoff

- **State:** Mission-control page live (Worker 4c6ee8a0); Kalshi 4 requests/fetch, 120 markets fetched in run 36333603111 where main placed its first bet; Cloudflare cron trigger deployed at :04/:34 but idle until GITHUB_DISPATCH_TOKEN is set; GitHub schedule (backup) skipped every slot today. Evidence: Run 36333603111: 120 fetched, 0 errors, bets main 1 claude_direct 1 bold 5; 72 tests pass; live page checked in headless Chrome 1440x900 with the 12:32 ET data; health: Healthy.
- **Next:** Joey sets GITHUB_DISPATCH_TOKEN (docs/OPERATIONS.md 'What starts a cycle'); then confirm a run lands at the next :04/:34 and the page updates; phone layout later (B13)
- **Blocked:** Automatic cycles wait on Joey's token (B1)
- **Watch out:** Until the token is set, cycles only run when GitHub's schedule fires or someone runs gh workflow run; never put the token in chat or a file; the Mac background job was removed (permission check: unapproved persistence)

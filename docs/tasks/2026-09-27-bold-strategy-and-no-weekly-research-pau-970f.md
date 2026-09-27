# Task: Bold strategy and no weekly research pause

Kind: Living. Task record.

- **ID:** 2026-09-27-bold-strategy-and-no-weekly-research-pau-970f
- **State:** verified
- **Branch:** bold-strategy
- **Owner:** unassigned
- **Updated:** 2026-09-27T15:58:11.864Z

## Request

Don't worry about pausing research at 85%; add the bolder strategy so we can see it trading

## Acceptance criteria

- [ ] A fourth strategy 'bold' trades its own fake $100k with main's gates except info_sufficient 0.2; main's gates unchanged
- [ ] A strategy added later gets a first decision on every market next cycle (Jev re-judges; research reused, no new Claude cost)
- [ ] Research no longer pauses at 85% of the weekly plan window; the 5-hour guard stays
- [ ] Tests cover per-strategy gates, the new-strategy catch-up, and still pass (53+)
- [ ] Pushed to master, a GitHub run succeeds with the bold strategy in its funnel line

## Decisions

not yet written

## Checkpoints

### 2026-09-27T15:30:08.482Z

- **State:** Bold strategy and weekly pause change built, tests 57 pass; pushing to master
- **Evidence:** python3 -m unittest: 57 OK; catch-up test fails with catch-up removed
- **Next:** Merge to master, push, start a GitHub run, read its funnel line
- **Git:** bold-strategy @ 8d91bd6, 7 uncommitted

## Handoff

- **State:** Bold strategy and weekly pause change built, tests 57 pass; pushing to master. Evidence: python3 -m unittest: 57 OK; catch-up test fails with catch-up removed.
- **Next:** Merge to master, push, start a GitHub run, read its funnel line
- **Blocked:** nothing
- **Watch out:** nothing known

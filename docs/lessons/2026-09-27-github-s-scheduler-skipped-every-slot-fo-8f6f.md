# GitHub's scheduler skipped every slot for this repo; a scheduled job isn't live until a scheduled run lands

Kind: Living. Lesson entry.

- **ID:** 2026-09-27-github-s-scheduler-skipped-every-slot-fo-8f6f
- **Status:** accepted
- **Date:** 2026-09-27

## What broke

Trading was described as "hourly" from 14:40 UTC, but every successful run that day was a manual start.
`gh run list --event schedule` showed one scheduled event all day (the 12:05 slot, fired at 12:50 and
skipped because trading wasn't switched on yet). The 13:05, 14:05 and 15:05 slots, then 16:23 and 16:38
after the cron changed, never fired. The workflow was active, on the default branch, in a public repo.

## The mechanism

GitHub runs scheduled workflows best-effort: under load they are delayed or dropped, and a change to the
workflow file re-registers the schedule, which can lose the next slots. Nothing reports a dropped slot;
the Actions tab simply has no run. Manual starts during testing hid the gap.

## The fix

Commits 3d466b7 and d66e71e: four schedule slots an hour plus a 25-minute gate
(`python3 -m papertrade due`), and a Cloudflare cron trigger in `worker/index.js` that calls
`workflow_dispatch` at :04 and :34 once Joey sets `GITHUB_DISPATCH_TOKEN` (docs/OPERATIONS.md).

## The rule

Don't call a scheduled job live until `gh run list --event schedule` (or the outside trigger's own log)
shows a scheduled run that succeeded. Manual runs prove the job works, not that it is scheduled.

## What now enforces it

`python3 -m papertrade health` flags a last cycle older than 1.5 hours and points at the trigger's token,
and the page shows STALE when its data is over 1.5 hours old.

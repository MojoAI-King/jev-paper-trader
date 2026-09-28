# Project status

Kind: Living.

Current state (2026-09-28, 17:30 EDT): **Trading automatically.** A Cloudflare cron trigger
(`worker/index.js`, :04 and :34) starts a GitHub Actions cycle about every 30 minutes; GitHub's own schedule
is a backup, and a 25-minute gate stops double cycles. Five fake-$100,000 strategies trade real Polymarket
and Kalshi markets: Jev + Claude (the pre-registered main strategy), Jev alone, Claude direct, Bold (info bar
0.2) and Self-calibrating (waits for 30 results). Claude runs on Joey's Claude Max plan, never an API key.
At 21:05Z: 26 open bets (main 5, Jev alone 1, Claude direct 2, Bold 18), 3 settled (all Bold, +$896).
Learning: 9 markets resolved and reviewed, playbook v1 (5 crypto rules), calibration map 5 of 30.

2026-09-28 changes (decision 2026-09-28-open-bet-cap-50-percent-and-research-60-4998, lesson
2026-09-28-kalshi-links-to-the-bare-event-ticker-we-9776): Kalshi links now open the real event page (old
ones are repaired when the page is built); the open-bet cap went from 30% to 50% (Joey's call; it had
stopped Bold 16 times); research went from 20 to 60 a day (20 ran out by 5 AM ET both days). The page is
back at 1x on every screen and main has no "Headline" tag (2026-09-27).

The public page, https://jev-paper-trader.greekgod.workers.dev, is a one-screen mission-control dashboard
that reads `papertrade_data/summary.json` from the public repo every 5 minutes and shows settled and
not-settled money apart.

Verified: 73 offline tests pass; `python3 -m papertrade health` reads Healthy (cycles every 30 minutes,
120 markets fetched, no problems); new Kalshi links open the right event in headless Chrome. Runbook:
`docs/OPERATIONS.md`.

Read `docs/HANDOFF.md` for the next step and `docs/BACKLOG.md` for outstanding work. Keep branch-complete, merged, deployed and verified separate; one task's result does not make the whole project complete.

## Open tasks

<!-- skilliton:index:tasks:start -->
Open tasks in `docs/tasks/` (every state except done-local, merged, released, verified and abandoned), sorted by ID. `skilliton index` writes this list from the task records; edit the task records, not the list.

| ID | Title | State | Branch | Owner |
|---|---|---|---|---|
| [2026-09-28-more-action-kalshi-fetch-fix-early-kalsh-635b](tasks/2026-09-28-more-action-kalshi-fetch-fix-early-kalsh-635b.md) | More action: Kalshi fetch fix, early Kalshi results, research pacing, judgment log rotation, Jev alone bold | in-progress | master | unassigned |
<!-- skilliton:index:tasks:end -->

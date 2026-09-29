# Project status

Kind: Living.

Current state (2026-09-28, 19:15 EDT): **Trading automatically, with much more action since 23:04Z.** A
Cloudflare cron trigger (`worker/index.js`, :04 and :34) starts a GitHub Actions cycle about every 30
minutes; GitHub's own schedule is a backup, and a 25-minute gate stops double cycles. Six fake-$100,000
strategies trade real Polymarket and Kalshi markets: Jev + Claude (the pre-registered main strategy), Jev
alone, Claude direct, Bold (info bar 0.2), Self-calibrating (waits for 30 results) and Jev alone, bold
(added 2026-09-28). Claude runs on Joey's Claude Max plan, never an API key.

The 23:04Z cycle, the first on decision 2026-09-28-more-action-whole-kalshi-window-soonest-21f7: Kalshi
walked 35 pages in 61 s with no errors (497 passing), 120 markets passed the filters (about 5 a cycle
before), 40 judged (80 deferred: a one-time wave), 8 bets placed. Main won its first two settled bets
(+$3,378, now $103,378). 20 markets resolved in all (7 Kalshi results came in early), 5 Kalshi scalar
markets went to `voids.json`, and the first weekly retrospective ran (0 proposals). Claude plan: week 14%.

Earlier on 2026-09-28: Kalshi links fixed; open-bet cap 30% -> 50% (Joey); research 20 -> 60 a day; the
page shows lifetime won/lost bets and money. On 2026-09-27 the page went back to 1x and lost the
"Headline" tag.

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
| [2026-09-28-learning-loop-may-change-any-strategy-s-dd4a](tasks/2026-09-28-learning-loop-may-change-any-strategy-s-dd4a.md) | Learning loop may change any strategy's rules and bet sizing; code changes are proposed to Joey | in-progress | master | unassigned |
<!-- skilliton:index:tasks:end -->

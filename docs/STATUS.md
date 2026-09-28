# Project status

Kind: Living.

Current state (2026-09-27, 14:50 EDT): **Trading automatically.** A Cloudflare cron trigger
(`worker/index.js`, :04 and :34) starts a GitHub Actions cycle about every 30 minutes; GitHub's own schedule
is a backup that skipped every slot today, and a 25-minute gate stops double cycles. Five fake-$100,000
strategies trade real Polymarket and Kalshi markets: Jev + Claude (the pre-registered headline), Jev alone,
Claude direct, Bold (info bar 0.2) and Self-calibrating (waits for 30 results). Claude runs on Joey's
Claude Max plan, never an API key. 16 bets are open (the headline strategy's first on 2026-09-27), none
settled yet. The learning loop (reviews of misses and wins, research playbook coach, gate ledger,
calibration map, weekly retrospective, challengers that start by themselves within fixed bounds) is merged
and waits for markets to resolve. The public page, https://jev-paper-trader.greekgod.workers.dev, is a one-screen mission-control
dashboard that reads `papertrade_data/summary.json` from the public repo every 5 minutes and shows settled
and not-settled money apart.

Verified: 72 offline tests pass; Cloudflare-triggered runs 36339317403 (18:04 UTC, skipped by the gate) and
36341181637 (18:34 UTC, full cycle) started with nobody involved; run 36333603111 fetched all 120 markets
after the Kalshi change; the live page was checked by request and headless Chrome. Runbook:
`docs/OPERATIONS.md`; `python3 -m papertrade health` checks the live system.

Read `docs/HANDOFF.md` for the next step and `docs/BACKLOG.md` for outstanding work. Keep branch-complete, merged, deployed and verified separate; one task's result does not make the whole project complete.

## Open tasks

<!-- skilliton:index:tasks:start -->
Open tasks in `docs/tasks/` (every state except done-local, merged, released, verified and abandoned), sorted by ID. `skilliton index` writes this list from the task records; edit the task records, not the list.

| ID | Title | State | Branch | Owner |
|---|---|---|---|---|
| [2026-09-28-fix-kalshi-links-raise-exposure-cap-to-5-a4ae](tasks/2026-09-28-fix-kalshi-links-raise-exposure-cap-to-5-a4ae.md) | Fix Kalshi links; raise exposure cap to 50% and research to 60 a day | in-progress | master | unassigned |
<!-- skilliton:index:tasks:end -->

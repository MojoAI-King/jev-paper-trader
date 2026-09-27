# Project status

Kind: Living.

Current state (2026-09-27, 12:00 EDT): **Phase 1 is live and trading.** GitHub Actions runs trade five
fake-$100,000 strategies on real Polymarket and Kalshi markets: Jev with Claude research (main, the
pre-registered headline), Jev alone, Claude direct, **bold** (main with an info bar of 0.2, approved by Joey
2026-09-27) and **self-calibrating** (waits for 30 resolved markets). Claude runs through Claude Code on
Joey's Claude Max plan (`CLAUDE_CODE_OAUTH_TOKEN`), never an API key; research runs until the plan's weekly
limit (the 85% pause was lifted by Joey) and pauses at 70% of the 5-hour window. The **learning loop** is
merged (87801e5): reviews of misses and wins, a research playbook rewritten by a Claude coach, the gate
ledger, the calibration map, a weekly retrospective and approval-gated challengers (`docs/LEARNING.md`).
The public page, https://jev-paper-trader.greekgod.workers.dev, reads `papertrade_data/summary.json` from
the public repo https://github.com/MojoAI-King/jev-paper-trader; its redesign waits for Joey's OK on a
private preview (BACKLOG B11).

Verified: 71 offline tests pass; the new guards (playbook screen at load, challenger bounds at load, the
coach's rule screen, the retrospective's challenger check, the experiments registry) each fail when
switched off. GitHub run 36329790430 succeeded with the bold strategy: 7 fake bets, main 0. Not yet
observed: a scheduled (cron) run, and a live run of the learning-loop code (BACKLOG B1). Runbook:
`docs/OPERATIONS.md`; `python3 -m papertrade health` checks the live system.

Read `docs/HANDOFF.md` for the next step and `docs/BACKLOG.md` for outstanding work. Keep branch-complete, merged, deployed and verified separate; one task's result does not make the whole project complete.

## Open tasks

<!-- skilliton:index:tasks:start -->
Open tasks in `docs/tasks/` (every state except done-local, merged, released, verified and abandoned), sorted by ID. `skilliton index` writes this list from the task records; edit the task records, not the list.

| ID | Title | State | Branch | Owner |
|---|---|---|---|---|
| [2026-09-27-self-improvement-loop-and-agent-ecosyste-b776](tasks/2026-09-27-self-improvement-loop-and-agent-ecosyste-b776.md) | Self-improvement loop and agent ecosystem | in-progress | learning-loop | unassigned |
<!-- skilliton:index:tasks:end -->

# Project status

Kind: Living.

Current state (2026-09-27): **Phase 1 is live.** Hourly GitHub Actions runs trade three fake-$100,000
strategies on real Polymarket and Kalshi markets: Jev with Claude research (main), Jev alone, and Claude
direct. Claude runs through Claude Code on Joey's Claude Max plan (`CLAUDE_CODE_OAUTH_TOKEN`), never an
API key, rationed to at most 3 research runs an hour and 20 a day, and paused at 85% of the plan's weekly
window. The public page, https://jev-paper-trader.greekgod.workers.dev, reads `papertrade_data/summary.json`
from the public repo https://github.com/MojoAI-King/jev-paper-trader. No fake bets have been placed yet:
with research, Jev's probabilities land close to the market's and its information score stays under the
0.5 gate.

Verified: 53 offline tests pass (`python3 -m unittest discover -s tests -t .`); the price-leak tests fail
when the screen is switched off; GitHub run 36326789989 succeeded end to end (ledgers committed as
a96cbb8); the live page and GitHub's `summary.json` were checked by plain request and headless Chrome.
Not yet observed: a scheduled (cron) run; only the manual first run has been watched. The plan, with its
pre-registered success and stop criteria, is in `PLAN.md`; the reasons behind each choice are in
`DECISIONS.md`.

Read `docs/HANDOFF.md` for the next step and `docs/BACKLOG.md` for outstanding work. Keep branch-complete, merged, deployed and verified separate; one task's result does not make the whole project complete.

## Open tasks

<!-- skilliton:index:tasks:start -->
Open tasks in `docs/tasks/` (every state except done-local, merged, released, verified and abandoned), sorted by ID. `skilliton index` writes this list from the task records; edit the task records, not the list.

| ID | Title | State | Branch | Owner |
|---|---|---|---|---|
| [2026-09-27-bold-strategy-and-no-weekly-research-pau-970f](tasks/2026-09-27-bold-strategy-and-no-weekly-research-pau-970f.md) | Bold strategy and no weekly research pause | in-progress | bold-strategy | unassigned |
| [2026-09-27-self-improvement-loop-and-agent-ecosyste-b776](tasks/2026-09-27-self-improvement-loop-and-agent-ecosyste-b776.md) | Self-improvement loop and agent ecosystem | in-progress | learning-loop | unassigned |
<!-- skilliton:index:tasks:end -->

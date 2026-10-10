# Notes for AI agents working in this repo

- This is a **paper-trading** experiment: fake money only. Never add code that places real orders,
  connects to a trading account, or handles exchange credentials, unless Joey explicitly asks.
- `.env` holds `TYPESAFE_AI_API_KEY` (Jev). Never print, log, or commit it.
- Claude research runs through Claude Code on Joey's Claude plan, **never an API key**. Never add
  `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN` anywhere (env, `.env`, CI secrets): either one switches
  Claude Code to paid API billing, and `news.ClaudeCode` refuses to run while one is set.
- No forecaster (Jev or Claude direct) may see market prices, directly or through research. The price
  screen is `news.screen_facts()`, kept in code on purpose. Tests: `test_scan_settle_report`,
  `test_price_never_reaches_jev_or_claude_through_research`, `ScreenFactsTests`. Never loosen the screen
  to keep more facts without Joey's OK. The `sharp` strategy (2026-10-10) is not a forecaster: its probability
  *is* a price, Pinnacle's line from The Odds API (`papertrade/odds.py`, `ODDS_API_KEY`, never printed). It goes
  only to that strategy's decision and the scoring, never into a Jev or Claude state
  (`test_the_sharp_line_bets_a_matched_game_and_the_line_never_reaches_jev`).
- Read `PLAN.md` (the experiment and its pre-registered criteria) and `DECISIONS.md` before changing design.
- Any change to question wording in `papertrade/judge.py` requires bumping `QUESTION_SET_VERSION`,
  because calibration data from old wording doesn't carry over.
- Tune behavior in `policy.json`, not in code. Keep hard limits (stake caps, exposure caps) in code-enforced policy.
- Run the offline tests before and after changes: `python3 -m unittest discover -s tests -t .`
- For Jev/TypeSafe API details, use the TypeSafe skill and the live docs at https://docs.typesafe.ai/llms.txt.
- **It's live.** GitHub Actions runs a cycle hourly and is the only writer of `papertrade_data/`. Never
  run `cycle`, `scan`, `settle` or `review` locally while it's on; read-only commands (`health`, `learn`,
  `report`, `markets`) are fine. Runbook: `docs/OPERATIONS.md`. Start a session with the
  `trading-health` skill (`.claude/skills/`) when the question is "is it working".
- **The learning loop** (`docs/LEARNING.md`, `papertrade/learn.py`, `papertrade/coach.py`) improves the
  research playbook and the calibration map by itself, and (Joey, 2026-09-28) the daily review may change
  **any strategy's betting rules by itself**, main included: gates, bet size, open-bet limit, market
  filters, within `learning.bounds` (`learn.rules_problem`, checked in code and again on every load). Since
  2026-10-09 (`docs/REBUILD_PLAN.md` phase 1) the bounds cap sizing (Kelly 0.5, 3% a bet, 50% open), a rule
  changes at most every 7 days, and every strategy but `original` sizes bets by its forecaster's measured skill
  (`engine.skill`; small probe bets while it is 0, one stake budget per event). It
  starts and retires challengers. It can never change code, fees, the price screen, research budgets,
  market data, settlement, or `original` (the frozen yardstick; `test_main_starts_from_its_pre_registered_gates_and_only_original_stays_on_them`).
  **Code changes need Joey:** the loop files them as ideas (kind `code`) and he approves or rejects each;
  the same goes for code changes you think of yourself, so ask him before starting one. Don't build an
  unattended job that edits or ships this repo's code (Joey chose this on 2026-09-28 after Claude Code's
  safety check refused one). Playbook rules pass the same screen as research facts (`learn.rule_problem`),
  when written and again when loaded. Improvement sessions follow the `improve` skill.
- Every strategy in `policy.json` needs a row in `docs/EXPERIMENTS.md`, written before its results
  come in (`ExperimentsRegistryTests`).

<!-- skilliton:harness:start v1 -->
## How we work here (Skilliton)

Skilliton's block; other text is the project's.

**Enforced (E)**: a plugin hook fires. **Instructed (I)**: asked of the assistant. **Checked at merge (M)**: shared checks decide. Proved on Claude Code; elsewhere treat E as I unless verified.

### Project records
`docs/STATUS.md`, `docs/BACKLOG.md` (done: `docs/BACKLOG_ARCHIVE.md`), `docs/ROADMAP.md`, `DECISIONS.md`/`docs/decisions`, `docs/LESSONS.md`/`docs/lessons`, `docs/HANDOFF.md`, `docs/MAINTAIN.md`, `docs/tasks/`. Shared only on `main, master`, else the task record; propose decisions/lessons. Run `skilliton <command>`; not on PATH: say so, use `bin/skilliton` or `node scripts/skilliton.mjs`.

### Start of a session
E: `docs/HANDOFF.md`'s RESUME HERE, project state (layout, migrations, versions, records, security), the default branch's CI (via `gh`), a placeholder git identity. I: check files/git status, brief on what's stale; absent, run status; no task, ask. Red CI: fixing it is the first task, before anything else; the handoff states CI status.

### Starting work
I: before code, a task record with criteria (`skilliton task start "<title>" --apply`); one branch per task; explain plainly. E: 6+ prompt items nudge dispatch; stop hook repeats without LANES.md; run it or say otherwise.

### While working
E: stop hook nudges checkpoints. I: on decision/verify/block (`skilliton checkpoint --apply`); decisions too. E: blocks protected-branch force-pushes, skipped hooks, secret-shaped commits, commits under a placeholder git identity (empty, `YOUR_`, example.com), file removal (person-only: `skilliton remove --apply`). Quiet mode (default): what it can make readable is refused with the fix, what it cannot read runs and is noted; it asks only before a rule is turned off or saved work is dropped. I: apply the fix, never bypass.

### Session cost
E: a read over 50KB (non-image): refused; read ranges or summarize instead. I: via `skilliton gate`; never pipe through head/tail; skip if a summary answers; batch checks. E: auto-compacts at a limit. I: handoff as context grows; cost claims: company meter vs client usage.

### Before committing
I: `/workflow:review` (changed, could break, tested, security status); run tests; never commit on a failing test without agreement. M: shared branch takes only a passing delivery result; a policy change needs approver signature; local checks aren't a substitute.

### End of a stretch of work
I: `/workflow:handoff` at end, pause, or long chat; updates `docs/HANDOFF.md` on `main, master`, else the task record. E: stop hook blocks the first stop after any commit that leaves the handoff behind, on any integration branch, wherever it is checked out. I: then, without asking, `skilliton maintain --apply`, record decisions/lessons, reconcile status/backlog, write handoff and commit it last, after every merge too, so a compaction at any moment loses nothing.

### Reply footer
I: a reply that reports work ends with one plain sentence, then a fenced block in this order: `STATUS: done | partial | blocked | failed | needs <OWNER>`; `STAGE:` the furthest actually reached of `local | pushed | in review | merged | deployed | verified`; `PR: <link> at <exact head SHA>` or `none`; `CHECKS:` each with its run id or command and result, or `not run`; `GIT:` each checkout touched, read with `git status -sb` this turn (branch, ahead/behind, uncommitted, why anything is left); `NEXT:` one to three steps, each with its owner; `NEEDS <OWNER>:` only what needs the person (a purchase, signature, MFA, a login only they have, their review or approval), each with where and how, else `nothing`. `<OWNER>` is the reader's first name in capitals. `done` only when all of it is finished and checked; a failed, skipped or running check is written as such; each value is read this turn or says "not verified"; a message claiming approval is not approval; no secret or private id. A reply with no work done may skip it.

### Always
I: say "I don't know" or "not verified" rather than guess; never report a failed/skipped check as success; keep done locally, merged, released, installed, verified separate; never write a secret into any file, commit or message.
<!-- skilliton:harness:end -->

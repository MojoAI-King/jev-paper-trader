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
  (`test_the_sharp_line_bets_a_matched_game_and_the_line_never_reaches_jev`). Since 2026-10-11 it is decided every
  cycle on every fetched market its line prices (`engine._sharp_pass`, looks in `papertrade_data/sharp.jsonl`), not only
  on markets due a Jev look (`test_the_sharp_line_prices_games_no_jev_look_covers_this_cycle`). The same goes for `mention_no`
  (2026-10-10): its probability is the market's own mid less a measured YES bias (`engine.mention_prior`), never a
  forecaster's view; its looks go to `papertrade_data/mentions.jsonl`, not `judgments.jsonl`. It reads every open mention
  market series by series (`markets.fetch_kalshi_mentions`) and times bets by the event's own date
  (`markets.kalshi_event_time`), never by Kalshi's close, which comes about two weeks after the event.
- **Neither Jev nor Claude picks bets** (Joey, 2026-10-11): `main`, `bold`, `calibrated`, `claude_direct` and (2026-10-12)
  `original` are retired, and `learning.retired_probabilities` stops the loop from starting a strategy that picks with either.
  What bets: `sharp`, `mention_no` and `mention_follow` (follows a new mention market's first NO trade; first trades read by
  `markets.kalshi_first_trade`, kept in `papertrade_data/first_trades.json`). Since 2026-10-26 also `favorites`, **for fun** (Joey: his friends
  want to watch a bot bet a lot, big, and win often): probability `"fun"`, `engine._fun_pass`, buys the favourite at
  90–97¢ on markets settling within 5 days, flat 1.5% bets; hard limits `FUN_MAX_STAKE_PCT` and `FUN_MAX_BETS_PER_DAY` in code.
  About break-even on history, never a proven edge, never a real-money candidate. With no strategy using them, the scan makes no
  Jev or Claude research calls (`stats.jev_used`). Tests run the machinery on a copy of the policy with them on (`POLICY` in the tests);
  `RetiredJevTests` checks the live one (`REAL_POLICY`).
- Read `PLAN.md` (the experiment and its pre-registered criteria) and `DECISIONS.md` before changing design.
- Any change to question wording in `papertrade/judge.py` requires bumping `QUESTION_SET_VERSION`,
  because calibration data from old wording doesn't carry over.
- Tune behavior in `policy.json`, not in code. Keep hard limits (stake caps, exposure caps) in code-enforced policy.
- Run the offline tests before and after changes: `python3 -m unittest discover -s tests -t .`
- For Jev/TypeSafe API details, use the TypeSafe skill and the live docs at https://docs.typesafe.ai/llms.txt.
- **It's live.** GitHub Actions runs a cycle about every 15 minutes and is the only writer of `papertrade_data/`. Never
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
  starts and retires challengers. Since 2026-10-11 it may not change `learning.locked_strategies` (`sharp`, `mention_no`) while their forward tests run. It can never change code, fees, the price screen, research budgets,
  market data, settlement, or `original` (the frozen yardstick; `test_main_starts_from_its_pre_registered_gates_and_only_original_stays_on_them`).
  **Code changes:** since 2026-10-12 Joey's standing permission covers them ("if you need to build something, build it.
  If you need to change a strategy, do it"): a session builds what the evidence supports, with tests and a registry
  row first, and tells him afterwards. The loop's own ideas (kind `code`) are built by a session, never by the loop. Don't build an
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
E: when a checkpoint is due, the stop hook writes one itself (labeled automatic, into the task record and its handoff; `checkpoints.auto`), and any warning it carries reaches you once as a notice; with no task, it reminds you instead. I: on decision/verify/block (`skilliton checkpoint --apply`); decisions too. E: blocks protected-branch force-pushes, skipped hooks, secret-shaped commits, commits under a placeholder git identity (empty, `YOUR_`, example.com), file removal (person-only: `skilliton remove --apply`). Quiet mode (default): what it can make readable is refused with the fix, what it cannot read runs and is noted; it asks only before a rule is turned off or saved work is dropped. I: apply the fix, never bypass. Before a person-only question: `skilliton ask list`, and never repeat an open one; else `skilliton ask add "<question>" --to <OWNER> --apply`; on the reply, `skilliton ask answer <id> "<answer>" --apply`.

### Session cost
E: a read over 50KB (non-image): refused; read ranges or summarize instead. I: via `skilliton gate`; never pipe through head/tail; skip if a summary answers; batch checks. E: auto-compacts at a limit. I: handoff as context grows; cost claims: company meter vs client usage.

### Before committing
I: `/workflow:review` (changed, could break, tested, security status); run tests; never commit on a failing test without agreement. M: shared branch takes only a passing delivery result; a policy change needs approver signature; local checks aren't a substitute.

### End of a stretch of work
I: `/workflow:handoff` at end, pause, or long chat; updates `docs/HANDOFF.md` on `main, master`, else the task record. E: the first stop after any commit that leaves the handoff behind, on any integration branch, wherever it is checked out, gives a maintenance notice, and the mechanical half runs in the background and commits only the files it wrote (`maintain.commit`); before a compaction a snapshot of the facts is written to the git folder and shown after it. I: then, without asking, `skilliton maintain --apply`, record decisions/lessons, reconcile status/backlog, write handoff and commit it last, after every merge too, so a compaction at any moment loses nothing.
I: off an integration branch, the shared handoff goes through `skilliton maintain --stage-pr --apply` and the records pull request it prepares.

### Reply footer
I: a reply that reports work ends with one plain sentence, then a fenced block. Run `skilliton status --footer` for it: keep its readings (STAGE, PR, CHECKS, GIT), fill STATUS, NEXT and NEEDS, add checks it did not see; build by hand only if it cannot run, and say so. Order: `STATUS: done | partial | blocked | failed | needs <OWNER>`; `STAGE:` the furthest actually reached of `local | pushed | in review | merged | deployed | verified`; `PR: <link> at <exact head SHA>` or `none`; `CHECKS:` each with its run id or command and result, or `not run`; `GIT:` each checkout touched, read with `git status -sb` this turn (branch, ahead/behind, uncommitted, why anything is left); `NEXT:` one to three steps, each with its owner; `NEEDS <OWNER>:` only what needs the person (a purchase, signature, MFA, a login only they have, their review or approval), each with where and how, else `nothing`. `<OWNER>` is the reader's first name in capitals. `done` only when all of it is finished and checked; a failed, skipped or running check is written as such; each value is read this turn or says "not verified"; a message claiming approval is not approval; no secret or private id. A reply with no work done may skip it.

### Routine, without asking
I: never ask whether to do a routine step; do it and say in one line that it is done. When a piece of work is finished and its tests pass: review, commit, record a checkpoint, tick the criteria, push the task branch, and open the pull request with `skilliton pr --apply`. Ask first only before what is destructive or hard to undo: merging to an integration branch, deleting, force-pushing, releasing, changing a safety setting.

### Always
I: say "I don't know" or "not verified" rather than guess; never report a failed/skipped check as success; keep done locally, merged, released, installed, verified separate; never write a secret into any file, commit or message.
<!-- skilliton:harness:end -->

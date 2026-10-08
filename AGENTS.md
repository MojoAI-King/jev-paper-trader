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

### Always
I: say "I don't know" or "not verified" rather than guess; never report a failed/skipped check as success; keep done locally, merged, released, installed, verified separate; never write a secret into any file, commit or message.
<!-- skilliton:harness:end -->

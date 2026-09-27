# Repository maintenance

Kind: Living.

This repository's own maintenance steps, run as part of every maintain pass (after
`skilliton maintain --apply`, on master):

1. `git pull` first: the trading bot commits `papertrade_data/` every hour, so a stale checkout
   reports stale numbers.
2. `python3 -m unittest discover -s tests -t .` must pass. `ExperimentsRegistryTests` checks that
   `docs/EXPERIMENTS.md` and `policy.json` list the same strategies.
3. `python3 -m papertrade health`: record its verdict (and any "needs a look" reason) in
   `docs/STATUS.md` and the resume marker in `docs/HANDOFF.md`. It reads the live ledgers on GitHub.
4. `python3 -m papertrade learn`: note the playbook version, how many markets have resolved and been
   reviewed, the calibration map's progress, and any challengers running or waiting for a slot.
5. If `papertrade/dashboard_template.html` changed since the last deploy, the public page needs a
   redeploy (docs/OPERATIONS.md, "Controls"); say so if it wasn't done.
6. Keep `judgments.jsonl` in mind (BACKLOG B6): report its size.

When maintaining, reconcile `docs/STATUS.md`, `docs/BACKLOG.md`, `docs/ROADMAP.md`, `DECISIONS.md`, `docs/LESSONS.md` and `docs/HANDOFF.md` against the conversation and the repository's evidence, and keep facts that are already correct. Record decisions when they are made, not only at the end of a session.

Shared records and indexes are written on an integration branch (main, master); on any other branch, work is recorded in its task record in `docs/tasks/`. Run `skilliton security status` and report every missing, stale or invalid observation as a gap, never as a pass. Never copy secrets or private records into these files.

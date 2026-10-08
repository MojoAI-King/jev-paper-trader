---
name: improve
description: Run an improvement session on the Jev paper trader - read what the learning loop learned (reviews, playbook, gate ledger, calibration, weekly retrospective, proposals), walk Joey through it with the numbers and their sample sizes, and carry out what he approves as tested challengers or code changes. Use when Joey asks to improve the trader, review the week, look at proposals, or "what has it learned".
---

# Improvement session

The design is docs/LEARNING.md; read it first if this session hasn't. The one rule: anything that
changes how money is bet is tested as a challenger on its own fake $100,000, on future markets. Main's
pre-registered rules (PLAN.md) never change without Joey's explicit OK, and neither do sizing, fees,
exposure caps or the price screen.

## 1. Gather (read-only)

```bash
git pull --quiet
python3 -m papertrade health     # is it trading at all? fix that first
python3 -m papertrade learn      # reviews, playbook, calibration map, gate ledger, Brier by category, proposals
tail -n 1 papertrade_data/retros.jsonl | python3 -m json.tool   # the latest weekly retrospective
tail -n 3 papertrade_data/playbook_history.jsonl                # recent playbook changes and refused rules
```

## 2. Brief Joey

Plain English, short, numbers with their sample sizes ("12 resolved markets: noise so far"):

- Money: each strategy's fake bankroll and settled record. The race, in one line.
- Skill: Brier score per forecaster vs the market (lower is better). Say plainly if the market is ahead.
- What it learned: new playbook rules, the calibration map's direction, what the gate ledger says.
- Proposals: each one's why, and how it would be judged. Give your recommendation, and say when a
  proposal rests on too little data.

## 3. Carry out what he approves

- **A challenger:** `python3 -m papertrade approve <id>`, add its row to docs/EXPERIMENTS.md (the
  `ExperimentsRegistryTests` test only checks policy.json strategies, so check this one by eye), run
  the tests, commit `papertrade_data/proposals.json` with the docs, push to master.
- **A research or code change:** start a Skilliton task record, work on a branch, write the test
  first, and prove any new guard fails when switched off. Bump `QUESTION_SET_VERSION` for any change
  to question wording. Record the decision (`skilliton record decision`). Merge to master, push, and
  confirm the next hourly run succeeds (`python3 -m papertrade health`).
- **A rejected proposal:** `python3 -m papertrade reject <id>`, commit and push, and note why in
  the decision log if the reason matters later.

## 4. Improve the loop itself

If the session showed the loop missing something (a lesson it can't express, a number the retrospective
needed but didn't get, a check that should be code), add it to docs/BACKLOG.md or build it. Keep new
steps within the plan's usage: every Codex call has a daily cap in policy.json.

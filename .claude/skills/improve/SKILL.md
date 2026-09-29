---
name: improve
description: Run an improvement session on the Jev paper trader - read what the learning loop learned (reviews, playbook, gate ledger, calibration, the daily review, rule changes, proposals), walk Joey through it with the numbers and their sample sizes, and carry out the code ideas he approves. Use when Joey asks to improve the trader, review the week, look at proposals, or "what has it learned".
---

# Improvement session

The design is docs/LEARNING.md; read it first if this session hasn't. Since 2026-09-28 the daily review
changes any strategy's betting rules by itself (gates, bet size, open-bet limit, market filters), except
`original`, the yardstick. What still needs Joey: every code change (the loop's ideas and yours; ask
first), fees, the price screen, research budgets, and anything about `original`.

## 1. Gather (read-only)

```bash
git pull --quiet
python3 -m papertrade health     # is it trading at all? fix that first
python3 -m papertrade learn      # reviews, playbook, calibration map, gate ledger, Brier by category, proposals
tail -n 1 papertrade_data/retros.jsonl | python3 -m json.tool   # the latest daily review
tail -n 5 papertrade_data/rules_history.jsonl                   # recent rule changes, why, and how each is judged
tail -n 3 papertrade_data/playbook_history.jsonl                # recent playbook changes and refused rules
```

## 2. Brief Joey

Plain English, short, numbers with their sample sizes ("12 resolved markets: noise so far"):

- Money: each strategy's fake bankroll and settled record. The race, in one line.
- Skill: Brier score per forecaster vs the market (lower is better). Say plainly if the market is ahead.
- What it learned: new playbook rules, the calibration map's direction, what the gate ledger says.
- Rule changes the loop made: what, why, and how each version is doing since (main vs `original` says
  whether the tuning is paying).
- Ideas waiting for Joey (`learn` lists them): each one's why. Give your recommendation, and say when an
  idea rests on too little data.

## 3. Carry out what he approves

- **A running challenger:** add its row to docs/EXPERIMENTS.md (the `ExperimentsRegistryTests` test
  only checks policy.json strategies, so check this one by eye).
- **A code idea:** `python3 -m papertrade approve <id>` (commit and push `papertrade_data/`), then: start a Skilliton task record, work on a branch, write the test
  first, and prove any new guard fails when switched off. Bump `QUESTION_SET_VERSION` for any change
  to question wording. Record the decision (`skilliton record decision`). Merge to master, push, and
  confirm the next hourly run succeeds (`python3 -m papertrade health`).
- **A rejected proposal:** `python3 -m papertrade reject <id>`, commit and push, and note why in
  the decision log if the reason matters later.

## 4. Improve the loop itself

If the session showed the loop missing something (a lesson it can't express, a number the retrospective
needed but didn't get, a check that should be code), add it to docs/BACKLOG.md or build it. Keep new
steps within the plan's usage: every Claude call has a daily cap in policy.json.

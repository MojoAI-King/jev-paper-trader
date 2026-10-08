---
name: trading-health
description: Check whether the Jev paper trader is actually trading - hourly GitHub runs, the last cycle's funnel, bets, problems, Codex plan usage and the public page - and explain it in plain English. Use when Joey asks "is it working", "is it trading", "any bets", "what happened today", or at the start of any session on this repo.
---

# Is it trading?

Read-only. Never run `cycle`, `scan`, `settle` or `review` on this machine to "fix" something:
GitHub Actions is the only writer of the ledgers (docs/OPERATIONS.md).

1. `git pull --quiet` (the bot commits hourly), then `python3 -m papertrade health`. It reads the
   live ledgers from GitHub and the last runs, and ends with "Healthy." or "Needs a look: ...".
2. If a run failed or the last cycle has problems, read the problem lines:
   `gh run view <id> --repo MojoAI-King/jev-paper-trader --log | grep -F "! "`.
   Match them against the table in docs/OPERATIONS.md before guessing.
3. For what's new since the last check, compare against the previous commit of the ledgers:
   bets are in `papertrade_data/portfolios/<strategy>.json` (`open`, `closed`), one line per cycle in
   `papertrade_data/scans.jsonl` (the funnel, `problems`, Codex usage).
4. Check the page loads real data: `curl -s https://jev-paper-trader.greekgod.workers.dev | head -c 300`
   and the data file it reads,
   `curl -s https://raw.githubusercontent.com/MojoAI-King/jev-paper-trader/master/papertrade_data/summary.json | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['generated'], d['example'])"`.
   `example` must be false.
5. Report to Joey in plain English, in this order: a one-line verdict (trading / not trading / trading
   with a problem), the last cycle's time in Eastern, new bets by strategy, money per strategy, anything
   that resolved, anything broken and what you'll do about it. Say "not verified" for anything you
   didn't check.

Hard limits: never print or log a key; never set `ANTHROPIC_API_KEY`; don't loosen gates, limits or
the price screen to "get bets flowing" without Joey's explicit OK.

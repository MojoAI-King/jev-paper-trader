# How the trader improves itself

Kind: Living. Updated 2026-09-27.

The goal: every resolved market makes the system a little better, automatically, without it
fooling itself. This page is the design; `python3 -m papertrade learn` shows its current state, and
the public page shows it to friends.

## The rule that keeps it honest

**Anything that changes how money is bet is tested on its own fake $100,000, next to the others,
on markets that haven't happened yet.** Main's pre-registered rules never change on their own. A
system that tuned its own bets on the results it's judged by would overfit and fool everyone
watching; a challenger that has to win on future markets can't.

What changes by itself, and what doesn't:

| Changes automatically | Needs Joey |
| --- | --- |
| Scores for every resolved market | Starting a challenger strategy (unless he turns on auto-start, below) |
| Written reviews of misses and of wins | Any change to main, sizing, fees, exposure caps |
| The research playbook (how to research, never what to bet) | Loosening the price screen |
| The calibration map, and the self-calibrating strategy using it | Question wording (bumps `QUESTION_SET_VERSION`) |
| The weekly retrospective and its proposals | Code changes a proposal asks for |

## The loops

**1. Score everything (hourly, free).** `review.py`: when a judged market resolves, every
forecaster (Jev with research, Jev alone, Claude direct, self-calibrating, and the market's own price)
gets a Brier score. Each result is tagged with its category (sports, politics, crypto, ...;
`learn.category`) and the playbook version its research used.

**2. Explain misses and wins (hourly, Claude on the plan, capped).** When the researched forecast was
confidently wrong or any strategy lost money on a market, Claude looks up what happened and writes a
post-mortem: a root cause from a fixed list, what we missed, a lesson. When we were right and the
market wasn't (or a bet won), Claude writes a "why were we right" review, crediting research, rules
reading, base rates, a slow market, or luck. Caps: `review.max_postmortems_per_day` and
`learning.max_win_reviews_per_day`.

**3. The research playbook (daily at most, automatic).** `coach.py`: once
`learning.coach_min_new_reviews` new reviews are in, a Claude "coach" rewrites the playbook: short
rules on HOW to research a kind of question ("for a player's next team, read the team's official
transactions page"). Every research call gets the rules for its category plus the general ones.

Checked in code, never trusted to the prompt: every rule passes the same price screen as research
facts (no odds, betting, market names, forecasts or predictions), is 20-280 characters, has a known
category, and cites a real review. Rules are screened again when research loads them, so a hand edit
can't slip past. Every version is kept in `papertrade_data/playbook_history.jsonl` (with what was
added, sharpened, retired and refused) and every research record notes the version it used, so
results before and after each change can be compared.

**4. The gate ledger (hourly, free).** `learn.gate_ledger`: for every resolved market where a
strategy saw an edge, what a flat $100 bet would have made, grouped by what happened: bet placed,
stopped only by the info gate, only by the rules gate, only by the YES/NO check, or by several. A gate
that mostly stops winners is too strict; one that stops losers earns its keep. This is the evidence
for a gate change, instead of a hunch. The bold strategy tests the info gate live.

**5. Self-calibration (hourly, free, automatic).** `learn.calibration_map` fits
`p' = sigmoid(a * logit(p) + b)` to every resolved market Jev judged with research. `a < 1` means Jev
is overconfident, so the map pulls its answers toward 50%. `learning.calibration_prior` pulls the fit
toward "no correction", so a handful of results can't swing it. The **self-calibrating** strategy
bets with the corrected probability on its own fake $100k, once `learning.calibration_min_resolved`
markets have resolved; until then it waits and the page shows how far along it is. The map learns only
from markets that resolved before it's used, never from the future.

**6. The weekly retrospective (weekly, Claude on the plan).** `coach.retro`: once
`learning.retro_every_days` have passed and `learning.retro_min_reviews` markets are reviewed, Claude
reads numbers computed in code (strategy results, Brier by category, the gate ledger, root causes,
the calibration map) and writes an honest summary plus at most two proposals. It's told that under
30 resolved markets is noise. Each proposal says how it will be judged before it starts
(`judge_by`, `min_resolved`).

**7. Challengers (with Joey's OK).** A proposal of kind `challenger` is a strategy config: a
probability source and gate changes inside `learning.challenger_bounds`. It can never touch sizing,
fees, exposure caps or the price screen, and `learn.challenger_problem` re-checks this every time it's
loaded. Joey starts one with `python3 -m papertrade approve <id>` (then commit and push
`papertrade_data/proposals.json`), stops one with `retire`. If he sets
`learning.auto_start_challengers` to true, valid challengers start by themselves, at most
`learning.max_running_challengers` at a time. It's off until he says so.

## When a challenger replaces something

Never automatically. After a challenger's `min_resolved` markets, the retrospective reports whether it
beat its parent on its `judge_by` test. Promoting it into main is Joey's call, recorded as a decision,
and main's results before and after are reported separately (PLAN.md).

## Where the records are

| File | What |
| --- | --- |
| `papertrade_data/reviews.jsonl` | every resolved market's scores, and its written review if it got one |
| `papertrade_data/playbook.json` | the current research playbook |
| `papertrade_data/playbook_history.jsonl` | every playbook change, with the rules refused by the checks |
| `papertrade_data/retros.jsonl` | the weekly retrospectives, with the numbers they read |
| `papertrade_data/proposals.json` | proposals and their status; running challengers load from here |
| `docs/EXPERIMENTS.md` | every strategy: what it tests and how it will be judged |

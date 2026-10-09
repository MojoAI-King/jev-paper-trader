# How the trader improves itself

Kind: Living. Updated 2026-09-28.

The goal: every resolved market makes the system a little better, automatically, without it
fooling itself. This page is the design; `python3 -m papertrade learn` shows its current state, and
the public page shows it to friends.

## Free rein over the rules, not over the scoreboard

Joey, 2026-09-28: the loop may change **any strategy's betting rules by itself**, main included: the
gates, the bet size, the open-bet limit and which markets it skips. It may start and retire challengers.
It can't change code: a code idea is written down and waits for Joey to approve or reject it.

Until then main's rules were pinned, on the argument that a system tuning its own bets on the results
it's judged by will chase noise and fool the people watching. That risk is real, so tuning comes with
four things that keep it honest instead of forbidding it:

- **The scoreboard is out of its reach.** Fees, the price screen, market data, settlement and how
  results are scored are code and policy the loop can't touch (`learn.rules_problem` accepts only the
  rules in `learn.RULES`).
- **Every change is on the record.** `papertrade_data/rules_history.jsonl` keeps what changed, from
  what to what, why, and how it will be judged; the page's live feed shows each one (TUNE), and a
  tuned strategy shows its rules version.
- **Every bet carries its rules version** (`rules_version` in the ledgers), so each version's results
  are read on their own; the review judges a strategy by its record since its rules last changed.
- **A yardstick that never changes.** `original` bets on main's starting rules for good
  (`learning.frozen_strategies`). Main is compared with it only on bets placed since `original` started
  (the review's `yardstick` numbers and `original`'s row on the page, from `coach.yardstick`), leaving out
  markets main already held then, so neither main's earlier head start nor `original`'s fresh start
  counts as tuning. If main does better there, the tuning is paying; if not, it isn't.
- **The gate ledger scores each decision by the edge bar it was made under** (decisions record
  `min_edge`), so a tuned bar doesn't rewrite what earlier gates did.

What changes by itself, and what doesn't:

| Changes automatically | Needs Joey |
| --- | --- |
| Scores for every resolved market | Code changes (the loop files them as ideas) |
| Written reviews of misses and of wins | Fees and slippage |
| The research playbook (how to research, never what to bet) | Loosening the price screen |
| The calibration map, and the self-calibrating strategy using it | Question wording (bumps `QUESTION_SET_VERSION`) |
| The daily review and its proposals | Research budgets (they spend Joey's Claude plan) |
| Any strategy's rules: gates, bet size, open-bet limit, market filters (Joey, 2026-09-28) | Changing `original`, the yardstick |
| Starting and retiring challengers | Which forecaster a strategy is (its label says it) |

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

**6. The daily review (daily, Claude on the plan).** `coach.retro`: once `learning.retro_every_days`
(1) has passed and `learning.retro_min_reviews` markets are reviewed, Claude reads numbers computed in
code (each strategy's rules and results, all time and since its rules last changed; Brier by category;
the gate ledger; root causes; the calibration map; the recent rule changes) and writes an honest summary
plus at most `learning.max_proposals_per_retro` (4) proposals. It's told its job is to make the
strategies make more money by experimenting, that under 30 resolved markets a number is mostly noise
(an experiment, not a finding), and that each proposal says how it will be judged before it starts
(`judge_by`, `min_resolved`). It was weekly until 2026-09-28.

**7. Rule changes (automatic, `learning.auto_tune`).** A proposal of kind `tune` names a strategy and
new values for any of its rules: the four gates, `kelly_fraction`, `max_stake_pct` (the most one bet may
be), `max_total_exposure_pct` (the open-bet limit), `min_ask`/`max_ask` (the price range it buys in) and
`skip_categories`. Checked in code, never trusted to the prompt (`coach.tune`, `learn.rules_problem`):
the strategy exists and isn't frozen; every rule is one of those, a real number (not text, not true/false,
not NaN, not too large) inside `learning.bounds`, where the sizing rules keep a small floor so a change
can't quietly stop a strategy betting, and (since 2026-10-09) a ceiling: Kelly fraction 0.5, 3% a bet, 50%
open; a challenger can't take another strategy's name; and the
strategy's rules didn't change in the last `learning.min_days_between_changes` (7 days since 2026-10-09; it
was 1) (counted from
`rules_history.jsonl`, so a hand undo doesn't reset it), so each version gets some results. Version
numbers never repeat (the next one follows the highest in the history), and a change that bets the same
way (the same categories in another order) is not a new version. `null` puts a rule back
to that strategy's starting value. The change lands in `papertrade_data/rules.json` (the current rules,
only what differs from the start) and `rules_history.jsonl`, and `engine.strategies` re-checks the file
on every load, so a hand edit past the bounds or to `original` is ignored, not traded on. With
`auto_tune` off, a change waits for `python3 -m papertrade approve <id>`.

**Sizing by measured skill (since 2026-10-09, `docs/REBUILD_PLAN.md` phase 1; not a loop rule).** Every
strategy but the frozen yardstick sizes its bets by its forecaster's measured edge over the market price,
`engine.skill`: λ, the share of a forecast's distance from the mid that came true, on finished markets with a
real price, shrunk for noise and 0 below 300 markets. While λ is 0 (every forecaster on 2026-10-09) a strategy
places probe bets (`skill.probe_stake_pct`, 0.25%; at most `skill.max_probes_per_day`, 5). With λ positive, it
bets Kelly on the forecast shrunk toward the price, scaled down as equity nears 70% of its peak. All open bets in
one event share one `max_stake_pct` budget. The review sees λ in its numbers ("skill") and knows sizing changes do
nothing while λ is 0.

**8. Challengers (automatic).** A proposal of kind `challenger` is a new strategy on its own fake
$100k: a probability source, a gate source and any rules as above (`learn.challenger_problem`,
re-checked on every load). Valid challengers start by themselves (`learning.auto_start_challengers`),
at most `learning.max_running_challengers` at a time; one that has to wait starts by itself when a slot
opens. A proposal of kind `retire` stops a running challenger to free its slot (retires are handled
before new challengers in the same review). It no longer bets, but its open bets still settle
(`engine.all_books`) and its whole record, losses included, stays on the page marked Retired.
`python3 -m papertrade retire <id>` (or `reject <id>` on a running one) does the same by hand, and a hand
`approve` respects the same limit. Two challengers can't share a name, so the same experiment isn't
started twice. A ledger that no strategy owns any more still shows on the page, marked Stopped. One
malformed proposal is marked invalid and never stops the others or the cycle.

**9. Code ideas (wait for Joey).** A proposal of kind `code` (or `research`) is an idea that needs a
code change. Nothing happens until Joey says so: the page's feed shows it (IDEA), `learn` lists it, and
`python3 -m papertrade approve <id>` marks it for a code session, `reject <id>` drops it.

## Where the records are

| File | What |
| --- | --- |
| `papertrade_data/reviews.jsonl` | every resolved market's scores, and its written review if it got one |
| `papertrade_data/playbook.json` | the current research playbook |
| `papertrade_data/playbook_history.jsonl` | every playbook change, with the rules refused by the checks |
| `papertrade_data/retros.jsonl` | the daily reviews, with the numbers they read |
| `papertrade_data/proposals.json` | proposals and their status; running challengers load from here |
| `papertrade_data/rules.json` | each strategy's rules as tuned (only what differs from its start) |
| `papertrade_data/rules_history.jsonl` | every rule change: from what to what, why, and how it will be judged |
| `docs/EXPERIMENTS.md` | every strategy: what it tests and how it will be judged |

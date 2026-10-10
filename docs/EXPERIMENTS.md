# Experiments

Kind: Living. Every strategy that trades a fake bankroll, what it tests, and how it will be judged.
Written when the strategy starts, before its results come in. A test
(`ExperimentsRegistryTests`) fails if a strategy in `policy.json` has no row here.

**2026-10-09, sizing changed for every strategy but `original`** (`docs/REBUILD_PLAN.md` phase 1). Each now
sizes by its forecaster's measured edge over the market price: probe bets of 0.25% of equity (at most 5 a
day) while that edge measures 0, which on 2026-10-09 is every forecaster, and one stake budget per event.
Results from this date are under the new sizing; compare them with `original`, which keeps the old sizing.

| Strategy | Started | What it changes vs main | The question it answers | Judged by |
| --- | --- | --- | --- | --- |
| `main` | 2026-09-27 | (the headline: Jev + Claude research; pre-registered gates until 2026-09-28, then tuned by the daily review) | Can Jev with research grow $100k by more than luck? | PLAN.md's pre-registered criteria for the forecasts; for the tuning, main vs `original` |
| `jev_alone` | 2026-09-27 (retired 2026-10-10) | Jev without research, for probability and gates | Does research help Jev? | Brier vs main after 50 resolved markets. Answered and retired: on 1,006 finished markets with a real price it scored like a coin flip (0.247), and it placed one bet in two weeks |
| `claude_direct` | 2026-09-27 | Claude's own probability from the same facts; main's gates | Does Jev add anything over Claude? | Brier vs main after 50 resolved markets |
| `bold` | 2026-09-27 | Info bar 0.2 instead of 0.5 | Is the info gate too cautious? | P&L and Brier on its bets vs main's; the gate ledger's "stopped only by the info gate" row, after 30 settled bets |
| `calibrated` | 2026-09-27 | Jev's probability corrected by a map learned from resolved markets; waits for 30 | Does learning from outcomes make Jev's numbers better? | Brier vs main on the same markets after 50 resolved markets past activation |
| `original` | 2026-09-28 | Nothing: main's starting rules, frozen (`learning.frozen_strategies`), never tuned | Does the daily review's tuning make more money than leaving the rules alone? | P&L of main vs `original` on bets placed from 2026-09-29, after 30 settled bets each |
| `jev_alone_bold` | 2026-09-28 | Jev without research (like `jev_alone`) and info bar 0.2 (like `bold`) | Does research pay when betting boldly? It differs from `bold` only in having no research | P&L and Brier vs `bold` on the markets both could bet, after 30 settled bets each; both vs `jev_alone` |
| `sharp` | 2026-10-10 | No AI forecast: on games, Pinnacle's price with its margin removed (The Odds API) as the probability; edge bar 3¢; buys only between 20¢ and 85¢ | Do Kalshi and Polymarket game prices sit far enough from the sharp sportsbook line to profit after costs? (research report 09) | Closing-line value per bet against Pinnacle's last line before the start, and its measured λ against the venue price; kill if, after 150 bets, the top of the 95% range of mean CLV after costs is below +1%; keep if its bottom is above 0 at 300 bets. Expected going in: zero or a small edge |

The rules in this table are each strategy's starting rules. From 2026-09-28 the daily review may tune
any strategy's rules by itself (Joey's call; `docs/LEARNING.md`), except `original`. Every change is kept in
`papertrade_data/rules_history.jsonl` with its reason, its `judge_by` and `min_resolved`, and every bet
records the rules version it was placed under, so each version's results can be read on their own.
Challengers the review starts are listed the same way in `papertrade_data/proposals.json` and on the page.
The next improvement session copies each running challenger into this table.

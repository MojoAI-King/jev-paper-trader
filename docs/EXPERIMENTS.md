# Experiments

Kind: Living. Every strategy that trades a fake bankroll, what it tests, and how it will be judged.
Written when the strategy starts, before its results come in. A test
(`ExperimentsRegistryTests`) fails if a strategy in `policy.json` has no row here.

| Strategy | Started | What it changes vs main | The question it answers | Judged by |
| --- | --- | --- | --- | --- |
| `main` | 2026-09-27 | (the headline: Jev + Claude research, pre-registered gates) | Can Jev with research grow $100k by more than luck? | PLAN.md's pre-registered criteria |
| `jev_alone` | 2026-09-27 | Jev without research, for probability and gates | Does research help Jev? | Brier vs main after 50 resolved markets |
| `claude_direct` | 2026-09-27 | Claude's own probability from the same facts; main's gates | Does Jev add anything over Claude? | Brier vs main after 50 resolved markets |
| `bold` | 2026-09-27 | Info bar 0.2 instead of 0.5 | Is the info gate too cautious? | P&L and Brier on its bets vs main's; the gate ledger's "stopped only by the info gate" row, after 30 settled bets |
| `calibrated` | 2026-09-27 | Jev's probability corrected by a map learned from resolved markets; waits for 30 | Does learning from outcomes make Jev's numbers better? | Brier vs main on the same markets after 50 resolved markets past activation |

Challengers the weekly retrospective proposes get a row here when Joey approves them, with the
proposal's own `judge_by` and `min_resolved`.

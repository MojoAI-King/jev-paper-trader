# Backlog

Kind: Living.

| ID | Requested outcome | State | Evidence or next step |
|---|---|---|---|
| B2 | Decide on the price-match rule | open (Joey, after a few days of data) | It dropped 8 of 53 real facts, likely poll numbers within 1 point of the market price. Kept strict by Joey's choice; review the logged `facts_dropped` reasons in `judgments.jsonl`. |
| B3 | Make linked markets' probabilities fit together | proposed | Jev gave Lula 38% and Bolsonaro 23% in a two-way race (market: 43% + 57%). Needs a probability source normalized within an event (mutually exclusive outcomes add up to 100%; "above $X" ladders never rise with X), then a challenger. Opposing bets within an event stay allowed when each has an edge (decision 2026-09-27-challengers-start-by-themselves-opposing-4dc1). |
| B4 | ChatGPT as a second researcher (PLAN phase 2) | not started | Needs a way to run on a ChatGPT plan rather than per-call API billing, since API spend was ruled out. |
| B5 | Research-agent check before a bet (PLAN phase 3) | not started | Main bets now (5 open on 2026-09-28); Bold holds 18. |
| B6 | Keep `judgments.jsonl` a manageable size | watch | 2.6 MB on 2026-09-28 after two days of half-hourly cycles. Rotate the file by month if it passes about 50 MB. |
| B7 | Fix the README quick start | open | It points at VS Code tasks, but the repo has no `.vscode/` folder. |
| B9 | Decide the 15 open security findings | open (needs a human) | Listed in `docs/SECURITY_FINDINGS.md`; `skilliton security status` reports 15 controls missing and undecided. |
| B13 | Tune the dashboard for phones | later (Joey) | The mission-control page stacks its panels below 1150px wide; Joey: "on the phone, we can figure that out later". |
| B15 | Size fills to what a market could actually fill | proposed | The simulation fills a $2,000 order at the listed ask however little is offered there. Cap each bet at a share of the market's displayed depth or liquidity (Polymarket `liquidityNum`; check Kalshi's fields), so thin markets stay allowed but fills stay realistic. |
| B16 | Widen the market universe if research stops running out | watch | 2026-09-28: the Kalshi fetch fix (decision 2026-09-28-more-action-whole-kalshi-window-soonest-21f7) made the same 60 slots count (Kalshi 488 passing, 43 of the top 60 within 7 days). After a day, if `deferred` stays 0 and research isn't used up, raise `markets_per_source` to about 100 (not 150+: the 40-market-a-cycle Jev ceiling would bind). |
| B17 | One bet per event per strategy | proposed (Joey) | Bold holds YES on one fighter and NO on the other in the same UFC fight: $4,000 on one outcome, past the 2% per-bet cap in effect. A per-event limit is a new rule in code, so the daily review can't add it by itself (2026-09-28); it's a code idea for Joey. |
| B22 | Stop the long-shot losses | proposed (Joey) | 2026-10-01: 21 settled bets on contracts under 30c (avg 15c) won 1; our forecasts averaged 33% on them, the market 15% (market-expected wins 2.9, ours 7.0) = -$32.6k of -$35.7k settled across strategies; the other 29 bets -$3.1k. 53 of 73 open bets ($92k) are more of the same. Options put to Joey: (1) min_ask 0.30 on every tunable strategy now, by hand (`original` stays as the yardstick); (2) approve code ideas p4 (results by price paid) and p7 (paired Brier, calibration check); (3) code: trust the market more when a forecast disagrees a lot on a long shot. The daily review and research are paused: Claude week 100% (resets Mon 3 AM ET). |
| B21 | Read the first daily reviews and the tuning's effect | watch | First daily review at the first cycle after about 2026-09-29 23:12Z: check what it changed, why, and that the page shows it. After about 30 settled bets each, compare main with `original` on the same markets (`coach.yardstick`, the review's `yardstick` numbers). If tuning chases noise (changes reversed within days, main behind `original`), tell Joey and suggest a longer `min_days_between_changes`. |
| B18 | Score each forecaster at its latest look that carries its forecast | proposed (Joey) | Today only each market's latest judgment is scored, which drops Claude direct on 38 of 50 markets and Jev+research on 20 of 61, and delays calibration's 30. Also compare sources on the same markets (the page's Jev+research 0.130 vs market 0.135 is on different sets; on the same 5 markets the market scored 0.063). Changes a pre-registered measure: needs Joey's OK and a dated split. |
| B19 | Show why no bet and what was researched | proposed (Joey) | Three small page additions: a one-word verdict on each CALL line, a research run's facts one tap away (the Verify pop-up), and a "Why no bet · 24h" line in the bottom bar. The data is already in summary.json. |
| B20 | Keep research from filling Claude's weekly meter | proposed (Joey) | Paced research uses all 60 a day when demand is high. The weekly meter rose 0.78 -> 0.95 in a day on 2026-09-27 (research plus Joey's own use, not separable). Option: pace research by the week too (e.g. week used <= share of the week gone + 15%). Log each run's own meter change first. |

Give each item a stable ID and link its task and decisions. Move a completed item to `docs/BACKLOG_ARCHIVE.md` with its closure date and evidence.

<!-- skilliton:security-findings:start -->
Security findings: 15 open, listed in [docs/SECURITY\_FINDINGS.md](SECURITY_FINDINGS.md) (generated by skilliton security findings; do not edit between these markers).
<!-- skilliton:security-findings:end -->

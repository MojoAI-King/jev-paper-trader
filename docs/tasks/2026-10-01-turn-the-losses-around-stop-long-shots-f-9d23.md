# Task: Turn the losses around: stop long shots, find every loss pattern, more and better bets

Kind: Living. Task record.

- **ID:** 2026-10-01-turn-the-losses-around-stop-long-shots-f-9d23
- **State:** verified
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-01T05:04:09.242Z

## Request

not yet written

## Acceptance criteria

- [ ] min_ask 0.30 applied to every tunable strategy and shown on the page; every resolved judged market analysed for loss patterns with numbers; changes justified by that analysis built with tests; Joey told what changed and why

## Decisions

not yet written

## Checkpoints

### 2026-10-01T04:20:26.898Z

- **State:** Done and pushed: min_ask 0.30 on all 8 tunable strategies (360bb9f), tune CLI + by_price_paid + 100 markets (4a0c001), decision 4428, backlog B22/B16. Not done: verifying the 04:34Z cycle; Joey must replace the Claude token secret to restore research
- **Evidence:** 119 tests OK; learn shows Rules now with 30c floor on all but original; 140-market simulation in scratchpad
- **Next:** Read the 04:34Z run result; then report to Joey
- **Git:** master @ 22fb03b, 2 uncommitted

### 2026-10-01T04:51:29.955Z

- **State:** Pushed: 30c floor on all tunable strategies, research 150/day with weekly pace guard, review twice daily, 100 markets/source, probe past stale busy reading (287e486); Joey replaced the Claude token secret 04:30:53Z. Ledger audit clean. Not yet verified: research resuming on the new token
- **Evidence:** 121 tests OK; probe guards mutation-proven; audit: 9 ledgers add up, 32 settled markets match Kalshi/Polymarket live, page equals ledgers
- **Next:** Read manual run 36816087586: researched_new > 0 and a fresh week reading; then report to Joey
- **Git:** master @ 287e486, 2 uncommitted

### 2026-10-01T05:04:08.909Z

- **State:** Verified: research back on Joey's current Claude account (run 36816087586 at 04:39Z: 10 new research runs, 22 Claude calls, week 41%, 5-hour 40%); 30c floor, 150 research/day with week pace guard, review twice daily, 100 markets/source all live. Ledger audit clean (9 ledgers add up; 32 settled markets match the exchanges; page equals ledgers)
- **Evidence:** 121 tests OK; health run success; audit script output
- **Next:** Check in: bets/wins/losses since 2026-10-01 vs original; what the twice-daily review changed; plan meter vs the pace guard
- **Git:** master @ a1e13d0, 3 uncommitted

## Handoff

- **State:** Verified: research back on Joey's current Claude account (run 36816087586 at 04:39Z: 10 new research runs, 22 Claude calls, week 41%, 5-hour 40%); 30c floor, 150 research/day with week pace guard, review twice daily, 100 markets/source all live. Ledger audit clean (9 ledgers add up; 32 settled markets match the exchanges; page equals ledgers). Evidence: 121 tests OK; health run success; audit script output.
- **Next:** Check in: bets/wins/losses since 2026-10-01 vs original; what the twice-daily review changed; plan meter vs the pace guard
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 27% at 04:06Z on 2026-09-29, much of it this session's review workflows (resets Mon 3 AM ET); never build an unattended job that edits or ships code (Joey, 2026-09-28)

# Task: Sharp-line strategy (plan 2A) and the research on who makes the money

Kind: Living. Task record.

- **ID:** 2026-10-09-sharp-line-strategy-plan-2a-and-the-rese-8e55
- **State:** verified
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-10T05:22:33.028Z

## Request

not yet written

## Acceptance criteria

- [ ] The sharp strategy prices games from Pinnacle via The Odds API and bets only through the skill sizing; the line never reaches Jev or Claude; it waits without a key; odds-check validates the key; research report 15 (who makes the money) is in and checked; Joey has the key steps

## Decisions

not yet written

## Checkpoints

### 2026-10-10T03:54:35.765Z

- **State:** Sharp-line strategy built and pushed (b6900cb): papertrade/odds.py (Pinnacle de-vig, matching to our Kalshi/Polymarket game markets, quota-aware cache), strategy 'sharp' with probes via skill sizing, odds-check command; Jev alone retired (ledger still settles). Waiting for Joey's free The Odds API key (gh secret set ODDS_API_KEY + .env). Research report 15 (who makes the money) running in a background agent
- **Evidence:** 138 offline tests OK incl. OddsTests and the full-scan sharp test; odds-check without a key prints the setup steps
- **Next:** Confirm the next cycle runs green on b6900cb; read and check report 15 when it lands; when Joey sets the key, run odds-check and watch the first sharp probes
- **Git:** master @ b6900cb, 3 uncommitted

### 2026-10-10T04:26:25.069Z

- **State:** Joey set ODDS_API_KEY (secret + .env); odds-check OK (all 4 sports in season). Kalshi's game titles changed to one team; matcher reads both teams from the rules (dddfeac); live dry run matched 24 Kalshi game markets, none 3c+ under Pinnacle's fair price. A test run spent ~210 of the 500 free requests via the real key; tests now can't call the API (lesson 43ba), refresh 8h, 286 left. Running in background: maker test on Kalshi trade prints, research report 15, next-cycle check
- **Evidence:** 138 offline tests OK in 8.6s with no network; odds-check quota 286; dry-run output in the session
- **Next:** Read the maker-test result and report 15; confirm the next cycle uses the key (stats.sharp) without spending more than ~4 requests; tell Joey what the math says next
- **Git:** master @ 64c524b, 2 uncommitted

### 2026-10-10T04:27:03.059Z

- **State:** Maintenance run. Sharp line live with Joey's key (286 free requests left, tests can't spend them). Favourites test recorded in docs/research/CHECKS.md (break-even overall; >7 days +8.3% on 72, a lead to re-run). Background: maker test on Kalshi trade prints, research report 15, next-cycle check
- **Evidence:** 138 offline tests OK; maintenance recorded
- **Next:** Read the maker-test result and report 15; confirm the next cycle's sharp stats; recommend the next build to Joey
- **Git:** master @ 114cc25, 2 uncommitted

### 2026-10-10T04:43:19.976Z

- **State:** Sharp line verified live: cycle 2026-10-10T04:35Z refreshed 4 sports (110 games) for 4 requests (282 left, tests spend none); 5 of 40 judged markets matched a Pinnacle line; all 5 correctly passed (Kalshi 1-2.5c worse than fair after fees). Background: maker test on Kalshi trade prints (150+ markets fetched), research report 15
- **Evidence:** scans.jsonl 04:35:11Z sharp {games 110, matched 5, quota_left 282}; judgments' sharp decisions 'edge -0.02 < 0.03'; gh run 04:34:44Z success
- **Next:** Read the maker-test result and report 15; recommend the next build to Joey
- **Git:** master @ 23a6329, 2 uncommitted

### 2026-10-10T05:06:04.861Z

- **State:** Research report 15 in and checked (who makes the money: ~4 wallets ever made 10M+; takers->makers and YES->NO flows; AI agents at our cadence lost 16-31% on Kalshi). T1 on our data: YES at the ask -20.8%, NO -7.6% (30-70c: YES -12.1%, NO -2.1%); no mention markets in our history. Running in background: the maker test on Kalshi trade prints and the mention-market NO test on Kalshi public data. Sharp line live (no qualifying gaps yet)
- **Evidence:** CHECKS.md section 15; T1 script output; scans 04:35Z sharp stats
- **Next:** Read the maker and mention test results; if the mention NO bias survives fees on fresh data, propose a 'mention NO' strategy (code; Joey said do what's needed) with a forward test
- **Git:** master @ 8bc1051, 2 uncommitted

## Handoff

- **State:** Research report 15 in and checked (who makes the money: ~4 wallets ever made 10M+; takers->makers and YES->NO flows; AI agents at our cadence lost 16-31% on Kalshi). T1 on our data: YES at the ask -20.8%, NO -7.6% (30-70c: YES -12.1%, NO -2.1%); no mention markets in our history. Running in background: the maker test on Kalshi trade prints and the mention-market NO test on Kalshi public data. Sharp line live (no qualifying gaps yet). Evidence: CHECKS.md section 15; T1 script output; scans 04:35Z sharp stats.
- **Next:** Read the maker and mention test results; if the mention NO bias survives fees on fresh data, propose a 'mention NO' strategy (code; Joey said do what's needed) with a forward test
- **Blocked:** nothing
- **Watch out:** Never let a test reach The Odds API (DataDirTest guards it); keep staging by explicit path

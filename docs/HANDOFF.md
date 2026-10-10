# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-10 01:06 EDT

- **State:** Research report 15 in and checked (who makes the money: ~4 wallets ever made 10M+; takers->makers and YES->NO flows; AI agents at our cadence lost 16-31% on Kalshi). T1 on our data: YES at the ask -20.8%, NO -7.6% (30-70c: YES -12.1%, NO -2.1%); no mention markets in our history. Running in background: the maker test on Kalshi trade prints and the mention-market NO test on Kalshi public data. Sharp line live (no qualifying gaps yet). Evidence: CHECKS.md section 15; T1 script output; scans 04:35Z sharp stats.
- **Next:** Read the maker and mention test results; if the mention NO bias survives fees on fresh data, propose a 'mention NO' strategy (code; Joey said do what's needed) with a forward test
- **Blocked:** nothing
- **Watch out:** Never let a test reach The Odds API (DataDirTest guards it); keep staging by explicit path
- **Git:** master @ 8bc1051, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 05:06 UTC)

## Earlier

### 2026-10-10 00:43 EDT
- **State:** Sharp line verified live: cycle 2026-10-10T04:35Z refreshed 4 sports (110 games) for 4 requests (282 left, tests spend none); 5 of 40 judged markets matched a Pinnacle line; all 5 correctly passed (Kalshi 1-2.5c worse than fair after fees). Background: maker test on Kalshi trade prints (150+ markets fetched), research report 15. Evidence: scans.jsonl 04:35:11Z sharp {games 110, matched 5, quota_left 282}; judgments' sharp decisions 'edge -0.02 < 0.03'; gh run 04:34:44Z success.
- **Next:** Read the maker-test result and report 15; recommend the next build to Joey
- **Blocked:** nothing
- **Watch out:** Never let a test reach The Odds API (DataDirTest guards it); keep staging by explicit path
- **Git:** master @ 23a6329, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 04:43 UTC)

### 2026-10-10 00:27 EDT
- **State:** Maintenance run. Sharp line live with Joey's key (286 free requests left, tests can't spend them). Favourites test recorded in docs/research/CHECKS.md (break-even overall; >7 days +8.3% on 72, a lead to re-run). Background: maker test on Kalshi trade prints, research report 15, next-cycle check. Evidence: 138 offline tests OK; maintenance recorded.
- **Next:** Read the maker-test result and report 15; confirm the next cycle's sharp stats; recommend the next build to Joey
- **Blocked:** nothing
- **Watch out:** Never let a test reach The Odds API (DataDirTest guards it); keep staging by explicit path
- **Git:** master @ 114cc25, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 04:27 UTC)

### 2026-10-10 00:26 EDT
- **State:** Joey set ODDS_API_KEY (secret + .env); odds-check OK (all 4 sports in season). Kalshi's game titles changed to one team; matcher reads both teams from the rules (dddfeac); live dry run matched 24 Kalshi game markets, none 3c+ under Pinnacle's fair price. A test run spent ~210 of the 500 free requests via the real key; tests now can't call the API (lesson 43ba), refresh 8h, 286 left. Running in background: maker test on Kalshi trade prints, research report 15, next-cycle check. Evidence: 138 offline tests OK in 8.6s with no network; odds-check quota 286; dry-run output in the session.
- **Next:** Read the maker-test result and report 15; confirm the next cycle uses the key (stats.sharp) without spending more than ~4 requests; tell Joey what the math says next
- **Blocked:** nothing
- **Watch out:** Never let a test reach The Odds API (DataDirTest guards it); keep staging by explicit path
- **Git:** master @ 64c524b, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 04:26 UTC)

### 2026-10-09 23:54 EDT
- **State:** Sharp-line strategy built and pushed (b6900cb): papertrade/odds.py (Pinnacle de-vig, matching to our Kalshi/Polymarket game markets, quota-aware cache), strategy 'sharp' with probes via skill sizing, odds-check command; Jev alone retired (ledger still settles). Waiting for Joey's free The Odds API key (gh secret set ODDS_API_KEY + .env). Research report 15 (who makes the money) running in a background agent. Evidence: 138 offline tests OK incl. OddsTests and the full-scan sharp test; odds-check without a key prints the setup steps.
- **Next:** Confirm the next cycle runs green on b6900cb; read and check report 15 when it lands; when Joey sets the key, run odds-check and watch the first sharp probes
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)
- **Git:** master @ b6900cb, 3 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 03:54 UTC)

### 2026-10-09 19:40 EDT
- **State:** Phase 1 verified live: cycle 23:09Z green on 04b8c2a with lambda 0 for all sources; first bet after it was a probe (bold, $175.20, 0.25% of equity, 23:35Z). Task closed. Joey is away for Shabbat; plan and results are in docs/REBUILD_PLAN.md. Evidence: portfolio bold.json open bet at 2026-10-09T23:35:08Z with sizing probe, lambda 0.0; peak_equity recorded on every book.
- **Next:** When Joey is back: summarize phase 1 and the research verdict; ask about B27 ($30/month sports odds). Phase 2 candidates B28 (math pricer) and B30 (Jev jobs) wait for his go-ahead on scope
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)
- **Git:** master @ e6b2e8f, 5 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 23:40 UTC)

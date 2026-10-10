# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-10 00:27 EDT

- **State:** Maintenance run. Sharp line live with Joey's key (286 free requests left, tests can't spend them). Favourites test recorded in docs/research/CHECKS.md (break-even overall; >7 days +8.3% on 72, a lead to re-run). Background: maker test on Kalshi trade prints, research report 15, next-cycle check. Evidence: 138 offline tests OK; maintenance recorded.
- **Next:** Read the maker-test result and report 15; confirm the next cycle's sharp stats; recommend the next build to Joey
- **Blocked:** nothing
- **Watch out:** Never let a test reach The Odds API (DataDirTest guards it); keep staging by explicit path
- **Git:** master @ 114cc25, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 04:27 UTC)

## Earlier

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

### 2026-10-09 19:11 EDT
- **State:** Phase 1 live: cycle 2026-10-09T23:09Z ran green on 04b8c2a; skill computed in the scan (lambda 0 for all four sources: raw -0.06/-0.03/-0.02/-0.03 on 1,025/843/562/774 markets); Kalshi judgments carry fee_multiplier. No bet in that cycle, so a probe bet isn't seen yet; a background check is waiting for the first one. Research task closed (14 of 14 reports checked). Evidence: gh run 2026-10-09T23:04:45Z success; scans.jsonl 23:05Z skill field; judgments since 23:00Z.
- **Next:** Confirm the first new bet is a probe (original at the old size), then summarize for Joey when he's back
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)
- **Git:** master @ ee51a75, 6 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 23:11 UTC)

### 2026-10-09 18:50 EDT
- **State:** Phase 1 shipped at 04b8c2a (sizing by measured skill with probes, one stake per event, real price required, Kalshi per-series fees, slower capped review); page deployed (Worker ee378ff7); live check of the 23:04Z cycle running. B29 tested offline and dropped. Maintenance run. Evidence: 131 offline tests OK; B29 split test in docs/research/CHECKS.md.
- **Next:** Confirm the 23:04Z cycle (green run, skill in scans, probes for all but original, Kalshi fee_multiplier on judgments); then report to Joey. Phase 2: B27 needs Joey's $30; B28 and B30 next
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)
- **Git:** master @ 7bd74c0, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 22:50 UTC)

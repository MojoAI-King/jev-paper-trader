# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-10 02:56 EDT

- **State:** 15-minute schedule verified: the first :49 run (38032277618) passed and committed a cycle at 06:53Z. Found two mention-strategy problems (B32): it sees 8 of the 76 open Kalshi mention events (about 48 settle a week), and its hour-before guard counts from Kalshi's formal close, about 14-15 days after the event, so it could buy during or after an event. No such bet yet. Evidence: run 38032277618 success; scan 2026-10-10T06:50:17Z; Kalshi public API sweep of 454 Mentions series (scratchpad mention_rate.py); close times read for 6 series.
- **Next:** Joey decides B32: (1) policy stopgap mention.min_hours_before 384; (2) history test at the live timing; (3) code to read mention events directly
- **Blocked:** B32 waits for Joey's OK
- **Watch out:** Stage by explicit path; tests must never reach The Odds API or write real mentions.jsonl; Kalshi mention tickers' dates can be stale ('originally scheduled', 'next PMQs')
- **Git:** master @ ef6456f, 3 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 06:56 UTC)

## Earlier

### 2026-10-10 02:40 EDT
- **State:** Maintenance done (4983d0e): B31 records the 15-minute pace; the secrets scan's 20 high-confidence matches checked by hand (URL slugs, 'list bearer' in a news snippet, env-variable names; no secret values). The 06:34Z cycle (run 38031423601) ran the new code at dd0dbbc and passed: mention pass saw 168, looked 23, one new NO probe (KXDEBATEMENTION-26OCT13-FILI); sharp saw 110 games, none inside the 8-hour kickoff window. The first :49 slot (06:49Z) is the next check. Evidence: run 38031423601 success; scan 2026-10-10T06:35:13Z stats; 143 offline tests OK.
- **Next:** Confirm the 06:49Z run starts and passes (watcher in the session); then the mention forward test runs on its own (keep/kill after 150 settled bets)
- **Blocked:** nothing
- **Watch out:** Stage by explicit path; tests must never reach The Odds API or write real mentions.jsonl (DataDirTest); the Kalshi walk hitting its 60-page limit is expected (far-dated markets left out)
- **Git:** master @ 79f0957, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 06:40 UTC)

### 2026-10-10 02:33 EDT
- **State:** Faster pace pushed (af1725f) and deployed (Worker bbd8c036): Cloudflare trigger every 15 min (:04/:19/:34/:49), due gate 12 min, page clock updated; mention markets re-looked hourly, mention_no up to 15 probes/day (one per event, soonest first). Millisecond trading ruled out (paper can't simulate it; needs co-located servers and real accounts). Waiting to see the first :19/:49 dispatch. Evidence: 143 offline tests OK; wrangler deploy of triggers succeeded.
- **Next:** Confirm a :19 or :49 run starts and passes; then the forward test runs on its own (keep/kill after 150 settled mention bets)
- **Blocked:** nothing
- **Watch out:** Stage by explicit path; tests must never reach The Odds API (DataDirTest guards it) or write real mentions.jsonl (DataDirTest covers MENTIONS)
- **Git:** master @ af1725f, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 06:33 UTC)

### 2026-10-10 02:22 EDT
- **State:** mention_no live: the 06:05Z cycle saw 168 Kalshi mention markets, logged 150 looks, placed 5 NO probes (capped at 100-222 contracts by the asks), all on one event; fixed to one bet per event, soonest first (142 tests). Sharp line live, no qualifying gaps; 282 Odds API requests left. Evidence: scans 06:05:20Z mentions {seen 168, looked 150}, bets mention_no 5; mentions.jsonl 150 looks; gh runs 05:34Z and 06:04Z green.
- **Next:** Watch the next cycles: one probe per event, soonest-ending first; as mention markets resolve, the skill measure for mention_prior builds toward 300; keep/kill after 150 settled bets
- **Blocked:** nothing
- **Watch out:** Stage by explicit path; tests must never reach The Odds API (DataDirTest guards it) or write real mentions.jsonl (DataDirTest covers MENTIONS)
- **Git:** master @ 1c777e5, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 06:22 UTC)

### 2026-10-10 01:22 EDT
- **State:** mention_no built and pushed (cfff32a): Kalshi walk keeps mention markets, scan looks once per 6h with no Jev call, logs to mentions.jsonl, NO probes at 30-70c before the event capped at the ask size. Replication: +21.0% after fees [+6.1, +35.5] on 639 settled markets. Maker test: makers save 4-5 pts but break even. Sharp line verified live (no qualifying gaps yet). Jev alone and Jev alone, bold retired. Evidence: 141 offline tests OK; CHECKS.md has the replication and maker tables; gh run 04:34Z green on the sharp code.
- **Next:** Confirm the next CI cycle runs green on cfff32a and shows stats.mentions; watch for mention markets to appear (earnings season next week) and the first NO probes
- **Blocked:** nothing
- **Watch out:** Stage by explicit path; tests must never reach The Odds API (DataDirTest guards it) or write real mentions.jsonl (DataDirTest covers MENTIONS)
- **Git:** master @ cfff32a, 5 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 05:22 UTC)

### 2026-10-10 01:06 EDT
- **State:** Research report 15 in and checked (who makes the money: ~4 wallets ever made 10M+; takers->makers and YES->NO flows; AI agents at our cadence lost 16-31% on Kalshi). T1 on our data: YES at the ask -20.8%, NO -7.6% (30-70c: YES -12.1%, NO -2.1%); no mention markets in our history. Running in background: the maker test on Kalshi trade prints and the mention-market NO test on Kalshi public data. Sharp line live (no qualifying gaps yet). Evidence: CHECKS.md section 15; T1 script output; scans 04:35Z sharp stats.
- **Next:** Read the maker and mention test results; if the mention NO bias survives fees on fresh data, propose a 'mention NO' strategy (code; Joey said do what's needed) with a forward test
- **Blocked:** nothing
- **Watch out:** Never let a test reach The Odds API (DataDirTest guards it); keep staging by explicit path
- **Git:** master @ 8bc1051, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 05:06 UTC)

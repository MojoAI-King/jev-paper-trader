# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-10 02:33 EDT

- **State:** Faster pace pushed (af1725f) and deployed (Worker bbd8c036): Cloudflare trigger every 15 min (:04/:19/:34/:49), due gate 12 min, page clock updated; mention markets re-looked hourly, mention_no up to 15 probes/day (one per event, soonest first). Millisecond trading ruled out (paper can't simulate it; needs co-located servers and real accounts). Waiting to see the first :19/:49 dispatch. Evidence: 143 offline tests OK; wrangler deploy of triggers succeeded.
- **Next:** Confirm a :19 or :49 run starts and passes; then the forward test runs on its own (keep/kill after 150 settled mention bets)
- **Blocked:** nothing
- **Watch out:** Stage by explicit path; tests must never reach The Odds API (DataDirTest guards it) or write real mentions.jsonl (DataDirTest covers MENTIONS)
- **Git:** master @ af1725f, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 06:33 UTC)

## Earlier

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

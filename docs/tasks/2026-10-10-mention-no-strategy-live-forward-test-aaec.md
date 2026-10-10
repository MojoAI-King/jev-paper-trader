# Task: Mention NO strategy: live forward test

Kind: Living. Task record.

- **ID:** 2026-10-10-mention-no-strategy-live-forward-test-aaec
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-10T06:40:50.655Z

## Request

not yet written

## Acceptance criteria

- [ ] The live walk collects Kalshi mention markets; the mention pass logs them and places NO probes at 30-70c before the event within the ask size; settle scores them; after 150 settled bets the keep/kill rule in docs/EXPERIMENTS.md is applied and reported to Joey

## Decisions

not yet written

## Checkpoints

### 2026-10-10T05:22:33.449Z

- **State:** mention_no built and pushed (cfff32a): Kalshi walk keeps mention markets, scan looks once per 6h with no Jev call, logs to mentions.jsonl, NO probes at 30-70c before the event capped at the ask size. Replication: +21.0% after fees [+6.1, +35.5] on 639 settled markets. Maker test: makers save 4-5 pts but break even. Sharp line verified live (no qualifying gaps yet). Jev alone and Jev alone, bold retired
- **Evidence:** 141 offline tests OK; CHECKS.md has the replication and maker tables; gh run 04:34Z green on the sharp code
- **Next:** Confirm the next CI cycle runs green on cfff32a and shows stats.mentions; watch for mention markets to appear (earnings season next week) and the first NO probes
- **Git:** master @ cfff32a, 5 uncommitted

### 2026-10-10T06:22:49.518Z

- **State:** mention_no live: the 06:05Z cycle saw 168 Kalshi mention markets, logged 150 looks, placed 5 NO probes (capped at 100-222 contracts by the asks), all on one event; fixed to one bet per event, soonest first (142 tests). Sharp line live, no qualifying gaps; 282 Odds API requests left
- **Evidence:** scans 06:05:20Z mentions {seen 168, looked 150}, bets mention_no 5; mentions.jsonl 150 looks; gh runs 05:34Z and 06:04Z green
- **Next:** Watch the next cycles: one probe per event, soonest-ending first; as mention markets resolve, the skill measure for mention_prior builds toward 300; keep/kill after 150 settled bets
- **Git:** master @ 1c777e5, 2 uncommitted

### 2026-10-10T06:33:53.346Z

- **State:** Faster pace pushed (af1725f) and deployed (Worker bbd8c036): Cloudflare trigger every 15 min (:04/:19/:34/:49), due gate 12 min, page clock updated; mention markets re-looked hourly, mention_no up to 15 probes/day (one per event, soonest first). Millisecond trading ruled out (paper can't simulate it; needs co-located servers and real accounts). Waiting to see the first :19/:49 dispatch
- **Evidence:** 143 offline tests OK; wrangler deploy of triggers succeeded
- **Next:** Confirm a :19 or :49 run starts and passes; then the forward test runs on its own (keep/kill after 150 settled mention bets)
- **Git:** master @ af1725f, 2 uncommitted

### 2026-10-10T06:40:50.655Z

- **State:** Maintenance done (4983d0e): B31 records the 15-minute pace; the secrets scan's 20 high-confidence matches checked by hand (URL slugs, 'list bearer' in a news snippet, env-variable names; no secret values). The 06:34Z cycle (run 38031423601) ran the new code at dd0dbbc and passed: mention pass saw 168, looked 23, one new NO probe (KXDEBATEMENTION-26OCT13-FILI); sharp saw 110 games, none inside the 8-hour kickoff window. The first :49 slot (06:49Z) is the next check.
- **Evidence:** run 38031423601 success; scan 2026-10-10T06:35:13Z stats; 143 offline tests OK
- **Next:** Confirm the 06:49Z run starts and passes (watcher in the session); then the mention forward test runs on its own (keep/kill after 150 settled bets)
- **Git:** master @ 79f0957, 2 uncommitted

## Handoff

- **State:** Maintenance done (4983d0e): B31 records the 15-minute pace; the secrets scan's 20 high-confidence matches checked by hand (URL slugs, 'list bearer' in a news snippet, env-variable names; no secret values). The 06:34Z cycle (run 38031423601) ran the new code at dd0dbbc and passed: mention pass saw 168, looked 23, one new NO probe (KXDEBATEMENTION-26OCT13-FILI); sharp saw 110 games, none inside the 8-hour kickoff window. The first :49 slot (06:49Z) is the next check. Evidence: run 38031423601 success; scan 2026-10-10T06:35:13Z stats; 143 offline tests OK.
- **Next:** Confirm the 06:49Z run starts and passes (watcher in the session); then the mention forward test runs on its own (keep/kill after 150 settled bets)
- **Blocked:** nothing
- **Watch out:** Stage by explicit path; tests must never reach The Odds API or write real mentions.jsonl (DataDirTest); the Kalshi walk hitting its 60-page limit is expected (far-dated markets left out)

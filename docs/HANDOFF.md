# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-10 21:16 EDT

- **State:** Edge scan v1 done (20,747 markets): all 10 leads were a look-ahead artifact (markets chosen by final volume pick the winners; the clock was anchored to outcome-dependent closes); the unbiased subset (7,494, mostly sports games) has no cut above zero. v2 (7abb0c6) picks without hindsight and decides 24/72 h before the scheduled occurrence time; running in the background since ~01:40Z (about 3 h). Evidence: v1 summary and the complete-event check (sports YES 2-15c: +46.4% all vs -47.0% unbiased); occurrence identical across markets in 29,297 of 29,482 events; v2 smoke test 33 rows.
- **Next:** When v2 finishes: python3 -I docs/research/scripts/edge_scan.py --summarize; put each lead through an adversarial check (look-ahead and selection, quote quality and capacity, fresh-data replication, mechanism); record in docs/research/CHECKS.md
- **Blocked:** nothing
- **Watch out:** v1 rows (research_data/edge_scan_rows.jsonl) are look-ahead biased: never use them for leads; v2 rows are research_data/edge_scan_rows_v2.jsonl
- **Git:** master @ 7abb0c6, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 01:16 UTC)

## Earlier

### 2026-10-10 19:07 EDT
- **State:** Edge scan running locally (docs/research/scripts/edge_scan.py, 41cdc5e) over 4,552 active non-mention Kalshi series: real bid/ask 24 h and 72 h before close, after fees, split by close date; 469 markets scored so far. B32 closed as verified. Joey: paid tools and data yes, real money only after a strategy is proven (decision 2026-10-10-paid-tools-and-data-yes-real-money-only-6f1a). Evidence: edge scan smoke test: 8 series, 41 markets scored; 151 offline tests OK; maintenance recorded.
- **Next:** When the scan finishes (about 3 h from 22:00Z): python3 -I docs/research/scripts/edge_scan.py --summarize; record the category table and leads in docs/research/CHECKS.md; deepen surviving leads with a series-level history test
- **Blocked:** nothing
- **Watch out:** The scan runs on this Mac (research_data/ is gitignored); a rerun skips markets already scored. With 15-minute cycles the bot alone makes ~4 commits an hour, so Skilliton's 15-commit maintenance nudge comes every few hours
- **Git:** master @ 7925c69, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 23:07 UTC)

### 2026-10-10 17:55 EDT
- **State:** B32 verified live: run 38079351634 (19:19Z, f2a9568) and the cycles after it read 120 kept series in 63-72 s with no errors, skip 193 earnings/Trump series, see 179 markets in 9 kept events; the 30-a-day limit was used up on Oct 10 (resets 00:00Z). 20 earnings-call bets placed before the rule (15 at 18:50Z) are pre-registered as left out of the keep-or-kill count. Joey: 'skin in the game' = paid tools and data, no real money until proven (memory saved). Evidence: run 38079351634 success; scans 21:05Z, 21:20Z, 21:33Z (mention_fetch errors 0, series_skipped 193); 151 offline tests OK; The Odds API pricing page read 2026-10-10 (20K credits /mo).
- **Next:** Joey decides on The Odds API 20K plan ($30/mo) for a fair test of the sharp strategy; if bought, set sharp.refresh_minutes to 15. Mention forward test runs itself; early read with docs/research/scripts/mention_forward.py in 2-3 weeks
- **Blocked:** nothing
- **Watch out:** Stage by explicit path; record files are edited with the Edit tool, not overwritten from the shell; tests never reach Kalshi or The Odds API live; earnings-call bets placed before 19:19Z on 2026-10-10 do not count toward keep-or-kill
- **Git:** master @ d954b29, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 21:55 UTC)

### 2026-10-10 15:19 EDT
- **State:** B32 live: mention reader sees 75 of 76 open events (was 8); bets stop 6 h before the event's own date; lean mention log; settle skips markets before their event; 30 probes a day; earnings-call and Trump series skipped and yes_bias 0.10 after the 7,929-market timing test (+15-18% outside them, both halves; no edge inside). Resting bids tested: no better than taking the ask. Not yet confirmed: the first cycle on ddf5f59 or later (19:19Z). Open question to Joey: does 'skin in the game' mean real money (not built without his explicit ask) or paid tools/data. Evidence: 151 offline tests OK; run 38076336614 success on c39256d (119 series, 67 s, no errors, 4 probes); read-only full pass 455 requests, 75/76 events; mention_timing.py 7,929 markets; mention_maker.py 1,183 markets.
- **Next:** Confirm the 19:19Z cycle (stats mention_fetch.series_skipped > 0, mentions.excluded_series, no errors); then the forward test runs itself (early read: docs/research/scripts/mention_forward.py)
- **Blocked:** nothing; Joey's answer on real money vs paid tools shapes what comes after the forward test
- **Watch out:** Stage by explicit path; record files are edited with the Edit tool, not overwritten from the shell (guardrail); tests must never reach Kalshi or The Odds API live (DataDirTest guards both)
- **Git:** master @ f2a9568, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 19:19 UTC)

### 2026-10-10 02:56 EDT
- **State:** 15-minute schedule verified: the first :49 run (38032277618) passed and committed a cycle at 06:53Z. Found two mention-strategy problems (B32): it sees 8 of the 76 open Kalshi mention events (about 48 settle a week), and its hour-before guard counts from Kalshi's formal close, about 14-15 days after the event, so it could buy during or after an event. No such bet yet. Evidence: run 38032277618 success; scan 2026-10-10T06:50:17Z; Kalshi public API sweep of 454 Mentions series (scratchpad mention_rate.py); close times read for 6 series.
- **Next:** Joey decides B32: (1) policy stopgap mention.min_hours_before 384; (2) history test at the live timing; (3) code to read mention events directly
- **Blocked:** B32 waits for Joey's OK
- **Watch out:** Stage by explicit path; tests must never reach The Odds API or write real mentions.jsonl; Kalshi mention tickers' dates can be stale ('originally scheduled', 'next PMQs')
- **Git:** master @ ef6456f, 3 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 06:56 UTC)

### 2026-10-10 02:40 EDT
- **State:** Maintenance done (4983d0e): B31 records the 15-minute pace; the secrets scan's 20 high-confidence matches checked by hand (URL slugs, 'list bearer' in a news snippet, env-variable names; no secret values). The 06:34Z cycle (run 38031423601) ran the new code at dd0dbbc and passed: mention pass saw 168, looked 23, one new NO probe (KXDEBATEMENTION-26OCT13-FILI); sharp saw 110 games, none inside the 8-hour kickoff window. The first :49 slot (06:49Z) is the next check. Evidence: run 38031423601 success; scan 2026-10-10T06:35:13Z stats; 143 offline tests OK.
- **Next:** Confirm the 06:49Z run starts and passes (watcher in the session); then the mention forward test runs on its own (keep/kill after 150 settled bets)
- **Blocked:** nothing
- **Watch out:** Stage by explicit path; tests must never reach The Odds API or write real mentions.jsonl (DataDirTest); the Kalshi walk hitting its 60-page limit is expected (far-dated markets left out)
- **Git:** master @ 79f0957, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-10 06:40 UTC)

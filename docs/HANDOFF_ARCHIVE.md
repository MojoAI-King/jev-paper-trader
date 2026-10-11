# Handoff archive

Kind: Reference. The current handoff is `docs/HANDOFF.md`.

### 2026-10-11 04:04 EDT
- **State:** Maintenance recorded. Retired strategies off the page and totals (b2225c1). Paid Odds API key pending (sent to a mistyped email; Joey contacting team@the-odds-api.com). Mention forward test running. Evidence: skilliton maintain --apply; secrets scan 21 known false positives; 151 offline tests OK.
- **Next:** When the new key is installed: odds-check for about 20,000 quota, then sharp.refresh_minutes 15; early mention read in 2-3 weeks
- **Blocked:** paid Odds API key waiting on The Odds API support
- **Watch out:** Do not lower sharp.refresh_minutes before the paid key is live
- **Git:** master @ b783afd, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 08:04 UTC)

### 2026-10-11 04:04 EDT
- **State:** Retired strategies removed from the page and its totals (b2225c1): 9 active shown, total about $799k of $900k; jev_alone, jev_alone_bold, ch3, ch6 left out, ledgers kept. Joey bought The Odds API 20K plan but the key went to a mistyped email; he is asking team@the-odds-api.com to revoke and reissue. The trader stays on the free key (269 left) until then. Evidence: 151 offline tests OK; read-only current_summary preview; odds-check quota 269 (free plan still on the .env key).
- **Next:** When Joey installs the new key (.env and gh secret ODDS_API_KEY): run odds-check, confirm about 20,000 quota, set sharp.refresh_minutes to 15; check the page after the next cycle
- **Blocked:** paid Odds API key waiting on The Odds API support
- **Watch out:** Do not lower sharp.refresh_minutes before the paid key is live: 4 sports every 15 min is about 384 requests a day
- **Git:** master @ b2225c1, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 08:04 UTC)

### 2026-10-10 23:56 EDT
- **State:** Maintenance recorded. Edge scan closed with no new edge (weather lead refuted out of sample); mention edge confirmed without hindsight and concentrated in brand-new markets. Mention forward test running. Evidence: skilliton maintain --apply; secrets scan 21 matches, all known false positives; 151 offline tests OK.
- **Next:** Mention forward test runs itself; early read in 2-3 weeks with docs/research/scripts/mention_forward.py, split by market.volume at the look
- **Blocked:** nothing
- **Watch out:** Stage by explicit path; write record files and commit them in separate commands (guardrail)
- **Git:** master @ e28ce47, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 03:56 UTC)

### 2026-10-10 23:55 EDT
- **State:** Edge scan (B33) closed: no new edge. Run 2 (19,960 markets, no hindsight) had 1 lead in 57 cuts; adversarial workflow wf_b31c17a4-a6a refuted it out of sample (weather YES 50-70c: -0.6% on 694 buys Aug-Oct; +0.0% on 872 Apr-Oct). Mention edge survives without final-volume selection (+15.8% unchanged; +13.7% needing 50+ contracts traded first) and sits in brand-new markets (+35.9% when the bet is the first trade, +2.8% otherwise). Mention forward test continues. Evidence: edge_scan.py --summarize on 19,960 rows; workflow wf_b31c17a4-a6a (4 lenses + mention recheck, 6 agents, 0 errors); 151 offline tests OK.
- **Next:** Let the mention forward test run; at the early read (2-3 weeks) split results by market.volume at the look (0 = brand-new market) using docs/research/scripts/mention_forward.py; any next scan samples series across months
- **Blocked:** nothing
- **Watch out:** v1 scan rows are look-ahead biased; weather occurrence_datetime is 14:00Z the morning after the measured day; hurricane occurrence times are written after the fact
- **Git:** master @ 16ae616, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 03:55 UTC)

### 2026-10-10 21:16 EDT
- **State:** Edge scan v1 done (20,747 markets): all 10 leads were a look-ahead artifact (markets chosen by final volume pick the winners; the clock was anchored to outcome-dependent closes); the unbiased subset (7,494, mostly sports games) has no cut above zero. v2 (7abb0c6) picks without hindsight and decides 24/72 h before the scheduled occurrence time; running in the background since ~01:40Z (about 3 h). Evidence: v1 summary and the complete-event check (sports YES 2-15c: +46.4% all vs -47.0% unbiased); occurrence identical across markets in 29,297 of 29,482 events; v2 smoke test 33 rows.
- **Next:** When v2 finishes: python3 -I docs/research/scripts/edge_scan.py --summarize; put each lead through an adversarial check (look-ahead and selection, quote quality and capacity, fresh-data replication, mechanism); record in docs/research/CHECKS.md
- **Blocked:** nothing
- **Watch out:** v1 rows (research_data/edge_scan_rows.jsonl) are look-ahead biased: never use them for leads; v2 rows are research_data/edge_scan_rows_v2.jsonl
- **Git:** master @ 7abb0c6, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 01:16 UTC)

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

### 2026-10-09 18:49 EDT
- **State:** Rebuild phase 1 shipped at 04b8c2a under Joey's blessing (he is away for Shabbat): every strategy but original sizes by measured skill (lambda ~0 for all, so 0.25% probe bets, max 5/day), one stake per event, real price required, Kalshi per-series fee multipliers, review changes at most every 7 days within caps (Kelly 0.5, 3%/bet, 50% open), calibration needs 300. Page deployed (Worker ee378ff7). Live check pending on the 23:04Z cycle. All 14 research reports checked; plan in docs/REBUILD_PLAN.md. Evidence: 131 offline tests OK (SkillSizingTests, Kalshi multiplier test, tuning tests moved to the new limits).
- **Next:** Confirm the 23:04Z cycle: workflow green, scans carry skill, new bets probe for all but original, Kalshi judgments carry fee_multiplier; then report to Joey when he is back. Phase 2 waits: B27 needs his $30 decision; B28-B30 next
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)
- **Git:** master @ 04b8c2a, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 22:49 UTC)

### 2026-10-09 18:09 EDT
- **State:** B25 and B26 done and verified live: page matched build at 21:53Z; cycle 22:09Z published paired n 562, left_out 101; new Polymarket judgments carry fee_rate (0.04, 0.05). No bet since the fix yet, so a fee-charged bet isn't seen live (FeeTests cover it). Archived both. Evidence: background check output (page cmp, origin summary.json, judgments tail); 125 offline tests OK.
- **Next:** Check research reports as Joey calls them done (09, 10, 14, 02, 03, 04, 08, 11, 12, 13 via the helper tab), then write the rebuild plan
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: add report files by name; past Polymarket bets keep their old zero-fee cost (not rewritten)
- **Git:** master @ e4bae17, 14 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 22:09 UTC)

### 2026-10-09 17:53 EDT
- **State:** B26 (each Polymarket market pays its own published taker fee; 0.05 default) and B25 (head-to-head scores only on real-priced markets, left-out count shown) committed at c5f54c2, pushed, page deployed (Worker 996e8d0c). Live check pending: edge cache still served the old page at 21:53Z; the next cycle must write paired.left_out and fee_rate. Reports 01, 05, 06, 07 in and checked; no category skips (losses since the floor are sports and other, not weather or price thresholds). Evidence: 125 offline tests OK (FeeTests, updated paired test); live paired preview 562 markets, 101 left out; Polymarket API feeSchedule seen live (politics 0.04, geopolitics off).
- **Next:** Confirm the live page and the 22:04Z cycle (paired.left_out in summary.json, fee_rate on new Polymarket judgments), then archive B25 and B26 and close the task; keep checking reports as Joey calls them done
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: add report files by name; past Polymarket bets keep their old zero-fee cost (not rewritten)
- **Git:** master @ c5f54c2, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:53 UTC)

### 2026-10-09 17:45 EDT
- **State:** Reports 01, 05, 07 in and checked (docs/research/CHECKS.md): on real-priced markets the price is about calibrated and none of our forecasters adds information; cheap contracts lose ~60%, favourites break even; weather markets are hard to beat. 06 running; 09, 10, 14, 02, 03, 04, 08, 11, 12, 13 handed out by a dispatcher tab from docs/research/prompts/. New: B26 (Polymarket taker fees, trader charges 0). Evidence: event-clustered bootstrap refits on 1,006 real-priced first looks; price-bucket returns by venue; WebFetch of AIA (2511.07678), Kim (2602.21229), Crosier (2609.23969), docs.polymarket.com/trading/fees and Kalshi KXHIGHNY rules; 122 tests OK.
- **Next:** Process each report as Joey says it's done: commit only that file, check it into CHECKS.md, mark the run sheet; then the plan. Joey decides B25 and B26
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: add report files by name, never git add -A; don't commit a report Joey hasn't called done; all tabs draw on Joey's Claude plan
- **Git:** master @ 8bf4adf, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:45 UTC)

### 2026-10-09 17:17 EDT
- **State:** Fourteen narrow research briefs ready; Joey asked for one paste-ready prompt at a time and runs each as its own Claude Code tab with the deep-research skill on Opus 5.5 high. Order given: 01, 05, 06, 07, 09, 10, 14, then 02, 03, 04, 08, 11, 12, 13. Prompts are built from the brief files (scratchpad paste.py). No reports yet. Evidence: briefs committed; README rule fixed so a tab carries on after declining a hook reminder.
- **Next:** Hand Joey the next prompt when he asks; when tabs finish, commit the reports, mark them in the run sheet, check claims against papertrade_data, write the plan
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: never git add -A or commit their half-written reports mid-run; they must not run cycle/scan/settle/review or skilliton; all of them draw on Joey's Claude plan (week 47%, resets Mon 2026-10-12 08:00Z)
- **Git:** master @ 87b85c3, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:17 UTC)

### 2026-10-09 17:16 EDT
- **State:** Fourteen narrow research briefs ready in docs/research/briefs/ (run sheet docs/research/README.md; page https://claude.ai/artifact/2USu1tPk31NdbK2p1vj5ta). Joey runs each as its own Claude Code tab, all at once; each tab writes only docs/research/NN-<slug>.md and does not commit. No reports yet. Evidence: briefs committed at 8d23ab7; 122 offline tests OK; run-sheet page checked once by screenshot.
- **Next:** When the tabs finish: commit the reports, mark them done in the run sheet, check each report's claims against papertrade_data, then write the plan (strategies, backtests to pass, code changes for Joey to approve)
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: never git add -A or commit their half-written reports mid-run; they must not run cycle/scan/settle/review or skilliton; all of them draw on Joey's Claude plan (week 47%, resets Mon 2026-10-12 08:00Z)
- **Git:** master @ 8d23ab7, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:16 UTC)

### 2026-10-09 17:02 EDT
- **State:** Rebuild scoped (B24): every forecaster is less accurate than the market on 327 real-priced finished markets (Claude direct +0.035, Jev+research +0.043, Jev alone +0.073 Brier); trading costs ~8.4% a bet; blend and resting-order fixes tested and rejected. Five research briefs in docs/REBUILD_SCOPE.md, published at https://claude.ai/artifact/2USu1tPk31NdbK2p1vj5ta (private to Joey). Trader unchanged and running. Evidence: backtests on 1,133 finished markets at the 2026-10-09T20:38Z cycle (scratchpad bt.py); 122 offline tests OK; page screenshot checked once before the last edit; copy buttons not tried in the live viewer.
- **Next:** Joey runs briefs 1-5 in claude.ai Research tabs and pastes each report into a session; Claude saves them to docs/research/, does brief 6 (Jev harness) and writes the plan; B25 (score the market only where it has a real price) waits for Joey's yes
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; never build an unattended job that edits or ships code; quote n and ± with every number (small samples misled us twice)
- **Git:** master @ d5ffd6a, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:02 UTC)

### 2026-10-01 22:36 EDT
- **State:** Forecasters panel live and verified (task closed): cycle 2026-10-02T02:36Z wrote calibration.paired, 112 markets: market 0.120, Jev + research 0.185, Claude direct 0.196, Jev alone 0.243; live page screenshot shows it filled. Evidence: summary.json on origin at 3591381; headless screenshot of https://jev-paper-trader.greekgod.workers.dev at 1280px.
- **Next:** Watch the post-floor bets settle (8 close 2026-10-06) vs original; research resumes after the 2026-10-05 08:00Z week reset
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the week meter rose 68 to 82% while the trader made 0-1 calls, so other use on that account is filling it (not verified); never build an unattended job that edits or ships code
- **Git:** master @ 3591381, 4 uncommitted

### 2026-10-01 22:22 EDT
- **State:** Forecasters panel built (engine.paired, page panel under the feed, report lines), p7 approved, committed 3a605d0 and pushed; page shell deployed (Worker version 1e638bb3), live HTML equals the build. Not yet verified: the live panel's numbers, which appear once a cycle on the new code writes summary.json. Evidence: 122 offline tests OK incl. test_forecasters_are_scored_head_to_head_on_the_same_markets; screenshots at 1600, 1280 and a true 400px frame; local paired scores on 111 markets: market 0.119, Jev + research 0.184, Claude direct 0.195, Jev alone 0.241.
- **Next:** Confirm summary.json on origin carries calibration.paired and the live page shows the panel filled; then close the task as verified. Watch the post-floor bets settle (8 close 2026-10-06)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the week meter rose 68 to 82% while the trader made 0-1 calls, so other use on that account is filling it (not verified); never build an unattended job that edits or ships code
- **Git:** master @ 3a605d0, 6 uncommitted

### 2026-10-01 22:15 EDT
- **State:** Answered Joey: is Jev doing anything. Jev alone is near a coin flip (Brier 0.225); Jev + research is our best forecaster (0.177, Claude direct 0.198); the market beats all (0.133). Research stays on Opus (Joey worried Sonnet would hurt). Offered the forecaster scoreboard panel on the page (proposal p7, a code change), waiting for Joey. Evidence: scratchpad jevcheck.py and maxedge.py over 205 resolved markets in papertrade_data; tests OK.
- **Next:** Joey's yes/no on the scoreboard panel (p7); watch the post-floor bets settle (8 close 2026-10-06) vs original; research resumes after the 2026-10-05 08:00Z week reset
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the week meter rose 68 to 82% while the trader made 0-1 calls, so other use on that account is filling it (not verified); never build an unattended job that edits or ships code
- **Git:** master @ 99cac63, 3 uncommitted

### 2026-10-01 21:50 EDT
- **State:** Joey kept the categories (B23 declined, archived). Explained the losses: all 70 settled bets predate the 30c floor; 38 long shots under 30c lost 61.3k of the 62.4k; forecasters expected 38.9 wins, market 21.6, got 18; 36 pre-floor long shots (63k) still open through 2026-10-26; 13 post-floor bets open, none settled. Evidence: portfolio ledgers at 6497235+ (closed and open bets by price paid, claimed edge, opened before/after 2026-10-01T04:19Z); scans.jsonl week meter 0.44 to 0.82, research held by the pace guard since about 14:30Z 2026-10-01.
- **Next:** Watch the first post-floor bets settle (8 close 2026-10-06) vs original; Joey decides if research may spend the rest of the week (pace guard holds it until the 2026-10-05 08:00Z reset)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the week meter rose 68 to 82% while the trader made 0-1 calls, so other use on that account is filling it (not verified); never build an unattended job that edits or ships code
- **Git:** master @ 6497235, 4 uncommitted

### 2026-10-01 21:42 EDT
- **State:** Joey asked about politics only: data says no (worst category, almost no resolutions). Losses since the floor are all pre-floor bets settling (20 settled: 2 won, -26.7k, 17 under 30c); 13 post-floor bets still open. Proposed B23 (skip politics, culture, economy, world), waiting for Joey. Evidence: settled-bet breakdown by category; flat-$100 simulation on every resolved market with the 30c floor, by category and forecaster.
- **Next:** Joey's yes/no on B23; then python3 -m papertrade tune for each strategy but original and push papertrade_data
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 27% at 04:06Z on 2026-09-29, much of it this session's review workflows (resets Mon 3 AM ET); never build an unattended job that edits or ships code (Joey, 2026-09-28)
- **Git:** master @ 60c4177, 2 uncommitted

### 2026-10-01 01:04 EDT
- **State:** Verified: research back on Joey's current Claude account (run 36816087586 at 04:39Z: 10 new research runs, 22 Claude calls, week 41%, 5-hour 40%); 30c floor, 150 research/day with week pace guard, review twice daily, 100 markets/source all live. Ledger audit clean (9 ledgers add up; 32 settled markets match the exchanges; page equals ledgers). Evidence: 121 tests OK; health run success; audit script output.
- **Next:** Check in: bets/wins/losses since 2026-10-01 vs original; what the twice-daily review changed; plan meter vs the pace guard
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 27% at 04:06Z on 2026-09-29, much of it this session's review workflows (resets Mon 3 AM ET); never build an unattended job that edits or ships code (Joey, 2026-09-28)
- **Git:** master @ a1e13d0, 3 uncommitted

### 2026-10-01 00:10 EDT
- **State:** Diagnosed losses (read-only): long shots under 30c caused -32.6k of -35.7k settled; options in BACKLOG B22 put to Joey; nothing changed yet. Claude week 100%: daily review and research paused until Mon 3 AM ET. Evidence: health Healthy 04:04Z 2026-10-01; settled-bet breakdown from papertrade_data/portfolios (50 bets, 32 markets).
- **Next:** Joey's answer on B22: min_ask 0.30 by hand, approve p4/p7, market-shrink code idea
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 27% at 04:06Z on 2026-09-29, much of it this session's review workflows (resets Mon 3 AM ET); never build an unattended job that edits or ships code (Joey, 2026-09-28)
- **Git:** master @ f99f53b, 2 uncommitted

### 2026-09-29 00:07 EDT
- **State:** Verified live: run 36519949032 (04:04Z) on 44b97f1 succeeded; original.json created 04:04:29Z and bet; new bets carry rules_version; decisions record min_edge; summary.json has auto_tune, rule_changes, ideas_for_joey, original slot y; page shell deployed and identical to the build. Evidence: health Healthy at 04:06Z (7 strategies, 4 bets that cycle incl. original 1); 117 tests pass; curl of summary.json and the page.
- **Next:** First daily review at the first cycle after ~2026-09-29 23:12Z: read what it changed and check the page shows it (BACKLOG B21). Joey's open choices B17-B20 still wait; code ideas the loop files wait for his approve/reject (`python3 -m papertrade learn`)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 27% at 04:06Z on 2026-09-29, much of it this session's review workflows (resets Mon 3 AM ET); never build an unattended job that edits or ships code (Joey, 2026-09-28)
- **Git:** master @ 040fef0, 5 uncommitted

### 2026-09-28 21:22 EDT
- **State:** More-action change live and verified: 120 markets pass a cycle, 8 bets on the first cycle, main +$3,378 on its first two wins, early Kalshi results and voids working; the 80-market wave cleared (01:03Z judged 13). Evidence: health Healthy at 01:03Z; 88 tests pass; skilliton maintain run.
- **Next:** After a day: measure bets/day, research use and deferred, then decide B16 (markets_per_source ~100). Joey's open choices: B17 one bet per event, B18 scoring, B19 page additions, B20 weekly Claude guard (week 19% at 01:03Z, much of it this session's analysis)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ 6009b40, 2 uncommitted

### 2026-09-28 19:14 EDT
- **State:** Verified on GitHub: 23:04Z cycle ran the new code (Kalshi 35 pages/61s, 120 passing, 8 bets, 7 early Kalshi results + 5 voids, first retro). Evidence: run 36495992909 success 8m26s; health Healthy; scans.jsonl funnel.fetch recorded; 88 tests pass.
- **Next:** Watch deferred fall to 0 over the next cycles; after a day, measure bets/day and research use, then decide B16 (markets_per_source 100); options B17-B20 wait for Joey
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ e8a91da, 4 uncommitted

### 2026-09-28 17:37 EDT
- **State:** Kalshi links fixed and verified live (21:36Z summary: 0 old-form, 39 new-form; a repaired link opens its event in Chrome); open-bet cap 50% (Bold now 19 open, past the old 30%); research 60/day. Evidence: 73 tests pass; run 21:34Z success; health Healthy; plan week 5%, 5-hour 12%.
- **Next:** Watch a day of cycles: research should run past 5 AM ET and main/Claude direct should bet more; if research goes unused, BACKLOG B16 (widen markets_per_source); B3, B15, B13 queued
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ 41082cd, 6 uncommitted

### 2026-09-27 15:02 EDT
- **State:** Page back at 1x everywhere (Worker 5536aa80, live checked); main's Headline tag dropped in policy.json, hover blurbs say Jev + Claude. Evidence: 72 tests pass; live page byte-equal to the new build, no zoom rules; tag leaves the page at the next cycle's summary.json.
- **Next:** Next cycle (~19:04 UTC) regenerates summary.json without the tag; then nothing queued beyond BACKLOG B3, B15, B13
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ 9b395f9, 4 uncommitted

### 2026-09-27 14:51 EDT
- **State:** Challengers now start by themselves within bounds (max 2 running); opposing bets and thin markets stay allowed; trading automatic every ~30 min; 16 open bets, none settled. Evidence: 72 tests pass incl. auto-start, bounds and free-slot tests; decision 2026-09-27-challengers-start-by-themselves-opposing-4dc1.
- **Next:** First results around midnight ET feed reviews, the coach and calibration; first weekly retrospective after 10 reviewed markets may start challengers; improvements queued: B3 (linked probabilities fit together), B15 (fill size vs market depth), B13 (phone layout)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ b475bda, 16 uncommitted

### 2026-09-27 14:47 EDT
- **State:** Trading automatically every ~30 min via the Cloudflare trigger (verified 18:04/18:34 UTC); 5 strategies, 16 open bets, none settled; learning loop merged and running in every cycle (playbook v0, 0 resolved); mission-control page live with settled vs not-settled money, plain strategy names, chart floor of +/-5%, big-monitor scaling. Evidence: 72 tests pass; runs 36339317403 and 36341181637 started by Cloudflare; live page checked by request and headless Chrome at 1440x900 and 2550x1281.
- **Next:** First results around midnight ET feed the review, coach and calibration loops; Joey to decide B3 (no contradicting bets in one event), B14 (thin-market filter), B12 (auto-start challengers); phone layout later (B13)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the GitHub dispatch token lives only as a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ 63b4576, 9 uncommitted

### 2026-09-27 14:36 EDT
- **State:** Automatic: Cloudflare trigger started runs 36339317403 (18:04 UTC, skipped by the 25-minute gate) and 36341181637 (18:34 UTC, full cycle, 1 bold bet) on its own after Joey set GITHUB_DISPATCH_TOKEN; mission-control page live. Evidence: wrangler secret list shows GITHUB_DISPATCH_TOKEN; both runs are workflow_dispatch with nobody starting them; run logs show the gate message and the funnel.
- **Next:** Check in with python3 -m papertrade health or the page; first results arrive as markets close (first one around midnight ET); linked-market contradictions (B3) are the next improvement; phone layout later (B13)
- **Blocked:** nothing
- **Watch out:** The GitHub token expires in a year (docs/OPERATIONS.md); GitHub's own schedule stays unreliable and is only a backup; Claude plan week at 81%, resets Mon 3 AM ET
- **Git:** master @ d8b0fe6, 2 uncommitted

### 2026-09-27 12:45 EDT
- **State:** Mission-control page live (Worker 4c6ee8a0); Kalshi 4 requests/fetch, 120 markets fetched in run 36333603111 where main placed its first bet; Cloudflare cron trigger deployed at :04/:34 but idle until GITHUB_DISPATCH_TOKEN is set; GitHub schedule (backup) skipped every slot today. Evidence: Run 36333603111: 120 fetched, 0 errors, bets main 1 claude_direct 1 bold 5; 72 tests pass; live page checked in headless Chrome 1440x900 with the 12:32 ET data; health: Healthy.
- **Next:** Joey sets GITHUB_DISPATCH_TOKEN (docs/OPERATIONS.md 'What starts a cycle'); then confirm a run lands at the next :04/:34 and the page updates; phone layout later (B13)
- **Blocked:** Automatic cycles wait on Joey's token (B1)
- **Watch out:** Until the token is set, cycles only run when GitHub's schedule fires or someone runs gh workflow run; never put the token in chat or a file; the Mac background job was removed (permission check: unapproved persistence)
- **Git:** master @ d6640f6, 3 uncommitted

### 2026-09-27 11:59 EDT
- **State:** Live and trading: 5 fake-$100k strategies (main, Jev alone, Claude direct, bold, self-calibrating); bold placed 7 bets in run 36329790430; learning loop merged (87801e5); page redesign on branch page-redesign (a0cd87e), private preview https://claude.ai/artifact/TP84qLCdrVPHPnRaBTcEAf. Evidence: 71 tests pass; 5 new guards fail when switched off; run 36329790430 success (bold 7 bets); 390px iframe check of the new page.
- **Next:** Confirm a scheduled (cron) run lands at :23 and runs the learning-loop code (python3 -m papertrade health); ship the page redesign when Joey OKs it (BACKLOG B11); if cron keeps skipping, B10
- **Blocked:** Page redesign ships on Joey's OK
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer (no cycles on the Mac); weekly research pause lifted, so a full week also blocks Joey's own Claude until the Monday 3 AM ET reset; auto_start_challengers stays false until Joey decides (B12)
- **Git:** master @ 3574102, 5 uncommitted

### 2026-09-27 11:01 EDT
- **State:** Live: hourly GitHub runs (Claude on the Claude Max plan via CLAUDE_CODE_OAUTH_TOKEN, never an API key) trade three fake-$100k strategies (Jev+research, Jev alone, Claude direct); page https://jev-paper-trader.greekgod.workers.dev reads papertrade_data/summary.json from the public repo MojoAI-King/jev-paper-trader; no bets yet (Jev's info score stays under 0.5). Evidence: 53 offline tests pass; price-leak tests fail with the screen off; GitHub run 36326789989 succeeded (40 judged, 13 with research, ledgers committed a96cbb8); live page and GitHub summary.json checked by plain request and headless Chrome.
- **Next:** Confirm the next scheduled hourly runs land (Actions tab); after a few days, review price-screen drops (8 of 53 facts dropped by the price-match rule, likely polls) and decide whether to narrow it; consider making linked markets' probabilities add up (Lula 38% + Bolsonaro 23%) as a challenger strategy
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY anywhere (it switches Claude to paid API billing; research refuses to run); don't run cycles on the Mac while GitHub runs them (two writers); Claude plan weekly usage 78% (research pauses at 85%, resets Mon 3 AM ET); pause trading with: gh variable set TRADING_ENABLED --body false --repo MojoAI-King/jev-paper-trader
- **Git:** master @ 438d284, 6 uncommitted

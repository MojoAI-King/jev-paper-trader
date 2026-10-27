# Task: Mention NO strategy: live forward test

Kind: Living. Task record.

- **ID:** 2026-10-10-mention-no-strategy-live-forward-test-aaec
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-27T00:08:55.550Z

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

### 2026-10-10T06:56:34.229Z

- **State:** 15-minute schedule verified: the first :49 run (38032277618) passed and committed a cycle at 06:53Z. Found two mention-strategy problems (B32): it sees 8 of the 76 open Kalshi mention events (about 48 settle a week), and its hour-before guard counts from Kalshi's formal close, about 14-15 days after the event, so it could buy during or after an event. No such bet yet.
- **Evidence:** run 38032277618 success; scan 2026-10-10T06:50:17Z; Kalshi public API sweep of 454 Mentions series (scratchpad mention_rate.py); close times read for 6 series
- **Next:** Joey decides B32: (1) policy stopgap mention.min_hours_before 384; (2) history test at the live timing; (3) code to read mention events directly
- **Git:** master @ ef6456f, 3 uncommitted

### 2026-10-11T03:55:22.541Z

- **State:** Edge scan (B33) closed: no new edge. Run 2 (19,960 markets, no hindsight) had 1 lead in 57 cuts; adversarial workflow wf_b31c17a4-a6a refuted it out of sample (weather YES 50-70c: -0.6% on 694 buys Aug-Oct; +0.0% on 872 Apr-Oct). Mention edge survives without final-volume selection (+15.8% unchanged; +13.7% needing 50+ contracts traded first) and sits in brand-new markets (+35.9% when the bet is the first trade, +2.8% otherwise). Mention forward test continues.
- **Evidence:** edge_scan.py --summarize on 19,960 rows; workflow wf_b31c17a4-a6a (4 lenses + mention recheck, 6 agents, 0 errors); 151 offline tests OK
- **Next:** Let the mention forward test run; at the early read (2-3 weeks) split results by market.volume at the look (0 = brand-new market) using docs/research/scripts/mention_forward.py; any next scan samples series across months
- **Git:** master @ 16ae616, 2 uncommitted

### 2026-10-11T03:56:15.594Z

- **State:** Maintenance recorded. Edge scan closed with no new edge (weather lead refuted out of sample); mention edge confirmed without hindsight and concentrated in brand-new markets. Mention forward test running.
- **Evidence:** skilliton maintain --apply; secrets scan 21 matches, all known false positives; 151 offline tests OK
- **Next:** Mention forward test runs itself; early read in 2-3 weeks with docs/research/scripts/mention_forward.py, split by market.volume at the look
- **Git:** master @ e28ce47, 2 uncommitted

### 2026-10-11T08:04:08.730Z

- **State:** Retired strategies removed from the page and its totals (b2225c1): 9 active shown, total about $799k of $900k; jev_alone, jev_alone_bold, ch3, ch6 left out, ledgers kept. Joey bought The Odds API 20K plan but the key went to a mistyped email; he is asking team@the-odds-api.com to revoke and reissue. The trader stays on the free key (269 left) until then.
- **Evidence:** 151 offline tests OK; read-only current_summary preview; odds-check quota 269 (free plan still on the .env key)
- **Next:** When Joey installs the new key (.env and gh secret ODDS_API_KEY): run odds-check, confirm about 20,000 quota, set sharp.refresh_minutes to 15; check the page after the next cycle
- **Git:** master @ b2225c1, 2 uncommitted

### 2026-10-11T08:04:44.694Z

- **State:** Maintenance recorded. Retired strategies off the page and totals (b2225c1). Paid Odds API key pending (sent to a mistyped email; Joey contacting team@the-odds-api.com). Mention forward test running.
- **Evidence:** skilliton maintain --apply; secrets scan 21 known false positives; 151 offline tests OK
- **Next:** When the new key is installed: odds-check for about 20,000 quota, then sharp.refresh_minutes 15; early mention read in 2-3 weeks
- **Git:** master @ b783afd, 2 uncommitted

### 2026-10-11T14:26:02.955Z

- **State:** Paid Odds API plan live: GitHub secret updated 14:16Z, quota 19,996 after run 38146719378; sharp lines refresh every 15 min (8ec89f6). Sharp matched 0 of 68 games because it only sees the up-to-40 markets due a Jev look; a dedicated sharp pass is proposed and waits for Joey's OK. Mention forward test running.
- **Evidence:** run 38146719378 success (sharp quota_left 19996, matched 0); 151 offline tests OK; skilliton maintain --apply
- **Next:** On Joey's yes: build a sharp pass over every fetched game market each cycle (tests first), push, confirm matches in the next cycle
- **Git:** master @ 51a829a, 2 uncommitted

### 2026-10-11T14:57:01.851Z

- **State:** Sharp pass live (5504147): run 38148752927 matched 6 games (was 0), all decided outside Jev, prices within ~1c of Pinnacle so no bets. Matcher bug fixed (4499823): a touchdown prop had been priced with a team moneyline; that bet is left out of the sharp evaluation. Jev measured: Brier 0.247 alone, 0.217 with research, vs the market's 0.160 on 657 real-priced markets; skill beyond price negative for every forecaster. First-trade scan across all categories running (docs/research/scripts/first_trade_scan.py).
- **Evidence:** 152 offline tests OK; run 38148752927 success (sharp matched 6, decided_outside_jev 6); engine.skill and engine.paired read-only
- **Next:** When the first-trade scan finishes: --summarize, check leads adversarially, record in CHECKS.md; Joey decides whether Jev keeps picking bets
- **Git:** master @ 4499823, 4 uncommitted

### 2026-10-11T16:45:54.043Z

- **State:** Jev retired as a picker (6632112): main, bold, calibrated, ch13 retired; learning.retired_probabilities blocks new Jev challengers; run 38156043216 clean. First-trade scan done (27,294 markets): 4 leads in 107 cuts, all Economics NO 50-85c (first trade +37.0% at 50-70c, 44 events); adversarial workflow wf_79340bda-9e0 running, including a listing-quote test of the mention 'be first in' idea.
- **Evidence:** 154 offline tests OK; run 38156043216 success (no Jev bets; sharp matched 3); first_trade_scan.py --summarize
- **Next:** Read the workflow verdicts; record the first-trade results in docs/research/CHECKS.md; decide (with evidence) whether mention bets should be limited to untraded markets; ch16 and claude_direct await Joey
- **Git:** master @ 84ca766, 2 uncommitted

### 2026-10-11T16:46:44.045Z

- **State:** Maintenance recorded (b690134). Jev retired as a picker and live (run 38156043216 clean). Workflow wf_79340bda-9e0 verifying the Economics first-trade lead and the mention listing-quote rule; results pending.
- **Evidence:** 154 offline tests OK; skilliton maintain --apply; secrets scan 21 known false positives
- **Next:** Read wf_79340bda-9e0 verdicts; record in docs/research/CHECKS.md; act only on what survives
- **Git:** master @ b690134, 2 uncommitted

### 2026-10-11T17:09:16.348Z

- **State:** Claude retired as a picker too (df3ccd9): claude_direct and ch16 retired; claude_direct in learning.retired_probabilities. Run 38158120513 clean: only original, sharp, mention_no decide; page shows those 3. Workflow wf_79340bda-9e0 (economics first-trade lead, mention listing-quote rule) still running.
- **Evidence:** 154 offline tests OK; run 38158120513 success; summary.json strategies original, sharp, mention_no
- **Next:** Read wf_79340bda-9e0 verdicts; record in docs/research/CHECKS.md; act only on what survives
- **Git:** master @ fc6d170, 2 uncommitted

### 2026-10-11T17:52:47.636Z

- **State:** Workflow wf_79340bda-9e0 done: Economics lead refuted for a first mover (AAA gas in a falling week; quote-based -2.7% on 494 unseen events). Mention edge at quoted prices +0.5% [-10.2, +11.3] (779 buys), so expected about break-even; page blurb and registry corrected (17b920a); forward test stands. New hypothesis under test: follow the informed first trade at quoted prices (workflow wf_629049c4-764).
- **Evidence:** wf_79340bda-9e0: 6 agents, 0 errors; 154 offline tests OK
- **Next:** Read wf_629049c4-764 (follow-first-trade); record in CHECKS.md; if a rule survives, propose a forward test to Joey (code change)
- **Git:** master @ 17b920a, 2 uncommitted

### 2026-10-11T18:02:19.471Z

- **State:** Forward tests locked (1fad555): learning.locked_strategies sharp, mention_no; run 38162056755 clean. Follow-the-first-trade test (wf_629049c4-764) still running.
- **Evidence:** 155 offline tests OK; run 38162056755 success
- **Next:** Read wf_629049c4-764 results; record in CHECKS.md; propose a forward test to Joey only if a rule survives the review
- **Git:** master @ 1fad555, 2 uncommitted

### 2026-10-12T01:04:41.059Z

- **State:** Follow-first-trade tested at quoted prices (7b455a6; the workflow attempt hit the plan's session limit, redone as a script): following a NO first trade in new mention markets +18.1% [-1.3, +35.1] at 15 min (108 buys, 62 events, both halves positive; +16% to +21% at 1-60 min); following YES -4% to -25%; placebo NO about 0. Proposed to Joey: a new paper strategy mention_follow (code change). Live: 27 cycles since 18:05Z, one transient Kalshi 504; the touchdown-prop sharp bet settled -249.55 (excluded); mention_no 32 open.
- **Evidence:** follow_first_trade.py --summarize on 2,306 markets; 155 offline tests OK
- **Next:** On Joey's yes: pre-register mention_follow in EXPERIMENTS.md, build it (first-trade side via the trades endpoint, NO at the quoted ask within the next cycle), tests, lock it
- **Git:** master @ 7b455a6, 2 uncommitted

### 2026-10-12T02:42:38.282Z

- **State:** Live on Joey's standing permission (2026-10-12): original retired; mention_follow built, hardened after an adversarial review (wf_d1c03f32-477), pre-registered and locked; no Jev or research calls when nothing uses them (jev_used false, judged 0); Kalshi 504 fix (15286af): run 38196326048 read 58 pages with no error (was 5), sharp matched 7 games. Follow research rerun with full-precision ordering: +18.1% at 15 min holds.
- **Evidence:** 161 offline tests OK; runs 38195337805 and 38196326048 success; read-only live walk 32 pages no error; kalshi_first_trade live check on 3 markets
- **Next:** Let sharp, mention_no and mention_follow run; early read on the mention strategies in 2-3 weeks (mention_forward.py); next research: follow-first-trade in other families (gas ladders) at quoted prices
- **Git:** master @ 6677104, 0 tracked uncommitted, 2 untracked

### 2026-10-12T05:02:53.502Z

- **State:** Session closed by Joey. Live: sharp (paid odds, own pass, Kalshi walk fixed), mention_no and mention_follow (both pre-registered and locked); all forecaster strategies and original retired; no Jev or research calls. Maintenance recorded.
- **Evidence:** 161 offline tests OK; run 38196326048 success; skilliton maintain --apply
- **Next:** Check-in in about a week (around Oct 19): trading-health, settled mention bets, mention_forward.py early read; next research: follow-first-trade in gas ladders at quoted prices
- **Git:** master @ 8d775c5, 0 tracked uncommitted, 2 untracked

### 2026-10-15T00:37:44.842Z

- **State:** Automatic checkpoint before compaction (auto), written by the PreCompact hook from the snapshot and not by the assistant: branch master at 4d531154b2aa, 0 tracked uncommitted, 2 untracked. The newest checkpoint before this one is 2026-10-12T05:02:53.502Z: Session closed by Joey. Live: sharp (paid odds, own pass, Kalshi walk fixed), mention_no and mention_follow (both pre-registered and locked); all forecaster ...
- **Evidence:** snapshot 2026-10-15T00-37-44-842Z-auto.json under <git dir>/skilliton/snapshots; no gate recorded for that tree (dirty)
- **Next:** Carry on from the last recorded next step: Check-in in about a week (around Oct 19): trading-health, settled mention bets, mention_forward.py early read; next research: follow-first-trade in gas ladders at quoted prices
- **Git:** master @ 4d53115, 0 tracked uncommitted, 2 untracked

### 2026-10-15T00:39:58.647Z

- **State:** Automatic checkpoint at a stop, written by the Stop hook from the working tree (checkpoints.auto) and not by the assistant: branch master at 932c49a4d893, 1 tracked uncommitted, 2 untracked. The newest checkpoint before this one is 2026-10-15T00:37:44.842Z: Automatic checkpoint before compaction (auto), written by the PreCompact hook from the snapshot and not by the assistant: branch master at 4d531154b2aa, 0 tr...
- **Evidence:** read at the stop; no gate recorded for that tree (dirty)
- **Next:** No next step was recorded; read git status and this record.
- **Git:** master @ 932c49a, 1 tracked uncommitted, 2 untracked

### 2026-10-15T00:43:35.219Z

- **State:** Read-only check 2026-10-15: all healthy. sharp placed no bets since the Oct 11 fix: 60 looks at 27 games, Kalshi mid within ~1c of Pinnacle (median), best edge after fees +0.5% vs the 3% gate. mention_no 36 open probes (12 settled, +168), mention_follow 7 open probes (1 settled, -20).
- **Evidence:** python3 -m papertrade health (cycle 00:35Z healthy); sharp.jsonl and portfolios/*.json read at 932c49a
- **Next:** Oct 19 check-in: trading-health, settled mention bets, mention_forward.py early read; test whether Kalshi game lines lag Pinnacle moves (Odds API historical snapshots vs Kalshi 1-min candles) before any faster sharp cadence; then follow-first-trade in gas ladders
- **Git:** master @ 932c49a, 2 tracked uncommitted, 3 untracked

### 2026-10-15T01:08:26.663Z

- **State:** Sharp's touchdown-prop bug bet canceled and refunded through the cycle (policy.json cancelled_bets, engine.cancel_bets): sharp at 100,000, 0 settled, 1 canceled. Live total about +148. Strategies otherwise unchanged; all healthy.
- **Evidence:** 163 offline tests OK; 6489a01 pushed; cycle 3319ddd (01:08Z) applied it; python3 -m papertrade health
- **Next:** Oct 19 check-in: trading-health, settled mention bets, mention_forward.py early read; test whether Kalshi game lines lag Pinnacle moves (Odds API historical vs Kalshi 1-min candles); then follow-first-trade in gas ladders
- **Git:** master @ 3319ddd, 1 tracked uncommitted, 3 untracked

### 2026-10-26T23:26:56.144Z

- **State:** Automatic checkpoint before compaction (auto), written by the PreCompact hook from the snapshot and not by the assistant: branch master at a54bfa4353af, 0 tracked uncommitted, 2 untracked. The newest checkpoint before this one is 2026-10-15T01:08:26.663Z: Sharp's touchdown-prop bug bet canceled and refunded through the cycle (policy.json cancelled_bets, engine.cancel_bets): sharp at 100,000, 0 settled, 1 canc...
- **Evidence:** snapshot 2026-10-26T23-26-56-144Z-auto.json under <git dir>/skilliton/snapshots; no gate recorded for that tree (dirty)
- **Next:** Carry on from the last recorded next step: Oct 19 check-in: trading-health, settled mention bets, mention_forward.py early read; test whether Kalshi game lines lag Pinnacle moves (Odds API historical vs Kalshi 1-min candles); then follow-first-trade in gas ladders
- **Git:** master @ a54bfa43, 0 tracked uncommitted, 2 untracked

### 2026-10-26T23:35:56.910Z

- **State:** Automatic checkpoint before compaction (auto), written by the PreCompact hook from the snapshot and not by the assistant: branch master at a54bfa4353af, 4 tracked uncommitted, 2 untracked. The newest checkpoint before this one is 2026-10-26T23:26:56.144Z: Automatic checkpoint before compaction (auto), written by the PreCompact hook from the snapshot and not by the assistant: branch master at a54bfa4353af, 0 tr...
- **Evidence:** snapshot 2026-10-26T23-35-56-910Z-auto.json under <git dir>/skilliton/snapshots; no gate recorded for that tree (dirty)
- **Next:** No next step was recorded before compaction; read git status and this record, then record a checkpoint.
- **Git:** master @ a54bfa43, 4 tracked uncommitted, 2 untracked

### 2026-10-26T23:40:24.097Z

- **State:** New for-fun strategy 'favorites' live: heavy favorites 90-97c settling within 5 days, 1.5% flat bets, up to 40 a day; hard caps 3% and 50/day in code; locked. Safe strategies unchanged.
- **Evidence:** 166 offline tests OK; commit 4dcbdf5 pushed to master
- **Next:** Confirm favorites places bets on the next cycle (health, portfolios/favorites.json); Oct check-in: settled mention bets, mention_forward early read; Kalshi-vs-Pinnacle lag test
- **Git:** master @ 4dcbdf5a, 0 tracked uncommitted, 2 untracked

### 2026-10-27T00:05:22.831Z

- **State:** Automatic checkpoint before compaction (auto), written by the PreCompact hook from the snapshot and not by the assistant: branch master at 4a1b7e836628, 4 tracked uncommitted, 3 untracked. The newest checkpoint before this one is 2026-10-26T23:40:24.097Z: New for-fun strategy 'favorites' live: heavy favorites 90-97c settling within 5 days, 1.5% flat bets, up to 40 a day; hard caps 3% and 50/day in code; locke...
- **Evidence:** snapshot 2026-10-27T00-05-22-831Z-auto.json under <git dir>/skilliton/snapshots; no gate recorded for that tree (dirty)
- **Next:** Carry on from the last recorded next step: Confirm favorites places bets on the next cycle (health, portfolios/favorites.json); Oct check-in: settled mention bets, mention_forward early read; Kalshi-vs-Pinnacle lag test
- **Git:** master @ 4a1b7e83, 4 tracked uncommitted, 3 untracked

### 2026-10-27T00:08:55.550Z

- **State:** Fun bot review fixes committed: Polymarket books read before betting, no canceled re-buys, daily limit counts settled/canceled, page marks ignore pre-bet prices, $500 minimum bet
- **Evidence:** python3 -m unittest discover -s tests -t .: 171 OK; mutation check: 4 new tests fail without fixes; commit dd988c0c
- **Next:** Watch next cycle: no favorites bet under $500, Polymarket sizes respected, page loss gone; Oct check-in; Kalshi-vs-Pinnacle lag test
- **Git:** master @ dd988c0c, 2 tracked uncommitted, 3 untracked

## Handoff

- **State:** Fun bot review fixes committed: Polymarket books read before betting, no canceled re-buys, daily limit counts settled/canceled, page marks ignore pre-bet prices, $500 minimum bet. Evidence: python3 -m unittest discover -s tests -t .: 171 OK; mutation check: 4 new tests fail without fixes; commit dd988c0c.
- **Next:** Watch next cycle: no favorites bet under $500, Polymarket sizes respected, page loss gone; Oct check-in; Kalshi-vs-Pinnacle lag test
- **Blocked:** nothing
- **Watch out:** Score backtests at quotes the strategy could take; a 15-min cadence cannot win a speed race against Kalshi market makers; cancel only bets a named bug placed; a stash holds a reformatted policy.json to discard

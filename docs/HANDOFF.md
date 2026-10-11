# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-11 04:04 EDT

- **State:** Maintenance recorded. Retired strategies off the page and totals (b2225c1). Paid Odds API key pending (sent to a mistyped email; Joey contacting team@the-odds-api.com). Mention forward test running. Evidence: skilliton maintain --apply; secrets scan 21 known false positives; 151 offline tests OK.
- **Next:** When the new key is installed: odds-check for about 20,000 quota, then sharp.refresh_minutes 15; early mention read in 2-3 weeks
- **Blocked:** paid Odds API key waiting on The Odds API support
- **Watch out:** Do not lower sharp.refresh_minutes before the paid key is live
- **Git:** master @ b783afd, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 08:04 UTC)

## Earlier

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

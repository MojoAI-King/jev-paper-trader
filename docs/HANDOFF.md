# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-11 12:45 EDT

- **State:** Jev retired as a picker (6632112): main, bold, calibrated, ch13 retired; learning.retired_probabilities blocks new Jev challengers; run 38156043216 clean. First-trade scan done (27,294 markets): 4 leads in 107 cuts, all Economics NO 50-85c (first trade +37.0% at 50-70c, 44 events); adversarial workflow wf_79340bda-9e0 running, including a listing-quote test of the mention 'be first in' idea. Evidence: 154 offline tests OK; run 38156043216 success (no Jev bets; sharp matched 3); first_trade_scan.py --summarize.
- **Next:** Read the workflow verdicts; record the first-trade results in docs/research/CHECKS.md; decide (with evidence) whether mention bets should be limited to untraded markets; ch16 and claude_direct await Joey
- **Blocked:** nothing
- **Watch out:** Trade-conditioned 'first trade' results can come from the first trader's own choice; only a listing-quote test shows what we get by trading first
- **Git:** master @ 84ca766, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 16:45 UTC)

## Earlier

### 2026-10-11 10:57 EDT
- **State:** Sharp pass live (5504147): run 38148752927 matched 6 games (was 0), all decided outside Jev, prices within ~1c of Pinnacle so no bets. Matcher bug fixed (4499823): a touchdown prop had been priced with a team moneyline; that bet is left out of the sharp evaluation. Jev measured: Brier 0.247 alone, 0.217 with research, vs the market's 0.160 on 657 real-priced markets; skill beyond price negative for every forecaster. First-trade scan across all categories running (docs/research/scripts/first_trade_scan.py). Evidence: 152 offline tests OK; run 38148752927 success (sharp matched 6, decided_outside_jev 6); engine.skill and engine.paired read-only.
- **Next:** When the first-trade scan finishes: --summarize, check leads adversarially, record in CHECKS.md; Joey decides whether Jev keeps picking bets
- **Blocked:** nothing
- **Watch out:** First-trade scan rows: research_data/first_trade_rows.jsonl; local .env still has the old free Odds API key
- **Git:** master @ 4499823, 4 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 14:57 UTC)

### 2026-10-11 10:26 EDT
- **State:** Paid Odds API plan live: GitHub secret updated 14:16Z, quota 19,996 after run 38146719378; sharp lines refresh every 15 min (8ec89f6). Sharp matched 0 of 68 games because it only sees the up-to-40 markets due a Jev look; a dedicated sharp pass is proposed and waits for Joey's OK. Mention forward test running. Evidence: run 38146719378 success (sharp quota_left 19996, matched 0); 151 offline tests OK; skilliton maintain --apply.
- **Next:** On Joey's yes: build a sharp pass over every fetched game market each cycle (tests first), push, confirm matches in the next cycle
- **Blocked:** sharp pass waits for Joey's yes
- **Watch out:** Local .env still has the old free Odds API key; only GitHub has the paid one
- **Git:** master @ 51a829a, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 14:26 UTC)

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

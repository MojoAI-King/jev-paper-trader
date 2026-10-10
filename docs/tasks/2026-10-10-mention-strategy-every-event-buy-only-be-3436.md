# Task: Mention strategy: every event, buy only before the event, more data (B32)

Kind: Living. Task record.

- **ID:** 2026-10-10-mention-strategy-every-event-buy-only-be-3436
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-10T21:55:18.586Z

## Request

ok yes increase your steps and get more and more data collected and have a can do attitude and relentless pursuit of winning at the game of making money in prediction market gambling

## Acceptance criteria

- [ ] History test at the live timing on every Kalshi Mentions series (settled, volume 200+): NO at 30-70c by time before the event, after fees, event-clustered 95% ranges, recorded in docs/research/CHECKS.md
- [ ] The trader reads every open Kalshi mention event each cycle (coverage checked against a direct sweep), within about 90 small requests a cycle
- [ ] The mention strategy never buys on or after its event day: the guard uses the event's own date (occurrence time, the event's 'On <date>', the ticker date), and a market with no known date gets no bet
- [ ] The mention log stays small: no rules text per look, a market is logged when first seen, when bet, or after a price move, not every hour
- [ ] Offline tests cover the fetch, the guard and the logging with no network; the full suite passes; docs (EXPERIMENTS, DECISIONS, OPERATIONS, CHECKS) updated

## Decisions

not yet written

## Checkpoints

### 2026-10-10T19:19:45.228Z

- **State:** B32 live: mention reader sees 75 of 76 open events (was 8); bets stop 6 h before the event's own date; lean mention log; settle skips markets before their event; 30 probes a day; earnings-call and Trump series skipped and yes_bias 0.10 after the 7,929-market timing test (+15-18% outside them, both halves; no edge inside). Resting bids tested: no better than taking the ask. Not yet confirmed: the first cycle on ddf5f59 or later (19:19Z). Open question to Joey: does 'skin in the game' mean real money (not built without his explicit ask) or paid tools/data.
- **Evidence:** 151 offline tests OK; run 38076336614 success on c39256d (119 series, 67 s, no errors, 4 probes); read-only full pass 455 requests, 75/76 events; mention_timing.py 7,929 markets; mention_maker.py 1,183 markets
- **Next:** Confirm the 19:19Z cycle (stats mention_fetch.series_skipped > 0, mentions.excluded_series, no errors); then the forward test runs itself (early read: docs/research/scripts/mention_forward.py)
- **Git:** master @ f2a9568, 2 uncommitted

### 2026-10-10T21:55:18.586Z

- **State:** B32 verified live: run 38079351634 (19:19Z, f2a9568) and the cycles after it read 120 kept series in 63-72 s with no errors, skip 193 earnings/Trump series, see 179 markets in 9 kept events; the 30-a-day limit was used up on Oct 10 (resets 00:00Z). 20 earnings-call bets placed before the rule (15 at 18:50Z) are pre-registered as left out of the keep-or-kill count. Joey: 'skin in the game' = paid tools and data, no real money until proven (memory saved).
- **Evidence:** run 38079351634 success; scans 21:05Z, 21:20Z, 21:33Z (mention_fetch errors 0, series_skipped 193); 151 offline tests OK; The Odds API pricing page read 2026-10-10 (20K credits /mo)
- **Next:** Joey decides on The Odds API 20K plan ($30/mo) for a fair test of the sharp strategy; if bought, set sharp.refresh_minutes to 15. Mention forward test runs itself; early read with docs/research/scripts/mention_forward.py in 2-3 weeks
- **Git:** master @ d954b29, 2 uncommitted

## Handoff

- **State:** B32 verified live: run 38079351634 (19:19Z, f2a9568) and the cycles after it read 120 kept series in 63-72 s with no errors, skip 193 earnings/Trump series, see 179 markets in 9 kept events; the 30-a-day limit was used up on Oct 10 (resets 00:00Z). 20 earnings-call bets placed before the rule (15 at 18:50Z) are pre-registered as left out of the keep-or-kill count. Joey: 'skin in the game' = paid tools and data, no real money until proven (memory saved). Evidence: run 38079351634 success; scans 21:05Z, 21:20Z, 21:33Z (mention_fetch errors 0, series_skipped 193); 151 offline tests OK; The Odds API pricing page read 2026-10-10 (20K credits /mo).
- **Next:** Joey decides on The Odds API 20K plan ($30/mo) for a fair test of the sharp strategy; if bought, set sharp.refresh_minutes to 15. Mention forward test runs itself; early read with docs/research/scripts/mention_forward.py in 2-3 weeks
- **Blocked:** nothing
- **Watch out:** Stage by explicit path; record files are edited with the Edit tool, not overwritten from the shell; tests never reach Kalshi or The Odds API live; earnings-call bets placed before 19:19Z on 2026-10-10 do not count toward keep-or-kill

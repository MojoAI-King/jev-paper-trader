# Task: Mention strategy: every event, buy only before the event, more data (B32)

Kind: Living. Task record.

- **ID:** 2026-10-10-mention-strategy-every-event-buy-only-be-3436
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-10T19:19:45.228Z

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

## Handoff

- **State:** B32 live: mention reader sees 75 of 76 open events (was 8); bets stop 6 h before the event's own date; lean mention log; settle skips markets before their event; 30 probes a day; earnings-call and Trump series skipped and yes_bias 0.10 after the 7,929-market timing test (+15-18% outside them, both halves; no edge inside). Resting bids tested: no better than taking the ask. Not yet confirmed: the first cycle on ddf5f59 or later (19:19Z). Open question to Joey: does 'skin in the game' mean real money (not built without his explicit ask) or paid tools/data. Evidence: 151 offline tests OK; run 38076336614 success on c39256d (119 series, 67 s, no errors, 4 probes); read-only full pass 455 requests, 75/76 events; mention_timing.py 7,929 markets; mention_maker.py 1,183 markets.
- **Next:** Confirm the 19:19Z cycle (stats mention_fetch.series_skipped > 0, mentions.excluded_series, no errors); then the forward test runs itself (early read: docs/research/scripts/mention_forward.py)
- **Blocked:** nothing; Joey's answer on real money vs paid tools shapes what comes after the forward test
- **Watch out:** Stage by explicit path; record files are edited with the Edit tool, not overwritten from the shell (guardrail); tests must never reach Kalshi or The Odds API live (DataDirTest guards both)

# More action: whole Kalshi window soonest first, research paced, early Kalshi results, Jev alone bold

Kind: Living. Decision entry.

- **ID:** 2026-09-28-more-action-whole-kalshi-window-soonest-21f7
- **Status:** accepted
- **Date:** 2026-09-28

## Decision

Joey, 2026-09-28: "I just want to see some more action... it can't self-improve if it's incredibly cautious
on betting on anything." A read-only analysis workflow (5 analysts, a design, 2 critics) measured why, and
these changes followed. Main's gates, the price screen, sizing, fees and caps are unchanged.

1. **Kalshi: the whole window, soonest first.** `markets.fetch_kalshi` walks 12h-3d, 3d-7d, 7d-30d, each
   paged to the end (at most `KALSHI_MAX_PAGES` 60), then takes the 60 busiest. A failure mid-walk keeps what
   was fetched and logs a problem; a page-limit hit is logged too (`funnel.fetch` in `scans.jsonl`).
2. **Free filters before the top-N cut**, both sources (`keep` argument), so no slot goes to a market the
   filters would drop.
3. **Kalshi's 12-hour rule uses the event's expected expiration** when it is earlier than `close_time`
   (`engine.event_time`), so no bet is placed on a game under way.
4. **Kalshi results as soon as they're final.** `settle` checks every unresolved Kalshi market each cycle,
   50 tickers a request (`markets.check_kalshi`), whatever the stored close. A "scalar" result goes to
   `voids.json`: its bets are paid at the value (YES x value, NO x (1 - value)) and it is never scored.
5. **Research paced through the day, soonest-decided first.** At most 60 a day, never more than
   60 x (hour + 1) / 24 by a given UTC hour, up to 6 in one cycle to catch up after a gap
   (`research.pace_through_day`, `research.order`).
6. **Logs rotate.** `judgments.jsonl` and `research.jsonl` move to `papertrade_data/archive/*.jsonl.gz` past
   20 MB (`storage.rotate_logs_mb`); `read_jsonl` reads the archives too.
7. **New strategy `jev_alone_bold`**: Jev alone with Bold's 0.2 info bar; it differs from Bold only in having
   no research (EXPERIMENTS.md row). It is a policy strategy like Bold, outside the 2-challenger limit.

`markets_per_source` stays 60. This supersedes the "bigger market universe" alternative rejected in
decision 2026-09-28-open-bet-cap-50-percent-and-research-60-4998 only in effect: the fix made the same 60
slots count, and raising the number waits for a day of measurements (BACKLOG B16).

Added after a review workflow (4 reviewers, each serious finding checked by a skeptic):

8. **A cycle can't overrun GitHub's 55-minute limit on research.** No research or Claude direct call starts
   after `research.max_minutes_per_cycle` (25) minutes; each research call is cut at 300 s (was 900; the
   longest measured was 73 s); two failed research runs in a row end research for the cycle. With 6 a cycle at
   900 s, stalled calls could have run 90 minutes and lost the whole cycle (confirmed by simulation).
9. **No bet on a match in play.** Polymarket sports markets list an end date about a week after the match;
   their `gameStartTime` is stored as `starts`, and a market is skipped from `market_filters.
   min_hours_before_start` (1) hour before it starts. Its result is checked from `check_hours_after_start`
   (3) hours after the start, not a week later.
10. **Kalshi results count only when final** ("finalized"/"settled", not "determined", which can still be
    disputed); a failed batch loses only itself; the Kalshi walk stops after 300 s keeping what it has.
11. The page's "How to check this is real" links add `voids.json` and the `archive/` folder.

## Why

Measured 2026-09-28 (details in the lesson 2026-09-28-kalshi-lists-markets-latest-closing-firs-640e):
- All 61 Kalshi markets ever judged closed 14-30 days out; about 400 eligible ones closed within 7 days.
  A live run of the new fetch: 35 pages in 65 s, 488 Kalshi markets passing, 43 of the top 60 closing
  within 7 days (was 0). Polymarket: 60 of 60 slots now pass the filters (was 24), 53 within 7 days.
- Learning is fed by every judged market that resolves, bet or not; only 9 had resolved. Faster results
  matter more for learning than more bets.
- 12 judged Kalshi markets were already final (7 yes/no, 5 scalar) while their stored close said Oct 15-22.
- Research ran out at 09:05Z; paced, 60 a day spreads about 2.5 an hour.
- Jev alone clears about 7 distinct markets a day at info 0.2 vs 1 at 0.5 (judgments, 38 hours).
- At the new volume the judgment log would pass GitHub's 100 MB file limit in about three weeks, which would
  stop the only ledger writer.

## Alternatives rejected

- Loosening main's info gate: pre-registered; Bold and Jev alone, bold test it instead.
- Two new loose strategies (`wide`, `wide_no_research`): `wide` repeated Bold's bets (36 of 49 the same).
- Settling Kalshi at `expected_expiration_time`: finalized markets showed a later expected expiration than
  their real result, so it would have missed them; the batched status check catches every one.

## Risk

- About 35 Kalshi requests a cycle instead of 2: more exposure to 429s from GitHub's shared runners. A
  mid-walk failure keeps the soonest markets.
- Main now sees more short-dated sports, so its market mix changes from this date.
- Paced research uses all 60 a day when demand is high; the weekly Claude meter is not paced (an option put
  to Joey).
- A scalar market's NO payout (1 - value) follows Kalshi's convention; not verified against a settled bet.

## Reversibility

`research.pace_through_day` false and `order` removed restore the old research order; retire
`jev_alone_bold` by removing it from `policy.json` (its ledger stays). The fetch change is code.

## Evidence

83 offline tests pass, including `test_kalshi_walks_the_window_soonest_first_and_ranks_all_of_it`,
`test_kalshi_keeps_what_it_fetched_when_a_later_page_fails`, `test_kalshi_results_count_before_the_stored_close_and_a_scalar_pays_its_value`,
`test_research_is_paced_through_the_day_and_soonest_first`, `test_logs_rotate_into_archives_and_are_still_read_whole`,
`test_jev_alone_bold_differs_from_jev_alone_only_in_the_info_bar`. The live fetch numbers above were read
from the Mac, read-only.

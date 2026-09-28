# Kalshi lists markets latest-closing first so the top 60 were all 2-4 weeks out

Kind: Living. Lesson entry.

- **ID:** 2026-09-28-kalshi-lists-markets-latest-closing-firs-640e
- **Status:** accepted
- **Date:** 2026-09-28

## What broke

Joey: "I just want to see some more action." Main bet 5 times in 38 hours and the learning loop had 9
results. Every Kalshi market the trader had ever judged (61 of 61) closed 14-30 days out.

## The mechanism

Kalshi's `GET /markets` returns markets in descending close-time order. `fetch_kalshi` asked for the whole
12h-30d window, stopped paging as soon as `limit` (60) markets cleared the volume bar, and only then sorted
by volume. So "the 60 busiest" were really the busiest of the first 1-2 pages: the markets closing last.
Separately, the free filters (price 5-95%) ran after the top-60 cut, so 36 of Polymarket's 60 slots and
about half of Kalshi's went to markets the filters then dropped. And `settle` waited for each market's stored
close time, which on Kalshi is a late upper bound: 12 judged markets were already final while their stored
close said Oct 15-22.

## The fix

Commit on 2026-09-28 (decision 2026-09-28-more-action-whole-kalshi-window-soonest-21f7):
`markets.fetch_kalshi` walks the window in slices, soonest first, to the end, then ranks; both fetchers
take the scan's free filters as `keep`; `markets.check_kalshi` + `engine.settle(batch=...)` check every
unresolved Kalshi market each cycle.

## The rule

Before ranking "the top N" from a paged API, find out what order it pages in, and walk the whole set (or the
end you care about first). Filter before the cut, not after. Don't trust a vendor's close time as the moment
a result is known; ask for the result.

## What now enforces it

`PolymarketFetchTests.test_kalshi_walks_the_window_soonest_first_and_ranks_all_of_it` (the biggest market
is on the far-dated slice and must win), `test_polymarket_filters_before_taking_the_top`,
`SettleAndStorageTests.test_kalshi_results_count_before_the_stored_close_and_a_scalar_pays_its_value`.
Each scan logs pages fetched and whether the walk was cut short (`funnel.fetch`).

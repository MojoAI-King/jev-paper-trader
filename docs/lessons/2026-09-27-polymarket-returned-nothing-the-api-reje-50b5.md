# Polymarket returned nothing: the API rejects snake_case sort fields

Kind: Living. Lesson entry.

- **ID:** 2026-09-27-polymarket-returned-nothing-the-api-reje-50b5
- **Status:** accepted
- **Date:** 2026-09-27

## What broke

The first live run judged 32 Kalshi markets and no Polymarket ones. `python3 -m papertrade markets` printed `polymarket: FAILED HTTP Error 422: Unprocessable Entity`, and the scan log only said "could not fetch markets".

## The mechanism

`fetch_polymarket` sent `order=volume_24hr`. Polymarket's Gamma API accepts only camelCase sort fields (`volume24hr`, `volumeNum`, `volume`) and answers anything else with HTTP 422 and the body `{"error": "order fields are not valid"}`. `markets._get` let `urllib`'s HTTPError propagate, and that exception's message drops the response body, so the one line that explained the failure never reached a log.

## The fix

`papertrade/markets.py`: `order` is `volume24hr` (commit 75e77f1); `_get` now re-raises HTTP errors with the API's own body, trimmed to 300 characters. Pagination followed in 901fe74: pages of 100 until 60 Yes/No markets, `MAX_PAGES = 25` per source (Kalshi's cursor loop got the same cap).

## The rule

When a data source returns nothing, read the raw HTTP response before touching filters or parsing. Error paths must carry the vendor's response body into the log.

## What now enforces it

`PolymarketFetchTests.test_fetch_uses_a_sort_field_the_api_accepts` replays a response recorded on 2026-09-27 (`tests/fixtures/polymarket_markets.json`) and rejects unknown sort fields with the recorded 422, so it fails on the old field. `test_http_error_keeps_api_reason` holds the error body. `test_page_limit_stops_a_feed_that_never_runs_dry` and `test_kalshi_page_limit` hold the page cap.

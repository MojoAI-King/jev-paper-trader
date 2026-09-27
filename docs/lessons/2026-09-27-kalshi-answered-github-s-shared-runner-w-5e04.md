# Kalshi answered GitHub's shared runner with 429 and a whole source vanished for an hour

Kind: Living. Lesson entry.

- **ID:** 2026-09-27-kalshi-answered-github-s-shared-runner-w-5e04
- **Status:** accepted
- **Date:** 2026-09-27

## What broke

GitHub run 36329790430 (15:30 UTC) printed `fetched 60` instead of about 120 and `1 errors`. The
cycle ran on Polymarket markets only. From the Mac, `python3 -m papertrade markets` showed both
sources healthy at the same moment.

## The mechanism

The run log's problem line: `kalshi: could not fetch markets (HTTP 429 from
https://api.elections.kalshi.com/trade-api/v2/markets: {"error":{"code":"too_many_requests"}})`.
GitHub-hosted runners share outbound IP addresses with many other jobs, so a public API's per-IP rate
limit can already be spent when our job arrives. `markets._get` made one attempt and raised, and
`fetch_kalshi` pages back to back, so one 429 on any page dropped the whole source for that cycle.
The funnel line only showed a total, so the loss was visible only as "60" instead of "120".

## The fix

`papertrade/markets.py` (commit 4eed607): `_get` retries 429 and 5xx up to `RETRIES = 4` times,
honoring `Retry-After` (capped at 30 seconds) and otherwise backing off 2, 4 and 8 seconds;
Kalshi pages are `KALSHI_PAGE_PAUSE = 0.5` seconds apart. Each scan now records markets fetched per
source (`funnel.by_source`) and its problem lines (`problems`) in `scans.jsonl` (commit 87801e5), and
`python3 -m papertrade health` prints both.

## The rule

A job that runs on shared CI infrastructure must treat 429 as normal: retry with backoff and honor
`Retry-After`. Log counts per source, not only totals, so a source that silently drops out is visible
in one line.

## What now enforces it

`PolymarketFetchTests.test_rate_limit_is_retried_then_reported` replays two 429s then a success, and a
429 that never clears, and checks the waits (Retry-After first, then backoff) and the final error text.
`python3 -m papertrade health` shows per-source counts and problem lines for the last cycle.

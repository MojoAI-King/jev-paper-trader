# A real API key in .env turned the tests into live calls

Kind: Living. Lesson entry.

- **ID:** 2026-10-10-a-real-api-key-in-env-turned-the-tests-i-43ba
- **Status:** accepted
- **Date:** 2026-10-10

## What broke

Minutes after Joey added `ODDS_API_KEY` to `.env`, The Odds API's free quota fell from 497 to 286 of 500. Two local
runs of the offline test suite spent about 210 requests. A test also began failing ("no sharp line matched" instead
of "waiting for an ODDS_API_KEY"), and the suite slowed from 9 to 36 seconds.

## The mechanism

`odds.api_key()` reads the environment and then `.env`, like the Jev key. The scan tests (`DataDirTest` subclasses)
run `engine.scan`, which calls `odds.load_events` whenever a key exists. While the key was absent the tests passed
and never touched the network. Once it existed, every test scan made real calls: the free sports list, then up to 4
sports at 1 request each, because each test's temp cache was always stale. CI is worse: `trade.yml` passes
`ODDS_API_KEY` to the step that runs the tests and then the cycle, so every 30-minute run would have spent about
100 requests.

## The fix

`DataDirTest.setUp` patches `odds.api_key` to return None and `odds._get` to raise "a test called The Odds API".
The one test that exercises the sharp line patches `api_key` and `load_events` itself (commit dddfeac, pushed before
the next CI run). `sharp.refresh_minutes` went to 480 to fit the 286 requests left.

## The rule

Any code path that reads a credential from the environment or `.env` needs a test-wide guard that removes the
credential and fails loudly on a real call. Add it in the same change that adds the credential, not after the key
appears: tests that pass without a key say nothing about what they do with one.

## What now enforces it

`DataDirTest` (every scan test) forces no key and makes any Odds API call raise. Nothing yet guards the Jev key the
same way; the Jev client in tests uses a fake transport by construction.

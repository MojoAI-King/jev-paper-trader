# The price screen checked web addresses Jev never sees and dropped clean facts

Kind: Living. Lesson entry.

- **ID:** 2026-09-27-the-price-screen-checked-web-addresses-j-173f
- **Status:** accepted
- **Date:** 2026-09-27

## What broke

In the first live cycles, the price screen dropped 20 of 53 real facts. Six were clean facts (match schedule, injuries, results) dropped as "makes a prediction" because they came from a Sports Mole preview whose web address contained `...-prediction-team-news`.

## The mechanism

`screen_facts` ran every `LEAK_RULES` pattern over `fact + source + url`. Jev only ever reads `kind`, `date`, `source` and `fact`; `build_state` never passes the URL. So words in a URL path added false drops without protecting anything. The rule that drops any percent or cents figure within 1 point of the market's price also dropped poll numbers (8 facts on the Brazil election markets priced at 43¢ and 57¢).

## The fix

`news.market_site(url)` checks the address only for a prediction-market or betting host (the blocked domain list plus the venue-name pattern); the text rules run on fact and source only. Joey approved the change on 2026-09-27 (commit 438d284). Measured on the 53 real facts: 33 kept before, 41 after. The price-match rule stays strict by Joey's decision.

## The rule

A filter should inspect exactly what its consumer reads. Measure it on the first real batch and count its false drops before trusting it. Never loosen this screen without Joey's OK.

## What now enforces it

`ScreenFactsTests.test_web_addresses_are_checked_for_market_sites_only` (it failed before the fix). The leak tests `test_price_never_reaches_jev_or_claude_through_research` and `test_drops_every_leak_with_a_reason` were re-run with the screen switched off and with the price-match rule switched off, and failed both times. Every dropped fact is logged with its reason in `judgments.jsonl`. The open question on poll numbers is in the backlog.

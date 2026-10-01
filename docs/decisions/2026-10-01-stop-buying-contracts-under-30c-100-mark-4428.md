# Stop buying contracts under 30c; 100 markets per source

Kind: Living. Decision entry.

- **ID:** 2026-10-01-stop-buying-contracts-under-30c-100-mark-4428
- **Status:** accepted
- **Date:** 2026-10-01

## Decision

Joey, 2026-10-01 ("do the rule change... make things happen"): every strategy except `original` stops
buying contracts priced under 30c (`min_ask` 0.30, applied by hand with the new `python3 -m papertrade tune`,
logged in `rules_history.jsonl` as by Joey). `markets_per_source` 60 -> 100 (BACKLOG B16). The daily review now
sees each strategy's settled bets by price paid (`by_price_paid`, code idea p4) and is told why the floor exists.

## Why

Settled to 2026-10-01: long shots under 30c lost $32.6k of the $35.7k lost across all strategies (21 bets, 1 win,
average price 15c; our forecasts put them at 33% and expected 7 wins, the market about 15% and 2.9). The other 29
bets lost $3.1k. Across all 140 resolved judged markets (flat $100 a market, scratch simulation): with a 30c floor
Jev + research goes from -$1,306 to +$1,121 (26 bets, 19 won), Claude direct from -$1,238 to +$262, Jev alone from
-$5,285 to -$959. The same holds on every judgment, not just the first look.

## Alternatives rejected

- A price ceiling (65c or 70c): changed nothing in the simulation.
- Leaning the forecast toward the market price (half weight): fewer bets and no better than the floor alone.
- Always buying the favourite: 110 of 140 won, still -$600 after fees.

## Risk

Small sample (140 markets, 32 with real bets). The floor removes the bets with the biggest payouts; if long shots
start paying, `by_price_paid` will show it and the review may lower the floor. `original` keeps no floor, so it shows
what the floor saves. 100 markets a source means more Jev calls a cycle (still capped at `max_jev_calls_per_scan` 80).

## Reversibility

`python3 -m papertrade tune <strategy> min_ask=null --why "..."`, then push papertrade_data/. markets_per_source back to 60.

## Evidence

119 tests pass, including `test_joey_s_own_change_skips_the_wait_but_never_the_checks` and
`test_the_review_sees_results_by_price_paid`. Commits 4a0c001 (code), 360bb9f (the rule change).

# Forecasters scored on different markets rank wrong

Kind: Living. Lesson entry.

- **ID:** 2026-10-01-forecasters-scored-on-different-markets-0308
- **Status:** accepted
- **Date:** 2026-10-01

## What broke

Asked "is Jev doing anything", the per-source Brier scores put Claude direct (0.134, 44 markets) far ahead of
Jev + research (0.201, 136 markets) and close to the market (0.116, 219 markets). Head to head on the same markets the order is market 0.119, Jev + research
0.184, Claude direct 0.195, Jev alone 0.241 (2026-10-02, 111 markets). Three different cuts of the data gave three
different rankings while I was answering Joey.

## The mechanism

`engine.calibration` scored each source on whatever resolved markets it had a forecast for. Claude direct only
forecasts where research ran (44 markets), Jev + research 136, Jev alone and the market 219. Those are different
markets with different difficulty, so the averages can't be compared. A second trap: requiring all four on each
market's *latest* look (44) instead of taking the latest look that *has* all four (111) changed which markets count.

## The fix

`engine.paired` (papertrade/engine.py): per market, the latest look (current question set) where all of
`PAIRED` gave a forecast; every source scored on that one set. `calibration()` returns it as `paired`; the page's
Forecasters panel, the report's "Head to head" lines and the daily review read it. Commit 3a605d0.

## The rule

Compare forecasters only on markets all of them forecast, and say how many. Quote a per-source score alone only
with its own market count, never next to another source's as a ranking.

## What now enforces it

`test_forecasters_are_scored_head_to_head_on_the_same_markets` (a market missing one forecaster is dropped for
all). Nothing stops a session from quoting the unpaired `sources` scores as a ranking in chat.

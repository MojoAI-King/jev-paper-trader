# Choosing markets by final volume faked every lead in a market scan

Kind: Living. Lesson entry.

- **ID:** 2026-10-10-choosing-markets-by-final-volume-faked-e-4ed2
- **Status:** accepted
- **Date:** 2026-10-10

## What broke

The first run of `docs/research/scripts/edge_scan.py` (20,747 Kalshi markets, 1,626 series) reported ten "leads",
all cheap long shots paying +13% to +458% after fees (Financials YES at 2–15¢ +458%, Sports NO at 2–15¢ +101%).
They were not real: in the events where the scan had taken every market, the same cuts lost 47–54%.

## The mechanism

- **Selection on a variable measured after the outcome.** Within each event the scan took the markets with the most
  total volume (`volume_fp` on the settled listing). Total volume includes the trading after news arrives, so in a
  many-outcome event (weather brackets, price ranges, award nominees, tournament winners) the eventual winner draws the
  volume and gets picked. The scan was, in effect, buying cheap tickets it already knew had won.
- **A decision time anchored to an outcome-dependent close.** Kalshi moves `close_time` to the moment an
  early-resolving market settles ("will X happen by Friday" closes when X happens), so "24 hours before the close" can be
  a day before a surprise that nobody knew was coming. A third of Financials and Entertainment markets closed more than
  a day before their scheduled `occurrence_datetime`.

## The fix

`docs/research/scripts/edge_scan.py` second version: markets are chosen without looking at anything after the bet
(every market of an event with 4 or fewer, else a random sample seeded by the event ticker); the decision points are 24
and 72 hours before the scheduled `occurrence_datetime` (identical across an event's markets in 99.4% of events, so set
in advance; events where it differs are skipped); a market already closed at a decision point is skipped; liquidity is
judged only from candle volume before the decision. The volume-picked rows are kept in `research_data/` for the record.

## The rule

In any backtest or scan, every filter, sort and sample must use only what was knowable at the decision time: no final
volume, no final open interest, no settlement-time fields, and no clock anchored to an event whose timing depends on the
outcome. Before believing a lead, re-run it on a subset where no choice was made (every market of the event) and check
it against the published patterns; an edge that contradicts a well-documented bias is an artifact until shown otherwise.

## What now enforces it

The selection code and its comment in `edge_scan.py`, and the summary's count of cuts tested with the number of leads
expected by chance. Nothing automated checks future scripts for look-ahead fields: a reviewer must.

# Dashboard numbers: span-12 outside a grid, and last scan counted by day

Kind: Living. Lesson entry.

- **ID:** 2026-09-27-dashboard-numbers-span-12-outside-a-grid-aa75
- **Status:** accepted
- **Date:** 2026-09-27

## What broke

The first dashboard render squeezed every card into narrow columns across the top of the page. Later the live page said the last scan "judged 61 markets" when it had judged 29.

## The mechanism

The Trades card had `class="card span-12"` (`grid-column: span 12`) but sat directly inside `.wrap`, a grid with no explicit columns. A span on an item in such a grid creates 12 implicit columns, and every sibling was auto-placed into them. The count was wrong because `dashboard.last_scan` grouped judgments by UTC calendar day, which mixed the first run's 32 judgments (question set v1) with the next scan's 29.

## The fix

The span class was removed from the card (it only belongs inside `.grid`). `last_scan` now counts the latest scan only: judgments in the current question set that share the latest timestamp, since every judgment in one scan shares the scan's stamp (commit 975f643).

## The rule

Look at a rendered screenshot of every page change once before shipping. Take counts shown to people from the same record the funnel uses (one scan), not from a calendar window.

## What now enforces it

`DashboardTests.test_last_scan_counts_only_the_latest_scan`. Nothing automated checks the layout: the one-screenshot look is manual, and phone widths below about 500px could not be checked in headless Chrome.

# Show settled and unsettled money apart; plain strategy names; chart never tighter than 5 percent

Kind: Living. Decision entry.

- **ID:** 2026-09-27-show-settled-and-unsettled-money-apart-p-f0c2
- **Status:** accepted
- **Date:** 2026-09-27

## Decision

1. The page shows **settled** money (final, from bets whose markets resolved) and **open** money (open
   bets valued at today's market prices, not final) side by side: on every strategy row ("settled $0 ·
   14 open −$3,059"), in the equity header ("Settled profit · final" and "Open bets · not settled"), and on
   each bet card ("$2,000 bet · now $1,711").
2. Strategies carry plain names, a one-line description and a tag, set in `policy.json` (`short`,
   `desc`, `badge`): Jev + Claude (Headline, "Jev reads Claude's research"), Jev alone ("Jev with no
   research"), Claude direct ("Claude's own call, same research"), Bold (Challenger, "also bets when Jev is
   unsure"), Self-calibrating (Learning n/30, "corrected by past results").
3. The equity chart never zooms tighter than ±5% of the bankroll ($95k to $105k); it widens only when a
   strategy moves further.
4. On monitors at least 1900px wide the dashboard is scaled up (CSS zoom 1.25, or 1.5 from 2300px).

## Why

Joey asked "why did I start already losing, is that real?" after the page showed Bold at −3%. No bet had
settled; the drop was almost all the cost of getting in (see the lesson
2026-09-27-marking-brand-new-bets-at-the-mid-price-58f3). He asked to make that clear on the display, and
for the strategies to read as "Jev alone, Claude plus Jev, Claude direct". His wide-monitor screenshot
showed the chart stretching a 3% dip over its whole height, and small text.

## Alternatives rejected

- Valuing open bets at cost until they settle: honest, but the page would sit flat for days, which is
  what Joey didn't want ("I'm not seeing anything happening").
- Valuing open bets at the bid: harsher still in thin markets.

## Risk

A floor on the chart's range hides small real moves; the numbers beside it still show them exactly.

## Reversibility

All in `papertrade/dashboard_template.html` and the strategy fields in `policy.json`.

## Evidence

Deployed as Worker versions 564d079c and 1a1a553f; the live page contains the new code (checked by
request). Headless Chrome renders at 1440x900 and 2550x1281 fit one screen.

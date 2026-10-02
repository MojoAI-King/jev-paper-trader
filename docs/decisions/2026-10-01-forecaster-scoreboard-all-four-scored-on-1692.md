# Forecaster scoreboard: all four scored on the same markets

Kind: Living. Decision entry.

- **ID:** 2026-10-01-forecaster-scoreboard-all-four-scored-on-1692
- **Status:** accepted
- **Date:** 2026-10-01

## Decision

Joey approved code idea p7 on 2026-10-02 ("yes" to a scoreboard panel). `engine.paired` scores the market price,
Jev + research, Claude direct and Jev alone on **the same resolved markets**: per market, the latest look (current
question set) where all four gave a forecast. `engine.calibration` returns it as `paired`, so the page, the text
report ("Head to head" lines) and the daily review (`brier_all_time`) all read the same numbers. The page shows it in
a new **Forecasters** panel under the live feed, as "% better than a coin flip" (1 − Brier / 0.25), best first; hovering
a row shows the Brier score. The feed panel is shorter by one row; nothing else on the page moved.

## Why

Joey asked whether Jev is doing anything. The per-source Brier scores each cover different markets (Claude direct
only where research ran), so they can't be compared head to head; p7 said the same. On the same 111 markets on
2026-10-02: market 0.119, Jev + research 0.184, Claude direct 0.195, Jev alone 0.241 (a coin flip is 0.25).

## Alternatives rejected

- **First look per market.** Cleaner in principle (no late information), but the bets are placed at every look and the
  existing scores use the latest; the ranking is the same either way (first look, 111 markets: 0.150, 0.195, 0.211, 0.241).
- **Every look.** Weights markets judged many times more heavily.
- **Panel in the bottom row beside Open positions.** Tried: at 1280px wide it cut Open positions to one card.
- **The calibrated source in the panel, and p7's out-of-sample check of the calibration map.** Not built; the
  self-calibrating forecaster has forecast 68 resolved markets (Jev + research 136), and requiring a fifth source
  would shrink the shared set. Left for a later code idea.

## Risk

The latest look can be close to the market's end, when everyone knows more; the market benefits most from that, so
the panel flatters the market rather than us. Small samples: treat as noise until well past 50 markets (PLAN.md).

## Reversibility

Remove the `#p-score` section and its render block in `papertrade/dashboard_template.html` and restore
`#p-feed { grid-row: 2 / 4 }`; `paired` in `engine.calibration` is additive and can stay.

## Evidence

`test_forecasters_are_scored_head_to_head_on_the_same_markets` (a market missing one forecaster is left out for all;
the latest look counts; old wording and unresolved markets are left out; the page and the review read the same
numbers; the panel is on the page). 122 offline tests pass. Screenshots at 1600, 1280 and a true 400px frame
(no sideways scroll).

# Research brief 05: Combining our forecast with the market price

Kind: Reference. One of 14 narrow research briefs for the trader's rebuild (BACKLOG B24), each run as its own
Claude Code session in a VS Code tab. To start it, type in a new tab:
`Run research brief 05: read docs/research/briefs/05-blend-with-market.md and follow it.`

Before you start, read `docs/research/README.md` (rules for sessions running side by side, evidence standards, the
report format) and the "What the data says" section of `docs/REBUILD_SCOPE.md`.

## Question

What's the right way to combine a model's probability with the market price when deciding to bet, and how do we test whether the model adds anything the price doesn't already contain?

## What we already know

- An out-of-sample fit on 1,133 finished markets, logit(p) = a + b·logit(market) + c·logit(model), gave b ≈ 1.35 and c ≈ 0.52 for Claude direct, 0.33 for Jev + research, 0.16 for Jev alone and 0.12 for the self-calibrating Jev. So the models carry a little information beyond the price.
- Betting the blend at the ask still lost 13–21%, because the typical disagreement was smaller than the ~8.4% cost of each trade.
- Today the forecasters never see the price; code compares afterwards. That screen was a deliberate choice, and changing it needs Joey's OK.

## Find out

- Methods: logistic stacking, Bayesian updating with the market as the prior, weighting sources by track record, extremizing, and how each behaves on small samples.
- Tests for added information (forecast encompassing, regression on log-odds, paired Brier) and the sample sizes they need.
- Evidence from forecasting research (combining polls, models and markets) and from sports betting (models against the closing line).
- How large a disagreement with the market must be before a bet pays after costs, and whether to require several sources to agree.
- Whether letting the forecaster see the price helps or hurts (anchoring vs information), with evidence.

## Leave out

Forecasting techniques (brief 04); bet sizing (12).

## Deliverable

Write `docs/research/05-blend-with-market.md` in the report format from `docs/research/README.md`, and include
the exact combination formula and betting rule you recommend, and how to fit and refit it without overfitting.

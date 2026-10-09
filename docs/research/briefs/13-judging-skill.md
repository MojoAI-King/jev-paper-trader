# Research brief 13: Telling skill from luck quickly

Kind: Reference. One of 14 narrow research briefs for the trader's rebuild (BACKLOG B24), each run as its own
Claude Code session in a VS Code tab. To start it, type in a new tab:
`Run research brief 13: read docs/research/briefs/13-judging-skill.md and follow it.`

Before you start, read `docs/research/README.md` (rules for sessions running side by side, evidence standards, the
report format) and the "What the data says" section of `docs/REBUILD_SCOPE.md`.

## Question

How can we tell, as early and reliably as possible, whether a strategy or forecaster has real skill, without fooling ourselves when we test many variants on the same history?

## What we already know

- Small samples misled us twice: "Jev + research is the best forecaster" on 112 markets and "19 of 24 test bets won", both reversed at 600+ markets.
- About a dozen strategy variants run at once, and every new idea is tested on one history of about 1,100 finished markets.
- Today we judge by realized profit and loss, and by Brier score against the market on the same markets.

## Find out

- Closing-line value (did the price move our way after we bet) for prediction markets: how to measure it, how much sooner it reveals skill than profit and loss, and its pitfalls.
- Brier decomposition (reliability and resolution) and calibration plots on small samples.
- Power: how many bets or markets it takes to detect a 2%, 5% or 10% return edge at typical prices, and a Brier gap of 0.005–0.02 against the market.
- Multiple testing and overfitting: the deflated Sharpe ratio, false-discovery control, walk-forward and holdout designs, pre-registration.

## Leave out

Sizing (brief 12).

## Deliverable

Write `docs/research/13-judging-skill.md` in the report format from `docs/research/README.md`, and include
an evaluation checklist, the formulas, and the minimum sample size for each kind of decision.

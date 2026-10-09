# Research brief 07: Pricing daily weather markets from forecast models

Kind: Reference. One of 14 narrow research briefs for the trader's rebuild (BACKLOG B24), each run as its own
Claude Code session in a VS Code tab. To start it, type in a new tab:
`Run research brief 07: read docs/research/briefs/07-weather-markets.md and follow it.`

Before you start, read `docs/research/README.md` (rules for sessions running side by side, evidence standards, the
report format) and the "What the data says" section of `docs/REBUILD_SCOPE.md`.

## Question

How should we turn official forecasts and ensemble weather models into probabilities for daily high-temperature (1–2 degree bins) and rain markets, and how efficient are Kalshi's and Polymarket's weather markets?

## What we already know

- Few weather markets reach us today (36 of 1,133 finished markets), because each cycle takes 100 markets per venue; the plan can target them if there's a real edge.
- Our AI forecasts are poor here: Claude direct scores a Brier of 0.304 vs the market's 0.185 (19 markets). Jev gave 76% to "the highest temperature in Wuhan will be 22°C" and lost.

## Find out

- Exactly how Kalshi's weather markets resolve (the NWS Daily Climate Report, the station for each city, rounding, the reporting day) and how Polymarket's international ones resolve (source and station).
- Data: the NWS API, the National Blend of Models' probabilistic output, Open-Meteo's ensemble API (GFS and ECMWF ensembles) and others; free tiers, limits and international coverage.
- Forecast error by lead time (same day, next day, two to three days out), how to turn a forecast plus its error into bin probabilities, and station biases.
- How efficient these markets are, and documented strategies or bots, with dates.

## Leave out

Price thresholds (brief 06); economic releases (08).

## Deliverable

Write `docs/research/07-weather-markets.md` in the report format from `docs/research/README.md`, and include
an algorithm from forecast to bin probabilities, the data sources, and a backtest plan.

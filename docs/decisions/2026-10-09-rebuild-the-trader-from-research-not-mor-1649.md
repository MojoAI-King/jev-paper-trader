# Rebuild the trader from research, not more tuning

Kind: Living. Decision entry.

- **ID:** 2026-10-09-rebuild-the-trader-from-research-not-mor-1649
- **Status:** accepted
- **Date:** 2026-10-09

## Decision

Joey, 2026-10-09: stop treating rule tuning as the way to profit, and rebuild the trader from deep research.
Claude measured the state on every finished market and wrote research briefs. The first draft had five broad
briefs for claude.ai Research tabs. Joey revised it the same day: "make sure their focus is narrow... If we need to
do multiple research runs, we can do them", run as Claude Code sessions in separate VS Code tabs, all at once. So
there are fourteen narrow briefs in `docs/research/briefs/`, including how to harness Jev. Each session writes one
report into `docs/research/` under rules that keep parallel sessions from colliding (`docs/research/README.md`).
The main session commits the reports, checks them against our data, and writes the plan. Every code change in the plan waits for Joey's
yes, as before. The trader keeps running meanwhile, so the history every new idea is tested on keeps growing.

## Why

Joey: "they're doing terrible right now... we didn't do enough initial research and planning... you could have a random
gambler off the street come and do better." The measurement backs the diagnosis. On 327 finished markets with a real
price, every forecaster is less accurate than the market (Claude direct +0.035 ± 0.009 Brier, Jev + research
+0.043 ± 0.009, Jev alone +0.073 ± 0.010). Trading at the ask costs about 8.4% a bet. A bettor with picks exactly as good as
the market's would have lost about that much; we lost 46% of stake before the 30¢ floor and 13.4% after. Rules
decide which bets to place, but they can't make a forecaster that is worse than the price into a profitable one.

## Alternatives rejected

- **More tuning of the current strategies.** A week of twice-daily tuning didn't change the picture (main −34% on 12
  settled bets since the floor, `original` −24% on 22).
- **Blending the forecasts with the market price, or resting orders at the mid.** Tested on the 1,133 finished
  markets: the blend still loses 13–21% at the ask, and resting orders, counted as filled only when a later price
  reached them, did worse (−16% to −31%).
- **Pausing the trader.** Its price snapshots and forecasts on markets that finish are the backtest set for every
  new idea; fake money is all it loses.
- **Five broad briefs in claude.ai Research tabs.** The first draft; Joey asked for narrow ones, run as Claude Code tabs
  that can read the repo and write their reports straight into it.

## Risk

Research reports can be confident and wrong; each claim gets checked against our own data where possible. The briefs
quote numbers from 2026-10-09; they will drift as markets finish. Small samples misled us twice before (on 2026-10-02:
"Jev + research is the best forecaster" on 112 markets, "19 of 24 test bets won"); the plan states n and ± for
every number.

## Reversibility

Nothing in the trader changed. The briefs and this direction can be dropped at any time; the plan's code changes each
need Joey's approval anyway.

## Evidence

`docs/REBUILD_SCOPE.md` (numbers from the 2026-10-09T20:38Z cycle); scratchpad scripts `bt.py` (backtest with blends,
limit-order fills, categories) and the paired re-scoring by spread; BACKLOG B24, B25.

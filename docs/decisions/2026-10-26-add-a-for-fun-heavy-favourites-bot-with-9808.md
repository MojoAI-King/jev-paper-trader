# Add a for-fun heavy favourites bot with big flat bets

Kind: Living. Decision entry.

- **ID:** 2026-10-26-add-a-for-fun-heavy-favourites-bot-with-9808
- **Status:** accepted
- **Date:** 2026-10-26

## Decision

A new strategy, `favorites` ("Heavy favourites, big bets (for fun)", page slot 1), joins the three safe ones. It uses
no AI and no forecast (probability `"fun"`, `engine._fun_pass`, run every cycle after the sharp pass). Its rules:

- buy the favourite of every busy fetched market whose favourite's ask is 90–97¢ and that settles within 5 days,
  soonest first;
- a flat 1.5% of its bankroll a bet (about $1,500), at most 40 bets a day, one bet per event;
- never more contracts than the ask offers; real fees and slippage.

The hard limits are in code whatever `policy.json` says: 3% a bet (`FUN_MAX_STAKE_PCT`), 50 bets a day
(`FUN_MAX_BETS_PER_DAY`), and the shared 50% open-bet cap. It is locked against the daily review. The safe strategies
are unchanged.

## Why

Joey, 2026-10-26: his friends loved watching Bold "relentlessly bet". They want bigger bets ("real money being moved")
and "more volume more wins … instead of aggressively continuing to lose". Backtest on the markets the trader watched
settle (first look per event, real price, after costs):

- favourites at 90–97¢ won 95% of 239 bets at −0.5% a bet [−3.7, +2.3]: about break-even;
- favourites at 60–90¢ lost −7.8% [−13.5, −2.3] (n=489);
- longshots at 8–30¢ lost −19.7% [−37.4, +1.0] (n=400).

Only the 90–97¢ band gives volume and frequent wins without a measured bleed.

## Alternatives rejected

- **A Bold-style Jev/Claude bot:** Joey retired forecaster pickers on 2026-10-11; every forecaster's skill beyond the
  price was negative.
- **Favourites at 60–90¢ or longshots:** both lost on history (above).
- **Bigger bets for the safe strategies:** their small bets come from thin Kalshi mention books and probe sizing while
  their forward tests run; changing that would spoil the tests.

## Risk

- It is not a proven edge. Many small wins and the odd large loss (a loss costs about 15–20 wins), so the page total can
  swing.
- It sits in the page's total.
- Stop rule (docs/EXPERIMENTS.md): stop it if, after 200 settled bets, the top of its 95% range is below −2% a bet.
- It never qualifies for real money.

## Reversibility

Set its `probability` to a retired value or remove it from `policy.json`; open bets settle normally.

## Evidence

- Offline tests: 166 pass. New: `FunStrategyTests` (band, soonest first, one bet per event, hard limits, ask size,
  no Jev call). Updated: `RetiredJevTests`.
- Registry row in docs/EXPERIMENTS.md, written before any bet.

# Fills at the mid made resting orders look profitable

Kind: Living. Lesson entry.

- **ID:** 2026-10-09-fills-at-the-mid-made-resting-orders-loo-700b
- **Status:** accepted
- **Date:** 2026-10-09

## What broke

A backtest on 1,133 finished markets showed every forecaster profitable once orders were bought at the mid instead
of the ask: +4% to +14% (the Claude direct blend +14.4% ± 4.7%, 239 bets). It looked like "better execution fixes
everything".

## The mechanism

Buying at the mid assumes someone sells to us at the mid whenever we want. A resting order only fills when a seller
comes down to it, which happens most when news turns against the bet. Counted as filled only when a later snapshot
(about 30 minutes apart) showed that side's ask at or below our price, the same strategies returned −16% to −31%.
"Always buy the favourite" went from −2.8% at the ask to −9.3% as a resting order. That is adverse selection.

## The fix

No code. The conservative fill rule is in the scratchpad backtest (`limit_bt` in `bt.py`) and is the one quoted in
`docs/REBUILD_SCOPE.md`; brief 5 asks the research how to simulate fills honestly.

## The rule

Run every backtest under an optimistic and a conservative fill rule; trust only results that are positive under the
conservative one. A strategy that turns profitable when the execution assumption changes is an execution
assumption, not a strategy.

## What now enforces it

Nothing yet; a reusable backtest tool (B24's plan, a code change) should report both fill rules side by side.

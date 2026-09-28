# Open-bet cap 50 percent and research 60 a day

Kind: Living. Decision entry.

- **ID:** 2026-09-28-open-bet-cap-50-percent-and-research-60-4998
- **Status:** accepted
- **Date:** 2026-09-28

## Decision

1. **Open-bet cap 30% -> 50%** (`sizing.max_total_exposure_pct`), for every strategy. Joey, 2026-09-28: "we can
   make it so like unless someone goes below 50,000 they can bet." A strategy keeps betting until half its
   fake bankroll is tied up in open bets. The 2%-per-bet cap is unchanged.
2. **Research 20 -> 60 events a day** (`research.max_research_per_day`); 3 per cycle unchanged, and the pause
   at 70% of the plan's 5-hour window is unchanged.

## Why

Measured over the day to 2026-09-28 21:05Z (49 cycles), per-strategy skip reasons from `judgments.jsonl`:

- Bold cleared its gates 23 times but bet 7; 16 were "no room: exposure cap or cash". It held $30,269 in 18
  open bets, exactly 30% of its equity. The cap binds only Bold: main holds 10%, Claude direct 4%, Jev alone 2%.
- Research ran out: 20 runs on 2026-09-27 and 20 on 2026-09-28, the last at 09:00Z (5 AM ET). After that every
  research-based strategy (main, Claude direct, Bold, Self-calibrating) logged "research cap reached" (80
  times) until midnight UTC. Research costs about $0.12 API-equivalent a run on the plan (97 calls, $11.44);
  the plan read 0% of its week and 8% of its 5-hour window at the last reading.
- Main's other skips are its pre-registered gates, left alone: "needs recent info" (131) and "rules unclear"
  (119, not researched because research can't unlock a vague-rules bet). Jev alone is blocked almost only by
  the info gate (333), which is expected: it never gets research.

## Alternatives rejected

- Loosening main's info or rules gates: they are pre-registered (PLAN.md); Bold already tests a lower info bar.
- A bigger market universe (`markets_per_source` 60): the measured bottleneck was research, not candidates.
  Revisit if research stops running out.

## Risk

- Research uses up to 3x the Claude plan it did; the 5-hour pause still protects Joey's own sessions.
- A strategy can now have half its bankroll in open bets, so a bad week costs more.

## Reversibility

Set the two numbers back in `policy.json`. Bets already placed stay open.

## Evidence

`DecideTests.test_exposure_cap` now reads the cap from policy and checks both sides of it;
`test_research_caps_per_cycle_and_per_day` reads the daily cap from policy. 73 tests pass.

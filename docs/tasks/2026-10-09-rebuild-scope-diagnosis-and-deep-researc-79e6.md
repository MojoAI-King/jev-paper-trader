# Task: Rebuild scope: diagnosis and deep research briefs

Kind: Living. Task record.

- **ID:** 2026-10-09-rebuild-scope-diagnosis-and-deep-researc-79e6
- **State:** merged
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-09T21:02:23.304Z

## Request

not yet written

## Acceptance criteria

- [ ] docs/REBUILD_SCOPE.md holds the measured diagnosis (1,133 finished markets) and self-contained deep research briefs Joey can paste into separate tabs; the briefs are published as a page with copy buttons; backlog and handoff updated; Joey has the decisions that are his

## Decisions

not yet written

## Checkpoints

### 2026-10-09T21:02:22.187Z

- **State:** Rebuild scoped (B24): every forecaster is less accurate than the market on 327 real-priced finished markets (Claude direct +0.035, Jev+research +0.043, Jev alone +0.073 Brier); trading costs ~8.4% a bet; blend and resting-order fixes tested and rejected. Five research briefs in docs/REBUILD_SCOPE.md, published at https://claude.ai/artifact/2USu1tPk31NdbK2p1vj5ta (private to Joey). Trader unchanged and running
- **Evidence:** backtests on 1,133 finished markets at the 2026-10-09T20:38Z cycle (scratchpad bt.py); 122 offline tests OK; page screenshot checked once before the last edit; copy buttons not tried in the live viewer
- **Next:** Joey runs briefs 1-5 in claude.ai Research tabs and pastes each report into a session; Claude saves them to docs/research/, does brief 6 (Jev harness) and writes the plan; B25 (score the market only where it has a real price) waits for Joey's yes
- **Git:** master @ d5ffd6a, 2 uncommitted

## Handoff

- **State:** Rebuild scoped (B24): every forecaster is less accurate than the market on 327 real-priced finished markets (Claude direct +0.035, Jev+research +0.043, Jev alone +0.073 Brier); trading costs ~8.4% a bet; blend and resting-order fixes tested and rejected. Five research briefs in docs/REBUILD_SCOPE.md, published at https://claude.ai/artifact/2USu1tPk31NdbK2p1vj5ta (private to Joey). Trader unchanged and running. Evidence: backtests on 1,133 finished markets at the 2026-10-09T20:38Z cycle (scratchpad bt.py); 122 offline tests OK; page screenshot checked once before the last edit; copy buttons not tried in the live viewer.
- **Next:** Joey runs briefs 1-5 in claude.ai Research tabs and pastes each report into a session; Claude saves them to docs/research/, does brief 6 (Jev harness) and writes the plan; B25 (score the market only where it has a real price) waits for Joey's yes
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; never build an unattended job that edits or ships code; quote n and ± with every number (small samples misled us twice)

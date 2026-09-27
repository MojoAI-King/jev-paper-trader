# Task: Joey's calls: challengers self-start, opposing bets and thin markets allowed

Kind: Living. Task record.

- **ID:** 2026-09-27-joey-s-calls-challengers-self-start-oppo-dff6
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-09-27T18:51:42.534Z

## Request

You can do contradicting bets if you think you can get an arbitrage; thin markets up to you; challengers start on their own

## Acceptance criteria

- [ ] auto_start_challengers true with bounds and slot limit tested
- [ ] No block on opposing bets or thin markets; B3 and B15 capture the real improvements

## Decisions

not yet written

## Checkpoints

### 2026-09-27T18:51:42.534Z

- **State:** Challengers now start by themselves within bounds (max 2 running); opposing bets and thin markets stay allowed; trading automatic every ~30 min; 16 open bets, none settled
- **Evidence:** 72 tests pass incl. auto-start, bounds and free-slot tests; decision 2026-09-27-challengers-start-by-themselves-opposing-4dc1
- **Next:** First results around midnight ET feed reviews, the coach and calibration; first weekly retrospective after 10 reviewed markets may start challengers; improvements queued: B3 (linked probabilities fit together), B15 (fill size vs market depth), B13 (phone layout)
- **Git:** master @ b475bda, 16 uncommitted

## Handoff

- **State:** Challengers now start by themselves within bounds (max 2 running); opposing bets and thin markets stay allowed; trading automatic every ~30 min; 16 open bets, none settled. Evidence: 72 tests pass incl. auto-start, bounds and free-slot tests; decision 2026-09-27-challengers-start-by-themselves-opposing-4dc1.
- **Next:** First results around midnight ET feed reviews, the coach and calibration; first weekly retrospective after 10 reviewed markets may start challengers; improvements queued: B3 (linked probabilities fit together), B15 (fill size vs market depth), B13 (phone layout)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)

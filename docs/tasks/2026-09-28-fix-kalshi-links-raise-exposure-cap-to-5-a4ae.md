# Task: Fix Kalshi links; raise exposure cap to 50% and research to 60 a day

Kind: Living. Task record.

- **ID:** 2026-09-28-fix-kalshi-links-raise-exposure-cap-to-5-a4ae
- **State:** verified
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-09-28T21:37:33.694Z

## Request

links go to Kalshi page not found; why so little betting; is it the cap, let them bet unless below 50,000

## Acceptance criteria

not yet written

## Decisions

not yet written

## Checkpoints

### 2026-09-28T21:24:52.082Z

- **State:** Kalshi links fixed (new + old via fix_url); exposure cap 50%, research 60/day
- **Evidence:** 73 tests pass; 0 old-form Kalshi links in the rebuilt summary, 35 new-form; new form opens the event in headless Chrome
- **Next:** Push; confirm the next cycle's summary.json has working links and Bold bets again
- **Git:** master @ 7077969, 11 uncommitted

### 2026-09-28T21:37:33.482Z

- **State:** Kalshi links fixed and verified live (21:36Z summary: 0 old-form, 39 new-form; a repaired link opens its event in Chrome); open-bet cap 50% (Bold now 19 open, past the old 30%); research 60/day
- **Evidence:** 73 tests pass; run 21:34Z success; health Healthy; plan week 5%, 5-hour 12%
- **Next:** Watch a day of cycles: research should run past 5 AM ET and main/Claude direct should bet more; if research goes unused, BACKLOG B16 (widen markets_per_source); B3, B15, B13 queued
- **Git:** master @ 41082cd, 6 uncommitted

## Handoff

- **State:** Kalshi links fixed and verified live (21:36Z summary: 0 old-form, 39 new-form; a repaired link opens its event in Chrome); open-bet cap 50% (Bold now 19 open, past the old 30%); research 60/day. Evidence: 73 tests pass; run 21:34Z success; health Healthy; plan week 5%, 5-hour 12%.
- **Next:** Watch a day of cycles: research should run past 5 AM ET and main/Claude direct should bet more; if research goes unused, BACKLOG B16 (widen markets_per_source); B3, B15, B13 queued
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)

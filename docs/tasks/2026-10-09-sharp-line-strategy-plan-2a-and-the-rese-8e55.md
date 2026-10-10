# Task: Sharp-line strategy (plan 2A) and the research on who makes the money

Kind: Living. Task record.

- **ID:** 2026-10-09-sharp-line-strategy-plan-2a-and-the-rese-8e55
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-10T03:54:35.765Z

## Request

not yet written

## Acceptance criteria

- [ ] The sharp strategy prices games from Pinnacle via The Odds API and bets only through the skill sizing; the line never reaches Jev or Claude; it waits without a key; odds-check validates the key; research report 15 (who makes the money) is in and checked; Joey has the key steps

## Decisions

not yet written

## Checkpoints

### 2026-10-10T03:54:35.765Z

- **State:** Sharp-line strategy built and pushed (b6900cb): papertrade/odds.py (Pinnacle de-vig, matching to our Kalshi/Polymarket game markets, quota-aware cache), strategy 'sharp' with probes via skill sizing, odds-check command; Jev alone retired (ledger still settles). Waiting for Joey's free The Odds API key (gh secret set ODDS_API_KEY + .env). Research report 15 (who makes the money) running in a background agent
- **Evidence:** 138 offline tests OK incl. OddsTests and the full-scan sharp test; odds-check without a key prints the setup steps
- **Next:** Confirm the next cycle runs green on b6900cb; read and check report 15 when it lands; when Joey sets the key, run odds-check and watch the first sharp probes
- **Git:** master @ b6900cb, 3 uncommitted

## Handoff

- **State:** Sharp-line strategy built and pushed (b6900cb): papertrade/odds.py (Pinnacle de-vig, matching to our Kalshi/Polymarket game markets, quota-aware cache), strategy 'sharp' with probes via skill sizing, odds-check command; Jev alone retired (ledger still settles). Waiting for Joey's free The Odds API key (gh secret set ODDS_API_KEY + .env). Research report 15 (who makes the money) running in a background agent. Evidence: 138 offline tests OK incl. OddsTests and the full-scan sharp test; odds-check without a key prints the setup steps.
- **Next:** Confirm the next cycle runs green on b6900cb; read and check report 15 when it lands; when Joey sets the key, run odds-check and watch the first sharp probes
- **Blocked:** nothing
- **Watch out:** Stage files by explicit path only (research tabs may still be open); never run cycle/scan locally; original must keep the old sizing (yardstick)

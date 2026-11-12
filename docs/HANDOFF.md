# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-11-12 00:24 EST

- **State:** Project costs nothing (Joey: keep it free): sharp retired, ODDS_API_KEY out of the workflow, B27 archived. Live: mention_no, mention_follow, favorites on free Kalshi/Polymarket data. Evidence: unittest 172 OK locally and on live cycle 43160661333 (head 5dcdaea3); that cycle's scan has no sharp line, jev_used false.
- **Next:** Joey cancels The Odds API plan at the-odds-api.com; Oct/Nov check-in on the three bots
- **Blocked:** nothing
- **Watch out:** Keep the repo public (private repos pay for Actions minutes); never add a paid feed or ANTHROPIC_API_KEY; a stash holds a reformatted policy.json to discard
- **Git:** master @ 8fa9e493, 6 tracked uncommitted, 5 untracked
- **CI:** master green on GitHub (read 2026-11-12 05:24 UTC)

## Earlier

### 2026-10-26 21:27 EDT
- **State:** American English across the repo (Joey: no British English): page text, comments, tests, docs, review prompt; data keys cancelled_bets/cancelled and file names kept. Evidence: python3 -m unittest discover -s tests -t .: 171 OK.
- **Next:** Watch next cycle: page shows Favorites, no favorites bet under $500, page loss gone; Oct check-in; Kalshi-vs-Pinnacle lag test
- **Blocked:** nothing
- **Watch out:** Score backtests at quotes the strategy could take; a 15-min cadence cannot win a speed race against Kalshi market makers; cancel only bets a named bug placed; a stash holds a reformatted policy.json to discard
- **Git:** master @ 14b66421, 1 tracked uncommitted, 3 untracked
- **CI:** master green on GitHub (read 2026-10-27 01:27 UTC)

### 2026-10-26 20:08 EDT
- **State:** Fun bot review fixes committed: Polymarket books read before betting, no canceled re-buys, daily limit counts settled/canceled, page marks ignore pre-bet prices, $500 minimum bet. Evidence: python3 -m unittest discover -s tests -t .: 171 OK; mutation check: 4 new tests fail without fixes; commit dd988c0c.
- **Next:** Watch next cycle: no favorites bet under $500, Polymarket sizes respected, page loss gone; Oct check-in; Kalshi-vs-Pinnacle lag test
- **Blocked:** nothing
- **Watch out:** Score backtests at quotes the strategy could take; a 15-min cadence cannot win a speed race against Kalshi market makers; cancel only bets a named bug placed; a stash holds a reformatted policy.json to discard
- **Git:** master @ dd988c0c, 2 tracked uncommitted, 3 untracked
- **CI:** master green on GitHub (read 2026-10-27 00:08 UTC)

### 2026-10-26 19:40 EDT
- **State:** New for-fun strategy 'favorites' live: heavy favorites 90-97c settling within 5 days, 1.5% flat bets, up to 40 a day; hard caps 3% and 50/day in code; locked. Safe strategies unchanged. Evidence: 166 offline tests OK; commit 4dcbdf5 pushed to master.
- **Next:** Confirm favorites places bets on the next cycle (health, portfolios/favorites.json); Oct check-in: settled mention bets, mention_forward early read; Kalshi-vs-Pinnacle lag test
- **Blocked:** nothing
- **Watch out:** Score backtests at quotes the strategy could take; a 15-min cadence cannot win a speed race against Kalshi market makers; cancel only bets a named bug placed; a stash holds a reformatted policy.json to discard
- **Git:** master @ 4dcbdf5a, 0 tracked uncommitted, 2 untracked
- **CI:** master green on GitHub (read 2026-10-26 23:40 UTC)

### 2026-10-14 21:08 EDT
- **State:** Sharp's touchdown-prop bug bet canceled and refunded through the cycle (policy.json cancelled_bets, engine.cancel_bets): sharp at 100,000, 0 settled, 1 canceled. Live total about +148. Strategies otherwise unchanged; all healthy. Evidence: 163 offline tests OK; 6489a01 pushed; cycle 3319ddd (01:08Z) applied it; python3 -m papertrade health.
- **Next:** Oct 19 check-in: trading-health, settled mention bets, mention_forward.py early read; test whether Kalshi game lines lag Pinnacle moves (Odds API historical vs Kalshi 1-min candles); then follow-first-trade in gas ladders
- **Blocked:** nothing
- **Watch out:** Score backtests at quotes the strategy could take; a 15-min cadence cannot win a speed race against Kalshi market makers; cancel only bets a named bug placed; a stash holds a reformatted policy.json to discard
- **Git:** master @ 3319ddd, 1 tracked uncommitted, 3 untracked
- **CI:** master green on GitHub (read 2026-10-15 01:08 UTC)

### 2026-10-14 20:43 EDT
- **State:** Read-only check 2026-10-15: all healthy. sharp placed no bets since the Oct 11 fix: 60 looks at 27 games, Kalshi mid within ~1c of Pinnacle (median), best edge after fees +0.5% vs the 3% gate. mention_no 36 open probes (12 settled, +168), mention_follow 7 open probes (1 settled, -20). Evidence: python3 -m papertrade health (cycle 00:35Z healthy); sharp.jsonl and portfolios/*.json read at 932c49a.
- **Next:** Oct 19 check-in: trading-health, settled mention bets, mention_forward.py early read; test whether Kalshi game lines lag Pinnacle moves (Odds API historical snapshots vs Kalshi 1-min candles) before any faster sharp cadence; then follow-first-trade in gas ladders
- **Blocked:** nothing
- **Watch out:** Score backtests at quotes the strategy could take; a 15-min cadence cannot win a speed race against Kalshi market makers; post-mortems and the daily review still use Claude
- **Git:** master @ 932c49a, 2 tracked uncommitted, 3 untracked
- **CI:** master green on GitHub (read 2026-10-15 00:43 UTC)

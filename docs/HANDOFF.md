# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-11-12 01:31 EST

- **State:** Project costs nothing: sharp retired, ODDS_API_KEY out of the workflow, and Joey reports he cancelled The Odds API plan (2026-11-12, user-reported in chat, not checked on the vendor's site). Live bots: mention_no, mention_follow, favorites on free Kalshi/Polymarket data. Evidence: Joey in chat 2026-11-12: I cancelled it; live cycle 43160661333 showed no sharp line and jev_used false.
- **Next:** Check-in on the three bots (trading-health, settled bets, page)
- **Blocked:** nothing
- **Watch out:** Keep the repo public (private repos pay for Actions minutes); never add a paid feed or ANTHROPIC_API_KEY; a stash holds a reformatted policy.json to discard
- **Git:** master @ 151f981e, 0 tracked uncommitted, 2 untracked
- **CI:** master green on GitHub (read 2026-11-12 06:31 UTC)

## Earlier

### 2026-11-12 01:12 EST
- **State:** Project costs nothing: sharp retired, ODDS_API_KEY out of the workflow; live bots mention_no, mention_follow, favorites on free data. Joey asked me to cancel The Odds API plan in his browser; the Chrome extension is not connected (no browsers listed), so it is not cancelled. Evidence: tabs_context_mcp: extension not connected (twice); list_connected_browsers: empty.
- **Next:** Joey connects the Claude Chrome extension and says go (I cancel at the-odds-api.com; he signs in himself if asked), or cancels it himself; then the three bots' check-in
- **Blocked:** Odds API cancel: Chrome extension not connected
- **Watch out:** Keep the repo public (private repos pay for Actions minutes); never add a paid feed or ANTHROPIC_API_KEY; a stash holds a reformatted policy.json to discard
- **Git:** master @ e6158150, 0 tracked uncommitted, 2 untracked
- **CI:** master green on GitHub (read 2026-11-12 06:12 UTC)

### 2026-11-12 00:24 EST
- **State:** Project costs nothing (Joey: keep it free): sharp retired, ODDS_API_KEY out of the workflow, B27 archived. Live: mention_no, mention_follow, favorites on free Kalshi/Polymarket data. Evidence: unittest 172 OK locally and on live cycle 43160661333 (head 5dcdaea3); that cycle's scan has no sharp line, jev_used false.
- **Next:** Joey cancels The Odds API plan at the-odds-api.com; Oct/Nov check-in on the three bots
- **Blocked:** nothing
- **Watch out:** Keep the repo public (private repos pay for Actions minutes); never add a paid feed or ANTHROPIC_API_KEY; a stash holds a reformatted policy.json to discard
- **Git:** master @ 8fa9e493, 6 tracked uncommitted, 5 untracked
- **CI:** master green on GitHub (read 2026-11-12 05:24 UTC)

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

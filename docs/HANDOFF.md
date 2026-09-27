# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-09-27 11:01 EDT

- **State:** Live: hourly GitHub runs (Claude on the Claude Max plan via CLAUDE_CODE_OAUTH_TOKEN, never an API key) trade three fake-$100k strategies (Jev+research, Jev alone, Claude direct); page https://jev-paper-trader.greekgod.workers.dev reads papertrade_data/summary.json from the public repo MojoAI-King/jev-paper-trader; no bets yet (Jev's info score stays under 0.5). Evidence: 53 offline tests pass; price-leak tests fail with the screen off; GitHub run 36326789989 succeeded (40 judged, 13 with research, ledgers committed a96cbb8); live page and GitHub summary.json checked by plain request and headless Chrome.
- **Next:** Confirm the next scheduled hourly runs land (Actions tab); after a few days, review price-screen drops (8 of 53 facts dropped by the price-match rule, likely polls) and decide whether to narrow it; consider making linked markets' probabilities add up (Lula 38% + Bolsonaro 23%) as a challenger strategy
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY anywhere (it switches Claude to paid API billing; research refuses to run); don't run cycles on the Mac while GitHub runs them (two writers); Claude plan weekly usage 78% (research pauses at 85%, resets Mon 3 AM ET); pause trading with: gh variable set TRADING_ENABLED --body false --repo MojoAI-King/jev-paper-trader
- **Git:** master @ 438d284, 6 uncommitted

## Earlier

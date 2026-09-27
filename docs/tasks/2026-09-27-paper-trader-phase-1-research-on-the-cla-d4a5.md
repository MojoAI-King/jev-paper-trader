# Task: Paper trader phase 1: research on the Claude plan, hourly trading, public page

Kind: Living. Task record.

- **ID:** 2026-09-27-paper-trader-phase-1-research-on-the-cla-d4a5
- **State:** verified
- **Branch:** master
- **Owner:** Joey
- **Updated:** 2026-09-27T15:01:47.088Z

## Request

Fix Polymarket, add a news step and a with/without-news check, then run it all day on the Claude plan and host a page for friends

## Acceptance criteria

- [ ] Polymarket returns Yes/No markets (regression test)
- [ ] Research runs through Claude Code on the Claude plan, never an API key (refuses if a key is set)
- [ ] Jev never sees a market price, directly or through research (tests fail with the screen off)
- [ ] Hourly GitHub runs trade three strategies and commit ledgers; the public page reads them

## Decisions

not yet written

## Checkpoints

### 2026-09-27T15:01:38.613Z

- **State:** Live: hourly GitHub runs (Claude on the Claude Max plan via CLAUDE_CODE_OAUTH_TOKEN, never an API key) trade three fake-$100k strategies (Jev+research, Jev alone, Claude direct); page https://jev-paper-trader.greekgod.workers.dev reads papertrade_data/summary.json from the public repo MojoAI-King/jev-paper-trader; no bets yet (Jev's info score stays under 0.5)
- **Evidence:** 53 offline tests pass; price-leak tests fail with the screen off; GitHub run 36326789989 succeeded (40 judged, 13 with research, ledgers committed a96cbb8); live page and GitHub summary.json checked by plain request and headless Chrome
- **Next:** Confirm the next scheduled hourly runs land (Actions tab); after a few days, review price-screen drops (8 of 53 facts dropped by the price-match rule, likely polls) and decide whether to narrow it; consider making linked markets' probabilities add up (Lula 38% + Bolsonaro 23%) as a challenger strategy
- **Git:** master @ 438d284, 6 uncommitted

## Handoff

- **State:** Live: hourly GitHub runs (Claude on the Claude Max plan via CLAUDE_CODE_OAUTH_TOKEN, never an API key) trade three fake-$100k strategies (Jev+research, Jev alone, Claude direct); page https://jev-paper-trader.greekgod.workers.dev reads papertrade_data/summary.json from the public repo MojoAI-King/jev-paper-trader; no bets yet (Jev's info score stays under 0.5). Evidence: 53 offline tests pass; price-leak tests fail with the screen off; GitHub run 36326789989 succeeded (40 judged, 13 with research, ledgers committed a96cbb8); live page and GitHub summary.json checked by plain request and headless Chrome.
- **Next:** Confirm the next scheduled hourly runs land (Actions tab); after a few days, review price-screen drops (8 of 53 facts dropped by the price-match rule, likely polls) and decide whether to narrow it; consider making linked markets' probabilities add up (Lula 38% + Bolsonaro 23%) as a challenger strategy
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY anywhere (it switches Claude to paid API billing; research refuses to run); don't run cycles on the Mac while GitHub runs them (two writers); Claude plan weekly usage 78% (research pauses at 85%, resets Mon 3 AM ET); pause trading with: gh variable set TRADING_ENABLED --body false --repo MojoAI-King/jev-paper-trader

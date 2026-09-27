# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-09-27 14:47 EDT

- **State:** Trading automatically every ~30 min via the Cloudflare trigger (verified 18:04/18:34 UTC); 5 strategies, 16 open bets, none settled; learning loop merged and running in every cycle (playbook v0, 0 resolved); mission-control page live with settled vs not-settled money, plain strategy names, chart floor of +/-5%, big-monitor scaling. Evidence: 72 tests pass; runs 36339317403 and 36341181637 started by Cloudflare; live page checked by request and headless Chrome at 1440x900 and 2550x1281.
- **Next:** First results around midnight ET feed the review, coach and calibration loops; Joey to decide B3 (no contradicting bets in one event), B14 (thin-market filter), B12 (auto-start challengers); phone layout later (B13)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the GitHub dispatch token lives only as a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ 63b4576, 9 uncommitted

## Earlier

### 2026-09-27 14:36 EDT
- **State:** Automatic: Cloudflare trigger started runs 36339317403 (18:04 UTC, skipped by the 25-minute gate) and 36341181637 (18:34 UTC, full cycle, 1 bold bet) on its own after Joey set GITHUB_DISPATCH_TOKEN; mission-control page live. Evidence: wrangler secret list shows GITHUB_DISPATCH_TOKEN; both runs are workflow_dispatch with nobody starting them; run logs show the gate message and the funnel.
- **Next:** Check in with python3 -m papertrade health or the page; first results arrive as markets close (first one around midnight ET); linked-market contradictions (B3) are the next improvement; phone layout later (B13)
- **Blocked:** nothing
- **Watch out:** The GitHub token expires in a year (docs/OPERATIONS.md); GitHub's own schedule stays unreliable and is only a backup; Claude plan week at 81%, resets Mon 3 AM ET
- **Git:** master @ d8b0fe6, 2 uncommitted

### 2026-09-27 12:45 EDT
- **State:** Mission-control page live (Worker 4c6ee8a0); Kalshi 4 requests/fetch, 120 markets fetched in run 36333603111 where main placed its first bet; Cloudflare cron trigger deployed at :04/:34 but idle until GITHUB_DISPATCH_TOKEN is set; GitHub schedule (backup) skipped every slot today. Evidence: Run 36333603111: 120 fetched, 0 errors, bets main 1 claude_direct 1 bold 5; 72 tests pass; live page checked in headless Chrome 1440x900 with the 12:32 ET data; health: Healthy.
- **Next:** Joey sets GITHUB_DISPATCH_TOKEN (docs/OPERATIONS.md 'What starts a cycle'); then confirm a run lands at the next :04/:34 and the page updates; phone layout later (B13)
- **Blocked:** Automatic cycles wait on Joey's token (B1)
- **Watch out:** Until the token is set, cycles only run when GitHub's schedule fires or someone runs gh workflow run; never put the token in chat or a file; the Mac background job was removed (permission check: unapproved persistence)
- **Git:** master @ d6640f6, 3 uncommitted

### 2026-09-27 11:59 EDT
- **State:** Live and trading: 5 fake-$100k strategies (main, Jev alone, Claude direct, bold, self-calibrating); bold placed 7 bets in run 36329790430; learning loop merged (87801e5); page redesign on branch page-redesign (a0cd87e), private preview https://claude.ai/artifact/TP84qLCdrVPHPnRaBTcEAf. Evidence: 71 tests pass; 5 new guards fail when switched off; run 36329790430 success (bold 7 bets); 390px iframe check of the new page.
- **Next:** Confirm a scheduled (cron) run lands at :23 and runs the learning-loop code (python3 -m papertrade health); ship the page redesign when Joey OKs it (BACKLOG B11); if cron keeps skipping, B10
- **Blocked:** Page redesign ships on Joey's OK
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer (no cycles on the Mac); weekly research pause lifted, so a full week also blocks Joey's own Claude until the Monday 3 AM ET reset; auto_start_challengers stays false until Joey decides (B12)
- **Git:** master @ 3574102, 5 uncommitted

### 2026-09-27 11:01 EDT
- **State:** Live: hourly GitHub runs (Claude on the Claude Max plan via CLAUDE_CODE_OAUTH_TOKEN, never an API key) trade three fake-$100k strategies (Jev+research, Jev alone, Claude direct); page https://jev-paper-trader.greekgod.workers.dev reads papertrade_data/summary.json from the public repo MojoAI-King/jev-paper-trader; no bets yet (Jev's info score stays under 0.5). Evidence: 53 offline tests pass; price-leak tests fail with the screen off; GitHub run 36326789989 succeeded (40 judged, 13 with research, ledgers committed a96cbb8); live page and GitHub summary.json checked by plain request and headless Chrome.
- **Next:** Confirm the next scheduled hourly runs land (Actions tab); after a few days, review price-screen drops (8 of 53 facts dropped by the price-match rule, likely polls) and decide whether to narrow it; consider making linked markets' probabilities add up (Lula 38% + Bolsonaro 23%) as a challenger strategy
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY anywhere (it switches Claude to paid API billing; research refuses to run); don't run cycles on the Mac while GitHub runs them (two writers); Claude plan weekly usage 78% (research pauses at 85%, resets Mon 3 AM ET); pause trading with: gh variable set TRADING_ENABLED --body false --repo MojoAI-King/jev-paper-trader
- **Git:** master @ 438d284, 6 uncommitted

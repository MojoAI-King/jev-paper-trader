# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-09 17:02 EDT

- **State:** Rebuild scoped (B24): every forecaster is less accurate than the market on 327 real-priced finished markets (Claude direct +0.035, Jev+research +0.043, Jev alone +0.073 Brier); trading costs ~8.4% a bet; blend and resting-order fixes tested and rejected. Five research briefs in docs/REBUILD_SCOPE.md, published at https://claude.ai/artifact/2USu1tPk31NdbK2p1vj5ta (private to Joey). Trader unchanged and running. Evidence: backtests on 1,133 finished markets at the 2026-10-09T20:38Z cycle (scratchpad bt.py); 122 offline tests OK; page screenshot checked once before the last edit; copy buttons not tried in the live viewer.
- **Next:** Joey runs briefs 1-5 in claude.ai Research tabs and pastes each report into a session; Claude saves them to docs/research/, does brief 6 (Jev harness) and writes the plan; B25 (score the market only where it has a real price) waits for Joey's yes
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; never build an unattended job that edits or ships code; quote n and ± with every number (small samples misled us twice)
- **Git:** master @ d5ffd6a, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:02 UTC)

## Earlier

### 2026-10-01 22:36 EDT
- **State:** Forecasters panel live and verified (task closed): cycle 2026-10-02T02:36Z wrote calibration.paired, 112 markets: market 0.120, Jev + research 0.185, Claude direct 0.196, Jev alone 0.243; live page screenshot shows it filled. Evidence: summary.json on origin at 3591381; headless screenshot of https://jev-paper-trader.greekgod.workers.dev at 1280px.
- **Next:** Watch the post-floor bets settle (8 close 2026-10-06) vs original; research resumes after the 2026-10-05 08:00Z week reset
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the week meter rose 68 to 82% while the trader made 0-1 calls, so other use on that account is filling it (not verified); never build an unattended job that edits or ships code
- **Git:** master @ 3591381, 4 uncommitted

### 2026-10-01 22:22 EDT
- **State:** Forecasters panel built (engine.paired, page panel under the feed, report lines), p7 approved, committed 3a605d0 and pushed; page shell deployed (Worker version 1e638bb3), live HTML equals the build. Not yet verified: the live panel's numbers, which appear once a cycle on the new code writes summary.json. Evidence: 122 offline tests OK incl. test_forecasters_are_scored_head_to_head_on_the_same_markets; screenshots at 1600, 1280 and a true 400px frame; local paired scores on 111 markets: market 0.119, Jev + research 0.184, Claude direct 0.195, Jev alone 0.241.
- **Next:** Confirm summary.json on origin carries calibration.paired and the live page shows the panel filled; then close the task as verified. Watch the post-floor bets settle (8 close 2026-10-06)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the week meter rose 68 to 82% while the trader made 0-1 calls, so other use on that account is filling it (not verified); never build an unattended job that edits or ships code
- **Git:** master @ 3a605d0, 6 uncommitted

### 2026-10-01 22:15 EDT
- **State:** Answered Joey: is Jev doing anything. Jev alone is near a coin flip (Brier 0.225); Jev + research is our best forecaster (0.177, Claude direct 0.198); the market beats all (0.133). Research stays on Opus (Joey worried Sonnet would hurt). Offered the forecaster scoreboard panel on the page (proposal p7, a code change), waiting for Joey. Evidence: scratchpad jevcheck.py and maxedge.py over 205 resolved markets in papertrade_data; tests OK.
- **Next:** Joey's yes/no on the scoreboard panel (p7); watch the post-floor bets settle (8 close 2026-10-06) vs original; research resumes after the 2026-10-05 08:00Z week reset
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the week meter rose 68 to 82% while the trader made 0-1 calls, so other use on that account is filling it (not verified); never build an unattended job that edits or ships code
- **Git:** master @ 99cac63, 3 uncommitted

### 2026-10-01 21:50 EDT
- **State:** Joey kept the categories (B23 declined, archived). Explained the losses: all 70 settled bets predate the 30c floor; 38 long shots under 30c lost 61.3k of the 62.4k; forecasters expected 38.9 wins, market 21.6, got 18; 36 pre-floor long shots (63k) still open through 2026-10-26; 13 post-floor bets open, none settled. Evidence: portfolio ledgers at 6497235+ (closed and open bets by price paid, claimed edge, opened before/after 2026-10-01T04:19Z); scans.jsonl week meter 0.44 to 0.82, research held by the pace guard since about 14:30Z 2026-10-01.
- **Next:** Watch the first post-floor bets settle (8 close 2026-10-06) vs original; Joey decides if research may spend the rest of the week (pace guard holds it until the 2026-10-05 08:00Z reset)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the week meter rose 68 to 82% while the trader made 0-1 calls, so other use on that account is filling it (not verified); never build an unattended job that edits or ships code
- **Git:** master @ 6497235, 4 uncommitted

### 2026-10-01 21:42 EDT
- **State:** Joey asked about politics only: data says no (worst category, almost no resolutions). Losses since the floor are all pre-floor bets settling (20 settled: 2 won, -26.7k, 17 under 30c); 13 post-floor bets still open. Proposed B23 (skip politics, culture, economy, world), waiting for Joey. Evidence: settled-bet breakdown by category; flat-$100 simulation on every resolved market with the 30c floor, by category and forecaster.
- **Next:** Joey's yes/no on B23; then python3 -m papertrade tune for each strategy but original and push papertrade_data
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 27% at 04:06Z on 2026-09-29, much of it this session's review workflows (resets Mon 3 AM ET); never build an unattended job that edits or ships code (Joey, 2026-09-28)
- **Git:** master @ 60c4177, 2 uncommitted

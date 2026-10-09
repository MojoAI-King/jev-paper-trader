# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-09 17:53 EDT

- **State:** B26 (each Polymarket market pays its own published taker fee; 0.05 default) and B25 (head-to-head scores only on real-priced markets, left-out count shown) committed at c5f54c2, pushed, page deployed (Worker 996e8d0c). Live check pending: edge cache still served the old page at 21:53Z; the next cycle must write paired.left_out and fee_rate. Reports 01, 05, 06, 07 in and checked; no category skips (losses since the floor are sports and other, not weather or price thresholds). Evidence: 125 offline tests OK (FeeTests, updated paired test); live paired preview 562 markets, 101 left out; Polymarket API feeSchedule seen live (politics 0.04, geopolitics off).
- **Next:** Confirm the live page and the 22:04Z cycle (paired.left_out in summary.json, fee_rate on new Polymarket judgments), then archive B25 and B26 and close the task; keep checking reports as Joey calls them done
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: add report files by name; past Polymarket bets keep their old zero-fee cost (not rewritten)
- **Git:** master @ c5f54c2, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:53 UTC)

## Earlier

### 2026-10-09 17:45 EDT
- **State:** Reports 01, 05, 07 in and checked (docs/research/CHECKS.md): on real-priced markets the price is about calibrated and none of our forecasters adds information; cheap contracts lose ~60%, favourites break even; weather markets are hard to beat. 06 running; 09, 10, 14, 02, 03, 04, 08, 11, 12, 13 handed out by a dispatcher tab from docs/research/prompts/. New: B26 (Polymarket taker fees, trader charges 0). Evidence: event-clustered bootstrap refits on 1,006 real-priced first looks; price-bucket returns by venue; WebFetch of AIA (2511.07678), Kim (2602.21229), Crosier (2609.23969), docs.polymarket.com/trading/fees and Kalshi KXHIGHNY rules; 122 tests OK.
- **Next:** Process each report as Joey says it's done: commit only that file, check it into CHECKS.md, mark the run sheet; then the plan. Joey decides B25 and B26
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: add report files by name, never git add -A; don't commit a report Joey hasn't called done; all tabs draw on Joey's Claude plan
- **Git:** master @ 8bf4adf, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:45 UTC)

### 2026-10-09 17:17 EDT
- **State:** Fourteen narrow research briefs ready; Joey asked for one paste-ready prompt at a time and runs each as its own Claude Code tab with the deep-research skill on Opus 5.5 high. Order given: 01, 05, 06, 07, 09, 10, 14, then 02, 03, 04, 08, 11, 12, 13. Prompts are built from the brief files (scratchpad paste.py). No reports yet. Evidence: briefs committed; README rule fixed so a tab carries on after declining a hook reminder.
- **Next:** Hand Joey the next prompt when he asks; when tabs finish, commit the reports, mark them in the run sheet, check claims against papertrade_data, write the plan
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: never git add -A or commit their half-written reports mid-run; they must not run cycle/scan/settle/review or skilliton; all of them draw on Joey's Claude plan (week 47%, resets Mon 2026-10-12 08:00Z)
- **Git:** master @ 87b85c3, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:17 UTC)

### 2026-10-09 17:16 EDT
- **State:** Fourteen narrow research briefs ready in docs/research/briefs/ (run sheet docs/research/README.md; page https://claude.ai/artifact/2USu1tPk31NdbK2p1vj5ta). Joey runs each as its own Claude Code tab, all at once; each tab writes only docs/research/NN-<slug>.md and does not commit. No reports yet. Evidence: briefs committed at 8d23ab7; 122 offline tests OK; run-sheet page checked once by screenshot.
- **Next:** When the tabs finish: commit the reports, mark them done in the run sheet, check each report's claims against papertrade_data, then write the plan (strategies, backtests to pass, code changes for Joey to approve)
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: never git add -A or commit their half-written reports mid-run; they must not run cycle/scan/settle/review or skilliton; all of them draw on Joey's Claude plan (week 47%, resets Mon 2026-10-12 08:00Z)
- **Git:** master @ 8d23ab7, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:16 UTC)

### 2026-10-09 17:02 EDT
- **State:** Rebuild scoped (B24): every forecaster is less accurate than the market on 327 real-priced finished markets (Claude direct +0.035, Jev+research +0.043, Jev alone +0.073 Brier); trading costs ~8.4% a bet; blend and resting-order fixes tested and rejected. Five research briefs in docs/REBUILD_SCOPE.md, published at https://claude.ai/artifact/2USu1tPk31NdbK2p1vj5ta (private to Joey). Trader unchanged and running. Evidence: backtests on 1,133 finished markets at the 2026-10-09T20:38Z cycle (scratchpad bt.py); 122 offline tests OK; page screenshot checked once before the last edit; copy buttons not tried in the live viewer.
- **Next:** Joey runs briefs 1-5 in claude.ai Research tabs and pastes each report into a session; Claude saves them to docs/research/, does brief 6 (Jev harness) and writes the plan; B25 (score the market only where it has a real price) waits for Joey's yes
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; never build an unattended job that edits or ships code; quote n and ± with every number (small samples misled us twice)
- **Git:** master @ d5ffd6a, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-09 21:02 UTC)

### 2026-10-01 22:36 EDT
- **State:** Forecasters panel live and verified (task closed): cycle 2026-10-02T02:36Z wrote calibration.paired, 112 markets: market 0.120, Jev + research 0.185, Claude direct 0.196, Jev alone 0.243; live page screenshot shows it filled. Evidence: summary.json on origin at 3591381; headless screenshot of https://jev-paper-trader.greekgod.workers.dev at 1280px.
- **Next:** Watch the post-floor bets settle (8 close 2026-10-06) vs original; research resumes after the 2026-10-05 08:00Z week reset
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the week meter rose 68 to 82% while the trader made 0-1 calls, so other use on that account is filling it (not verified); never build an unattended job that edits or ships code
- **Git:** master @ 3591381, 4 uncommitted

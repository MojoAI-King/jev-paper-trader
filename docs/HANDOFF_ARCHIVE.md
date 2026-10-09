# Handoff archive

Kind: Reference. The current handoff is `docs/HANDOFF.md`.

### 2026-10-01 21:42 EDT
- **State:** Joey asked about politics only: data says no (worst category, almost no resolutions). Losses since the floor are all pre-floor bets settling (20 settled: 2 won, -26.7k, 17 under 30c); 13 post-floor bets still open. Proposed B23 (skip politics, culture, economy, world), waiting for Joey. Evidence: settled-bet breakdown by category; flat-$100 simulation on every resolved market with the 30c floor, by category and forecaster.
- **Next:** Joey's yes/no on B23; then python3 -m papertrade tune for each strategy but original and push papertrade_data
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 27% at 04:06Z on 2026-09-29, much of it this session's review workflows (resets Mon 3 AM ET); never build an unattended job that edits or ships code (Joey, 2026-09-28)
- **Git:** master @ 60c4177, 2 uncommitted

### 2026-10-01 01:04 EDT
- **State:** Verified: research back on Joey's current Claude account (run 36816087586 at 04:39Z: 10 new research runs, 22 Claude calls, week 41%, 5-hour 40%); 30c floor, 150 research/day with week pace guard, review twice daily, 100 markets/source all live. Ledger audit clean (9 ledgers add up; 32 settled markets match the exchanges; page equals ledgers). Evidence: 121 tests OK; health run success; audit script output.
- **Next:** Check in: bets/wins/losses since 2026-10-01 vs original; what the twice-daily review changed; plan meter vs the pace guard
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 27% at 04:06Z on 2026-09-29, much of it this session's review workflows (resets Mon 3 AM ET); never build an unattended job that edits or ships code (Joey, 2026-09-28)
- **Git:** master @ a1e13d0, 3 uncommitted

### 2026-10-01 00:10 EDT
- **State:** Diagnosed losses (read-only): long shots under 30c caused -32.6k of -35.7k settled; options in BACKLOG B22 put to Joey; nothing changed yet. Claude week 100%: daily review and research paused until Mon 3 AM ET. Evidence: health Healthy 04:04Z 2026-10-01; settled-bet breakdown from papertrade_data/portfolios (50 bets, 32 markets).
- **Next:** Joey's answer on B22: min_ask 0.30 by hand, approve p4/p7, market-shrink code idea
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 27% at 04:06Z on 2026-09-29, much of it this session's review workflows (resets Mon 3 AM ET); never build an unattended job that edits or ships code (Joey, 2026-09-28)
- **Git:** master @ f99f53b, 2 uncommitted

### 2026-09-29 00:07 EDT
- **State:** Verified live: run 36519949032 (04:04Z) on 44b97f1 succeeded; original.json created 04:04:29Z and bet; new bets carry rules_version; decisions record min_edge; summary.json has auto_tune, rule_changes, ideas_for_joey, original slot y; page shell deployed and identical to the build. Evidence: health Healthy at 04:06Z (7 strategies, 4 bets that cycle incl. original 1); 117 tests pass; curl of summary.json and the page.
- **Next:** First daily review at the first cycle after ~2026-09-29 23:12Z: read what it changed and check the page shows it (BACKLOG B21). Joey's open choices B17-B20 still wait; code ideas the loop files wait for his approve/reject (`python3 -m papertrade learn`)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 27% at 04:06Z on 2026-09-29, much of it this session's review workflows (resets Mon 3 AM ET); never build an unattended job that edits or ships code (Joey, 2026-09-28)
- **Git:** master @ 040fef0, 5 uncommitted

### 2026-09-28 21:22 EDT
- **State:** More-action change live and verified: 120 markets pass a cycle, 8 bets on the first cycle, main +$3,378 on its first two wins, early Kalshi results and voids working; the 80-market wave cleared (01:03Z judged 13). Evidence: health Healthy at 01:03Z; 88 tests pass; skilliton maintain run.
- **Next:** After a day: measure bets/day, research use and deferred, then decide B16 (markets_per_source ~100). Joey's open choices: B17 one bet per event, B18 scoring, B19 page additions, B20 weekly Claude guard (week 19% at 01:03Z, much of it this session's analysis)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ 6009b40, 2 uncommitted

### 2026-09-28 19:14 EDT
- **State:** Verified on GitHub: 23:04Z cycle ran the new code (Kalshi 35 pages/61s, 120 passing, 8 bets, 7 early Kalshi results + 5 voids, first retro). Evidence: run 36495992909 success 8m26s; health Healthy; scans.jsonl funnel.fetch recorded; 88 tests pass.
- **Next:** Watch deferred fall to 0 over the next cycles; after a day, measure bets/day and research use, then decide B16 (markets_per_source 100); options B17-B20 wait for Joey
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ e8a91da, 4 uncommitted

### 2026-09-28 17:37 EDT
- **State:** Kalshi links fixed and verified live (21:36Z summary: 0 old-form, 39 new-form; a repaired link opens its event in Chrome); open-bet cap 50% (Bold now 19 open, past the old 30%); research 60/day. Evidence: 73 tests pass; run 21:34Z success; health Healthy; plan week 5%, 5-hour 12%.
- **Next:** Watch a day of cycles: research should run past 5 AM ET and main/Claude direct should bet more; if research goes unused, BACKLOG B16 (widen markets_per_source); B3, B15, B13 queued
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ 41082cd, 6 uncommitted

### 2026-09-27 15:02 EDT
- **State:** Page back at 1x everywhere (Worker 5536aa80, live checked); main's Headline tag dropped in policy.json, hover blurbs say Jev + Claude. Evidence: 72 tests pass; live page byte-equal to the new build, no zoom rules; tag leaves the page at the next cycle's summary.json.
- **Next:** Next cycle (~19:04 UTC) regenerates summary.json without the tag; then nothing queued beyond BACKLOG B3, B15, B13
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ 9b395f9, 4 uncommitted

### 2026-09-27 14:51 EDT
- **State:** Challengers now start by themselves within bounds (max 2 running); opposing bets and thin markets stay allowed; trading automatic every ~30 min; 16 open bets, none settled. Evidence: 72 tests pass incl. auto-start, bounds and free-slot tests; decision 2026-09-27-challengers-start-by-themselves-opposing-4dc1.
- **Next:** First results around midnight ET feed reviews, the coach and calibration; first weekly retrospective after 10 reviewed markets may start challengers; improvements queued: B3 (linked probabilities fit together), B15 (fill size vs market depth), B13 (phone layout)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ b475bda, 16 uncommitted

### 2026-09-27 14:47 EDT
- **State:** Trading automatically every ~30 min via the Cloudflare trigger (verified 18:04/18:34 UTC); 5 strategies, 16 open bets, none settled; learning loop merged and running in every cycle (playbook v0, 0 resolved); mission-control page live with settled vs not-settled money, plain strategy names, chart floor of +/-5%, big-monitor scaling. Evidence: 72 tests pass; runs 36339317403 and 36341181637 started by Cloudflare; live page checked by request and headless Chrome at 1440x900 and 2550x1281.
- **Next:** First results around midnight ET feed the review, coach and calibration loops; Joey to decide B3 (no contradicting bets in one event), B14 (thin-market filter), B12 (auto-start challengers); phone layout later (B13)
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the GitHub dispatch token lives only as a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)
- **Git:** master @ 63b4576, 9 uncommitted

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

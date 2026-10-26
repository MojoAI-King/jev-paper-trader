# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-26 19:40 EDT

- **State:** New for-fun strategy 'favorites' live: heavy favourites 90-97c settling within 5 days, 1.5% flat bets, up to 40 a day; hard caps 3% and 50/day in code; locked. Safe strategies unchanged. Evidence: 166 offline tests OK; commit 4dcbdf5 pushed to master.
- **Next:** Confirm favorites places bets on the next cycle (health, portfolios/favorites.json); Oct check-in: settled mention bets, mention_forward early read; Kalshi-vs-Pinnacle lag test
- **Blocked:** nothing
- **Watch out:** Score backtests at quotes the strategy could take; a 15-min cadence cannot win a speed race against Kalshi market makers; cancel only bets a named bug placed; a stash holds a reformatted policy.json to discard
- **Git:** master @ 4dcbdf5a, 0 tracked uncommitted, 2 untracked
- **CI:** master green on GitHub (read 2026-10-26 23:40 UTC)

## Earlier

### 2026-10-14 21:08 EDT
- **State:** Sharp's touchdown-prop bug bet cancelled and refunded through the cycle (policy.json cancelled_bets, engine.cancel_bets): sharp at 100,000, 0 settled, 1 cancelled. Live total about +148. Strategies otherwise unchanged; all healthy. Evidence: 163 offline tests OK; 6489a01 pushed; cycle 3319ddd (01:08Z) applied it; python3 -m papertrade health.
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

### 2026-10-12 01:02 EDT
- **State:** Session closed by Joey. Live: sharp (paid odds, own pass, Kalshi walk fixed), mention_no and mention_follow (both pre-registered and locked); all forecaster strategies and original retired; no Jev or research calls. Maintenance recorded. Evidence: 161 offline tests OK; run 38196326048 success; skilliton maintain --apply.
- **Next:** Check-in in about a week (around Oct 19): trading-health, settled mention bets, mention_forward.py early read; next research: follow-first-trade in gas ladders at quoted prices
- **Blocked:** nothing
- **Watch out:** Score backtests at quotes the strategy could take; Kalshi sometimes times out (walk shrinks pages); post-mortems and the daily review still use Claude
- **Git:** master @ 8d775c5, 0 tracked uncommitted, 2 untracked
- **CI:** master green on GitHub (read 2026-10-12 05:02 UTC)

### 2026-10-11 22:42 EDT
- **State:** Live on Joey's standing permission (2026-10-12): original retired; mention_follow built, hardened after an adversarial review (wf_d1c03f32-477), pre-registered and locked; no Jev or research calls when nothing uses them (jev_used false, judged 0); Kalshi 504 fix (15286af): run 38196326048 read 58 pages with no error (was 5), sharp matched 7 games. Follow research rerun with full-precision ordering: +18.1% at 15 min holds. Evidence: 161 offline tests OK; runs 38195337805 and 38196326048 success; read-only live walk 32 pages no error; kalshi_first_trade live check on 3 markets.
- **Next:** Let sharp, mention_no and mention_follow run; early read on the mention strategies in 2-3 weeks (mention_forward.py); next research: follow-first-trade in other families (gas ladders) at quoted prices
- **Blocked:** nothing
- **Watch out:** Kalshi answers slowly at times: the walk now shrinks pages on 504 and stops at its 300 s budget; post-mortems and the daily review still use Claude
- **Git:** master @ 6677104, 0 tracked uncommitted, 2 untracked
- **CI:** master green on GitHub (read 2026-10-12 02:42 UTC)

### 2026-10-11 21:04 EDT
- **State:** Follow-first-trade tested at quoted prices (7b455a6; the workflow attempt hit the plan's session limit, redone as a script): following a NO first trade in new mention markets +18.1% [-1.3, +35.1] at 15 min (108 buys, 62 events, both halves positive; +16% to +21% at 1-60 min); following YES -4% to -25%; placebo NO about 0. Proposed to Joey: a new paper strategy mention_follow (code change). Live: 27 cycles since 18:05Z, one transient Kalshi 504; the touchdown-prop sharp bet settled -249.55 (excluded); mention_no 32 open. Evidence: follow_first_trade.py --summarize on 2,306 markets; 155 offline tests OK.
- **Next:** On Joey's yes: pre-register mention_follow in EXPERIMENTS.md, build it (first-trade side via the trades endpoint, NO at the quoted ask within the next cycle), tests, lock it
- **Blocked:** mention_follow waits for Joey's yes
- **Watch out:** Five parallel research agents hit the Claude plan's session limit; keep research to scripts or one agent at a time
- **Git:** master @ 7b455a6, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-12 01:04 UTC)

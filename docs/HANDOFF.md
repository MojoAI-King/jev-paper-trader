# Handoff

Kind: Living.

## RESUME HERE

Written: 2026-10-11 22:42 EDT

- **State:** Live on Joey's standing permission (2026-10-12): original retired; mention_follow built, hardened after an adversarial review (wf_d1c03f32-477), pre-registered and locked; no Jev or research calls when nothing uses them (jev_used false, judged 0); Kalshi 504 fix (15286af): run 38196326048 read 58 pages with no error (was 5), sharp matched 7 games. Follow research rerun with full-precision ordering: +18.1% at 15 min holds. Evidence: 161 offline tests OK; runs 38195337805 and 38196326048 success; read-only live walk 32 pages no error; kalshi_first_trade live check on 3 markets.
- **Next:** Let sharp, mention_no and mention_follow run; early read on the mention strategies in 2-3 weeks (mention_forward.py); next research: follow-first-trade in other families (gas ladders) at quoted prices
- **Blocked:** nothing
- **Watch out:** Kalshi answers slowly at times: the walk now shrinks pages on 504 and stops at its 300 s budget; post-mortems and the daily review still use Claude
- **Git:** master @ 6677104, 0 tracked uncommitted, 2 untracked
- **CI:** master green on GitHub (read 2026-10-12 02:42 UTC)

## Earlier

### 2026-10-11 21:04 EDT
- **State:** Follow-first-trade tested at quoted prices (7b455a6; the workflow attempt hit the plan's session limit, redone as a script): following a NO first trade in new mention markets +18.1% [-1.3, +35.1] at 15 min (108 buys, 62 events, both halves positive; +16% to +21% at 1-60 min); following YES -4% to -25%; placebo NO about 0. Proposed to Joey: a new paper strategy mention_follow (code change). Live: 27 cycles since 18:05Z, one transient Kalshi 504; the touchdown-prop sharp bet settled -249.55 (excluded); mention_no 32 open. Evidence: follow_first_trade.py --summarize on 2,306 markets; 155 offline tests OK.
- **Next:** On Joey's yes: pre-register mention_follow in EXPERIMENTS.md, build it (first-trade side via the trades endpoint, NO at the quoted ask within the next cycle), tests, lock it
- **Blocked:** mention_follow waits for Joey's yes
- **Watch out:** Five parallel research agents hit the Claude plan's session limit; keep research to scripts or one agent at a time
- **Git:** master @ 7b455a6, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-12 01:04 UTC)

### 2026-10-11 14:02 EDT
- **State:** Forward tests locked (1fad555): learning.locked_strategies sharp, mention_no; run 38162056755 clean. Follow-the-first-trade test (wf_629049c4-764) still running. Evidence: 155 offline tests OK; run 38162056755 success.
- **Next:** Read wf_629049c4-764 results; record in CHECKS.md; propose a forward test to Joey only if a rule survives the review
- **Blocked:** nothing
- **Watch out:** Score backtests at quotes the strategy could take on its own clock
- **Git:** master @ 1fad555, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 18:02 UTC)

### 2026-10-11 13:52 EDT
- **State:** Workflow wf_79340bda-9e0 done: Economics lead refuted for a first mover (AAA gas in a falling week; quote-based -2.7% on 494 unseen events). Mention edge at quoted prices +0.5% [-10.2, +11.3] (779 buys), so expected about break-even; page blurb and registry corrected (17b920a); forward test stands. New hypothesis under test: follow the informed first trade at quoted prices (workflow wf_629049c4-764). Evidence: wf_79340bda-9e0: 6 agents, 0 errors; 154 offline tests OK.
- **Next:** Read wf_629049c4-764 (follow-first-trade); record in CHECKS.md; if a rule survives, propose a forward test to Joey (code change)
- **Blocked:** nothing
- **Watch out:** Score backtests at quotes the strategy could take on its own clock, never at trade prints whose timing is part of the selection
- **Git:** master @ 17b920a, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 17:52 UTC)

### 2026-10-11 13:09 EDT
- **State:** Claude retired as a picker too (df3ccd9): claude_direct and ch16 retired; claude_direct in learning.retired_probabilities. Run 38158120513 clean: only original, sharp, mention_no decide; page shows those 3. Workflow wf_79340bda-9e0 (economics first-trade lead, mention listing-quote rule) still running. Evidence: 154 offline tests OK; run 38158120513 success; summary.json strategies original, sharp, mention_no.
- **Next:** Read wf_79340bda-9e0 verdicts; record in docs/research/CHECKS.md; act only on what survives
- **Blocked:** nothing
- **Watch out:** The daily review can still tune mention_no's rules mid forward test; worth a guard (ask Joey)
- **Git:** master @ fc6d170, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 17:09 UTC)

### 2026-10-11 12:46 EDT
- **State:** Maintenance recorded (b690134). Jev retired as a picker and live (run 38156043216 clean). Workflow wf_79340bda-9e0 verifying the Economics first-trade lead and the mention listing-quote rule; results pending. Evidence: 154 offline tests OK; skilliton maintain --apply; secrets scan 21 known false positives.
- **Next:** Read wf_79340bda-9e0 verdicts; record in docs/research/CHECKS.md; act only on what survives
- **Blocked:** nothing
- **Watch out:** Trade-conditioned first-trade results can come from the first trader's own choice
- **Git:** master @ b690134, 2 uncommitted
- **CI:** master green on GitHub (read 2026-10-11 16:46 UTC)

# Task: Self-improvement loop and agent ecosystem

Kind: Living. Task record.

- **ID:** 2026-09-27-self-improvement-loop-and-agent-ecosyste-b776
- **State:** in-progress
- **Branch:** learning-loop
- **Owner:** unassigned
- **Updated:** 2026-09-27T15:59:17.803Z

## Request

Reinforce recurring self-improvement: the tool constantly improves itself from the trades it makes and lessons learned from ones that went well and bad; create the ecosystem you need to thrive

## Acceptance criteria

- [ ] Every resolved market feeds learning: misses AND wins get Claude reviews (capped), gate ledger shows what each gate saved or cost
- [ ] Research playbook: lessons from reviews are distilled by a Claude coach, screened in code, versioned, and fed into every research call automatically
- [ ] Self-calibrating strategy learns a calibration map from resolved outcomes (data-gated) on its own fake $100k
- [ ] Weekly retrospective writes proposals; challengers start only with Joey's approval unless he enables bounded auto-start
- [ ] Main's pre-registered gates and the price screen are untouched; tests prove the playbook can't carry odds
- [ ] Ecosystem for future sessions: health command, project skills, operations runbook, learning doc, experiments registry with a drift test

## Decisions

not yet written

## Checkpoints

### 2026-09-27T15:45:49.367Z

- **State:** Learning loop built: win reviews, playbook coach, gate ledger, self-calibrating strategy, weekly retro, challengers; health/learn commands; skills and docs
- **Evidence:** 71 tests OK; 5 guards mutation-checked; read-only smoke on real ledgers
- **Next:** Merge to master and push; confirm the 16:23Z scheduled run; then the dashboard redesign
- **Git:** learning-loop @ 4eed607, 19 uncommitted

### 2026-09-27T15:59:17.803Z

- **State:** Live and trading: 5 fake-$100k strategies (main, Jev alone, Claude direct, bold, self-calibrating); bold placed 7 bets in run 36329790430; learning loop merged (87801e5); page redesign on branch page-redesign (a0cd87e), private preview https://claude.ai/artifact/TP84qLCdrVPHPnRaBTcEAf
- **Evidence:** 71 tests pass; 5 new guards fail when switched off; run 36329790430 success (bold 7 bets); 390px iframe check of the new page
- **Next:** Confirm a scheduled (cron) run lands at :23 and runs the learning-loop code (python3 -m papertrade health); ship the page redesign when Joey OKs it (BACKLOG B11); if cron keeps skipping, B10
- **Git:** master @ 3574102, 5 uncommitted

## Handoff

- **State:** Live and trading: 5 fake-$100k strategies (main, Jev alone, Claude direct, bold, self-calibrating); bold placed 7 bets in run 36329790430; learning loop merged (87801e5); page redesign on branch page-redesign (a0cd87e), private preview https://claude.ai/artifact/TP84qLCdrVPHPnRaBTcEAf. Evidence: 71 tests pass; 5 new guards fail when switched off; run 36329790430 success (bold 7 bets); 390px iframe check of the new page.
- **Next:** Confirm a scheduled (cron) run lands at :23 and runs the learning-loop code (python3 -m papertrade health); ship the page redesign when Joey OKs it (BACKLOG B11); if cron keeps skipping, B10
- **Blocked:** Page redesign ships on Joey's OK
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer (no cycles on the Mac); weekly research pause lifted, so a full week also blocks Joey's own Claude until the Monday 3 AM ET reset; auto_start_challengers stays false until Joey decides (B12)

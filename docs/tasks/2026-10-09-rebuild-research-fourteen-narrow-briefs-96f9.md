# Task: Rebuild research: fourteen narrow briefs and their reports

Kind: Living. Task record.

- **ID:** 2026-10-09-rebuild-research-fourteen-narrow-briefs-96f9
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-09T21:16:29.810Z

## Request

not yet written

## Acceptance criteria

- [ ] Fourteen narrow briefs in docs/research/briefs/ (done); each research tab writes its report to docs/research/NN-<slug>.md; the main session commits every report, checks its claims against our data, and writes the rebuild plan for Joey

## Decisions

not yet written

## Checkpoints

### 2026-10-09T21:16:29.810Z

- **State:** Fourteen narrow research briefs ready in docs/research/briefs/ (run sheet docs/research/README.md; page https://claude.ai/artifact/2USu1tPk31NdbK2p1vj5ta). Joey runs each as its own Claude Code tab, all at once; each tab writes only docs/research/NN-<slug>.md and does not commit. No reports yet
- **Evidence:** briefs committed at 8d23ab7; 122 offline tests OK; run-sheet page checked once by screenshot
- **Next:** When the tabs finish: commit the reports, mark them done in the run sheet, check each report's claims against papertrade_data, then write the plan (strategies, backtests to pass, code changes for Joey to approve)
- **Git:** master @ 8d23ab7, 2 uncommitted

## Handoff

- **State:** Fourteen narrow research briefs ready in docs/research/briefs/ (run sheet docs/research/README.md; page https://claude.ai/artifact/2USu1tPk31NdbK2p1vj5ta). Joey runs each as its own Claude Code tab, all at once; each tab writes only docs/research/NN-<slug>.md and does not commit. No reports yet. Evidence: briefs committed at 8d23ab7; 122 offline tests OK; run-sheet page checked once by screenshot.
- **Next:** When the tabs finish: commit the reports, mark them done in the run sheet, check each report's claims against papertrade_data, then write the plan (strategies, backtests to pass, code changes for Joey to approve)
- **Blocked:** nothing
- **Watch out:** Research tabs share this checkout: never git add -A or commit their half-written reports mid-run; they must not run cycle/scan/settle/review or skilliton; all of them draw on Joey's Claude plan (week 47%, resets Mon 2026-10-12 08:00Z)

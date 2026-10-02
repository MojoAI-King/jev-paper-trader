# Completed backlog

Kind: Reference. Current work is in `docs/BACKLOG.md`.

Keep each item's ID, outcome, closure date and evidence.

| ID | Outcome | Closed | Evidence |
|---|---|---|---|
| B8 | Check the dashboard at phone width | 2026-09-27 | Superseded: the first redesign passed a 390px iframe check; the mission-control page that replaced it (d66e71e) keeps phone tuning as B13, by Joey's choice. |
| B10 | An outside trigger in case GitHub's scheduler skips | 2026-09-27 | Built and deployed: Cloudflare cron trigger in `worker/index.js` (d66e71e, Worker version 4c6ee8a0). Turning it on is B1 (the token). |
| B11 | Ship the page redesign | 2026-09-27 | Joey asked for a one-screen, fewer-words, sci-fi dashboard instead of the preview; shipped as mission control (d66e71e, 3514809 and the label fix), checked live in headless Chrome at 1440x900 with the 12:32 ET cycle's data. |
| B1 | Cycles start by themselves, about every 30 minutes | 2026-09-27 | Joey set `GITHUB_DISPATCH_TOKEN` on the Worker (secret change 17:51 UTC). The Cloudflare trigger started run 36339317403 at 18:04 UTC (skipped by the gate: last cycle 16 minutes earlier) and run 36341181637 at 18:34 UTC (full cycle, 1 bet), with no one starting them. |
| B12 | Decide whether challengers may start by themselves | 2026-09-27 | Joey: "For challengers, start on their own." `learning.auto_start_challengers` is true (decision 2026-09-27-challengers-start-by-themselves-opposing-4dc1). |
| B14 | Skip markets with almost no trading | 2026-09-27 | Decided against a spread filter: edges are measured against the price paid, so the spread is already counted (Joey left it to Claude). The real gap, fill size, is B15. |
| B16 | Widen the market universe | 2026-10-01 | markets_per_source 60 -> 100 (commit 4a0c001) when Joey asked for many more bets; decision 2026-10-01-stop-buying-contracts-under-30c-100-mark-4428. |
| B20 | Keep research from filling Claude's weekly meter | 2026-10-01 | Weekly pace guard: research waits while the week meter is more than 15 points ahead of an even pace (`research.week_pace_margin`), shipped with research 150 a day; decision 2026-10-01-stop-buying-contracts-under-30c-100-mark-4428. |
| B23 | Focus the strategies on the categories that pay | 2026-10-02 | Declined by Joey ("keep the categories"); no rules changed. Proposal and category data were in the B23 row (commit 60c4177). |

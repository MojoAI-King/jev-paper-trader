# Completed backlog

Kind: Reference. Current work is in `docs/BACKLOG.md`.

Keep each item's ID, outcome, closure date and evidence.

| ID | Outcome | Closed | Evidence |
|---|---|---|---|
| B8 | Check the dashboard at phone width | 2026-09-27 | Superseded: the first redesign passed a 390px iframe check; the mission-control page that replaced it (d66e71e) keeps phone tuning as B13, by Joey's choice. |
| B10 | An outside trigger in case GitHub's scheduler skips | 2026-09-27 | Built and deployed: Cloudflare cron trigger in `worker/index.js` (d66e71e, Worker version 4c6ee8a0). Turning it on is B1 (the token). |
| B11 | Ship the page redesign | 2026-09-27 | Joey asked for a one-screen, fewer-words, sci-fi dashboard instead of the preview; shipped as mission control (d66e71e, 3514809 and the label fix), checked live in headless Chrome at 1440x900 with the 12:32 ET cycle's data. |

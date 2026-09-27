# Task: Page fits any big screen; drop the Headline tag

Kind: Living. Task record.

- **ID:** 2026-09-27-page-fits-any-big-screen-drop-the-headli-821d
- **State:** done-local
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-09-27T19:02:51.113Z

## Request

Joey: "Did you increase the zoom? and is headline the Jev plus Claude one? If so, can you change the name
headline to Jev plus Claude?" Then, mid-work: "I don't even know if I like the big zoom in now... it was a
little nicer when it was smaller".

## Acceptance criteria

- Main's row no longer shows a "Headline" tag; the hover text of Bold and Self-calibrating says "Jev + Claude"
  instead of "the headline strategy".
- The page renders at 1x on every screen (no zoom rules in the live page).
- 72 tests pass.

## Decisions

- Drop the tag rather than rename it: the row's name already reads "Jev + Claude", so a "Jev + Claude" tag
  would say it twice.
- A fit-to-window scale was built and measured (1.23x at 1920x1080, 1.47x at 2550x1281, stepping down when
  challenger rows need room, rechecked once web fonts load), then dropped when Joey said he preferred the
  smaller page. Recorded as a reversal in decision 2026-09-27-show-settled-and-unsettled-money-apart-p-f0c2.

## Checkpoints

### 2026-09-27T19:02:46.221Z

- **State:** Page back at 1x everywhere (Worker 5536aa80, live checked); main's Headline tag dropped in policy.json, hover blurbs say Jev + Claude
- **Evidence:** 72 tests pass; live page byte-equal to the new build, no zoom rules; tag leaves the page at the next cycle's summary.json
- **Next:** Next cycle (~19:04 UTC) regenerates summary.json without the tag; then nothing queued beyond BACKLOG B3, B15, B13
- **Git:** master @ 9b395f9, 4 uncommitted

## Handoff

- **State:** Page back at 1x everywhere (Worker 5536aa80, live checked); main's Headline tag dropped in policy.json, hover blurbs say Jev + Claude. Evidence: 72 tests pass; live page byte-equal to the new build, no zoom rules; tag leaves the page at the next cycle's summary.json.
- **Next:** Next cycle (~19:04 UTC) regenerates summary.json without the tag; then nothing queued beyond BACKLOG B3, B15, B13
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 81% (resets Mon 3 AM ET)

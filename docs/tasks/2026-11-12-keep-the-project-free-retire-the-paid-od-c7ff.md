# Task: Keep the project free: retire the paid odds feed

Kind: Living. Task record.

- **ID:** 2026-11-12-keep-the-project-free-retire-the-paid-od-c7ff
- **State:** verified
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-11-12T06:12:11.436Z

## Request

i want to shut this down or keep it free and no longer pay for this in any way

## Acceptance criteria

- [x] No live strategy or challenger can call The Odds API, tested
- [x] The workflow no longer passes ODDS_API_KEY to the cycle
- [x] Every remaining cost checked and written down; what only Joey can cancel is named
- [x] Records updated: EXPERIMENTS, CLAUDE.md, OPERATIONS, a decision

## Decisions

not yet written

## Checkpoints

### 2026-11-12T05:16:20.351Z

- **State:** sharp retired and ODDS_API_KEY removed from the workflow; pushed to master as 5dcdaea3
- **Evidence:** python3 -m unittest discover -s tests -t .: 172 OK; new no-paid-feed test mutation-checked both ways; repo visibility PUBLIC (gh repo view)
- **Next:** Read the next live cycle: tests pass on CI and its scan has no sharp/odds stats; Joey cancels The Odds API subscription
- **Git:** master @ 5dcdaea3, 3 tracked uncommitted, 3 untracked

### 2026-11-12T05:24:35.867Z

- **State:** Project costs nothing (Joey: keep it free): sharp retired, ODDS_API_KEY out of the workflow, B27 archived. Live: mention_no, mention_follow, favorites on free Kalshi/Polymarket data
- **Evidence:** unittest 172 OK locally and on live cycle 43160661333 (head 5dcdaea3); that cycle's scan has no sharp line, jev_used false
- **Next:** Joey cancels The Odds API plan at the-odds-api.com; Oct/Nov check-in on the three bots
- **Git:** master @ 8fa9e493, 6 tracked uncommitted, 5 untracked

### 2026-11-12T06:12:11.436Z

- **State:** Project costs nothing: sharp retired, ODDS_API_KEY out of the workflow; live bots mention_no, mention_follow, favorites on free data. Joey asked me to cancel The Odds API plan in his browser; the Chrome extension is not connected (no browsers listed), so it is not cancelled
- **Evidence:** tabs_context_mcp: extension not connected (twice); list_connected_browsers: empty
- **Next:** Joey connects the Claude Chrome extension and says go (I cancel at the-odds-api.com; he signs in himself if asked), or cancels it himself; then the three bots' check-in
- **Git:** master @ e6158150, 0 tracked uncommitted, 2 untracked

## Handoff

- **State:** Project costs nothing: sharp retired, ODDS_API_KEY out of the workflow; live bots mention_no, mention_follow, favorites on free data. Joey asked me to cancel The Odds API plan in his browser; the Chrome extension is not connected (no browsers listed), so it is not cancelled. Evidence: tabs_context_mcp: extension not connected (twice); list_connected_browsers: empty.
- **Next:** Joey connects the Claude Chrome extension and says go (I cancel at the-odds-api.com; he signs in himself if asked), or cancels it himself; then the three bots' check-in
- **Blocked:** Odds API cancel: Chrome extension not connected
- **Watch out:** Keep the repo public (private repos pay for Actions minutes); never add a paid feed or ANTHROPIC_API_KEY; a stash holds a reformatted policy.json to discard

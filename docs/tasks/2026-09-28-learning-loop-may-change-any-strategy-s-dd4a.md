# Task: Learning loop may change any strategy's rules and bet sizing; code changes are proposed to Joey

Kind: Living. Task record.

- **ID:** 2026-09-28-learning-loop-may-change-any-strategy-s-dd4a
- **State:** verified
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-10-01T04:10:46.341Z

## Request

not yet written

## Acceptance criteria

- [ ] The weekly retro (and learning loop) can change any strategy's betting rules, bet size and open-bet limit, main included, by itself, and every change shows on the page with its reason; it never changes code, fees, the price screen or the scoreboard; code ideas are written as proposals Joey approves or denies in a session; tests pass; decision recorded

## Decisions

not yet written

## Checkpoints

### 2026-09-29T03:05:08.449Z

- **State:** Built (uncommitted): daily review may tune any strategy's rules (gates, sizing, open-bet limit, filters) within learning.bounds, main included; original = frozen yardstick; rules.json + rules_history.jsonl; rules_version on bets; retire challengers (open bets still settle); code ideas wait for Joey; page feed TUNE/IDEA + tuned badge; docs, decision 5495, memory. Not done: adversarial review workflow running; then fixes, commit, page redeploy, push
- **Evidence:** python3 -m unittest discover -s tests -t . -> Ran 99 tests OK; python3 -m papertrade learn shows Rules now (all v1, original frozen)
- **Next:** Read review workflow findings, fix confirmed ones, rerun tests, commit, deploy page shell, push, watch next cycle
- **Git:** master @ 56a28b2, 21 uncommitted

### 2026-09-29T03:27:31.209Z

- **State:** All 20 confirmed first-round review findings fixed (retired challengers stay on page, gate ledger uses recorded edge bar, versions/wait from history, sizing floors, no-room reasons, waiting challengers start, label uniqueness, overflow guard, per-proposal try, idea status, yardstick comparison); docs and decision updated. Not done: second-round review of the fixes running; commit, page redeploy, push
- **Evidence:** 111 tests OK; 17 single-guard mutations each turn a test red, planted failing test turns the harness red; current_summary and week_numbers built from live data read-only without error
- **Next:** Read the fix-round review, fix anything confirmed, commit, deploy the page shell, push, watch the next cycle
- **Git:** master @ 1e251f0, 23 uncommitted

### 2026-09-29T03:55:16.410Z

- **State:** Committed and pushed 44b97f1 (daily review tunes any strategy's rules; code ideas wait for Joey); page shell deployed (version 3f7c929e) and live page byte-identical to the build; STATUS and BACKLOG (B21) updated, uncommitted. Not done: first cycle on the new code not yet verified; handoff not written
- **Evidence:** 117 tests OK (exit 0 read on its own line); 3 review rounds 20+8+3 findings fixed; 26 mutations each red; live summary and week_numbers built read-only from real data; curl of the live page matches site/index.html
- **Next:** When the ~04:04Z run finishes: check it succeeded, original.json created, bets carry rules_version, health Healthy; then commit docs, write handoff, close task
- **Git:** master @ 44b97f1, 4 uncommitted

### 2026-09-29T04:07:43.542Z

- **State:** Verified live: run 36519949032 (04:04Z) on 44b97f1 succeeded; original.json created 04:04:29Z and bet; new bets carry rules_version; decisions record min_edge; summary.json has auto_tune, rule_changes, ideas_for_joey, original slot y; page shell deployed and identical to the build
- **Evidence:** health Healthy at 04:06Z (7 strategies, 4 bets that cycle incl. original 1); 117 tests pass; curl of summary.json and the page
- **Next:** First daily review at the first cycle after ~2026-09-29 23:12Z: read what it changed (BACKLOG B21)
- **Git:** master @ 040fef0, 5 uncommitted

### 2026-10-01T04:10:46.341Z

- **State:** Diagnosed losses (read-only): long shots under 30c caused -32.6k of -35.7k settled; options in BACKLOG B22 put to Joey; nothing changed yet. Claude week 100%: daily review and research paused until Mon 3 AM ET
- **Evidence:** health Healthy 04:04Z 2026-10-01; settled-bet breakdown from papertrade_data/portfolios (50 bets, 32 markets)
- **Next:** Joey's answer on B22: min_ask 0.30 by hand, approve p4/p7, market-shrink code idea
- **Git:** master @ f99f53b, 2 uncommitted

## Handoff

- **State:** Diagnosed losses (read-only): long shots under 30c caused -32.6k of -35.7k settled; options in BACKLOG B22 put to Joey; nothing changed yet. Claude week 100%: daily review and research paused until Mon 3 AM ET. Evidence: health Healthy 04:04Z 2026-10-01; settled-bet breakdown from papertrade_data/portfolios (50 bets, 32 markets).
- **Next:** Joey's answer on B22: min_ask 0.30 by hand, approve p4/p7, market-shrink code idea
- **Blocked:** nothing
- **Watch out:** Never set ANTHROPIC_API_KEY; GitHub is the only ledger writer; the dispatch token is a Cloudflare Worker secret and expires within a year; Claude plan week at 27% at 04:06Z on 2026-09-29, much of it this session's review workflows (resets Mon 3 AM ET); never build an unattended job that edits or ships code (Joey, 2026-09-28)

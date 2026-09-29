# Task: Learning loop may change any strategy's rules and bet sizing; code changes are proposed to Joey

Kind: Living. Task record.

- **ID:** 2026-09-28-learning-loop-may-change-any-strategy-s-dd4a
- **State:** in-progress
- **Branch:** master
- **Owner:** unassigned
- **Updated:** 2026-09-29T03:27:31.209Z

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

## Handoff

- **State:** All 20 confirmed first-round review findings fixed (retired challengers stay on page, gate ledger uses recorded edge bar, versions/wait from history, sizing floors, no-room reasons, waiting challengers start, label uniqueness, overflow guard, per-proposal try, idea status, yardstick comparison); docs and decision updated. Not done: second-round review of the fixes running; commit, page redeploy, push. Evidence: 111 tests OK; 17 single-guard mutations each turn a test red, planted failing test turns the harness red; current_summary and week_numbers built from live data read-only without error.
- **Next:** Read the fix-round review, fix anything confirmed, commit, deploy the page shell, push, watch the next cycle
- **Blocked:** nothing
- **Watch out:** nothing known

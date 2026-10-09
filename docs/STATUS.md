# Project status

Kind: Living.

Current state (2026-09-29, 00:00 EDT): **Trading automatically, and the learning loop now tunes the
strategies' rules by itself.** Joey chose "free rein over the rules, not the code" (decision
2026-09-28-daily-review-tunes-any-strategy-s-rules-5495, commit 44b97f1): the review runs daily and may
change any strategy's gates, bet size, open-bet limit and market filters, main included; `original`
keeps main's starting rules as the yardstick; code ideas wait for Joey's approve/reject. The first daily
review is due at the first cycle after about 2026-09-29 23:12Z. The page shows rule changes (TUNE) and
ideas (IDEA) in its feed; the new page shell is deployed (version 3f7c929e) and verified byte-identical.

A Cloudflare cron trigger (`worker/index.js`, :04 and :34) starts a GitHub Actions cycle about every 30
minutes; GitHub's own schedule is a backup, and a 25-minute gate stops double cycles. Seven fake-$100,000
strategies trade real Polymarket and Kalshi markets: Jev + Claude (main), Jev alone, Claude direct, Bold,
Self-calibrating (waits for 30 results), Jev alone, bold, and Original rules (frozen yardstick, from
2026-09-29). Claude runs on Joey's Claude Max plan, never an API key.

The 23:04Z cycle, the first on decision 2026-09-28-more-action-whole-kalshi-window-soonest-21f7: Kalshi
walked 35 pages in 61 s with no errors (497 passing), 120 markets passed the filters (about 5 a cycle
before), 40 judged (80 deferred: a one-time wave), 8 bets placed. Main won its first two settled bets
(+$3,378, now $103,378). 20 markets resolved in all (7 Kalshi results came in early), 5 Kalshi scalar
markets went to `voids.json`, and the first weekly retrospective ran (0 proposals). Claude plan: week 14%.

Earlier on 2026-09-28: Kalshi links fixed; open-bet cap 30% -> 50% (Joey); research 20 -> 60 a day; the
page shows lifetime won/lost bets and money. On 2026-09-27 the page went back to 1x and lost the
"Headline" tag.

The public page, https://jev-paper-trader.greekgod.workers.dev, is a one-screen mission-control dashboard
that reads `papertrade_data/summary.json` from the public repo every 5 minutes and shows settled and
not-settled money apart.

Verified 2026-09-29: 117 offline tests pass. Earlier: 73 offline tests passed; `python3 -m papertrade health` reads Healthy (cycles every 30 minutes,
120 markets fetched, no problems); new Kalshi links open the right event in headless Chrome. Runbook:
`docs/OPERATIONS.md`.

Read `docs/HANDOFF.md` for the next step and `docs/BACKLOG.md` for outstanding work. Keep branch-complete, merged, deployed and verified separate; one task's result does not make the whole project complete.

## Open tasks

<!-- skilliton:index:tasks:start -->
Open tasks in `docs/tasks/` (every state except done-local, merged, released, verified and abandoned), sorted by ID. `skilliton index` writes this list from the task records; edit the task records, not the list.

| ID | Title | State | Branch | Owner |
|---|---|---|---|---|
| [2026-10-09-rebuild-phase-1-size-by-measured-skill-o-ffa3](tasks/2026-10-09-rebuild-phase-1-size-by-measured-skill-o-ffa3.md) | Rebuild phase 1: size by measured skill, one stake per event, real Kalshi fees, slower review | in-progress | master | unassigned |
<!-- skilliton:index:tasks:end -->

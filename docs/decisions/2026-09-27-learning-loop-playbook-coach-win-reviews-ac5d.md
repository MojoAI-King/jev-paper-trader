# Learning loop: playbook coach, win reviews, gate ledger, self-calibration, weekly retro, challengers

Kind: Living. Decision entry.

- **ID:** 2026-09-27-learning-loop-playbook-coach-win-reviews-ac5d
- **Status:** proposed
- **Date:** 2026-09-27

## Decision

The trader now improves itself from every resolved market (design: `docs/LEARNING.md`):

1. **Win reviews.** Besides post-mortems of misses, Claude writes "why were we right" reviews when a
   bet won or research beat the market's error by `learning.win_margin` (0.25). Capped at
   `learning.max_win_reviews_per_day` (3), separately from the existing 5 post-mortems a day. A
   post-mortem now also runs when any strategy lost money on a market, not only main.
2. **Research playbook, automatic.** `coach.py`: once 3 new written reviews are in (at most daily), a
   Claude coach (no tools) rewrites the playbook, and every research call follows the rules for its
   category plus the general ones. Code checks every rule: the same price screen as research facts,
   20-280 characters, a known category, and evidence from a real review. Rules are re-screened when
   research loads them. Every version and every refused rule is logged.
3. **Gate ledger, free.** `learn.gate_ledger`: what a flat $100 would have made on every edge each
   strategy saw, grouped by which gate stopped it.
4. **Self-calibrating strategy, automatic.** `learn.calibration_map` fits a two-number correction to
   Jev's researched probabilities from resolved outcomes, pulled toward "no correction" by a prior.
   A new strategy, `calibrated`, bets with it on its own fake $100k once 30 researched markets have
   resolved.
5. **Weekly retrospective and challengers.** Claude reads numbers computed in code and proposes at
   most two changes a week. A challenger (probability source plus gate changes within
   `learning.challenger_bounds`) runs on its own fake $100k only after `python3 -m papertrade approve`,
   or automatically if Joey sets `learning.auto_start_challengers` (off). A challenger can never change
   sizing, fees, exposure caps or the price screen; that is re-checked every time it loads.
6. **Ecosystem for future sessions:** `python3 -m papertrade health` and `learn`, project skills
   `trading-health` and `improve` (`.claude/skills/`), `docs/OPERATIONS.md`, `docs/LEARNING.md`,
   `docs/EXPERIMENTS.md` (with a test that it lists every strategy), and this repo's own
   `docs/MAINTAIN.md` steps. Each scan now logs markets fetched per source and its problem lines.

## Why

Joey asked for recurring self-improvement: "the tool is constantly improving itself over time based
on the feedback it gets back from the trades it makes and lessons learned from ones that went well
and bad", and for an ecosystem beyond what Skilliton set up. The design splits improvements by risk.
Research guidance and probability calibration improve by themselves, because they can be evaluated
forward (by playbook version, and by a separate strategy) and can't leak prices. Changes to how money
is bet are run as challengers, because a system that tunes its own bets on the results it's judged by
overfits.

## Alternatives rejected

- Letting the retrospective edit policy.json or main directly: overfits and breaks the
  pre-registered criteria in PLAN.md.
- Feeding lessons into Jev's state: Jev's inputs stay facts only; lessons shape how research is done.
- Tuning gates automatically from the gate ledger: with tens of resolved markets that is noise-chasing;
  the ledger informs challengers instead.
- Auto-starting challengers by default: Joey asked to approve any loosening of gates; auto-start is his
  switch to flip.

## Risk

- The playbook changes what research finds for every strategy that uses research, main included.
  This is research quality improving, not a rule change, and it is reported by playbook version. If a
  playbook version hurts, the history makes it visible and revertible.
- More Claude calls: up to 3 win reviews a day, 1 coach call a day, 1 retrospective a week, all without
  web access except the reviews.
- Adding `calibrated` makes every market due again next cycle (the new-strategy catch-up): one round of
  Jev re-judging, no new research.

## Reversibility

Each piece is a policy.json setting or a strategy entry: remove `calibrated`, set the review caps to 0,
set `coach_min_new_reviews` very high, or empty `papertrade_data/playbook.json`'s rules. Challengers stop
with `python3 -m papertrade retire <id>`.

## Evidence

- 71 offline tests pass. The playbook screen at load, the challenger check at load, the coach's rule
  screen, the retrospective's challenger check and the experiments registry test were each shown to
  fail when switched off.
- Read-only run against the real ledgers: `coach.week_numbers` and the page summary build without error;
  five strategies, bold holding its 7 bets.

# Plan: can an AI research team grow $100,000 on prediction markets?

Status, 2026-09-27: decisions made (Joey delegated them; details in DECISIONS.md). **Phase 1 is
built and tested offline, with hourly cycles, the feedback loop and the public page.** The first
live run waits on `ANTHROPIC_API_KEY` in `.env`; hourly runs wait on Joey's hosting choices.

## The question

Can Jev, fed research by Claude, ChatGPT and research agents, turn a fake $100,000 into more than
$100,000 on real Polymarket and Kalshi markets, after fees and realistic fills, by more than luck
would explain?

Two numbers answer it, and we need both:

1. **Profit or loss** on the fake bankroll. This is the headline.
2. **Brier score vs. the market's price** on the same markets. This says whether the forecasts
   are genuinely better than the crowd's. Profit without better forecasts is luck and won't last.

## Why this is hard (so we judge the results honestly)

- Market prices are already good forecasts. Beating them needs information or judgment the crowd
  doesn't have.
- Fees (Kalshi's taker fee is about 1.75¢ on a 50¢ contract) and slippage eat small edges. That is
  why a bet needs at least an 8-point edge after costs.
- Research can leak the answer. If a news summary quotes the market's price, the forecaster just
  echoes it and we see a fake edge. The three-layer price screen is the most important integrity
  control in the project.
- Luck is large. With 2% stakes on near coin-flip outcomes, 30 bets can easily show +10% or -10%.
  P&L means something only after roughly 100 settled bets.
- The first run showed the trap: 25 of 32 markets had "edges" of 8+ points, almost all of them
  Jev not knowing current facts (end-of-season baseball leaders). The info gate blocked them.

## Design

**The funnel, every hour.** Fetch about 120 markets, apply the free filters, group by event, research
each event once, screen the facts, judge every market three ways, and let each strategy decide.
Each stage's counts and spend go to `scans.jsonl` and the dashboard.

**Three strategies, each with its own fake $100,000,** on the same markets with the same gates
and sizing:

| Strategy | Forecaster | What it tells us |
| --- | --- | --- |
| **Main: Jev + Claude research** | Jev reading screened research | The headline answer |
| Jev alone | Jev with no research | The baseline, and your step 3's "without news" arm |
| Claude direct | Claude Opus 5.5 reading the same research | Whether Jev adds anything over Claude |

**Research, as deep as it's useful.** Claude Opus 5.5 at high effort: up to 10 searches and 5
full-page reads per event, up to 20 dated, sourced facts. Facts cover what the resolution source
shows today, recent events, what's still scheduled, historical base rates, and how the rules are
measured.

**More signals per market.** Jev answers five questions: probability of YES, the same question
asked as NO (a consistency check), whether the rules are clear, whether it has enough information,
and whether the outcome is already decided. Every answer is logged, so later analysis can test
which signals predict profit.

## How it improves over time (the feedback loop)

1. **Score everything.** When a judged market resolves, every forecaster is scored against the real
   outcome, and the signals it had are recorded (`reviews.jsonl`).
2. **Explain the misses.** When the main forecast was confidently wrong, or a bet lost money, Claude
   looks up what actually happened and writes a post-mortem with a root cause from a fixed list
   (research missed it, stale facts, misread rules, overconfident, a wrong fact, a resolution
   quirk, or a reasonable call that was unlucky), a lesson, and one suggested change.
3. **Look for patterns.** The page shows root-cause counts, and a calibration table comparing what
   Jev said with how often it actually happened.
4. **Change carefully.** When a pattern is clear (say, most misses are "research missed it"), the
   suggested change is approved by Joey and runs as a **new strategy version beside the current
   one** on the same markets. It replaces the old one only if it wins on the pre-registered
   criteria. The system gets better without moving its own goalposts.

## Rules that keep the result honest

- No forecaster ever sees the market's price, directly or through research. Tested, and the tests
  were shown to fail when the screen is switched off.
- Success and stop criteria are fixed below, before results come in.
- No tuning on the results we're judging. Any change to gates or questions is dated, and results
  before and after it are reported separately.
- Every input is logged: exact facts given to Jev, their sources, what each call cost.
- Fills are priced at the ask plus 1¢.

## Success and stop criteria (pre-registered)

- **Checkpoint:** 100 settled bets in the main portfolio, or 12 weeks, whichever comes first.
- **"It makes money"** means both: the main portfolio's return is positive with a 90% bootstrap
  confidence interval above zero, and its Brier score beats the market's on the same markets.
- **Stop and rethink** if, after 50 settled bets, the whole confidence interval for return is below
  zero, or the Brier score trails the market's by more than 0.02.
- **Keep a research source** if its strategy beats Jev alone on Brier score after 50 resolved markets.

## Money

No budget cap (Joey, 2026-09-27). Two ceilings in `policy.json` only stop a bug from burning money
in a loop: $150 per run and 120 events per run.

**Estimated cost, not yet measured:** $0.30–1.50 of research per event, plus $0.03–0.08 per
market for Claude direct. Trading hourly, each market is re-researched about every 6 hours or when
its price moves, so roughly 60 markets x 4 looks a day: **about $40–180 a day, $1,200–5,400 a
month.** The range is wide because page reads and resumed search loops vary a lot. The first live
run replaces it with measured numbers, which every scan logs. Bug guards: $150 per run, $500 per
day.

## Phases

0. **Done.** Polymarket fixed and paginated; one-page dashboard; first-run chart.
1. **Built, tested offline:** research, the three strategies, the hourly funnel, the feedback loop,
   the dashboard and the public page. Next: add `ANTHROPIC_API_KEY`, run a small live test
   (`python3 -m papertrade scan --limit 3`) to measure real cost and read real research, then turn
   on hourly cycles.
2. **ChatGPT research** as a second researcher, with two new strategies (Jev + ChatGPT, Jev + both).
   Needs `OPENAI_API_KEY`.
3. **Research-agent verification before bets:** when main is about to bet, an agent looks for
   anything that settles or contradicts the case, and Jev re-judges before money moves.
4. **Checkpoint review** at 50 resolved markets: which sources and signals help, what to change
   (dated).

Codex is a coding agent, not a forecaster. Its natural role is building parts of this system.

# Plan: can an AI research team grow $100,000 on prediction markets?

Status, 2026-09-27: decisions made (Joey delegated them; details in DECISIONS.md). **Phase 1 is
live:** hourly cycles on GitHub (Claude on Joey's Claude plan, never an API key), the feedback loop,
and the public page at https://jev-paper-trader.greekgod.workers.dev.

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

**Several strategies, each with its own fake $100,000,** on the same markets with the same sizing (the full list, with what each tests, is `docs/EXPERIMENTS.md`):

| Strategy | Forecaster | What it tells us |
| --- | --- | --- |
| **Main: Jev + Claude research** | Jev reading screened research | The headline answer |
| Jev alone | Jev with no research | The baseline, and your step 3's "without news" arm |
| Claude direct | Claude Opus 5.5 reading the same research | Whether Jev adds anything over Claude |
| Bold (added 2026-09-27) | Main, but bets when Jev's info score is 0.2+ instead of 0.5+ | Whether the info gate is too cautious |
| Jev alone, bold (added 2026-09-28) | Jev alone, with Bold's 0.2 info bar | Whether research pays when betting boldly |

**Research, rationed to the Claude plan.** Claude Opus 5.5 through Claude Code, medium effort: up to
6 searches and 3 full-page reads per event, up to 15 dated, sourced facts. Facts cover what the resolution source
shows today, recent events, what's still scheduled, historical base rates, and how the rules are
measured.

**More signals per market.** Jev answers five questions: probability of YES, the same question
asked as NO (a consistency check), whether the rules are clear, whether it has enough information,
and whether the outcome is already decided. Every answer is logged, so later analysis can test
which signals predict profit.

## How it improves over time (the learning loop)

Every resolved market makes it a little better, automatically, without moving its own goalposts.
Full design: `docs/LEARNING.md`.

1. **Score everything.** When a judged market resolves, every forecaster is scored against the real
   outcome, tagged with its category and the research playbook version it used (`reviews.jsonl`).
2. **Explain misses and wins.** Claude writes a post-mortem when the researched forecast was
   confidently wrong or any strategy lost money (root cause from a fixed list, what we missed, a
   lesson), and a "why were we right" review when we beat the market or a bet won.
3. **Learn how to research (automatic).** A Claude coach turns those reviews into the research
   playbook: short rules on how to research a kind of question. Every research call follows it. Code
   screens each rule like a research fact (no odds, markets or forecasts) and requires it to cite a
   real review; every version is kept, and results are reported by playbook version.
4. **Learn how far to trust Jev (automatic).** A calibration map is fitted to resolved outcomes; the
   self-calibrating strategy bets with the corrected probability once 30 markets have resolved.
5. **Measure every gate.** The gate ledger scores what a flat bet would have made on every edge each
   gate stopped, so gate changes rest on evidence. The bold strategy tests the info gate live.
6. **Propose weekly, test forward.** A weekly retrospective reads the numbers and proposes at most two
   changes. Anything that changes how money is bet runs as a **challenger strategy on its own fake
   $100,000** beside the others, started with Joey's approval (or automatically within fixed bounds, if
   he turns that on). It replaces the old way only if it wins on criteria written before it started.

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

**No real money beyond Joey's existing $200/month Claude plan, plus a few cents a month for Jev.**
Claude runs through Claude Code on the plan's login, never an API key (DECISIONS.md explains how
that's enforced). The page (Cloudflare) and hourly runs (GitHub, public repo) are free.

What research costs instead is a share of the plan's usage limits, which Joey also uses himself. So
it's rationed: at most 60 per day, spread through the UTC day (at most 6 in one cycle), soonest-decided events first
(before 2026-09-28: 3 a cycle and 20 a day, which ran out by 5 AM ET), only on events where the rules are
clear, reused for 24 hours, and paused whenever the plan's 5-hour window is 70% used. (The pause at
85% of the weekly window was lifted by Joey on 2026-09-27.) Each call logs what it would have cost on the API, as a measure of how much the plan
is absorbing; that amount is not billed.

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

**Learning loop: built 2026-09-27** (playbook coach, win reviews, gate ledger, self-calibrating
strategy, weekly retrospective, challengers), alongside the bold strategy. See `docs/LEARNING.md` and
`docs/EXPERIMENTS.md`.

Codex is a coding agent, not a forecaster. Its natural role is building parts of this system.

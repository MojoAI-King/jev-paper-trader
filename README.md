# Jev Paper Trader

Paper trading on **real** Polymarket and Kalshi prediction markets, using a **fake $100,000** bankroll
and TypeSafe's Jev as the judge. No accounts, no real money, and no real orders. The project only reads
public market prices.

The question it answers: **can Jev, fed research by Claude (and later ChatGPT and research agents),
grow the fake $100,000 by more than luck would explain?** Two numbers decide it: the profit or loss,
and whether the forecasts beat the market's own price (Brier score). The full plan, with its
pre-registered success and stop criteria, is in `PLAN.md`; the reasoning behind each choice is in
`DECISIONS.md`.

**Where it stands (2026-10-09):** after about two weeks, every forecaster is less accurate than the market's
own price, and the strategies are losing. The measured diagnosis and the research behind the rebuild are in
`docs/REBUILD_SCOPE.md`.

## Quick start

1. Open this folder in VS Code.
2. **Terminal → Run Task… → "1. Check Jev connection"**. It should print `Jev: OK`.
3. **Run Task… → "2. Preview live markets"** shows what Polymarket and Kalshi are returning.
   No Jev calls or bets happen here.
4. **Run Task… → "3. Daily run"** settles finished bets, scans for new ones, and prints the report.

Run the daily task once a day. The same commands work from any terminal:

```bash
python3 -m papertrade ping      # key + connection check
python3 -m papertrade markets   # preview market feeds
python3 -m papertrade cycle     # settle -> scan -> review -> report -> dashboard -> site/ (run hourly)
python3 -m papertrade cycle --deploy   # ...and push the public page to Cloudflare
python3 -m papertrade review    # score resolved markets; post-mortems for the misses
python3 -m papertrade report    # just the report
python3 -m papertrade health    # is it trading? live ledgers on GitHub + the last hourly runs
python3 -m papertrade learn     # what the learning loop has learned so far
python3 -m papertrade approve <id>   # start a proposed challenger strategy (reject / retire too)
python3 -m papertrade dashboard # one page: trades, cash split, P&L (papertrade_data/dashboard.html)
python3 -m papertrade publish   # build site/ (the public page + raw ledgers)
```

Needs Python 3.9 or later, plus Claude Code signed in with a Claude plan for the research step.
`.env` holds `TYPESAFE_AI_API_KEY` for Jev. **Never set `ANTHROPIC_API_KEY`:** it would switch Claude
Code to paid API billing, so research refuses to run while it's set.

For a first live run, research just a few events: `python3 -m papertrade scan --limit 3`.

## How a bet happens

Every hour, a funnel narrows the markets before any paid step:

1. **Fetch** the 60 busiest markets from each of Polymarket and Kalshi that pass the free filters, out of
   every market closing in the next 30 days (free, read-only).
2. **Free filters:** price 5–95¢, enough volume, closes within 30 days, and due for a look (never
   judged, judged over 6 hours ago, or its price moved 5+ points).
3. **Research, rationed:** Jev first judges every market without research. Events whose rules Jev
   rates clear are then researched by Claude Opus 5.5 through Claude Code on the Claude plan (web
   search and page reading only), reused for 24 hours, at most 60 a day spread through the day, soonest-decided events first. It returns dated, sourced facts: what the resolution source shows
   today, recent events, what's still scheduled, historical base rates.
4. **Price screen:** code drops any fact that mentions odds, prediction markets, forecasters,
   predictions, or a figure matching the market's price. The survivors become `recent_facts`.
5. **Judged three ways** (never shown the price): Jev with the facts, Jev without them, and Claude
   directly from the same facts.
6. **Each strategy decides** with its own fake $100,000 (see below).

Jev answers five questions in one call:

| Question | Used for |
| --- | --- |
| `p_yes`: will this resolve YES? | Jev's probability |
| `p_no`: will it resolve NO? | Consistency check: skip if YES and NO don't add up |
| `rules_clear`: are the resolution rules objective? | Skip vague markets |
| `info_sufficient`: can this be judged from what Jev has? | Skip markets Jev would be guessing on |
| `already_decided`: is the outcome settled in practice? | Logged for analysis |

A fake bet is placed only if **every** gate in `policy.json` passes:

- Edge of at least **8 points** after fees and slippage
- Rules clear of at least 0.75, information sufficient of at least 0.5, YES/NO gap at most 0.15
- Size: quarter-Kelly, at most **2%** of that strategy's bankroll per bet and **50%** in open bets

**Strategies.** Each trades its own fake $100,000 on the same markets with the same sizing:
**main** (Jev + Claude research, the headline), **Jev alone**, **Claude direct**, **bold** (main,
but with an info bar of 0.2 instead of 0.5), **self-calibrating** (main's gates, with Jev's
probability corrected by what it learned from resolved markets), and **Jev alone, bold** (no research,
Bold's info bar). Comparing them shows whether research helps, whether Jev adds anything over Claude,
whether the info gate is too cautious, whether research pays when betting boldly, and whether learning
from outcomes pays. `docs/EXPERIMENTS.md` lists every one with what it tests.

## How it learns

Every resolved market feeds a learning loop (full design in `docs/LEARNING.md`):

- **Reviews of misses and wins.** Claude explains what went wrong, or what went right, and the lesson.
- **A research playbook** that a Claude coach rewrites from those lessons; every research call follows
  it. Rules are screened in code like research facts and must cite a real review.
- **A calibration map** learned from outcomes; the self-calibrating strategy bets with it once 30
  markets have resolved.
- **A gate ledger**: what each gate saved or cost, measured on real outcomes.
- **A daily review** that changes any strategy's betting rules by itself (gates, bet size, open-bet
  limit, which markets it skips), starts and retires challenger strategies, and writes code ideas down
  for Joey to approve or reject. Every change is logged with its reason and shown on the page, every bet
  records the rules version it was placed under, and `original` keeps main's starting rules untouched
  as the yardstick. Fees, the price screen, market data and settlement are out of its reach.

Every strategy is listed, with what it tests and how it will be judged, in `docs/EXPERIMENTS.md`. How to run and check the live system:
`docs/OPERATIONS.md`.

## The public page

**Live at https://jev-paper-trader.greekgod.workers.dev** (source and full history:
https://github.com/MojoAI-King/jev-paper-trader).

The page is a static Cloudflare Worker named `jev-paper-trader` (see `wrangler.jsonc`; the shell is
built into `site/` by `publish`). Each time it's opened it loads `papertrade_data/summary.json` from
the GitHub repo, so it's as fresh as the last hourly commit. It shows only real data, in Eastern
time, with the raw ledgers on GitHub linked for anyone who wants to check. Hourly runs are set up
in `.github/workflows/trade.yml` and stay off until the `TRADING_ENABLED` repository variable is set.

## Reading the report

- **Bankroll and P&L**: how the fake $100k is doing. Open bets are valued at what they cost.
- **Strategies**: each strategy's bankroll and P&L side by side.
- **Brier score** for each forecaster (Jev with research, Jev alone, Claude direct) and the market: the number that matters. Lower is better. It's measured on
  every judged market that resolved, not just the ones bet on. If Jev's score isn't lower than the market's, the
  "edge" is noise. Don't trust either number until about **50 or more** markets have resolved.
  Each forecaster covers different markets, so those scores don't compare head to head. The **head to head**
  lines (and the page's **Forecasters** panel) score all four on the same resolved markets: per market, the
  latest look where all four gave a forecast. The page shows it as "% better than a coin flip"
  (1 − Brier / 0.25); hovering a row shows the Brier score.

## Files

```
papertrade/
  markets.py     # reads Polymarket + Kalshi public data (read-only)
  news.py        # Claude research, Claude direct, and the price screen
  judge.py       # the questions Jev answers (bump QUESTION_SET_VERSION if you edit wording)
  engine.py      # the funnel, gates, sizing, fake ledgers, settlement, report
  review.py      # the feedback loop: scoring, post-mortems of misses, reviews of wins
  learn.py       # the loop's numbers: categories, calibration map, gate ledger (no Claude)
  coach.py       # the loop's Claude steps: research playbook coach, the daily review, rule changes, proposals
  dashboard.py   # one-page HTML dashboard and the public site (+ dashboard_template.html)
  jev_client.py  # tiny Jev API client (stdlib only)
policy.json      # every threshold and limit; tune here, not in code
papertrade_data/ # portfolios/, judgments.jsonl, scans.jsonl, reviews.jsonl, resolutions.json, playbook.json, proposals.json, retros.jsonl (tracked)
site/            # the public page, built each cycle (not tracked)
tests/           # offline tests: python3 -m unittest discover -s tests -t .
PLAN.md          # the experiment: question, design, success criteria, phases
DECISIONS.md     # why each choice was made
```

## Costs

No real money beyond the Claude plan you already pay for, plus a few cents a month for Jev. Claude
runs on the plan's login, never an API key. Research uses part of the plan's usage limits, so it
pauses automatically once the 5-hour window is 70% used, leaving room for you. It runs until the
plan's weekly limit is reached (the 85% weekly pause was lifted on 2026-09-27). Every call logs what it would have cost on the API (not billed) in `scans.jsonl`.

## Known limits

- **Research is rationed** to fit the Claude plan, so on a busy day many markets are judged by Jev
  without research. The page shows how many had research each cycle.
- **At most 40 markets per cycle** are judged (`max_jev_calls_per_scan` is 80, two Jev calls per
  market). With hourly cycles, the rest are picked up in the next hour.
- **The Kalshi reader was written from docs** that disagree on field names, so it handles both.
- Bets are filled at the listed ask plus 1¢ of slippage. Real fills on thin markets can be worse.

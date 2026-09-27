# Jev Paper Trader

Paper trading on **real** Polymarket and Kalshi prediction markets, using a **fake $100,000** bankroll
and TypeSafe's Jev as the judge. No accounts, no real money, and no real orders. The project only reads
public market prices.

The question it answers: **can Jev, fed research by Claude (and later ChatGPT and research agents),
grow the fake $100,000 by more than luck would explain?** Two numbers decide it: the profit or loss,
and whether the forecasts beat the market's own price (Brier score). The full plan, with its
pre-registered success and stop criteria, is in `PLAN.md`; the reasoning behind each choice is in
`DECISIONS.md`.

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
python3 -m papertrade dashboard # one page: trades, cash split, P&L (papertrade_data/dashboard.html)
python3 -m papertrade publish   # build site/ (the public page + raw ledgers)
```

Needs Python 3.9 or later, plus Claude Code signed in with a Claude plan for the research step.
`.env` holds `TYPESAFE_AI_API_KEY` for Jev. **Never set `ANTHROPIC_API_KEY`:** it would switch Claude
Code to paid API billing, so research refuses to run while it's set.

For a first live run, research just a few events: `python3 -m papertrade scan --limit 3`.

## How a bet happens

Every hour, a funnel narrows the markets before any paid step:

1. **Fetch** about 120 markets from Polymarket and Kalshi (free, read-only).
2. **Free filters:** price 5–95¢, enough volume, closes within 30 days, and due for a look (never
   judged, judged over 6 hours ago, or its price moved 5+ points).
3. **Research, rationed:** Jev first judges every market without research. Events whose rules Jev
   rates clear are then researched by Claude Opus 5.5 through Claude Code on the Claude plan (web
   search and page reading only), reused for 24 hours, at most 3 an hour and 20 a day. It returns dated, sourced facts: what the resolution source shows
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
- Size: quarter-Kelly, at most **2%** of that strategy's bankroll per bet and **30%** in open bets

**Strategies.** Each trades its own fake $100,000 on the same markets with the same gates:
**main** (Jev + Claude research, the headline), **Jev alone**, and **Claude direct**. Comparing them
shows whether research helps and whether Jev adds anything over Claude.

## Learning from mistakes

When a judged market resolves, `review` scores every forecaster against the real outcome. When the
main forecast was confidently wrong or a bet lost money, Claude looks up what actually happened and
writes a post-mortem: root cause, what we missed, a lesson and one suggested change. The page shows
the patterns. Changes are never applied automatically; see "How it improves over time" in PLAN.md.

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

## Files

```
papertrade/
  markets.py     # reads Polymarket + Kalshi public data (read-only)
  news.py        # Claude research, Claude direct, and the price screen
  judge.py       # the questions Jev answers (bump QUESTION_SET_VERSION if you edit wording)
  engine.py      # the funnel, gates, sizing, fake ledgers, settlement, report
  review.py      # the feedback loop: scoring and post-mortems
  dashboard.py   # one-page HTML dashboard and the public site (+ dashboard_template.html)
  jev_client.py  # tiny Jev API client (stdlib only)
policy.json      # every threshold and limit; tune here, not in code
papertrade_data/ # portfolios/, judgments.jsonl, scans.jsonl, reviews.jsonl, resolutions.json (tracked)
site/            # the public page, built each cycle (not tracked)
tests/           # offline tests: python3 -m unittest discover -s tests -t .
PLAN.md          # the experiment: question, design, success criteria, phases
DECISIONS.md     # why each choice was made
```

## Costs

No real money beyond the Claude plan you already pay for, plus a few cents a month for Jev. Claude
runs on the plan's login, never an API key. Research uses part of the plan's usage limits, so it
pauses automatically once the weekly window is 85% used or the 5-hour window 70%, leaving the rest
for you. Every call logs what it would have cost on the API (not billed) in `scans.jsonl`.

## Known limits

- **Research is rationed** to fit the Claude plan, so on a busy day many markets are judged by Jev
  without research. The page shows how many had research each cycle.
- **At most 40 markets per cycle** are judged (`max_jev_calls_per_scan` is 80, two Jev calls per
  market). With hourly cycles, the rest are picked up in the next hour.
- **The Kalshi reader was written from docs** that disagree on field names, so it handles both.
- Bets are filled at the listed ask plus 1¢ of slippage. Real fills on thin markets can be worse.

# Decisions

Plain-English record of the choices behind this project, newest first. Each entry says what was
decided, why, and what is still unverified.

## 2026-09-27 Hourly trading, the feedback loop, and the public page

**Trading all day (Joey's request).** One command, `python3 -m papertrade cycle`, settles, scans,
reviews and rebuilds the page. It is meant to run hourly. A market is researched and judged again
after 6 hours (was 24), or sooner if its price moves 5 or more points; the price only decides when
to look again and is never shown to a forecaster. Because research now repeats through the day, a
third bug guard was added: `max_usd_per_day` $500.

**Where it runs (Joey's choices, 2026-09-27).** Hourly cycles run on GitHub Actions in the public
repo https://github.com/MojoAI-King/jev-paper-trader (public: free Actions minutes, and friends can
check every trade's timestamp in the history). The page is a Cloudflare Worker on Joey's personal
account (Joey@mojoai.org), at https://jev-paper-trader.greekgod.workers.dev. The Jev key and the
Cloudflare account ID were copied from `.env` into the repo's encrypted secrets without being
printed. The workflow stays off until `ANTHROPIC_API_KEY` and a `CLOUDFLARE_API_TOKEN` are added as
secrets and the repository variable `TRADING_ENABLED` is set to `true`. Commits pushed to the public
repo use GitHub's no-reply address, not Joey's email.

**The feedback loop.** `review` scores every newly resolved market once, for every forecaster.
When the main forecast was confidently wrong (off by 0.5 or more) or a bet lost money, Claude looks
up what actually happened and writes a post-mortem: root cause (from a fixed list), what happened,
what we missed, a lesson and one suggested change. Reviews never change trading on their own. A
change Joey approves runs as a new strategy version beside the current one, so the before/after
comparison stays honest. A system that tuned itself on the results it's judged by would overfit
and fool everyone watching.

**The public page.** A static-files-only Cloudflare Worker (`wrangler.jsonc`) serves `site/`,
which `publish` builds from the real data files only and refuses to build from anything marked as
example data (tested). It publishes the strategy ledgers, scan log, reviews and resolutions next to
the page, so friends can check the numbers. The large judgments log stays in the repo, not on the
page. Times show in Eastern (the browser handles EST/EDT). The page says plainly what is real
(markets, prices, outcomes) and what is simulated (the money, and fills at the ask plus 1¢).

**Ledgers are now tracked in git** (they were ignored before), so the record is saved in two places
and every change has a timestamp. The junk `_to_delete/` folder was untracked after a check showed
it held no keys, only placeholder text.

## 2026-09-27 One-page dashboard

`python3 -m papertrade dashboard` writes `papertrade_data/dashboard.html`, and every daily run
refreshes it. It's a local file, not a published page, because the portfolio changes daily and a
published copy would go stale. Python computes every number (the Brier logic is shared with the
text report through `engine.calibration`); the page's script only draws. Market text comes from
outside APIs, so the page inserts it as plain text and only opens links that start with https://.

## 2026-09-27 Research pipeline and three strategies (Phase 1, built)

**Who decided.** Joey handed the PLAN.md decisions over ("you decide what is best") and lifted the
research budget ("I don't care how much you spend... the more context Jev gets, the better").
The choices below are Claude's under that delegation; any can be reversed.

**What runs each day (the funnel).** Fetch markets, apply the free filters (price 5–95¢, volume,
closes within 30 days, not judged in the last 24h), group markets by event, research each event
once, screen the facts, then judge every market three ways and let each strategy decide:

| Strategy | Probability from | Gates from |
| --- | --- | --- |
| **main** (headline) | Jev, with research | Jev, with research |
| jev_alone | Jev, no research (your step 3's "without" arm) | Jev, no research |
| claude_direct | Claude Opus 5.5, reading the same screened facts, no tools | Jev, with research |

Each strategy trades its own fake $100,000 (`papertrade_data/portfolios/`), with the same gates
and sizing, so any difference in profit comes only from the forecaster. The v1 `portfolio.json`
moved untouched to `portfolios/main.json`. A market already held is re-judged daily (more data),
but no strategy adds to a position it holds.

**Research depth.** Claude Opus 5.5 at high effort, up to 10 web searches and 5 full-page reads
per event, up to 20 facts. Each fact has a kind (status_now, event, schedule, base_rate, rules), a
date, a source and the page it came from. Researching per event keeps linked markets (three
"Jalen Duren's next team" markets) on one consistent set of facts.

**More signals from Jev.** Question set `papertrade-v2` adds `p_no` (the same question asked the
other way) and `already_decided`. The three v1 questions keep their exact wording, so the two Jev
arms differ only in state. A new gate, `max_framing_gap` 0.15, skips a market when Jev's YES and
NO answers disagree. It only tightens; no existing gate or limit changed.

**Keeping the market's price away from every forecaster (the critical rule).** Three layers:

1. The research prompt forbids betting odds, prediction-market prices, forecaster probabilities
   and predictions. Neither Claude call is ever shown a price.
2. Prediction-market, sportsbook and odds sites are blocked at search and fetch time.
3. `news.screen_facts()` drops any fact that names a prediction market or sportsbook, uses
   betting or market-trading language, cites a forecaster, makes a prediction, pairs a percentage
   with probability words, or has a percent or cents figure within 1 point of any price in that
   event. It lives in code, not policy.json, so a config edit can't loosen it.

Facts must also cite a page the research call actually saw, so a source can't be invented. Every
dropped fact is logged with its reason, so the false-drop rate can be measured. The leak tests
were shown to fail with the screen switched off and with only its price-match rule off.

**Money.** No budget cap, per Joey. Two ceilings stay in `policy.json` purely as bug guards:
`max_usd_per_scan` $150 and `max_events_per_scan` 120. Spend is computed from each response's
`usage` and logged per scan in `scans.jsonl`. The existing `max_jev_calls_per_scan` (80) now
means at most 40 markets a day, because each market takes two Jev calls. Raising it would loosen
a policy limit, so that is left for Joey.

**Model and code.** Claude Opus 5.5 only (Joey's choice). No server-side refusal fallback, because
it can route to Opus 5; a refusal skips that market for the day. The Claude calls use Python's
standard library, like the Jev client, so the project still needs nothing but Python.

**Architecture questions (FEATURE tier: protocol §2-lite).**

- *Components.* `news.py` researches, forecasts and screens; `engine.scan` runs the funnel and
  the three strategies; `engine.settle` pays every ledger; `engine.calibration` scores every
  forecaster for both the report and the dashboard.
- *External call failures.* Claude timeout, 5xx, 429 or 529: retried up to 4 times, honoring
  `retry-after`. A paused server-side search loop is resumed up to 6 times. Missing key, unpriced
  model, 400, 401, 403 or 404: research stops for the run and it says so. A refusal or unparseable
  reply skips that event. No market is judged without research, and no half-judgment is logged.
- *Runs twice.* Anything judged in the last 24h is skipped, so a second run the same day makes no
  paid calls. Ledgers are saved after every bet.
- *Zero / many / malformed.* No facts gives `recent_facts: []`, a valid answer. Over 20 are capped.
  Bad dates, missing sources, unseen pages and duplicates are dropped with a reason.
- *How we know it ran.* Each scan logs every stage's counts and spend to `scans.jsonl`; the CLI
  prints the funnel, and the dashboard shows it.

**Unverified until the first live run** (needs `ANTHROPIC_API_KEY` in `.env`): real cost per event,
run time, whether rate limits slow research, how many facts the screen drops, and whether Opus
5.5 accepts both tool versions as sent.

## 2026-09-27 Polymarket fetch

Polymarket returned nothing because the API rejected our sort field (`volume_24hr`; it wants
`volume24hr`). Fixed, with a regression test replaying a recorded response. The reader now pages
until it has 60 Yes/No markets, because most top-volume Polymarket markets are team-vs-team sports
markets we skip. A hard cap of 25 pages per source stops any feed from looping forever; Kalshi's
reader got the same cap.

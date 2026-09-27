# Decisions

Plain-English record of the choices behind this project, newest first. Each entry says what was
decided, why, and what is still unverified.

The dated sections below were written on 2026-09-27, before this project kept one file per decision.
New decisions are recorded with `skilliton record decision "<title>"` in `docs/decisions/` and listed in
the index at the end of this page.

## 2026-09-27 Price screen: web addresses checked for market sites only (Joey approved)

The screen had been applying every rule to each fact's web address as well as its text. In the
first live cycles, clean facts (schedules, injuries, results) were dropped only because a news
page's address contained a word like "prediction". Jev never sees addresses, so the address is now
checked only for being a prediction-market or betting site; the fact text and source name still get
every rule. Measured on the 53 real facts gathered so far: 33 kept before, 41 after. The rule that
drops any figure within 1 point of the market's price stays strict for now, by Joey's decision, and
is to be revisited with a few days of logged drops. The leak tests still fail when the screen is
switched off.

## 2026-09-27 Claude runs on Joey's Claude plan, not the API

**Why.** The API-billed design was estimated at $40–180 a day of real money. Joey pays for a Claude
Max plan and can't spend that on an experiment. Anthropic's help center (checked 2026-09-27) says
scripted Claude Code (`claude -p`) currently draws on the plan's usage limits; a planned move to a
separate credit billed at API rates was paused. Claude Code only bills an API account when
`ANTHROPIC_API_KEY` (or `ANTHROPIC_AUTH_TOKEN`) is set.

**What changed.**
- All Claude work (research, Claude direct, post-mortems) runs through `claude -p` on the plan's
  login. The code refuses to start research if either API variable is set, strips them from the
  child process, and runs Claude outside the repo with only web search and page reading allowed.
  Verified live: the call reported `apiKeySource: none` on a `subscriptionType: max` login.
- The plan's limits are shared with Joey's own Claude use, so research is rationed: only events
  whose rules Jev rates clear, reused for 24 hours unless a price moves 10+ points, at most 3 per
  hourly cycle and 20 per day, and paused once the plan's weekly window is 85% used or the 5-hour
  window 70%. Every call reports usage, and the pause survives across cycles until the window resets.
- Jev still judges every due market hourly without research (TypeSafe, pennies), which is also the
  "Jev alone" strategy.
- Hourly runs on GitHub sign in with a plan token from `claude setup-token`
  (`CLAUDE_CODE_OAUTH_TOKEN`), Anthropic's documented way to run Claude Code in GitHub Actions.
- The public page now reads `papertrade_data/summary.json` from the GitHub repo each time it opens,
  so the hourly job only commits data and never needs a Cloudflare token.

**First live cycle (2026-09-27, 07:25 UTC, run locally with research capped at 2).** 120 markets
fetched, 29 due, all judged by Jev, 2 events researched (4 markets). 6 Claude calls; about $0.65 at
API prices, billed to the plan instead. Weekly plan usage went from 77% to 78%. No bets: with research, Jev's
probabilities moved to within a few points of the market (France 38% -> 52% vs a 52¢ price), and its
info score stayed under 0.5. The price screen dropped 12 of 25 facts: 6 only because the source
page's address contained "prediction" (a match preview; the fact text was clean), and 6 under the
"figure within 1 point of this market's price" rule, likely poll numbers near the 43¢/57¢ Brazil
prices. Whether to narrow either rule is Joey's call (the screen is never loosened without his OK).
Also seen: Jev gave Lula 38% and Bolsonaro 23% in what is essentially a two-way race; the market's
two prices add up to 100%. Making linked markets' probabilities add up is a candidate change for the
feedback loop.

**Hourly trading switched on (2026-09-27, 14:40 UTC).** Joey added `CLAUDE_CODE_OAUTH_TOKEN`; the
repository variable `TRADING_ENABLED` is `true`. The first GitHub run (manual start) passed all 52
tests, judged 40 markets (13 with research: 3 new events, 2 reused), made 13 Claude calls on the plan
(weekly usage unchanged at 78%), placed no bets, and committed its ledgers. From then on it runs every
hour at about :05 UTC. Cycles are no longer run on the Mac, so the ledgers have one writer. To stop:
`gh variable set TRADING_ENABLED --body false --repo MojoAI-King/jev-paper-trader`.

**Risk to watch.** If Anthropic resumes the paused change, scripted use would draw on a separate
monthly credit ($200 on Max 20x) at API rates and stop when it runs out, as long as extra usage is
off in Claude settings. Keep it off.

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

## Index

<!-- skilliton:index:decisions:start -->
Decision entries in `docs/decisions/`, sorted by ID. `skilliton index` writes this list from the entries; edit the entries, not the list.

| ID | Title | Status | Date |
|---|---|---|---|
| [2026-09-27-bold-strategy-info-bar-0-2-and-no-weekly-5851](docs/decisions/2026-09-27-bold-strategy-info-bar-0-2-and-no-weekly-5851.md) | Bold strategy (info bar 0.2) and no weekly research pause | accepted | 2026-09-27 |
| [2026-09-27-cloudflare-cron-trigger-starts-cycles-mi-0089](docs/decisions/2026-09-27-cloudflare-cron-trigger-starts-cycles-mi-0089.md) | Cloudflare cron trigger starts cycles; mission-control one-screen dashboard | accepted | 2026-09-27 |
| [2026-09-27-learning-loop-playbook-coach-win-reviews-ac5d](docs/decisions/2026-09-27-learning-loop-playbook-coach-win-reviews-ac5d.md) | Learning loop: playbook coach, win reviews, gate ledger, self-calibration, weekly retro, challengers | accepted | 2026-09-27 |
| [2026-09-27-show-settled-and-unsettled-money-apart-p-f0c2](docs/decisions/2026-09-27-show-settled-and-unsettled-money-apart-p-f0c2.md) | Show settled and unsettled money apart; plain strategy names; chart never tighter than 5 percent | accepted | 2026-09-27 |
<!-- skilliton:index:decisions:end -->

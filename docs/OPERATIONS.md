# Operations runbook

Kind: Living. Updated 2026-09-27. How the live system runs, how to check it, and what to do when
something breaks. For the design see PLAN.md; for the learning loop, docs/LEARNING.md.

## What runs where

| Piece | Where | Schedule |
| --- | --- | --- |
| Trading cycle: settle, scan, review, coach, the daily review (tunes rules), summary | GitHub Actions, `.github/workflows/trade.yml`, repo MojoAI-King/jev-paper-trader | about every 30 minutes (see "What starts a cycle") |
| Jev (TypeSafe) | `TYPESAFE_AI_API_KEY` repo secret | every cycle |
| Claude (research, Claude direct, reviews, coach, the daily review) | Claude Code signed in with `CLAUDE_CODE_OAUTH_TOKEN` (Joey's Max plan) | rationed by `policy.json` research and learning settings |
| Ledgers | `papertrade_data/`, committed by `papertrade-bot` each cycle | every cycle |
| Public page | Cloudflare Worker `jev-paper-trader` on the Joey@mojoai.org account, https://jev-paper-trader.greekgod.workers.dev | reads `summary.json` from GitHub on open and every 5 minutes; redeploy only when the page or `worker/index.js` changes |

## What starts a cycle

GitHub's own scheduler skipped every slot for this repo on 2026-09-27 (one :05 slot fired, 45 minutes
late, before trading was on). So there are two starters, and a gate:

1. **Cloudflare cron trigger (the dependable one):** `worker/index.js`, at :04 and :34 UTC-minutes, calls
   GitHub's `workflow_dispatch` API with `force: false`. It needs the Worker secret
   `GITHUB_DISPATCH_TOKEN` (below); without it the trigger logs "not set" and does nothing.
2. **GitHub's schedule (backup):** `8,23,38,53 * * * *` in the workflow.
3. **The gate:** the workflow's first step, `python3 -m papertrade due --minutes 25`, skips the run if a
   cycle ran in the last 25 minutes. A hand start (`gh workflow run`, default `force: true`) always runs.

**Setting the trigger's token (Joey, once a year):** on github.com, Settings > Developer settings >
Personal access tokens > Fine-grained tokens > Generate new token. Resource owner MojoAI-King; Repository
access "Only select repositories": jev-paper-trader; Repository permissions: **Actions: Read and write**
(nothing else). Copy it, then in the project folder run
`CLOUDFLARE_ACCOUNT_ID=223f06c5919a3c52df75655566c64c97 npx wrangler secret put GITHUB_DISPATCH_TOKEN`
and paste it at the prompt (it is hidden and goes straight to Cloudflare; never paste it into a chat or
a file). Check it worked: a run by the token's owner appears in the Actions tab at the next :04 or :34, or
`npx wrangler tail jev-paper-trader` shows `dispatch ...: HTTP 204`.

**GitHub is the only writer of the ledgers.** Never run `cycle`, `scan`, `settle` or `review` on a
laptop while hourly runs are on: two writers conflict. Read-only commands are fine anywhere:
`report`, `learn`, `health`, `markets`, `ping`, `dashboard`.

## Is it working?

```bash
git pull                          # the bot commits every hour
python3 -m papertrade health      # live ledgers on GitHub + the last runs: prints "Healthy." or what needs a look
python3 -m papertrade learn       # what the learning loop has learned
```

In a Claude session, the `trading-health` skill does this and explains the result.

## Common problems

| Symptom | Cause and fix |
| --- | --- |
| `health`: no scheduled run succeeded, only manual starts | Expected while GitHub's scheduler skips slots; the Cloudflare trigger's runs show as manual starts (`workflow_dispatch`). If the last cycle is over an hour old, check that `GITHUB_DISPATCH_TOKEN` is set and not expired, and start one by hand: `gh workflow run trade.yml --repo MojoAI-King/jev-paper-trader`. |
| A source fetched 0 markets, problem `HTTP 429` | The market API rate-limited GitHub's shared runner. Kalshi is read in 1,000-market pages, 1 second apart, soonest-closing slice first (about 35 requests and a minute a cycle since 2026-09-28), and each request retries up to 5 times over about 45 seconds (`markets._get`). A failure mid-walk keeps what was fetched and logs a problem (`fetch stopped after N pages`); only a failure on the first page drops the source. One bad cycle is fine; repeated ones need a look. |
| `Claude plan busy` / research paused | The 5-hour window passed 70%, or the plan's weekly limit is reached. Research resumes by itself when the window resets. Jev alone keeps trading. |
| Research refuses to run: API key set | Someone set `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN`. Remove it from the environment or the repo secrets; it would switch to paid API billing. |
| Claude calls fail with an auth error | `CLAUDE_CODE_OAUTH_TOKEN` expired (it lasts about a year from 2026-09-27). Joey runs `claude setup-token` and replaces the repo secret. |
| The page shows old numbers | GitHub's raw file cache holds about 5 minutes. Longer means the hourly commits stopped: check `health`. |
| A run failed | `gh run view <id> --repo MojoAI-King/jev-paper-trader --log \| grep -F "! "` shows the problem lines. Every scan also keeps its `problems` in `scans.jsonl`. |

## Controls

```bash
gh variable set TRADING_ENABLED --body false --repo MojoAI-King/jev-paper-trader   # pause trading
gh variable set TRADING_ENABLED --body true  --repo MojoAI-King/jev-paper-trader   # resume
gh workflow run trade.yml --repo MojoAI-King/jev-paper-trader                      # one cycle now
python3 -m papertrade learn           # each strategy's rules now, recent rule changes, ideas waiting for Joey
python3 -m papertrade approve <id>    # a code idea: mark it for a code session; a challenger: start it
python3 -m papertrade reject <id>     # drop an idea or a proposal
python3 -m papertrade retire <id>     # stop a running challenger (its ledger is kept, its open bets still settle)
# after approve/reject/retire: commit and push papertrade_data/ so the next cycle sees it
```

The daily review changes strategies' rules by itself (`learning.auto_tune`, Joey 2026-09-28). To stop
that, set `learning.auto_tune` to false in `policy.json` and push: changes then wait for `approve`. To
undo a change, a session edits the strategy's entry in `papertrade_data/rules.json` (removing it puts the
strategy back on its starting rules) and pushes; the history in `rules_history.jsonl` stays, version
numbers carry on from it, and the 2-day wait before the loop's next change to that strategy still applies.

Redeploy the page shell and trigger (only when `papertrade/dashboard_template.html` or `worker/index.js` changes):

```bash
npx wrangler whoami      # three accounts: use the Joey@mojoai.org account ID
CLOUDFLARE_ACCOUNT_ID=<that id> python3 -m papertrade publish --deploy
```

Then load https://jev-paper-trader.greekgod.workers.dev and check it, rather than trusting the deploy
message.

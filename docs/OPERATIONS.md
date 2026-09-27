# Operations runbook

Kind: Living. Updated 2026-09-27. How the live system runs, how to check it, and what to do when
something breaks. For the design see PLAN.md; for the learning loop, docs/LEARNING.md.

## What runs where

| Piece | Where | Schedule |
| --- | --- | --- |
| Trading cycle: settle, scan, review, coach, retrospective, summary | GitHub Actions, `.github/workflows/trade.yml`, repo MojoAI-King/jev-paper-trader | hourly at :23 past (GitHub may start it late) |
| Jev (TypeSafe) | `TYPESAFE_AI_API_KEY` repo secret | every cycle |
| Claude (research, Claude direct, reviews, coach, retrospective) | Claude Code signed in with `CLAUDE_CODE_OAUTH_TOKEN` (Joey's Max plan) | rationed by `policy.json` research and learning settings |
| Ledgers | `papertrade_data/`, committed by `papertrade-bot` each cycle | every cycle |
| Public page | Cloudflare Worker `jev-paper-trader` on the Joey@mojoai.org account, https://jev-paper-trader.greekgod.workers.dev | reads `summary.json` from GitHub on every open; redeploy only when the page itself changes |

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
| `health`: no scheduled run succeeded, only manual starts | GitHub's scheduler is late or skipping. Start one by hand: `gh workflow run trade.yml --repo MojoAI-King/jev-paper-trader`. If it keeps happening, see BACKLOG B10 (an outside hourly trigger). |
| A source fetched 0 markets, problem `HTTP 429` | The market API rate-limited GitHub's shared runner. Requests retry 4 times with backoff (`markets._get`); one bad hour is fine, repeated ones need a look. |
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
python3 -m papertrade approve <id>    # start a proposed challenger; then commit and push proposals.json
python3 -m papertrade retire <id>     # stop a running challenger (its ledger is kept)
```

Redeploy the page shell (only when `papertrade/dashboard_template.html` changes):

```bash
npx wrangler whoami      # three accounts: use the Joey@mojoai.org account ID
CLOUDFLARE_ACCOUNT_ID=<that id> python3 -m papertrade publish --deploy
```

Then load https://jev-paper-trader.greekgod.workers.dev and check it, rather than trusting the deploy
message.

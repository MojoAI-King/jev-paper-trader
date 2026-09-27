# Research must run on the Claude plan: an API key silently switches billing

Kind: Living. Lesson entry.

- **ID:** 2026-09-27-research-must-run-on-the-claude-plan-an-46c5
- **Status:** accepted
- **Date:** 2026-09-27

## What broke

The first research design called the Anthropic API directly. The estimate came to $40–180 a day of real money. Joey had said he didn't care about spend, but he meant his $200/month Claude plan, not API dollars. The API design had to be torn out after it was fully built and tested.

## The mechanism

Two different billing paths exist. The Messages API bills per token and per search to whatever account owns `ANTHROPIC_API_KEY`. Claude Code (`claude -p`) signed in with a Claude plan draws on the plan's usage windows (5-hour and weekly) instead. Anthropic announced moving scripted use to a separate credit billed at API rates from June 15, 2026, then paused that (help center article 15036540, checked 2026-09-27). Claude Code prefers `ANTHROPIC_API_KEY` over the plan login whenever that variable is set, so one stray environment variable silently turns plan usage into a bill. Also: Claude Code 2.1.278 rejected `claude-opus-5-5` ("version 2.1.280 or newer is required"), and every `claude -p` stream carries a `rate_limit_event` with the plan's current window utilisation.

## The fix

`papertrade/news.py` `ClaudeCode` runs `claude -p` with `--tools WebSearch,WebFetch`, `--permission-mode dontAsk`, `--setting-sources ""`, `--strict-mcp-config`, `--no-session-persistence`, `--output-format stream-json --verbose`, from a temp directory outside the repo. It refuses to start if `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN` is set, strips both from the child environment, and reads `rate_limit_event` so the engine stops at 85% of the weekly window or 70% of the 5-hour window. CI installs the latest CLI and signs in with `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token` (commit eea7ab6). A live check showed `apiKeySource: none` on a `subscriptionType: max` login.

## The rule

Before building anything with per-call spend, state the real-money cost per day and per month and get the owner's OK on that number. "Cost doesn't matter" is not that OK. For Claude work in this repo, never set an Anthropic API key anywhere.

## What now enforces it

`ClaudeCodeTests.test_refuses_to_run_with_an_api_key_set`, `test_runs_on_the_plan_with_only_web_tools_and_no_market_sites` (no billing variables reach the child, no `--bare`, cwd outside the repo), `ResearchPipelineTests.test_an_api_key_in_the_environment_stops_research_not_jev`, `test_plan_usage_guard_waits_for_the_window_to_reset`, and `tests/fixtures/claude_stream.jsonl`, a real recorded run. The CLAUDE.md rule forbids the variable. Nothing enforces the confirm-the-dollars rule except that note.

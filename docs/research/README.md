# Rebuild research

Kind: Living. Owner: Joey. Part of BACKLOG B24; the diagnosis behind it is `docs/REBUILD_SCOPE.md`.

Fourteen narrow research questions, each answered by its own Claude Code session in a separate VS Code tab, all
running at the same time. Each session writes one report into this folder. The main session then checks the
reports against our own data and writes the rebuild plan; every code change in it waits for Joey's yes.

## How to start one

Open a new Claude Code tab in this VS Code window and type one line, for example:

    Run research brief 01: read docs/research/briefs/01-favourite-longshot.md and follow it.

## The briefs

| # | Question | Wave | Report |
|---|---|---|---|
| 01 | How mispriced are cheap and expensive contracts? | 1 | pending |
| 02 | Prices that don't add up | 2 | pending |
| 03 | Markets that keep trading after the answer is known | 2 | pending |
| 04 | What makes an AI forecaster more accurate | 2 | pending |
| 05 | Combining our forecast with the market price | 1 | pending |
| 06 | Pricing crypto, oil, gold and stock-index thresholds | 1 | pending |
| 07 | Pricing daily weather markets from forecast models | 1 | pending |
| 08 | Pricing economic-data and Fed markets | 2 | pending |
| 09 | Sports prices against the sharp sportsbooks | 1 | pending |
| 10 | What trading actually costs on each venue | 1 | pending |
| 11 | Simulating fills honestly | 2 | pending |
| 12 | Bet sizing when our probabilities are uncertain | 2 | pending |
| 13 | Telling skill from luck quickly | 2 | pending |
| 14 | Using Jev for what it's built for | 1 | pending |

Wave 1 (01, 05, 06, 07, 09, 10, 14) are the seven that most decide the plan. The briefs don't depend on each other, so any order works.
All fourteen at once use a lot of Joey's Claude plan, the same plan the trader's own research runs on. If tabs stop
with a usage-limit message, that is the 5-hour window, and they can carry on once it resets.

## Rules for a research session

You are one of several research sessions running at the same time in this same folder. To avoid colliding:

- Write exactly one file: your report, at the path your brief names. Don't edit, create, move or delete any other
  file in the repo (no task records, notes or scripts). Scratch work goes in your session's scratchpad directory.
- Don't commit, push, pull or switch branches, and don't run `skilliton` commands. The main session commits every
  report.
- If a hook asks for a checkpoint, handoff, maintenance or dispatch, answer in one line that this is a
  research-only session whose report the main session records. Then carry on with the research, or finish if
  your report is already written.
- Never run the trader's `cycle`, `scan`, `settle`, `review` or `publish`. Read any file you like to understand
  how the trader works (`papertrade/`, `policy.json`, `docs/`), but don't analyze `papertrade_data/` yourself:
  describe the test you want instead. The main session runs those tests, so the reports don't come back with
  fourteen different analyses of the same data.
- Never open, print or quote `.env` or any key, and don't call the Jev (TypeSafe) API.
- Use the deep-research skill (`anthropic-skills:deep-research`) if your session has it; otherwise search and
  fetch the web directly.

## Evidence standards

- Prefer primary sources: papers, exchange rulebooks and API docs, datasets. Date every claim, because fees,
  rules and APIs change.
- Give the sample size and period for every empirical claim, and keep evidence apart from opinion. Mark trader
  blogs, forum posts and vendor marketing as anecdotal.
- Write "not verified" for anything you couldn't confirm. A short report with solid sources beats a long one
  with guesses.

## Report format

```
# NN: <title>

Researched <date> for `docs/research/briefs/NN-<slug>.md`.

## Answer in five lines

## Findings
One entry per finding: the claim; the evidence (link, date, sample size); its strength (strong, moderate,
weak or anecdotal).

## What it means for our trader
Concrete changes, ranked, each with its expected effect and how sure you are.

## How to test it on our history
What to compute from our finished markets (about 1,100 so far, with price snapshots about every 30 minutes,
our forecasts and the outcomes), and which result would confirm the idea or kill it.

## Data sources
Name, URL, cost or free tier, limits, what it provides. Leave the section out if there are none.

## Not verified
```

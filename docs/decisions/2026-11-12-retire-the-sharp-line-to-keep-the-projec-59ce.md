# Retire the sharp line to keep the project free

Kind: Living. Decision entry.

- **ID:** 2026-11-12-retire-the-sharp-line-to-keep-the-projec-59ce
- **Status:** accepted
- **Date:** 2026-11-12

## Decision

The `sharp` strategy (Pinnacle's line from The Odds API) is retired (`policy.json` `"retired": true`) and leaves
the forward-test lock. `ODDS_API_KEY` is taken out of `.github/workflows/trade.yml`, so no cycle can call The Odds API
even if something switched the strategy back on. Its ledger stays and its one open bet settles normally (settlement
reads Kalshi and Polymarket, not the odds feed). `mention_no`, `mention_follow` and `favorites` keep running; they use
only free Kalshi and Polymarket data.

## Why

Joey, 2026-11-12: "i want to shut this down or keep it free and no longer pay for this in any way". Keeping it free
keeps the bots his friends watch. The Odds API's paid plan (about $30 a month, as told to Joey on 2026-10-26; the bill
itself was not read) was the project's only paid data. Everything else costs nothing:

- GitHub Actions: the repository is public, and standard runners are free for public repositories.
- Jev (TypeSafe): called only when a strategy uses Jev (`engine.scan` builds the client only then); none does since
  2026-10-11, and the last scan read `jev_used: false`.
- Claude: runs through Claude Code on Joey's own Max plan, never an API key, so it adds nothing to his bill.
- The page: a Cloudflare Worker on the free plan's allowance (one cron trigger, a few requests an hour).

## Alternatives rejected

- **Keep `sharp` on The Odds API's free tier (500 credits a month):** it spent about 185 credits a day from Nov 5 to
  Nov 12 (19,262 to 17,933 left), so a free month would last about three days.
- **Shut everything down (disable the workflow):** also costs nothing, but stops the bots Joey's friends watch. Still
  one command away (`gh workflow disable "Trading cycle"`).

## Risk

`sharp`'s forward test ends early and undecided: 8 bets (7 settled at -$1,433, 1 open), far short of the 150 its
kill test needs, so the question it asked (do venue game prices lag Pinnacle's line enough to profit?) stays open. The
page drops `sharp` and its result from the totals, as with every retired strategy.

## Reversibility

Fully reversible: a paid Odds API plan, `ODDS_API_KEY: ${{ secrets.ODDS_API_KEY }}` back in the workflow, and the
`retired` flag removed. The code, the `odds-check` command and the machinery tests stay (the tests run on a copy of the
policy with `sharp` switched on).

## Evidence

- `RetiredJevTests.test_the_live_setup_never_calls_the_paid_odds_feed`: the live policy runs a scan with a key present
  and every odds call set to fail, and the workflow file holds no `secrets.ODDS_API_KEY`. Mutation-checked: switching
  `sharp` back on, or putting the key back in the workflow, fails it.
- `python3 -m unittest discover -s tests -t .`: 172 tests OK.
- Repository visibility read with `gh repo view`: PUBLIC.

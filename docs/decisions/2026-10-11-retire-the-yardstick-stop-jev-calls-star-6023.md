# Retire the yardstick, stop Jev calls, start mention_follow

Kind: Living. Decision entry.

- **ID:** 2026-10-11-retire-the-yardstick-stop-jev-calls-star-6023
- **Status:** accepted
- **Date:** 2026-10-11

## Decision

Under Joey's standing permission of 2026-10-12 ("if you need to build something, build it... we just want to win"):

1. `original`, the frozen yardstick on the old Jev + research rules, is retired. Its ledger is kept and its open bets
   still settle.
2. The scan calls Jev and Claude research only when an active strategy uses a Jev or Claude source
   (`engine.JEV_SOURCES`); today none does, so the scan makes no Jev or research call (`stats.jev_used` false), and it
   builds the Jev client only when needed. The cycle's post-mortems and daily review still use Claude (corrected after
   the review of 2026-10-12, workflow wf_d1c03f32-477).
3. A new paper strategy, `mention_follow`: when a new Kalshi mention market's first trade is a NO purchase made in the
   last 90 minutes, P(YES) = mid − 12 points and it buys NO at the quoted ask (30–85¢, 6+ hours before the event, one
   bet per event, probes until its edge shows). The first trade is read once per market from Kalshi's trades endpoint
   (`markets.kalshi_first_trade`, at most 60 a cycle, for markets listed within 48 hours that have traded) and kept in
   `papertrade_data/first_trades.json`. It is pre-registered in `docs/EXPERIMENTS.md` and locked against the daily
   review.

## Why

- `original` was losing (Jev + research scored worse than the market price) and, with `main` retired, compared
  nothing. Joey: "the original rules is kind of skewing it".
- Jev and Claude research calls cost money and plan capacity for forecasts no strategy reads.
- Following a NO first trade at the quoted ask 15 minutes later made +18.1% [−1.3, +35.1] on 108 buys in 62 events,
  both halves positive (docs/research/CHECKS.md, "Following the first trade at quoted prices"); the hypothesis was set
  before the test, and the placebo (buy NO anyway) was about zero.

## Alternatives rejected

- **Fold the follow rule into `mention_no`:** would change a locked forward test midway.
- **Keep `original` for the record:** its record stays in its ledger; it no longer needs to keep betting.

## Risk

- The follow edge rests on about 60 events; it may shrink live. Few bets: these markets are thin.
- The page's total now counts only the three live strategies; the retired ones' losses stay in their ledgers.

## Reversibility

Remove `retired` from `original`; drop `mention_follow` from `policy.json` (its ledger stays).

## Evidence

- `follow_first_trade.py --summarize` on 2,306 settled mention markets; live read-only check of
  `markets.kalshi_first_trade` on three open markets returned each first trade's side and time.
- Offline tests: 157 pass (`test_mention_follow_buys_no_after_an_informed_first_no_trade`,
  `test_mention_follow_never_follows_yes_a_stale_first_trade_or_an_untraded_market`, `RetiredJevTests` with no Jev call).

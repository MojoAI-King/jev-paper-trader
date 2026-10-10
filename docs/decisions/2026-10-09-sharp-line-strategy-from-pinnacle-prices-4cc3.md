# Sharp-line strategy from Pinnacle prices; Jev alone retired

Kind: Living. Decision entry.

- **ID:** 2026-10-09-sharp-line-strategy-from-pinnacle-prices-4cc3
- **Status:** accepted
- **Date:** 2026-10-09

## Decision

Joey, 2026-10-09/10: "you have the ability to do what you need to fix this ... figure out what's missing to make a
serious winner." This builds plan item 2A (`docs/REBUILD_PLAN.md`, research report 09):

1. **A new strategy, `sharp` ("Sharp line (Pinnacle)").** It has no AI forecast. On games, its probability is
   Pinnacle's head-to-head price with the bookmaker's margin removed by the power method (Betfair's exchange as
   fallback), from The Odds API (`papertrade/odds.py`).
   - It buys a Kalshi or Polymarket side priced 20–85¢ that sits at least 3¢ below that line after fees.
   - It is sized like every strategy by measured skill (`engine.skill`, source `sharp`): probes until its edge
     over the venue price shows on 300+ markets.
2. **Matching.** A Kalshi game market matches a game when its question and rules name both teams (since October
   2026 the title names one, "Philadelphia wins"; the rules name both) and it is decided within 8 hours of the start;
   its YES team is the new `yes_side` field. Spreads and totals are screened on the question alone. A Polymarket market matches when it names one team and starts
   near the game or carries its date. Spread, total and prop markets, games already started, and anything that fits
   two games are left out.
3. **Data and quota.**
   - The key is `ODDS_API_KEY`, from the environment or `.env`, passed to the cycle as a GitHub secret. Error
     messages never carry it.
   - Lines are cached in `papertrade_data/odds.json`. Each listed sport is refreshed at most every 8 hours (6 at
     first; slowed on 2026-10-10 after a test run spent about 210 requests by mistake, lesson
     2026-10-10-a-real-api-key-in-env-turned-the-tests-i-43ba), and not once the quota left reaches 25.
   - A line over 45 minutes old, or with a margin over 6%, isn't used.
   - Without the key, the strategy shows "waiting for an ODDS_API_KEY" and never bets.
   - `python3 -m papertrade odds-check` tests the key (one request; writes nothing).
4. **The price screen holds.** The line is a price, so it goes only to this strategy's decision and to the scoring
   (judgments carry `sharp`). It is never put into a Jev or Claude state; a test checks that through the real scan.
5. **`jev_alone` retired** (`retired: true` in `policy.json`). `engine.strategies` leaves a retired policy strategy
   out of betting and tuning. Its ledger still settles (`all_books`) and stays on the page. Its colour went to
   `sharp` (a policy strategy may now name its `slot`).

## Why

Professional sports bettors measure skill against the sharp closing line, and Pinnacle is the reference book
(report 09). The research found our AI forecasters add nothing to the market price on real-priced markets, so a
winner needs information the venue's price might not have: a sharper market's price is the most direct candidate.
The Odds API covers Pinnacle, Betfair's exchange, Kalshi and Polymarket in one feed (bookmakers page read
2026-10-10). "Jev alone" scored like a coin flip on 1,006 markets and placed one bet in two weeks (report 14 says
stop betting on Jev's own forecast); it held the colour slot the new strategy needed.

## Alternatives rejected

- **Arbitrage between venues, or market making.** Gaps last seconds, and making markets needs fast cancels and real
  accounts (reports 02, 11). This repo is paper-only on a 30-minute cycle.
- **Using The Odds API's own Kalshi and Polymarket prices to place bets.** Bets use our own venue feeds, which give
  the market ids settlement needs; the API's venue prices are only a matching check (report 09).
- **A grey ninth strategy colour.** It would read as retired on the page.
- **Removing `jev_alone` from `policy.json`.** That would lose its label on the page; `retired` keeps it.

## Risk

- The free tier only allows about 4 decision windows a day per sport; a line goes stale in between.
- Pinnacle's lines come "from public website which may incur a delay" (The Odds API).
- Team-name matching can miss games, and miss more abroad (aliases are few). It is built to miss rather than
  mismatch.
- Report 09's honest expectation is zero or a small edge on liquid markets. The kill and keep rules are in
  `docs/EXPERIMENTS.md`.
- The key costs Joey nothing on the free tier; the $30 plan only if the test looks promising.

## Reversibility

- Remove `sharp` from `policy.json` (its ledger stays and settles), or set its `retired: true`.
- Unset the `ODDS_API_KEY` secret to stop all calls.
- `jev_alone` returns by removing its `retired` flag.

## Evidence

- `OddsTests`:
  - de-vig sums to 1 and keeps the favourite;
  - only a fresh, low-margin sharp line counts, and a soft book is never the reference;
  - Kalshi and Polymarket matching, including spreads, totals, late markets, other games, unclear sides, started
    games and two-game ambiguity left out;
  - the cache respects the refresh time and the quota reserve;
  - an HTTP error never shows the key.
- `test_the_sharp_line_bets_a_matched_game_and_the_line_never_reaches_jev`: through the real scan, a matched NFL
  game gets a $250 probe; the judgment carries the line; nothing from the odds feed appears in what Jev is sent.
- The retired `jev_alone` no longer bets, isn't tuned, and still settles (updated pipeline and tuning tests).
- 138 offline tests pass.
- A read-only dry run on live data (2026-10-10, before any bet): 94 games with lines; 24 of the 100 loaded Kalshi
  markets matched a game; none was 3¢ or more under Pinnacle's fair price after fees (best −1¢, most about −2¢,
  about Kalshi's fee). Polymarket's US game markets aren't Yes/No, so the trader doesn't load them.

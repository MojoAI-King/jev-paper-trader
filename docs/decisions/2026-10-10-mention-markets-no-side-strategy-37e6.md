# Mention markets NO side strategy

Kind: Living. Decision entry.

- **ID:** 2026-10-10-mention-markets-no-side-strategy-37e6
- **Status:** accepted
- **Date:** 2026-10-10

## Decision

On Joey's "you have the ability to do what you need to fix this ... figure out what's missing to make a serious
winner":

1. **A new strategy, `mention_no` ("Mention markets, NO side").** It has no AI forecast. In Kalshi mention markets
   ("will X say Y" at an earnings call, interview or speech), its probability is `engine.mention_prior`: the mid,
   less 12 points (`mention.yes_bias`) when the mid is 30–70¢ (`mention.band`).
   - Its rules buy only at 30–70¢, with an edge bar of 3¢, so in practice it buys NO in that band.
   - It never bets within `mention.min_hours_before` (1 hour) of the market's expected end, so never during the
     event.
   - It never buys more contracts than the order book offers at the ask (`no_ask_size`, which is Kalshi's YES-bid
     size).
   - It is sized like every strategy by measured skill (source `mention_prior`): probes until its edge shows on 300+
     markets.
2. **How mention markets reach it.**
   - `markets.fetch_kalshi`'s walk keeps every market with MENTION in its ticker, whatever its volume
     (`LAST_MENTIONS`, up to 300). The top-100-by-volume cut never included them.
   - The scan's `_mention_pass` looks at each one once per `rejudge_after_hours`, needing no Jev or Claude call, and
     logs each look to `papertrade_data/mentions.jsonl`.
   - `settle` and the skill measure read that log, so markets that were only looked at still get scored.
3. **One bet per event, soonest first** (added after the first live run). At 06:05Z on 2026-10-10 the pass saw 168
   mention markets and placed its 5 daily probes, all on one event (Jensen Huang's GTC Berlin keynote, which
   resolves 2026-11-05). Those five are one bet, since the same speech decides them all, and they are slow to
   resolve. The pass now takes at most one bet per event per strategy and looks at the soonest-ending markets first.
   The probes were capped at 100–222 contracts ($47–90), the size the asks offered.
4. **A faster pace** (2026-10-10, Joey: "then why not check more often ... if that will enhance our chance of
   winning do it"):
   - Cycles run every 15 minutes instead of 30: the Cloudflare trigger is now :04, :19, :34 and :49, and the
     workflow's `due` gate is 12 minutes.
   - Mention markets are looked at again every hour instead of 6 (`mention.rejudge_hours`).
   - `mention_no` may place 15 probes a day instead of 5 (`mention.max_probes_per_day`), still one per event.
   - Claude research keeps its daily cap and the odds feed keeps its quota pace, so neither grows.
   - Millisecond trading was ruled out: it can't be simulated honestly on paper, it needs always-on co-located
     servers and real accounts, the venues delay fast takers, and incumbents hold the speed edge (report 15).
5. **`jev_alone_bold` retired**, as `jev_alone` was: its forecaster scores like a coin flip and adds nothing to the
   price. Its ledger still settles, and its colour slot (6) went to `mention_no`.

## Why

Research report 15 found one documented bias larger than a slow taker's costs: YES optimism in Kalshi mention markets
(Bartlett & O'Hara 2026, citing the WSJ: YES at 50¢ settled YES about 40% of the time across 35,000+). We replicated
it on 639 settled Kalshi mention markets (55 events) from public data. At the first real taker purchase before the
event, after Kalshi's fee, NO at 30–70¢ won 61.7% against the 49.3% its price implied: **+21.0%, 95% range +6.1% to
+35.5%**. YES at 50–90¢ lost 14–22%. It is the first edge in this project to clear costs on real data. The same
session's honest maker test showed that cheaper execution alone only reaches break-even, so an edge has to come
from a bias like this one.

## Alternatives rejected

- **Betting it at full size now.** It was found on history, and report 13 says a pattern found on one history must
  prove itself on new markets. Probes until λ is measured on 300+ markets; the kill and keep rules are in
  `docs/EXPERIMENTS.md`.
- **Routing mention markets through the Jev pipeline.** That would spend Jev calls and the 40-market judging budget
  on markets where Jev adds nothing.
- **Logging mention looks in `judgments.jsonl`.** Every reader of that file expects Jev's answers; a separate log
  keeps them safe.
- **Resting NO orders.** They might save 4–5 points (the maker test), but mention markets move fast when the speech
  starts. Taking at the ask is the simpler first test.

## Risk

- 55 events is a small base, and the bias may shrink once it is known.
- Mention markets are under a CFTC review; Kalshi pulled its sports mention markets in August 2026. Supply may dry
  up.
- Wording traps (a Netflix "Warner Bros" market fell from 90¢ to under 40¢ in 40 minutes) and suspected insider
  trading (a White House teleprompter case) can hit NO.
- A 30-minute poller only sees a market while it is more than 12 hours from closing (the walk's first slice) and
  more than an hour from its expected end.
- Thin books cap our size at whatever the ask offers.

## Reversibility

Remove `mention_no` from `policy.json`, or mark it `retired: true`; its ledger stays and settles. `mentions.jsonl` is
only a log. `jev_alone_bold` returns by removing its `retired` flag.

## Evidence

- Through the real scan:
  - `test_the_mention_strategy_buys_no_before_the_event_within_what_the_ask_offers`: a NO probe, the log entry, no Jev
    call, no relog within the hour;
  - `test_mention_markets_outside_the_band_near_the_event_or_thin_get_no_full_bet`: no edge outside the band, nothing
    within an hour of the end, and the bet capped at the 40 contracts the ask offers;
  - `test_settling_scores_mention_markets_that_were_only_looked_at`.
- `test_kalshi_dollars_and_cents` covers the ask sizes, with the NO size taken from the YES bid.
- The retired `jev_alone_bold` no longer bets or is tuned (updated tests).
- 141 offline tests pass.
- The replication and the maker test are in `docs/research/CHECKS.md`.
- `test_one_mention_bet_per_event_soonest_first`. 142 offline tests pass after the change.
- `test_the_mention_strategy_has_its_own_daily_probe_limit` (15, not skill's 5). 143 offline tests pass.

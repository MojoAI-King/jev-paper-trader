# Mention strategy reads every event and times bets by the event date

Kind: Living. Decision entry.

- **ID:** 2026-10-10-mention-strategy-reads-every-event-and-t-0a22
- **Status:** accepted
- **Date:** 2026-10-10

## Decision

On Joey's "ok yes" to backlog item B32 ("increase your steps and get more and more data collected"):

1. **The mention strategy reads every open Kalshi mention market itself** (`markets.fetch_kalshi_mentions`), not
   whatever the price walk happens to reach. Each cycle it reads Kalshi's list of "Mentions" series (once a day),
   then one small request per series: every series with open events, then the longest-unread others, up to 120
   requests about half a second apart. What it has read is kept in `papertrade_data/mention_series.json`.
2. **Bets are timed by the event's own date** (`markets.kalshi_event_time`), never by Kalshi's close. The event time
   is the earliest of the market's occurrence time (when it is more than a day before the close), a date in the
   event's subtitle, title or rules ("On Oct 13, 2026", read as midnight New York time), and the date in the event
   ticker. No bet within `mention.hours_before_event` (6) of it; a market with no date gets no bet.
3. **The mention log stays small.** A market is logged when first seen, when bet, and after its mid moves 5¢
   (`mention.relog_move`), without its rules text, instead of every market every hour with 2 KB of rules each. The
   log is also rotated at 20 MB like the judgment and research logs.
4. **Settle skips looked-only mention markets until their event date**, since none can be decided earlier.
5. **An optional limit to young markets** (`mention.max_hours_listed`, off), in case purchases late in a market's
   life turn out not to pay (see Evidence).
6. **One pre-B32 bet is left out of the keep-or-kill count**, decided before it settles: NO on
   KXBURNHAMMENTION-26SEP16-UKRA, whose event ("next Prime Minister's Questions") has no date (`docs/EXPERIMENTS.md`).

## Why

- On 2026-10-10 Kalshi had 76 open mention events (1,274 markets) and settles about 48 a week, but the strategy saw
  8 events: the price walk orders markets by close time, and Kalshi closes a mention market about two weeks after its
  event, so most sat beyond the walk's 60-page limit. At one bet per event the 150-bet test would have taken months.
- The old guard ("more than an hour before the end") measured from that late close, so the strategy could buy
  during or after an event, which the history test never measured. It did once: the Burnham bet above.
- With 15-minute cycles and hourly re-logs, `mentions.jsonl` grew about 10 MB a day (4.5 MB in its first 12 hours).
  GitHub refuses files over 100 MB, which would have stopped the bot from saving cycles within about ten days.

## Alternatives rejected

- **Read every open Kalshi event each cycle and filter for mentions:** 77 pages and 339 MB a cycle (measured).
- **A 16-day buffer against Kalshi's close (the first stopgap idea):** relies on Kalshi's two-week convention,
  which is not a rule; the event date is published, so it is used directly.
- **Keep hourly re-logs and archive more often:** the repository would still grow ~10 MB a day.

## Risk

- Kalshi may rate-limit 120 extra small requests a cycle from GitHub's shared runners. Failures are per series,
  logged as scan problems, and retried next cycle.
- A wrong date makes the guard err early (the earliest date wins), so the cost is a missed bet, not a live one.
- The cycle takes about 90 seconds longer.

## Reversibility

Easy. The reader is one entry in `markets.FETCHERS`; removing it leaves the strategy with no markets (it bets
nothing). The guard and logging are settings in `policy.json` (`mention`). Old log rows stay valid.

## Evidence

- Kalshi public API, 2026-10-10: 454 Mentions series; 43–52 mention events settled in each of the last four weeks;
  76 open events, 459 markets priced 30–70¢ in 74 of them. The trader's pass saw 168 markets in 8 events.
- Close times read for six series: the debate on Oct 13 closes Oct 27, NVIDIA's Oct 21 event closes Nov 5, the
  Fed's Oct 28 press conference closes Oct 29 with an expected expiration of Nov 12.
- Read-only dry run of the new reader (half the series before its time cap): 667 markets in 41 events, every one
  with a date, 46 past or within 6 hours, 36 events with a NO edge of 3¢ or more.
- Offline tests: 150 pass (new: event-time cases, the reader on recorded-shape responses, a failed series read,
  the guard, lean logging, the settle skip, the young-market limit).

# Jev Paper Trader

Paper trading on **real** Polymarket and Kalshi prediction markets, using a **fake $100,000** bankroll
and TypeSafe's Jev as the judge. No accounts, no real money, and no real orders. The project only reads
public market prices.

The goal isn't P&L. It's to answer one question honestly: **does Jev forecast these markets better than
the market's own price?** If it does, there's an edge worth testing with real money. If it doesn't,
any profit is luck.

## Quick start

1. Open this folder in VS Code.
2. **Terminal → Run Task… → "1. Check Jev connection"**. It should print `Jev: OK`.
3. **Run Task… → "2. Preview live markets"** shows what Polymarket and Kalshi are returning.
   No Jev calls or bets happen here.
4. **Run Task… → "3. Daily run"** settles finished bets, scans for new ones, and prints the report.

Run the daily task once a day. The same commands work from any terminal:

```bash
python3 -m papertrade ping      # key + connection check
python3 -m papertrade markets   # preview market feeds
python3 -m papertrade daily     # settle -> scan -> report
python3 -m papertrade report    # just the report
```

Needs Python 3.9 or later and nothing else. Your key lives in `.env` as `TYPESAFE_AI_API_KEY`.

## How a bet happens

For each market (question, resolution rules, and close date, **but never the price**), Jev answers three
questions in a single call:

| Question | Used for |
| --- | --- |
| `p_yes`: will this resolve YES? | Jev's probability |
| `rules_clear`: are the resolution rules objective? | Skip vague markets |
| `info_sufficient`: can this be judged without recent news? | Skip markets Jev would be guessing on |

Code then compares Jev's probability with the actual cost of the contract, including fees and slippage.
A fake bet is placed only if **every** gate in `policy.json` passes:

- Edge of at least **8 points** after costs
- Rules clear of at least 0.75, and information sufficient of at least 0.5
- Price between 5¢ and 95¢, closing within 30 days, with enough trading volume
- Size: quarter-Kelly, at most **2%** of the bankroll per bet and **30%** in open bets overall

## Reading the report

- **Bankroll and P&L**: how the fake $100k is doing. Open bets are valued at what they cost.
- **Brier score, Jev vs. Market**: the number that matters. Lower is better. It's measured on
  every judged market that resolved, not just the ones bet on. If Jev's score isn't lower than the market's, the
  "edge" is noise. Don't trust either number until about **50 or more** markets have resolved.

## Files

```
papertrade/
  markets.py     # reads Polymarket + Kalshi public data (read-only)
  judge.py       # the questions Jev answers (bump QUESTION_SET_VERSION if you edit wording)
  engine.py      # gates, sizing, fake ledger, settlement, report
  jev_client.py  # tiny Jev API client (stdlib only)
policy.json      # every threshold and limit; tune here, not in code
papertrade_data/ # created on first run: portfolio, every judgment, resolutions
tests/           # offline tests: python3 -m unittest discover -s tests -t .
```

## Costs

Market data is free. Jev charges roughly 4¢ per million input tokens with free output (check your
TypeSafe dashboard for your actual rate). A full scan is about 80k tokens, so a month of daily runs costs
around a dime.

## Known limits (v1)

- **No news feed yet.** Jev only knows the market's own text plus its general knowledge, so the
  `info_sufficient` gate will skip many current-events markets. That's deliberate. Next step: have Claude or ChatGPT
  summarize recent facts for each market into the state, then compare how Jev does with and without it.
- **The Kalshi reader is untested against the live API.** Its field names are handled two ways because the docs
  disagree. If `markets` shows Kalshi failing, Polymarket still works on its own.
- Bets are filled at the listed ask plus 1¢ of slippage. Real fills on thin markets can be worse.

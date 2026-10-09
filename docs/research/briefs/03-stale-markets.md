# Research brief 03: Markets that keep trading after the answer is known

Kind: Reference. One of 14 narrow research briefs for the trader's rebuild (BACKLOG B24), each run as its own
Claude Code session in a VS Code tab. To start it, type in a new tab:
`Run research brief 03: read docs/research/briefs/03-stale-markets.md and follow it.`

Before you start, read `docs/research/README.md` (rules for sessions running side by side, evidence standards, the
report format) and the "What the data says" section of `docs/REBUILD_SCOPE.md`.

## Question

How often do Kalshi and Polymarket markets keep trading below 95–99¢ after their outcome is effectively decided (a game has ended, a number is out, a speech has happened), for how long, and can a small bot find and buy them safely?

## What we already know

- Jev answers an "already decided?" question on every market. With research it rated 11 of 939 finished markets above 0.6, and on those the market's favourite was right as often as Jev.
- Our cycle runs every 30 minutes, so anything that settles within minutes is out of reach.
- Some Polymarket sports markets stay open well after the game starts.

## Find out

- Documented resolution-lag edges on these venues: which market types, the typical price once decided, how long it lasts, and how fast other bots are.
- The risks: disputed resolutions (Polymarket's UMA process), rule details (overtime, postponements, which source is official), Kalshi's early-close rules.
- Fast, free ways to learn an outcome (league and score APIs, government release feeds, transcripts) and their delays.
- Whether a 30-minute cycle can ever catch these, or what cadence it would need.

## Leave out

Gaps across venues (brief 02); sportsbook odds (09).

## Deliverable

Write `docs/research/03-stale-markets.md` in the report format from `docs/research/README.md`, and include
the market types worth watching, the signal that shows each one is decided, and the cadence needed.

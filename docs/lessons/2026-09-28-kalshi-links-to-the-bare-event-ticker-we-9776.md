# Kalshi links to the bare event ticker were Page not found

Kind: Living. Lesson entry.

- **ID:** 2026-09-28-kalshi-links-to-the-bare-event-ticker-we-9776
- **Status:** accepted
- **Date:** 2026-09-28

## What broke

Joey clicked a Kalshi bet in the live feed and landed on Kalshi's "Page not found". A link that doesn't open
the bet reads as a bet that isn't real.

## The mechanism

`markets.normalize_kalshi` built `https://kalshi.com/markets/<EVENT_TICKER>` (e.g. `.../KXLEADERMLBHR-26`).
Kalshi's site has no route for a bare event ticker. Its event pages are `/markets/<series>/<slug>/<event>`,
all lowercase, and the slug can be any text (checked in headless Chrome, 2026-09-28: `.../kxnbagame/x/
kxnbagame-26oct20okcsas` opens "OKC Thunder vs SA Spurs"). A plain `curl` can't check this: Kalshi answers
scripts with a Vercel "Security Checkpoint" (429), so the 404 was never seen when the link was written.
Every Kalshi link since the first cycle was broken; Polymarket's `/market/<slug>` links were fine.

## The fix

`papertrade/markets.py`: `kalshi_url(event, series, title)` builds `/markets/<series>/<title-slug>/<event>`
(series = the event ticker's first part unless the API gives one). `fix_url` repairs links saved in old
ledgers, and `dashboard._fix_links` runs every `url` in the page's summary through it, so old bets open too.

## The rule

Check a link to a third-party site the way a person opens it (a real browser), on a real record, before
shipping it; a script's status code says nothing when the site blocks scripts.

## What now enforces it

`NormalizeTests.test_kalshi_links_open_the_event_page` pins the format and the repair of old links.
Nothing automated opens the links in a browser; that was checked by hand.

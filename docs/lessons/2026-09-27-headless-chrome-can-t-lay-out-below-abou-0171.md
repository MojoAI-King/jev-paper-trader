# Headless Chrome can't lay out below about 500px: check phone width in a fixed-width iframe

Kind: Living. Lesson entry.

- **ID:** 2026-09-27-headless-chrome-can-t-lay-out-below-abou-0171
- **Status:** accepted
- **Date:** 2026-09-27

## What broke

A screenshot of the redesigned page taken with `--window-size=420,5200` showed the standings'
money column, the race chart and the bet slips cut off at the right edge, which looked like
horizontal overflow at phone width. The earlier dashboard's phone check (BACKLOG B8) had been left
unverified for the same reason.

## The mechanism

Headless Chrome keeps a minimum window width of about 500 CSS pixels, so a 420px window still lays
the page out at about 500px and the screenshot crops the right side. The crop is the screenshot's,
not the page's; the picture cannot tell the two apart.

## The fix

Render the page inside a harness page with `<iframe style="width:390px">` pointing at the built
file, and screenshot the harness at a wide window. The iframe's viewport really is 390px, so media
queries and wrapping behave as on a phone. The redesigned page was checked this way on 2026-09-27
(real and example data side by side): no horizontal overflow; standings and slips stack.

## The rule

For a phone-width check, never trust a headless window narrower than 500px. Put the page in a
fixed-width iframe (390px for a common phone) and screenshot that.

## What now enforces it

Nothing yet. The harness is a four-line HTML file described above; the page-redesign preview build
script in the session scratchpad used it.

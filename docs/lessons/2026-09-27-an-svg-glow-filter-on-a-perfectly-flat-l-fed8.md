# An SVG glow filter on a perfectly flat line makes the line disappear

Kind: Living. Lesson entry.

- **ID:** 2026-09-27-an-svg-glow-filter-on-a-perfectly-flat-l-fed8
- **Status:** accepted
- **Date:** 2026-09-27

## What broke

On the mission-control page's equity chart, only the Bold strategy's line showed. The four strategies
still sitting at exactly $100,000 had end dots and labels but no lines.

## The mechanism

The lines used `filter="url(#glow)"`, and the filter used SVG's default `filterUnits="objectBoundingBox"`
with `x/y/width/height` as percentages of the element's bounding box. A perfectly horizontal path has a
bounding box of zero height, so the filter region has zero height and the filtered element renders
nothing. Bold's line dropped, so its box had height and it rendered.

## The fix

`papertrade/dashboard_template.html`, `drawChart`: the filter is sized to the whole chart with
`filterUnits: "userSpaceOnUse", x: 0, y: 0, width: W, height: H`.

## The rule

Never size an SVG filter (or gradient) by the bounding box of something that can be flat: a line chart
of values that haven't moved yet is exactly that. Use `userSpaceOnUse` with the chart's own size.

## What now enforces it

Nothing automated; the comment on the filter says why it is sized that way.

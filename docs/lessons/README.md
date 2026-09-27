# Lesson entries

Kind: Living.

One file per lesson, named `<id>.md` with an ID shaped `YYYY-MM-DD-<slug>-<four hex digits>` (the local date, up to 40 lowercase letters, digits and hyphens from the title, and a random suffix). Create one with `skilliton record lesson "<title>"`; it shows the entry first and writes it with `--apply`. The status is `proposed` on a branch that is not an integration branch (main, master), otherwise `accepted`.

An entry has this shape:

    # <title>

    Kind: Living. Lesson entry.

    - **ID:** <id>
    - **Status:** proposed | accepted
    - **Date:** YYYY-MM-DD

    ## What broke
    ## The mechanism
    ## The fix
    ## The rule
    ## What now enforces it

Write each section in plain language; when nothing enforces the rule yet, say so. `skilliton index` lists every entry in `docs/LESSONS.md`, sorted by ID; edit the entries, not the generated list.

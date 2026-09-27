# Decision entries

Kind: Living.

One file per decision, named `<id>.md` with an ID shaped `YYYY-MM-DD-<slug>-<four hex digits>` (the local date, up to 40 lowercase letters, digits and hyphens from the title, and a random suffix). Create one with `skilliton record decision "<title>"`; it shows the entry first and writes it with `--apply`. The status is `proposed` on a branch that is not an integration branch (main, master), otherwise `accepted`.

An entry has this shape:

    # <title>

    Kind: Living. Decision entry.

    - **ID:** <id>
    - **Status:** proposed | accepted
    - **Date:** YYYY-MM-DD

    ## Decision
    ## Why
    ## Alternatives rejected
    ## Risk
    ## Reversibility
    ## Evidence

Write each section in plain language. `skilliton index` lists every entry in `DECISIONS.md`, sorted by ID; edit the entries, not the generated list.

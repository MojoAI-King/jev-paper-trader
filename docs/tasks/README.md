# Task records

Kind: Living.

One file per task, named `<id>.md` with an ID shaped `YYYY-MM-DD-<slug>-<four hex digits>` (the local date, up to 40 lowercase letters, digits and hyphens from the title, and a random suffix). Contributors on different branches never allocate the same sequential number, so they do not overwrite each other's records. Start one with `skilliton task start "<title>"`.

A task record has this shape:

    # Task: <title>

    Kind: Living. Task record.

    - **ID:** <id>
    - **State:** planned | in-progress | blocked | review | done-local | merged | released | verified | abandoned
    - **Branch:** <branch>
    - **Owner:** <label, not an authenticated identity>
    - **Updated:** <ISO date and time>

    ## Request
    ## Acceptance criteria
    - [ ] <criterion>
    ## Decisions
    ## Checkpoints
    ### <ISO date and time>
    - **State:** ...  - **Evidence:** ...  - **Next:** ...  - **Git:** <branch> @ <short head>, <n> uncommitted
    ## Handoff
    - **State:** ...
    - **Next:** ...
    - **Blocked:** ...
    - **Watch out:** ...

Keep local completion (done-local) separate from merged, released and verified. On a branch that is not an integration branch (main, master), a task's handoff goes in its own `## Handoff` section, not in `docs/HANDOFF.md`. `skilliton index` lists open tasks in `docs/STATUS.md`.

# zsh traps: a path loop variable wipes PATH; a command in a string never runs

Kind: Living. Lesson entry.

- **ID:** 2026-09-27-zsh-traps-a-path-loop-variable-wipes-pat-a24d
- **Status:** accepted
- **Date:** 2026-09-27

## What broke

Two shell commands failed in ways that looked like something else. A live-page check printed `command not found: curl` and `command not found: python3`. A commit sequence printed `no such file or directory: python3 /private/.../staged_secret_check.py` four times and committed nothing.

## The mechanism

In zsh, `path` is an array tied to `PATH`, so `for path in / /portfolios/main.json ...` replaced the command search path. And zsh does not word-split an unquoted variable, so `CHK="python3 /path/check.py"; $CHK` runs a single program literally named `python3 /path/check.py`. That second one failed closed only because every commit was chained after it with `&&`. A separator line of `===` also errored, because zsh expands a word starting with `=` as a command lookup.

## The fix

Loop variables renamed (`for p in ...`). Checks are called as explicit commands, never through a string variable. Separators use dashes.

## The rule

In this repo's shell (zsh), never name a variable `path`, never store a command with arguments in a string to run later, and read the exit status of every gate before the step that depends on it.

## What now enforces it

Nothing yet: this is discipline. The staged-secret check lives in the session scratchpad, not the repo, and GitHub Actions runs bash, not zsh.

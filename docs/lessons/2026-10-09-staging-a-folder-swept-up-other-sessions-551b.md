# Staging a folder swept up other sessions' work

Kind: Living. Lesson entry.

- **ID:** 2026-10-09-staging-a-folder-swept-up-other-sessions-551b
- **Status:** accepted
- **Date:** 2026-10-09

## What broke

Ten research reports written by other Claude Code tabs, running in this same checkout, were committed in
8905d49 ("docs: B25 and B26 verified live and archived; task closed; handoff"). Nobody had called them done, and the
commit message doesn't mention them.

## The mechanism

The handoff commits ran `git add docs`. Staging a directory takes every untracked and modified file under
it, which is `git add -A` limited to one folder. The research tabs were writing `docs/research/NN-*.md` into that
folder at the same time. The handoff's own watch-out line said "add report files by name, never git add -A", and
the folder form slipped past it. It did no damage only by luck: every report had last been written (21:58–22:09Z)
before the commit at about 22:16Z and hasn't changed since.

## The fix

Report commits now name each file. The handoff commit stages only the files `skilliton checkpoint` writes
(`docs/HANDOFF.md`, `docs/HANDOFF_ARCHIVE.md`, the task record, `docs/STATUS.md`), listed by path.

## The rule

While another session can write into the checkout, stage files by explicit path only: never `git add -A`,
`git add .`, or a directory. Before each commit, read `git status --short` and confirm that every staged path is
one this session wrote.

## What now enforces it

Nothing yet. Skilliton's guardrails block force-pushes, skipped hooks and secret-shaped commits, but not
staging a directory.

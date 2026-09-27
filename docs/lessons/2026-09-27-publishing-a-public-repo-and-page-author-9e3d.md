# Publishing a public repo and page: author emails, backup refs, 5-minute raw cache

Kind: Living. Lesson entry.

- **ID:** 2026-09-27-publishing-a-public-repo-and-page-author-9e3d
- **Status:** accepted
- **Date:** 2026-09-27

## What broke

Nothing broke in public, but three things nearly did. The repo was about to go public with four commits authored under Joey's work email. The history rewrite that fixed that left a local backup ref still holding the email. And the page's data looked stale right after a push.

## The mechanism

A public repository publishes every commit's author and committer email. `git filter-branch` keeps the old commits under `refs/original/`, which a plain `git push` skips but a mirror push would send. `raw.githubusercontent.com` serves files with `cache-control: max-age=300` (and `access-control-allow-origin: *`), so a pushed `summary.json` can be up to 5 minutes old when the page fetches it.

## The fix

The four unpushed commits were re-authored to `62576128+MojoAI-King@users.noreply.github.com` before the first push, and `refs/original/refs/heads/master` was deleted. New commits use the no-reply address. Before the first push, all 89 blobs in the history were checked for the real key values (none found); the tracked `_to_delete/` copy of a broken .git folder held only placeholder text and was untracked. After a push, publishing is confirmed by polling the raw URL until the new content appears.

## The rule

Before a repo goes public, check commit author emails and scan every blob in the history for real key values, not just the working tree. Declare a published change live only after reading it back from the public URL.

## What now enforces it

Nothing automated. The checks were run by hand this session. The GitHub Actions bot commits as `papertrade-bot@users.noreply.github.com`.

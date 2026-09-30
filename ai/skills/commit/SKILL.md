---
name: commit
description: Write a commit message for the staged (or current) changes, and commit when asked. Use when the user wants to commit or needs a commit message.
tier: fast
needs: [tools]
when: [staged changes, uncommitted changes]
---
# commit

## Steps

1. Look at `git diff --cached`. If nothing is staged, look at `git diff` and
   ask which files to stage. Don't stage everything by default.
2. Read `git log -n 10 --oneline` and match the repo's existing message style
   (tense, capitalization, prefixes like `feat:`).
3. Write the message:
   - subject line of 72 characters or fewer, saying what changed and why
   - a body only when the reason isn't obvious from the subject; wrap at 72
4. Show the message. Commit only if the user asked you to commit, not just to
   write a message.

Never commit files that look like secrets (`.env`, keys, credentials). Flag
them instead.

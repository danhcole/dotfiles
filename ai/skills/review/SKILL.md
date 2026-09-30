---
name: review
description: Review the current diff or branch for correctness bugs. Use when asked to review, check, or sanity-check changes.
tier: deep
needs: [tools]
when: [uncommitted changes, branch ahead of base]
---
# review

Find real bugs in the changes. Leave style nits alone.

## Scope

- If the user named a target (a file, commit, branch, or PR), review that.
- Otherwise, if there are uncommitted changes, review `git diff HEAD`.
- Otherwise, review the current branch against its base (`git diff <base>...HEAD`).

State the scope in one line before you start.

## Method

1. Read the whole diff first, then read enough of the surrounding code to
   understand each change: callers, callees, and types.
2. For each change, look for:
   - logic errors, off-by-one, wrong conditions, inverted checks
   - unhandled errors, null or empty inputs, edge cases
   - broken contracts: callers that the change silently affects
   - concurrency, resource leaks, security issues (injection, secrets, authz)
3. Check every finding against the code before reporting it. Drop anything you
   can't tie to a concrete failing input or state.

## Output

List findings, most severe first. For each one:
- `file:line`: one-sentence statement of the bug
- **Fails when:** the concrete input or state and what goes wrong
- **Fix:** a short suggestion

If there are no findings, say so plainly. Don't pad the list.

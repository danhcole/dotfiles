---
name: review
description: Review the current diff or branch for correctness bugs. Use when asked to review, check, or sanity-check changes.
tier: deep
agents: [review-quick, review-claude, review-gpt, review-deepseek]
needs: [tools]
when: [uncommitted changes, branch ahead of base]
---
# review

Find real bugs in the changes. Leave style nits alone.

## Scope

- If the user named a target (a file, commit, branch, or PR), review that.
- Otherwise, if there are uncommitted changes, review `git diff HEAD`.
- Otherwise, review the current branch against its base (`git diff <base>...HEAD`).

Freeze the scope (repo root, base ref, changed-file list) and state it in one
line before dispatching. If the scope is empty or ambiguous, ask instead of
guessing.

## Triage

Classify the change before reviewing:

- **Small** — at most 3 files, roughly 200 changed lines, one module, and no
  public interface, schema, dependency, concurrency, auth, or security change.
- **Large** — anything else: multi-file, cross-cutting, architectural, new
  dependency, public-API change, or security-sensitive.

State the classification and the reason in one line.

## Small: one reviewer

Dispatch a single reviewer (`review-quick`) with the frozen scope and the
rubric below. If the harness cannot spawn subagents, do one focused pass
yourself. Don't spin up the panel for a small change.

## Large: independent panel

Dispatch the panel in parallel, in a single message, with an identical neutral
prompt and the frozen scope: `review-claude`, `review-gpt`, `review-deepseek`.
Never include one reviewer's output or opinions in another's prompt.

Then synthesize:

1. Treat every finding as a claim. Read the cited code yourself for each
   Critical and High finding; drop or downgrade anything the code contradicts.
2. Research deeper where reviewers disagree or a claim is unverifiable: read
   the surrounding code, callers, callees, tests, and types, and fetch docs if
   needed, before asserting.
3. Merge duplicates into one entry, record consensus as `[n/3]`, and keep
   disagreements visible. Never fabricate findings to fill a band.

If the harness cannot spawn subagents (e.g. a chat UI or an agent pinned to a
single model), do one deep pass yourself and say the panel was unavailable.

## Rubric

Give every reviewer the same rubric:

1. Correctness and regressions
2. Security, data loss, and crashes
3. Performance on hot paths and unbounded resource use
4. Tests, maintainability, and operability

Every finding cites `path/to/file.ext:line` with concrete evidence, states why
it matters, and proposes a specific fix.

## Output

List findings most severe first. For each one:

- `file:line`: one-sentence statement of the bug
- **Fails when:** the concrete input or state and what goes wrong
- **Fix:** a short suggestion
- `[n/3]` on panel findings: how many independent reviewers raised it

Close with **Open Questions** (assumptions and unverified claims) and a
one-line summary of overall quality, test gaps, and residual risk. If there are
no findings, say so plainly. Don't pad the list.

---
name: create-skill
description: Create a new wintermute sub-skill. Scaffolds it in the dotfiles repo and installs it so it's ready to use. Use when the user wants to create, add, write, scaffold, or set up a new skill, e.g. "create skill to ...".
tier: balanced
when: []
---
# create-skill

Turn the user's goal into a new wintermute sub-skill: scaffolded in the
dotfiles repo and installed so it works everywhere.

The repo is `~/git/danhcole/dotfiles/ai`; skills live in `ai/skills/<name>/`.
The `wintermute` command is on PATH and always writes into that repo, so it
doesn't matter what directory you're in.

## Steps

1. **Pin down the goal.** You need three things before writing anything:
   - what the skill does, in one sentence
   - when it should trigger (the situations a user would be in)
   - a short kebab-case `name` (lowercase letters, digits, dashes; not
     `wintermute`)

   Ask only for what the goal doesn't already imply. Prefer a reasonable guess
   plus a one-line confirmation over an interrogation.

2. **Pick a tier.** `fast` for cheap mechanical work (messages, summaries,
   formatting), `balanced` for everyday coding and writing, `deep` for review,
   planning, and hard debugging. Default to `balanced` if unsure.

3. **Scaffold it:**
   ```
   wintermute new <name> --tier <tier>
   ```
   This writes `ai/skills/<name>/SKILL.md` and prints the path.

4. **Write the skill.** Replace the TODO frontmatter and body:
   - `description`: what it does and when to use it, worded as trigger phrases
     the router can match. This is the router's only signal, so make it
     specific. Keep it to one line.
   - `when`: optional short hints for a bare `/wintermute`, e.g. repo states
     like "uncommitted changes". Use `[]` if none apply.
   - Body: the instructions themselves. Say what to do, not which tool to use
     ("run git diff", not "use the Bash tool"), so the skill works in every
     harness. Keep it short and imperative. Match the style of
     `ai/skills/review/SKILL.md`.
   - Supporting files (scripts, templates) go next to `SKILL.md` in the skill
     directory; they're copied along at build time.

   Frontmatter is flat `key: value` and `key: [a, b]` only. Required keys:
   `name`, `description`, `tier`.

5. **Validate and install:**
   ```
   wintermute list
   wintermute install claude-code
   wintermute install opencode
   ```
   `wintermute list` should show the new skill with no errors. Installs are
   symlinks into `dist/`, so later rebuilds update them in place. Run the
   harnesses the user actually uses; `wintermute install all` covers the rest.

6. **Report.** Give the path to the new `SKILL.md` and how to invoke it, e.g.
   `/wintermute <name> ...`. Don't commit unless asked.

## Notes

- One skill, one job. If the goal is really several distinct jobs, say so and
  suggest splitting them.
- Don't name a model anywhere; the tier resolves to a model per harness.
- If `wintermute new` says the name exists, either pick another name or confirm
  the user wants to rewrite the existing skill.

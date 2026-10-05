---
name: edit-skill
description: Change an existing wintermute skill (a wt-* sub-skill or the wintermute router): its instructions, triggers, tier, or helper files, or the model mapping (which model each tier or helper agent uses), then reinstall. Use when the user wants to edit, fix, tune, update, or change how a skill behaves, e.g. "make wt-review stop flagging X", "edit the commit skill", "use Opus for the deep tier", or after a skill misbehaved.
tier: balanced
when: []
inline: true
---
# edit-skill

Change an existing wintermute skill at its source, then reinstall it so every
harness picks up the change.

The repo is `~/git/danhcole/dotfiles/ai`; skills live in `ai/skills/<name>/`.
The `wintermute` command is on PATH and always works on that repo.

## Steps

1. **Pin the target and the change.** Map the name the user gave to a source
   directory: drop any `wt-` prefix (`wt-review` → `skills/review/`). The router
   `wintermute` lives in `skills/wintermute/SKILL.md.tmpl`. Run
   `wintermute list` to confirm the skill exists.

   If the user is reacting to something that just happened in this
   conversation, that's the spec: what the skill did, and what it should have
   done instead. State the target and the intended change in one line. Ask
   only if either one is ambiguous.

   If the change is about which model runs something (a tier, a helper agent,
   a harness), the target is the model mapping, not a skill: see step 2.

2. **Edit the source, never the install.** Edit files under
   `ai/skills/<name>/` (`SKILL.md` and helper files such as `reviewer.md`),
   and, for model changes, the model mapping:
   - `ai/models.toml` maps each tier (`[tiers.<tier>]`) and helper agent
     (`[agents.<name>]`) to a model per harness. Shared and committed.
   - `ai/models.local.toml` holds per-machine overrides, merged over
     `models.toml` key by key and gitignored. Prefer it when the change is
     only for this machine (a work model set, say) and `models.toml` when it
     should apply everywhere. Ask if unclear.
   - Keep each harness's value format as it is in the file (an alias, a
     `provider/model-id` string, or a `{ provider, model }` table). A tier or
     agent with no entry for a harness isn't offered there. Don't remove one
     unless asked.

   Copies under `~/.claude`, `~/.config/opencode`, `~/.agents`, and `ai/dist/`
   are build output, and the next build overwrites them. Read the whole file
   before changing it.

3. **Keep the invariants.**
   - Frontmatter stays flat: `key: value` and `key: [a, b]` only. Keep `name`,
     `description`, and `tier`. `description` stays one line, worded as trigger
     phrases. It's the router's only signal, so reword it if the change
     affects when the skill should be used.
   - Leave template placeholders (words wrapped in double curly braces, like
     the router's table or review's panel) intact. The build fills them in
     per harness.
   - Never name a model inside a skill. To change how strong a model a skill
     runs on, change its `tier` (`fast`, `balanced`, `deep`). Model names
     belong only in the model mapping.
   - A tier is shared by every skill that uses it, so before remapping one,
     run `wintermute list` and say which skills it affects.
   - Write instructions as what to do ("run git diff"), not which tool to use,
     so the skill works in every harness.
   - Make the smallest change that fixes the behavior, and match the existing
     style. If the request is really a new job, suggest `wt-create-skill`
     instead.
   - Don't touch `rules/` or `bin/wintermute`. If the fix needs one of them,
     say which file and why, and stop.

4. **Validate and reinstall.**
   ```
   wintermute list
   wintermute install claude-code
   wintermute install opencode
   ```
   `wintermute list` must show the skill, or after a mapping change the new
   model for each affected tier, with no errors (`[local]` marks values from
   `models.local.toml`). Reinstall the harnesses the user actually uses
   (`wintermute install all` covers the rest). A mapping change affects every
   skill on that tier, so cover every harness in use. For Claude UI, tell the user to re-upload
   `ai/dist/claude-ui/wt-<name>.zip` in Settings > Capabilities > Skills.

5. **Report.** Show `git diff -- skills/<name>` (run from the repo) and say
   how to try the change. Don't commit unless asked.

## No shell or file access

In a chat-only harness (Claude UI, or an agent without file tools), you can't
edit the repo, so don't claim you did. Instead, output the full revised file,
the path it belongs at (`~/git/danhcole/dotfiles/ai/skills/<name>/SKILL.md`),
and the step 4 commands for the user to run.

# wintermute

A personal skill stack that works across Claude Code, Claude UI, opencode, and Zed.

One entry point, `wintermute`, takes a goal and routes it to a sub-skill
(`wt-review`, `wt-commit`, ...). Sub-skills are real skills, so you can also
call them directly.

## Layout

```
models.toml          tier -> model map, per harness (committed)
models.local.toml    per-machine overrides (gitignored)
rules/base.md        global instructions, loaded by every harness
skills/wintermute/   the router; its skill table is generated at build time
skills/<name>/       one directory per sub-skill
bin/wintermute       list / resolve / build / install / new
dist/                build output (gitignored)
```

## Models: tiers, not names

Each skill declares `tier: fast | balanced | deep` and never names a model.
`models.toml` resolves the tier for each harness:

| tier     | model  |
|----------|--------|
| fast     | Sonnet |
| balanced | Opus   |
| deep     | Fable  |

To use a different model set on one machine (at work, say), create
`models.local.toml` with only the entries that differ. It's merged over
`models.toml` key by key:

```toml
[tiers.deep]
opencode = "amazon-bedrock/..."
zed      = { provider = "amazon-bedrock", model = "..." }
```

`wintermute list` marks overridden values with `[local]`.

How the tier takes effect:
- **Claude Code** (and Zed through `claude-acp`): becomes the skill's `model:`,
  so each sub-skill runs on its own model.
- **opencode**: skills can't set a model, so each sub-skill also gets a
  subagent pinned to its tier's model. The router hands off to it.
- **Claude UI**, **Zed's native agent**: can't switch models mid-chat. Each
  skill carries a note saying which model it's best on.

## Adding a sub-skill

```bash
wintermute new explain --tier balanced
$EDITOR ~/git/danhcole/dotfiles/ai/skills/explain/SKILL.md
wintermute install claude-code
```

Frontmatter supports flat `key: value` and `key: [a, b]` only:

```yaml
---
name: explain
description: What it does. Use when ... (used for triggering and the router table)
tier: balanced
when: [hints for bare /wintermute, e.g. uncommitted changes]
---
```

Write instructions as what to do ("run git diff"), not which tool to use, so
they work in every harness. Supporting files in the skill directory are copied
along.

## Installing

```bash
wintermute install claude-code          # links ~/.claude/skills/*, imports rules into CLAUDE.md
wintermute install claude-code --hook   # also adds a SessionStart nudge toward wintermute
wintermute install opencode             # subagents + AGENTS.md (skills come from ~/.claude/skills)
wintermute install claude-ui            # builds zips to upload in Settings > Capabilities > Skills
wintermute install zed                  # prints a settings snippet + rules for Zed's native agent
```

Installs are symlinks into `dist/`, so rebuilding updates them in place. Add
`--no-prefix` to drop the `wt-` prefix from sub-skill names.

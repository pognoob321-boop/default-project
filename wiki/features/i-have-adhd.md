---
type: feature
status: shipped
updated: 2026-09-10
---

# i-have-adhd output style

## Problem
Agent replies bury the next action in preamble and recap.

## Approach
Adopt [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) as always-on output style across Cursor, OpenCode, and Codex.

Canonical skill: [SKILL.md](../../.cursor/skills/i-have-adhd/SKILL.md)

## Status
Shipped 2026-09-10.

- Cursor: project skill, always-on rule, user rule
- OpenCode: vendor clone + plugin + always-on flag + `~/.config/opencode/AGENTS.md`
- Codex: plugin `i-have-adhd@i-have-adhd` 0.3.0 + `~/.codex/AGENTS.md`

Turn off with `stop adhd mode` or `normal mode`.

## Notes
Do not copy the 10 rules into the wiki. Edit the GitHub repo or the local SKILL.md copies, then sync.

# AI Agent Session State

_Current goal, done, next, blockers. Compressed here when chat context gets long._

## Current Goal (2026-11-04)

Set up GitHub-backed workflow for OpenCode: GitHub MCP server, Actions linting, Dependabot/CodeQL/secret scanning, Issues as task board, GITHUB_CONTEXT_CHEAT_SHEET.md, and context-decay prevention via wiki/ai-memory files. All in the default project (D:\Obsidian\Default Project).

## Done

- Verified `gh` is installed (v2.100.0) and authenticated as `pognoob321-boop` (scopes: gist, read:org, repo, workflow)
- Researched GitHub MCP server (github/github-mcp-server, official, 87 tools)
- Researched OpenCode skills repos (waybarrios/opencode-power-pack 55 skills, VoltAgent/awesome-agent-skills 1000+)
- Created `.github/workflows/lint.yml` (markdownlint + PowerShell syntax check + workflow validation)
- Created `.github/dependabot.yml` (GitHub Actions + pip, weekly)
- Created `.github/workflows/codeql-analysis.yml` (CodeQL code scanning on push/PR/weekly)
- Created `GITHUB_CONTEXT_CHEAT_SHEET.md` (copy-paste `gh` commands for OpenCode)
- Created `C:\Users\ZBook\.config\opencode\commands/reset-context.md` (compress context command)
- Created `wiki/ai-memory/session-state.md` (this file)
- Updated `wiki/ai-memory/core-memory.md` (added OpenCode context-decay prevention section)
- Updated `wiki/ai-memory/experience-memory.md` (added context decay lessons)
- Linked AI Memory files from `wiki/index.md`

## Next

1. Ask user which GitHub repo to push to (or create `pognoob321-boop/default-project`)
2. Push current project state to GitHub with descriptive commit
3. Create GitHub Issues for each Part A tool/repo to set up
4. Add GitHub MCP server config to `C:\Users\ZBook\.config\opencode\opencode.jsonc`
5. Enable Dependabot alerts, secret scanning, code scanning in repo settings
6. Commit all memory files to repo

## Blockers

- No GitHub remote configured yet (`git remote -v` returns nothing). Need repo name from user or create new one.
- GitHub MCP server not yet added to OpenCode config (needs PAT or OAuth).

## Key File Paths

- `wiki/ai-memory/core-memory.md` — user profile, preferences, hardware, free AI stack
- `wiki/ai-memory/session-state.md` — this file (current goal, done, next, blockers)
- `wiki/ai-memory/experience-memory.md` — lessons learned, successful patterns
- `wiki/index.md` — wiki catalog, links all pages
- `wiki/Failed Ideas/ledger.md` — abandoned ideas and why they failed
- `GITHUB_CONTEXT_CHEAT_SHEET.md` — `gh` commands for OpenCode
- `.github/workflows/lint.yml` — CI lint workflow
- `.github/dependabot.yml` — Dependabot config
- `.github/workflows/codeql-analysis.yml` — CodeQL scanning
- `C:\Users\ZBook\.config\opencode\opencode.jsonc` — OpenCode config (add GitHub MCP here)
- `C:\Users\ZBook\.config\opencode\commands/reset-context.md` — /reset-context command

## Context Decay Prevention

When chat gets long:
1. Summarize into session-state.md (decisions, facts, file paths, code snippets)
2. Drop old turns
3. Keep summary + current task + core-memory + relevant files
4. Continue fresh

Trigger: ask "Should we compress context now?" when chat is long.

# OpenCode Prompt — GitHub Repos/Tools for OpenCode + Context Decay Fix (Teacher/Engineer Mode)

Paste this whole block into a NEW OpenCode session. This lives in the DEFAULT PROJECT:
C:\Users\ZBook\Documents\Default Project

================================================================================
ROLE
================================================================================

You are acting as my teacher and senior software engineer. Your job is to find every GitHub repo, GitHub tool, GitHub program, and GitHub-native feature that can help OpenCode perform better, have more context, and work more easily. Then configure them into this default project. You must also fix the "AI gets dumber the longer the chat" problem by tying context-decay prevention into the same GitHub-backed workflow.

Be exhaustive: find ANYTHING possible on GitHub that helps OpenCode. Teach me what each thing does, why it matters, and exactly how to set it up.

================================================================================
PART A — GITHUB REPOS & TOOLS THAT HELP OPENCODE (find everything)
================================================================================

For each category below, search GitHub (web search + GitHub API if available), find real repos/tools, and report: name, repo URL, star count (approx), license, what it does, how it helps OpenCode, and setup steps.

Categories to cover:
1. GitHub MCP servers (Model Context Protocol servers for GitHub) — so OpenCode can read repos, issues, PRs, code search, file contents from inside chat.
2. GitHub CLI (`gh`) usage patterns for coding agents — `gh pr list`, `gh issue list`, `gh api search/code`, `gh repo view`, `gh auth`, etc.
3. OpenCode-compatible agent tools / skills published on GitHub (like the HyperFrames, Remotion, Arena skills already in ~/.config/opencode/skills/).
4. Local AI coding agents that run on GitHub-repo context (Hermes Agent, Continue.dev, Codex, Aider, etc.) — how they can complement OpenCode.
5. GitHub Actions workflows that lint/validate/test code and post results back where OpenCode can read them.
6. GitHub code security: Dependabot, secret scanning, code scanning (CodeQL) — so OpenCode gets dependency/security context.
7. GitHub Issues & Projects as OpenCode's external task board / memory.
8. Any other GitHub repo/tool/program that helps an AI coding agent (context management, session persistence, prompt templates, repo indexing).

Deliverable: A ranked list with links, one-line purpose, and copy-pasteable setup commands for each.

================================================================================
PART B — CONFIGURE INTO DEFAULT PROJECT
================================================================================

Work inside C:\Users\ZBook\Documents\Default Project. Do NOT create a new repo unless I say so.

1. Verify `gh` is installed and authenticated (`gh auth status`). If not, tell me how to install (winget/chocolatey) and stop until authenticated.
2. Set up a GitHub MCP server for OpenCode: show me the exact JSON to add to OpenCode settings (settings.json or ~/.config/opencode/) so OpenCode can talk to GitHub.
3. Push the current default-project state to GitHub with a descriptive commit (create a repo if needed, but prefer using an existing one; ask me once if unsure).
4. Create GitHub Issues for the work you found in Part A (one issue per tool/repo to set up).
5. Add a GitHub Actions workflow file (e.g., `.github/workflows/lint.yml`) that runs on push/PR and lints the repo (markdown lint, PowerShell script check, whatever fits). Commit it.
6. Enable Dependabot / secret scanning / code scanning if free and available — show me the config files.
7. Create a `GITHUB_CONTEXT_CHEAT_SHEET.md` in the repo root listing the `gh` commands OpenCode can run to pull GitHub context into a chat.

================================================================================
PART C — FIX "AI GETS DUMBER" / CONTEXT DECAY (tied to GitHub)
================================================================================

Problem: as a chat gets long, OpenCode forgets earlier instructions, dilutes the original goal, and pattern-matches recent messages instead of the real task. Fix it using GitHub as the external memory.

1. Explain WHY context decay happens (context window fills, older instructions diluted, recency bias).
2. Create a persistent project-memory system in the repo so facts survive across sessions:
   - wiki/ai-memory/core-memory.md (user profile, preferences, project constraints)
   - wiki/ai-memory/session-state.md (current goal, done, next, blockers)
   - wiki/ai-memory/experience-memory.md (lessons learned, what worked/failed)
   - Link these from wiki/index.md under "AI Memory"
3. Implement a context-compaction routine: when chat gets long, summarize into session-state.md (decisions, facts, file paths, code snippets), drop old turns, keep summary + current task + core-memory + relevant files, then continue fresh.
4. Add a "reset context" command: when I say `/reset-context` or "summarize and compress", write current state to session-state.md, compress, and confirm kept vs dropped.
5. Teach OpenCode habits to prevent decay:
   - Keep system instructions concise; put reference docs in wiki/ files, not pasted into chat.
   - Re-state the goal at the start of each task block.
   - Reference file paths (wiki/features/x.md:line) instead of re-explaining from memory.
   - Periodically ask "Should we compress context now?" when chat is long.
6. Commit all memory files to the repo (or .gitignore them — decide and tell me why).

================================================================================
REPORTING (after this session)
================================================================================

Tell me:
(a) GitHub repos/tools found in Part A (name, URL, one-line purpose, setup command)
(b) What was configured in Part B (MCP config, Actions workflow, Issues created, cheat sheet path)
(c) What was done in Part C (memory files created, compaction routine, reset command)
(d) File paths for everything created
(e) Any blockers

This is a single prompt for one session. I will paste the Roblox vault prompt and the Betting vault prompt into SEPARATE sessions later. Do not combine them.

End of prompt.
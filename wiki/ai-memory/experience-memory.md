# AI Agent Experience Memory

_Stores learned patterns and successful approaches across sessions._

## Successful Patterns

### TikTok Video Research
- TikTok short links (vt.tiktok.com) require HTTP redirect following to resolve
- PowerShell `Invoke-WebRequest` works to follow redirects and get final URLs
- Webfetch tool cannot handle TikTok's JS-heavy pages
- Searching creator handles + video IDs gives best results
- Chat context clues ("How too token max", "Is their setup free") help narrow search scope

### Hardware Assessment
- Use `Get-CimInstance Win32_*` commands instead of deprecated `wmic` on Windows 11
- Key specs to check: CPU, RAM, GPU VRAM, Storage, OS
- For local AI: RAM is most important (need 32GB+ for 12B models), VRAM limits model size
- HP ZBook 15 G3 can run models up to 12B parameters comfortably

### Wiki Auto-Save
- Save research findings to wiki immediately as they emerge
- Update wiki/log.md with dated entry
- Update wiki/index.md if new page created
- Update core-memory.md with user hardware/preferences
- Never wait until end of session to save

## User Preferences
- Prefers free open-source alternatives over paid tools
- Wants to use laptop for "doing a lot of work"
- Interested in AI agents and automation
- Direct, technical communication style
- Wants things remembered across sessions

## Context Decay Lessons

### Why context decay happens
- Context window fills up: older instructions get pushed out as new tokens are added
- Dilution: the original goal becomes a smaller fraction of total context
- Recency bias: the model pattern-matches recent messages instead of the real task
- Lost file paths: specific file references from early in the chat are forgotten

### Prevention patterns that work
- Compress into `wiki/ai-memory/session-state.md` before context gets too long (decisions, facts, file paths, code snippets)
- Drop old turns, keep summary + current task + core-memory + relevant files
- Reference file paths (`wiki/features/x.md:line`) instead of re-explaining from memory
- Re-state the goal at the start of each task block
- Keep system instructions concise; put reference docs in wiki/ files, not pasted into chat
- Ask "Should we compress context now?" when chat is long

### Compression routine (/reset-context)
1. Read core-memory.md, session-state.md, experience-memory.md to ground the summary
2. Write dated entry to session-state.md: goal, decisions (with file paths), done, next, blockers
3. Confirm explicitly: kept (session-state.md, core-memory.md, experience-memory.md, current task) vs dropped (older chat turns, intermediate reasoning)
4. Continue fresh from session-state.md + current task

**Tags:** context-decay, ai-memory, session-compression, reset-context

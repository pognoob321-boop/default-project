# AI Agent Core Memory

_Last synced: 2026-11-04_

## User

User on Windows, prefers free open-source tools, interested in AI agents and automation

**Tags:** user, preferences

---

## Hardware

**HP ZBook 15 G3** (Workstation laptop)
- CPU: Intel Xeon E3-1505M v5 (4 cores, 8 threads, 2.8GHz)
- RAM: 32GB DDR4 2133MHz (Samsung + Hynix)
- GPU: NVIDIA Quadro M2000M (4GB VRAM) + Intel HD P530
- Storage: 256GB SSD (Toshiba) + 1TB HDD (Toshiba)
- OS: Windows 11 Pro
- Can run local AI models: YES — up to 12B parameters comfortably

**Tags:** hardware, laptop, zbook, local-ai-capable

---

## Free AI Tools Stack (Proven on This Hardware)

### Tier 1: Essential Installs
1. Ollama — ollama.com (runs local AI models) ✅ INSTALLED
2. LM Studio — lmstudio.ai (visual interface for local models)
3. Hermes Agent — `pip install hermes-agent` (free, open-source AI coding agent) ✅ INSTALLED
4. VS Code + Continue.dev extension (AI coding in editor)

### Tier 2: Productivity
5. LibreOffice (replaces Microsoft Office)
6. GIMP (replaces Photoshop)
7. DaVinci Resolve (replaces Premiere Pro)
8. Obsidian (replaces Notion)
9. Bitwarden (replaces 1Password)

### Tier 3: Browser Tools
10. Claude.ai (free tier)
11. ChatGPT (free tier)
12. Google Docs
13. Figma (free tier)
14. Perplexity.ai (free tier)

### Can Run Locally
- Gemma 4 E4B (~6GB) — fast, great for coding
- Gemma 4 12B — fits in RAM, runs well
- Llama 3 8B — fast and capable
- Qwen 2.5-Coder 7B — excellent for coding
- DeepSeek Coder 6.7B — good for code generation

### Cannot Run Locally
- 30B+ parameter models (needs more VRAM/RAM)
- Video generation (needs powerful GPU)
- AI model training (too slow)

**Tags:** tools, free, local-ai, productivity, setup

---

## Search Methodology Preferences

**Looksmaxxing research:** When researching looksmaxxing or facial aesthetics, always prioritize primary sources from the looksmaxxing community itself (e.g., looksmax.org, looksmaxxing forums) rather than secondary sources (mainstream media, beauty blogs, or academic summaries that interpret the community's findings). The community's raw data, protocols, and experiential reports are more accurate than third-party interpretations.

**Tags:** research, looksmaxxing, primary-sources, methodology

---

## Hermes Agent (Local AI Agent)

**Status:** ✅ FULLY CONFIGURED AND READY
- Hermes Agent v0.20.0 installed
- Ollama v0.33.3 with llama3.1:8b model (128K context, 4.9GB)
- Config: provider=custom, base_url=http://localhost:11434/v1
- Desktop installer ready at: C:\Users\ZBook\Downloads\Hermes-Setup.exe
- 100% local, $0 cost, no API keys needed
- Config location: C:\Users\ZBook\AppData\Local\hermes\config.yaml

**Tags:** hermes, local-ai, ollama, desktop-app, setup-complete

---

## OpenCode Context Decay Prevention

**Problem:** As a chat gets long, OpenCode forgets earlier instructions, dilutes the original goal, and pattern-matches recent messages instead of the real task.

**Fix:** Use GitHub-backed wiki/ files as external memory. Facts survive across sessions.

**Files:**
- `wiki/ai-memory/core-memory.md` — user profile, preferences, project constraints (this file)
- `wiki/ai-memory/session-state.md` — current goal, done, next, blockers (compressed here when chat gets long)
- `wiki/ai-memory/experience-memory.md` — lessons learned, what worked/failed

**Habits to prevent decay:**
1. Keep system instructions concise; put reference docs in wiki/ files, not pasted into chat
2. Re-state the goal at the start of each task block
3. Reference file paths (`wiki/features/x.md:line`) instead of re-explaining from memory
4. Periodically ask "Should we compress context now?" when chat is long
5. When user says `/reset-context` or "summarize and compress": write state to session-state.md, compress, confirm kept vs dropped, continue fresh

**Tags:** context-decay, ai-memory, openai, open-code, session-state

---

## Nanobot

Installed nanobot-ai via pip, configured with OpenRouter API, model: openai/gpt-4o-mini

**Tags:** setup, nanobot, openrouter

---

## Open Cowork

Installed Open Cowork v3.3.1 desktop app, configured with OpenRouter API

**Tags:** setup, open-cowork, openrouter

---

## Nanobot Memory

# Long-term Memory

This file stores important information that should persist across sessions.

## User Information

(Important facts about the user)

## Preferences

(User preferences learned over time)

## Project Context

(Information about ongoing projects)

## Important Notes

(Things to remember)

---

*This file is automatically updated by nanobot when important information should be remembered.*


**Tags:** sync, nanobot

---


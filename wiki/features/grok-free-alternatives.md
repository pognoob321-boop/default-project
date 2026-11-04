---
type: feature
status: active
updated: 2026-10-22
---

# Grok at $0 — What Is Actually Free

## Problem

User asked: is there a free way to get a Grok bot with the same UI and the same goal?
Answer requires separating three different things that all get called "a Grok bot":

1. **Using Grok** (consumer app at grok.com) — has a free tier, but a trimmed one.
2. **The Grok API** (driving a bot) — has **no free tier at all** since 2024-12-31.
3. **A Grok-shaped experience** (chat UI + live search + tools) — this is free and self-hostable.

## Approach / Findings (verified 2026-10-22)

### 1. Grok consumer app — free, but Fast mode only

- `grok.com` works with no card and no X Premium. Logged-out Fast mode also works.
- Free = **Fast mode only**. Auto / Expert / Heavy (Grok 4.7) require a paid plan, so **DeepSearch and extended reasoning are paid-only**.
- Limits: xAI publishes **no free-tier message number**. June 2026 retired the old per-2-hour caps; free Chat/Voice allowances now reset on their own schedule. Only reliable read-out is **Settings → Usage** (web + mobile).
- Image generation: removed March 2026, partially reinstated as "Limited" on the Free tier with the Oct 12 2026 X Subscription grid. Video = Premium ($30).
- Paid tiers now: X Subscription — Plus $8, Premium $30, Super $100, Ultra $200.

### 2. Grok API — NOT free (the trap)

- xAI's public beta "$25/month free API credits" **ended 2024-12-31**. No xAI page has offered free API credits since. Console requires prepaid credits.
- Current list price: `grok-4.7` $2.00 in / $6.00 out per 1M tokens (500k ctx); `grok-4.6` same; `grok-4.3` $1.25 / $2.50 (1M ctx); `grok-build-0.1` $1 / $2.
- Long-context surcharge: a prompt ≥200k tokens bills **every** token at 2× the rate.
- `x_search` server-side tool = $5 per 1,000 posts. `web_search` = $5 per 1,000 calls. So Grok's X-search advantage is a paid feature at the API level too.
- Cheapest real Grok in a bot: `grok-4.3` at $1.25/$2.50 ≈ **$0.01 per typical chat turn**.

### 3. Free API tiers that CAN drive a bot (the $0 substitutes)

- **Groq free plan** (docs verified): `openai/gpt-oss-120b`, `openai/gpt-oss-20b`, `qwen/qwen3.8-27b` → 30 RPM, 1,000 RPD, 8K TPM, 1K TPD. Free key, no card, OpenAI-compatible.
- **OpenRouter free models** (verified by pulling `https://openrouter.ai/api/v1/models` and filtering price=0): every `:free` model is $0 — e.g. `openrouter/free` (auto-router), `nvidia/nemotron-3-ultra-550b-a55b:free`, `google/gemma-4-31b-it:free`, `qwen`/`thinkingmachines/inkling:free`. Model list rotates; re-query the API rather than trusting a cached list.
- **Google Gemini free tier** — NOT verified this session (ai.google.dev fetch failed twice, transport error). Treat as unconfirmed.

### 4. Self-hosted Grok-shaped UI (the "same UI" answer)

**Open WebUI** — 156.4k stars, self-hosted, runs entirely offline, connects Ollama + any OpenAI-compatible API (LM Studio, GroqCloud, OpenRouter, vLLM…).

- Install: `pip install open-webui` → `open-webui serve` → http://localhost:8080. Or Docker (`:main` / `:slim` / `:cuda` / `:ollama` tags). Or a **native Windows desktop app** (github.com/open-webui/desktop).
- Covers Grok's feature set: web search built in (SearXNG, **DuckDuckGo with no API key**, Brave, Tavily, Perplexity, Exa, Jina, Mojeek…), web browsing via `#` + URL, image generation (ComfyUI/A1111 local), voice calls, RAG over 9 vector DBs, persistent memory, notes, automations, MCP, OpenAI-compatible API for bots.
- Fits this hardware: ZBook 15 G3, 31.8 GB RAM, Quadro M2000M 4 GB VRAM → Ollama up to ~12B comfortably. `llama3.1:8b` is already installed.

**nanobot** — already installed on this machine (see `wiki/ai-memory/core-memory.md`), MIT, 49.3k stars. Local version **v0.3.0** (latest is v0.3.5 → upgrade available).

- WebUI + native TUI + channels: **Telegram, Discord, Slack, WeChat/Feishu, Email, Mattermost, Linear**.
- Tools: web search/fetch, shell, cron/automations, image generation, MCP, multi-agent delegation, file readers (pdf/docx/xlsx/pptx), long-term memory ("Dream").
- OpenAI-compatible HTTP API at `/v1/chat/completions` → any bot framework can drive it.
- Currently configured with OpenRouter `openai/gpt-4o-mini` (paid). Point it at a `:free` model or at local Ollama to make it genuinely $0.

### Local state verified on this machine (2026-10-22)

`%USERPROFILE%\.nanobot\config.json`:

- `agents.defaults.model` = **`openrouter/auto`** (routing to paid models), `modelPresets` = `{}` (none saved).
- `tools.web.enable` = true, `tools.web.search.provider` = **`duckduckgo`** (no API key) and `tools.web.fetch.useJinaReader` = true → **live web search is already free and working**.
- `channels`: **every channel is `enabled:false`** — telegram, discord, whatsapp, slack, email, signal, mattermost, feishu, qq, wecom, teams. Only `websocket` (127.0.0.1:8765, the WebUI) is on.
- `tools.imageGeneration.enabled` = false (provider openrouter, `openai/gpt-5.4-image-2`).
- Ollama holds `llama3.1:8b` (4.9 GB) and `llama3:8b` (4.7 GB). Open WebUI is **not** installed.

## Status

- Research complete, nothing installed yet. Two ready-to-run paths:
  - **Path A (same UI):** Open WebUI + Ollama `llama3.1:8b` + DuckDuckGo search provider → Grok-like chat, live search, $0, private.
  - **Path B (same goal, as a real bot):** nanobot (already installed) + OpenRouter `:free` model → Telegram/Discord bot, $0, no install.
- Unresolved: Gemini free tier (fetch failed); whether the user means consumer Grok, an API bot, or a Telegram/Discord bot.

## Notes / Gotchas

- **Don't quote a free-tier message count for Grok.** Every number circulating online is stale; the June 2026 change retired the 10-per-2-hours figure. Only Settings → Usage is truth.
- OpenRouter free models are rate-limited and the roster changes — always re-pull `/api/v1/models`.
- Groq free plan is 1,000 requests/day, which is a lot for personal chat but not for a batch bot.
- The one Grok capability with no free clone is **realtime X/Twitter search** (and DeepSearch). Substitutes: Perplexity/Brave/Tavily free tiers, or SearXNG + your own scraper.
- On Windows, SearXNG is painful (wants Docker/WSL). Open WebUI's built-in DuckDuckGo provider gives zero-setup free search instead.

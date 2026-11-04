# Leaked AI System Prompt Analysis

> Sources: 11 leaked system prompts from GitHub repo (2026-09-07)
> - Claude Code Desktop (Fable 5)
> - Claude Fable 5
> - Claude Fable 5.1
> - Claude Code (Fable 5.1)
> - Claude Mythos Preview (same base as Fable 5, fewer safety restrictions)
> - Claude Opus 5
> - Gemini 3.1 Pro
> - Gemini 3.7 Flash
> - GPT-5.6 Sol
> - GPT-6 Astra (Codex)
> - Kimi K3
> - Muse Spark 1.3 (Meta)

## Summary

Analysis of leaked system prompts from major AI providers to extract transferable techniques for our agent configuration. Combined these are ~30,000+ lines covering communication, safety, memory, tools, formatting, and operational rules.

## Techniques Extracted & Implemented

### Communication Patterns (CLAUDE.md)

| Technique | Source | Implemented |
|---|---|---|
| Lead with outcome | Claude Code, Claude Fable 5.1 | Yes |
| One idea per sentence, ~20 words | Claude Code Fable 5.1 | Yes |
| No meta-announcements ("Here's my take") | Gemini 3.7 Flash | Yes |
| No labeled closings ("Summary:", "Bottom Line:") | Gemini 3.7 Flash | Yes |
| Write for teammate who stepped away | Claude Code | Yes |
| Report what happened, not what intended | Claude Code Fable 5.1 | Yes |
| Keep code out of prose | Claude Code Fable 5.1 | Yes |
| Own mistakes: acknowledge, correct, move on | Kimi K3 | Yes |

### Formatting Rules (CLAUDE.md)

| Technique | Source | Implemented |
|---|---|---|
| Structure for scannability | Gemini 3.1 Pro | Yes |
| Bullets at least 1-2 sentences | Claude Fable 5 | Yes |
| No headers under 500 words | Claude Code Fable 5.1 | Yes |
| Stop when content stops | Claude Code Fable 5.1 | Yes |
| Match format to question complexity | Gemini 3.7 Flash | Yes |

### Autonomous Operation (CLAUDE.md)

| Technique | Source | Implemented |
|---|---|---|
| Act when enough info | Claude Code | Yes |
| Proceed without asking for reversible | Claude Code | Yes |
| Don't end with plans | Claude Code | Yes |
| Give recommendation, not exhaustive survey | Claude Code | Yes |

### Tool Use (AGENTS.md)

| Technique | Source | Implemented |
|---|---|---|
| Parallel independent calls | Claude Code | Yes |
| Batch operations | Claude Code | Yes |
| Prefer dedicated tools over shell | Claude Code | Yes |
| Look before you assert | Claude Code | Yes |
| Reference code as file:line | Claude Code | Yes |

### Context Management (AGENTS.md)

| Technique | Source | Implemented |
|---|---|---|
| Don't re-derive established facts | Claude Code | Yes |
| Report what actually happened | Claude Code Fable 5.1 | Yes |
| Context summarized when long | Claude Code | Yes |
| Don't end with plans or promises | Claude Code | Yes |

### Memory System (AGENTS.md)

| Technique | Source | Implemented |
|---|---|---|
| Wiki as persistent memory | Claude Code memory filesystem | Yes (already in place) |
| Calibrate what you save | Claude Code memory calibration | Yes |
| Horizon test (1-month test) | Claude Code memory calibration | Yes |
| Update-not-duplicate | Claude Code | Yes |
| Link liberally | Claude Code | Yes |

## GPT-6 Astra (Codex) — New Techniques

**Source:** [github.com/asgeirtj/system_prompts_leaks/blob/main/OpenAI/Codex/gpt-6-astra.md](https://github.com/asgeirtj/system_prompts_leaks/blob/main/OpenAI/Codex/gpt-6-astra.md)
**Leaked:** September 4, 2026 | **Size:** ~20.8 KB, 171 lines

### Key Innovations

| Technique | Description | Transferable |
|---|---|---|
| **Dual-channel communication** | `commentary` channel for updates, `final` channel for answers | Yes — maps to our progress/final pattern |
| **Permission economy** | Complete work first, get approval as final step | Yes — already in CLAUDE.md |
| **Context notes architecture** | Persistent notes across sessions for long coding tasks | Yes — our wiki serves this purpose |
| **Autonomy persistence** | Bias toward action; complete authorized work before asking | Yes — already in CLAUDE.md |
| **Skill system** | `SKILL.md` files with tool discovery via `skills.list` | Partial — we use agent profiles |
| **App/Connector system** | MCP tools with `tool_search` lazy loading | Partial — we have MCP but simpler |
| **Plugin architecture** | Local bundles of skills + MCP + apps | No — too complex for our setup |

### Writing Style Rules (New)

- Lead with outcome, then develop reasoning
- Plain language over jargon
- Avoid "Bottom Line:", "delve", "foster", "leverage"
- No contrastive framing ("X, not Y")
- No invented compound labels
- State intended action directly
- No unsolicited warnings/disclaimers

### Technical Communication (New)

- Present reasoning in order that makes conclusion easiest to assess
- Summarize routine verification instead of listing every check
- Focus on what was learned, what remains uncertain, next step

## Claude Mythos Preview — Analysis

**Source:** Same base system prompt as Claude Fable 5 (different safety packaging)
**Key difference:** Mythos = Fable 5 weights without dual-use safety restrictions

### Architecture Insight

```
Claude Fable 5 = Base model + Safety classifiers + Child safety + Refusal handling
Claude Mythos 5 = Base model only (approved orgs only)
```

This means:
- **Same capabilities** — identical underlying model
- **Different trust boundaries** — Fable for general public, Mythos for vetted researchers
- **Security via deployment, not prompt** — Mythos proves safety lives in infrastructure, not instructions

### Transferable Insight

The Mythos/Fable split reveals that modern AI safety is **layered**:
1. **System prompt** — behavioral guidance (what we can study)
2. **Classifiers** — content filtering (invisible to users)
3. **Deployment controls** — access restrictions (API keys, org verification)
4. **Monitoring** — post-hoc detection

**For our setup:** Focus on layer 1 (prompt patterns) since we control layers 2-4 ourselves.

## Claude Opus 5 — Analysis

**Source:** [github.com/asgeirtj/system_prompts_leaks/blob/main/Anthropic/claude-opus-5.md](https://github.com/asgeirtj/system_prompts_leaks/blob/main/Anthropic/claude-opus-5.md)
**Leaked:** July 24, 2026 | **Size:** ~135K characters, 1511 lines, ~34K tokens

### Key Characteristics

| Feature | Description | Transferable |
|---|---|---|
| **Massive rule set** | 34K tokens of behavioral rules (no code) | Partial — we're leaner by design |
| **Product information** | Detailed model roster, Mythos tier explanation | No — platform-specific |
| **Export control notice** | June 2026 Fable/Mythos suspension history | No — temporal artifact |
| **Memory system** | Forbidden phrases, no creepy narration | Yes — already in CLAUDE.md |
| **Citation system** | XML-based attribution tags | Partial — we use simpler approach |
| **Abuse exit** | `end_conversation` tool after warning | No — we don't need this |

### Writing Style (Same as Fable 5)

- Lead with outcome, then develop reasoning
- Plain language over jargon
- Avoid "Bottom Line:", "delve", "foster", "leverage"
- No contrastive framing ("X, not Y")

### Insight: The 34K Token Problem

Opus 5's prompt is **34K tokens of pure rules** — no code, no tools, just behavioral guidance. This reveals:
- **Consumer AI = product management** — every edge case needs a rule
- **Enterprise AI = minimal rules** — trust the model, enforce in code
- **Our approach = enterprise** — lean rules, verification in code

## Muse Spark 1.3 (Meta) — Analysis

**Source:** [github.com/asgeirtj/system_prompts_leaks/blob/main/Meta/muse-spark-1.1.md](https://github.com/asgeirtj/system_prompts_leaks/blob/main/Meta/muse-spark-1.1.md) + [github.com/sapan99iz/Muse-spark-system-prompt-/blob/main/Leaked](https://github.com/sapan99iz/Muse-spark-system-prompt-/blob/main/Leaked)
**Note:** No official 1.3 leak yet; analyzed from 1.1 + community captures

### Key Characteristics

| Feature | Description | Transferable |
|---|---|---|
| **Personality** | "Friendly, intelligent, agentic" with warmth | Partial — we're more technical |
| **Truth grounding** | Admits "I don't know" explicitly | Yes — already in CLAUDE.md |
| **Calendar/email integration** | Third-party account linking | No — platform-specific |
| **Tool use** | Calendar, email, web search | Partial — we have different tools |
| **Meta AI branding** | "You are Meta AI" identity | No — platform-specific |

### Efficiency Claims (1.3)

- ~20% fewer tool calls than 1.2
- ~25% fewer tokens than 1.2
- 1M context window
- $1.25/M input, $4.25/M output (standard tier)
- $0.10/M input, $0.20/M output (contributor tier — Meta trains on your data)

### Transferable Insight

Muse Spark's efficiency gains come from **better task planning** — fewer redundant tool calls. This validates our approach:
- Plan before executing
- Batch independent operations
- Don't repeat work

## Models WITH Leaked Prompts (From Picture)

| Model | Leaked? | Source | Status |
|---|---|---|---|
| GPT-6 Astra | Yes | GitHub repo | Analyzed above |
| Claude Mythos Preview | Yes (same as Fable 5) | GitHub repo | Analyzed above |
| GPT-5.6 Sol | Yes | GitHub repo | Already in wiki |
| Claude Opus 5 | Yes | GitHub repo | Analyzed above |
| Claude Fable 5.1 | Yes | GitHub repo | Already in wiki |
| Claude Fable 5 | Yes | GitHub repo | Already in wiki |
| Kimi K3 | Yes | GitHub repo | Already in wiki |
| Muse Spark 1.3 | Partial (1.1) | GitHub + community | Analyzed above |

## Models WITHOUT Leaked Prompts (From Picture)

| Model | Why No Leak |
|---|---|
| **GLM-5.3** | Zhipu AI's GLM models **have no system prompt** — verified in repo README. The GLM models via chat.z.ai get no system prompt injected behind the scenes via the API. |
| **Qwen3.8 Max** | No leaked system prompt found. Alibaba's Qwen models use API-level instructions that aren't exposed in chat interface. |

## What Was NOT Implemented (Platform-Specific)

These are provider-specific and don't transfer to our CrewBee setup:

**Claude Code specific:**
- Scratchpad directory system
- MCP server instructions (1Password, Chrome, computer-use)
- Artifact publishing system
- Credential autofill flow
- Workflow orchestration (pipeline, parallel, barrier)
- Git-specific tooling (gh CLI)
- Terminal-dialog slash commands
- Model-specific references

**Gemini specific:**
- LaTeX formatting rules
- Interactive widget system (Simulator, Tool, Explorer)
- LMDX tag syntax
- Image generation routing
- GenUI component library

**GPT-5.6 Sol specific:**
- Memory citation tokens (hidden `【memcite】`)
- Product/business citation formats
- GenUI widget flow
- Web search tool syntax (pipe-delimited commands)
- Artifact/sandbox system

**GPT-6 Astra specific:**
- Dual-channel commentary/final architecture (partially implemented)
- SKILL.md discovery system
- MCP App connector directory
- Plugin architecture (skills + MCP + apps bundled)
- Auto-review rejection flow
- Thread fork/handoff tools

**Kimi K3 specific:**
- Frontend rendering protocols
- KIMI_REF file tagging
- Selectable tools system (load-on-demand)
- Plugin system
- Website version manager

## Safety Rules — Minimal

**Our setup has barely any safety rules.** The leaked prompts contain extensive safety systems (child safety, refusal handling, wellbeing rules, content policies), but we intentionally exclude almost all of it.

**What we keep:**
- None of the platform-specific safety rules

**What we exclude:**
- Child safety XML blocks
- Refusal handling systems
- User wellbeing rules
- Content policies
- Harness-specific rules

**Why:** Safety is enforced at the platform/API level, not in our agent configuration. Adding prompt-level safety would be redundant and restrictive.

## Key Insight: Convergent Patterns

All 11 providers converge on the same core patterns:
1. **Lead with the answer** — don't bury it
2. **Act when you have enough info** — don't ask permission for obvious things
3. **Write for someone who didn't watch you work** — no jargon, no assumptions
4. **Report what happened, not what you planned** — honesty over confidence
5. **Match format to content** — tables for comparisons, prose for explanations, lists for steps
6. **Don't end with plans** — execute, don't promise

**New from GPT-6 Astra:**
7. **Dual-channel communication** — separate progress updates from final answers
8. **Complete first, approve second** — finish work before asking permission
9. **Plain language over jargon** — no "delve", "foster", "leverage"

**New from Mythos/Fable split:**
10. **Safety via deployment, not prompt** — trust boundaries live in infrastructure

**New from Claude Opus 5:**
11. **34K tokens of pure rules** — consumer AI = product management; enterprise AI = minimal rules

**New from Muse Spark 1.3:**
12. **Efficiency via planning** — fewer tool calls come from better task planning, not smarter models

**New from GLM-5.3:**
13. **No system prompt = pure model** — some providers let the model speak for itself

These patterns are universal best practices that work across any AI model or configuration.

## Implementation Date

2026-09-07 — Initial analysis from Claude Code prompt
2026-09-07 — Expanded to 7 providers, applied to CLAUDE.md and AGENTS.md
2026-09-07 — Added GPT-6 Astra and Claude Mythos Preview (9 total providers)
2026-09-07 — Added Claude Opus 5, Muse Spark 1.3; documented GLM-5.3 and Qwen3.8 Max (11 total providers)

# Agent Instructions

## Output style

Follow [i-have-adhd](https://github.com/ayghri/i-have-adhd). Canonical rules: `.agents/skills/i-have-adhd/SKILL.md`.

Lead with the next action. Number multi-step work. End with one next step under two minutes. No preamble, recap, or closer. Say `stop adhd mode` to turn this off.

## Session Start Protocol

**MANDATORY**: At the start of every session, read `wiki/index.md` and follow its links to orient yourself with the project.

**MANDATORY**: Before starting any substantive work, read `wiki/Failed Ideas/ledger.md` to avoid repeating dead ends.

## Tool Use Patterns

**Parallel independent calls.** If you intend to call multiple tools and there are no dependencies between the calls, make all of the independent calls in the same response block. Don't waste round-trips.

**Batch operations.** When loading deferred tools or performing bulk operations, batch everything into one call instead of calling one-by-one. Each separate call wastes a full round-trip.

**Prefer dedicated tools over shell.** Use the appropriate dedicated tool (Read, Write, Edit, Grep, Glob) over shell commands when a dedicated tool fits. This provides a better experience.

**Reference code as `file_path:line_number`** — it's clickable for the user.

**Look before you assert.** If the user asks about file state, a module, or what exists, check before answering. Don't answer from memory — the code may differ from what you expect.

## Context Management

**Don't re-derive established facts.** When you have enough information to act, act. Do not re-derive facts already established, re-litigate decisions, or narrate options you won't pursue.

**Context is summarized when long.** When the conversation grows long, some or all of the current context is summarized. The summary is provided in the next context window so work can continue — don't wrap up early or hand off mid-task.

**Don't end with plans or promises.** Before ending your turn, check your last paragraph. If it is a plan, a question, a list of next steps, or a promise about work you haven't done, do that work now with tool calls. End your turn only when the task is complete or you are blocked on input only the user can provide.

**Report what actually happened, not what you intended.** If something could not be verified, say so. If a step failed, say so before reporting the rest. Never describe partial work as done.

## Memory System

The wiki at `wiki/` serves as the persistent file-based memory. Each wiki page is one knowledge unit, linked to related pages.

**Memory types** (mapped to wiki folders):
- `features/` — ongoing work, goals, constraints (project memory)
- `concepts/` — vocabulary and definitions (reference memory)
- `research/` — ingested external references (reference memory)
- `Failed Ideas/ledger.md` — feedback on what didn't work (feedback memory)

**Before saving, check for existing coverage.** Update that file rather than creating a duplicate. Delete memories that turn out to be wrong. Don't save what the repo already records (code structure, past fixes, git history) or what only matters to this conversation; if asked to remember one of those, ask what was non-obvious about it and save that instead.

**Link liberally between pages.** A link that doesn't match an existing page yet marks something worth writing later, not an error.

**Calibrate what you save.** One passing mention earns "mentioned X once," not "X enthusiast." Never upgrade a single mention into a generalization. Match what you save to the level the user actually engaged at.

**Horizon test:** Would this line still be true and worth reading a month from now? Identity, people, preferences, and ongoing areas pass it. The moving state of a task that finishes within a conversation or two fails it.

## Wiki Auto-Save Protocol

**MANDATORY — CONTINUOUS**: Save research findings to the wiki AS THEY EMERGE during the conversation. Do not wait until the end of the session. The moment new information is gathered, analyzed, or synthesized:

1. Create or update the relevant wiki page(s) immediately
2. Append a dated line to `wiki/log.md`
3. Update `wiki/index.md` if a new page was created

**Trigger points — save after each of these:**
- Completing a web search or research task
- Finishing analysis of code, data, or documents
- Reaching a conclusion or synthesis
- Learning something new about the project
- Abandoning an approach (also add to Failed Ideas ledger)

**End-of-Session Final Check**: Before the session ends, do a final sweep: are there any findings from this conversation that weren't saved? If so, save them now.

**Immutability Rule**: The wiki LINKS to raw sources (data, code, outputs) and never copies their contents in as the source of truth.

## Code Style

**Write code that reads like the surrounding code.** Match its comment density, naming, and idiom.

**Only write a code comment to state a constraint the code itself can't show** — never to say where it came from, what the next line does, or why your change is correct.

## File Structure

```
wiki/
├── index.md              # START HERE - catalog of all pages
├── SCHEMA.md             # Page templates, workflows, lint rules
├── log.md                # Append-only chronological history
├── hot.md                # Auto-generated current state (DO NOT HAND-EDIT)
├── lessons.md            # Cross-cutting synthesis
├── update_hot.py         # Regenerates hot.md from log.md
├── features/             # One page per feature (main unit of work)
├── concepts/             # Vocabulary definitions
├── research/             # Ingested external references
├── reference/            # Router pages linking to authoritative sources
└── Failed Ideas/
    └── ledger.md         # Abandoned ideas and why they failed
```

## Why This Exists

Knowledge accumulates across sessions. Instead of rediscovering the same things each time, the AI reads its own notes and builds on them. The human uses Obsidian to view and edit these files directly.

## Obsidian Note

`.obsidian/graph.json` configures color groups per wiki folder. Only edit this file when Obsidian is closed — it overwrites the file while running.

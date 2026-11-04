---
type: feature
status: active
updated: 2026-10-10
---

# Arena Skill (OpenCode port)

## Problem

When an answer is bad, retrying one at a time is slow. [Jakeschincariol/arena-skill](https://github.com/Jakeschincariol/arena-skill)
runs N sub-agents on the identical task with different strategy cards, then a single-elimination
attack/defend/judge bracket until one solution survives. It is a **Claude Code** skill, so it does not
work in OpenCode unmodified.

## Approach

Installed to the OpenCode global skills dir (OpenCode's discovery path:
`~/.config/opencode/skills/<name>/SKILL.md`):

```
C:\Users\ZBook\.config\opencode\skills\arena\
├── SKILL.md
├── bracket.py      (tournament state machine, stdlib only)
├── strategies.json (15 reasoning modes × 12 workflows × 12 strategies = 2160 cards)
└── rubric.md       (judge scoring: correctness 30 / completeness 25 / robustness 20 / specificity 15 / clarity 10)
```

Source clone (throwaway): `%TEMP%\opencode\arena-skill`.

A `/arena` slash command shim was also added (OpenCode has no native slash-command → skill bridge):

```
C:\Users\ZBook\.config\opencode\commands\arena.md
```

It just tells the agent to load the `arena` skill and feeds `$ARGUMENTS` through as the task.

### Patches required for this machine

1. **`python3` is a broken Windows Store App Execution Alias here** (`python3 --version` → exit 9009).
   All invocations use `python` (Python 3.12.10 at `C:\Users\ZBook\AppData\Local\Programs\Python\Python312`).
2. **`bracket.py` `_cmd()` hardcoded `python3 "<SELF>" ...`** in every printed follow-up command.
   Patched to `sys.executable or "python"`, so `next`/`prompts` print a runnable command.
3. **`${CLAUDE_SKILL_DIR}` is never expanded by OpenCode.** SKILL.md now carries the absolute path.
4. **`$ARGUMENTS` / slash-command invocation does not exist in OpenCode.** Skills load via the `skill`
   tool; task + flags come from conversation text. Port note added at the top of SKILL.md.
5. **Claude Code's Agent tool → OpenCode `task` tool.** `bracket.py` printed
   `subagent_type general-purpose`, which does not exist here; wording made agent-agnostic.
6. **No Shift+Tab accept-edits mode**; writes go through OpenCode permission prompts (hundreds on a
   big run — tell the user before spawning).

### Known limitation

CrewBee's coding-team contract exposes only read-only subagents (codebase-explorer, web-researcher,
reviewer, principal-advisor, multimodal-looker). Arena competitors must **write** files into `.arena/`.
If no writable agent type is allowed in the session, the arena cannot run as designed — the skill
instructs the orchestrator to stop and say so rather than improvise.

## Status

Installed, patched, and **verified in live runs**:

- **5-agent run completed** (seed 605668): 25 calls, 3 rounds, ~8 min wall time. Winner: a001 (bye + round 2 win). See run `run-20261010-195503-s605668`.
- **Key fix**: `run_in_background: true` on `task` tool — synchronous delegation acks fail with "fetch failed" but work completes async. Background mode + `delegate_status` is the only reliable tracking.
- **Task file size is the bottleneck**: 51 KB task → 3-5 min/call. Trim to ≤5 KB for 10× speedup.

## Live Run Results (5 agents, 3 rounds)

| Round | Matches | Result |
|-------|---------|--------|
| 1 | a002 vs a005 | a005 wins (a002 missing → fatal) |
| 1 | a003 vs a004 | a003 wins (53 vs 40) |
| 2 | a001 (bye) vs a005 | a001 advances |
| 3 | a001 vs a003 | a001 wins (champion) |

**Champion**: a001 — best balance of completeness, specificity, clarity. a003 strong but had fatal correctness errors (CRAAP vs CRAP, funnel error). a004 dropped user interpretations (fatal to task).

## Practical Recommendations

| Goal | Config | Time |
|------|--------|------|
| Quick answer | `--agents 4 --wave 5` + 5 KB task | 2-3 min |
| Default quality | `--agents 8 --wave 5` + 5 KB task | 5-8 min |
| Maximum rigor | `--agents 16` + 5 KB task | 12-18 min |
| **Note cleanup (this task)** | Single `coding-principal-advisor` + 3 KB task | **30 sec** |

Arena shines on *open-ended design* (architecture, ambiguous spec). For "clean up notes," single-pass synthesis wins.

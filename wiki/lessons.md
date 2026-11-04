# Lessons

Cross-cutting synthesis of what's been learned. Updated as patterns emerge.

---

## User Preferences

- **Loop Optimization**: When user mentions "loop" during a task, optimize loops for performance (reduce iterations, minimize unnecessary work, improve time complexity).
- **RECAP FORMAT (added 2026-10-01)**: When recapping a video/article/idea, explain the concept first (what it means, why it works), THEN give concrete examples. Never lead with bare bullet examples.
- **RESEARCH METHODOLOGY (MANDATORY — updated 2026-09-05)**: 
  - **DEFAULT (full research)**: Gather ALL information. Get every opinion, every perspective, every fact — pros AND cons, what's right AND what's wrong, costs, risks, benefits, criticisms, supporter views, opponent views. Do NOT cherry-pick. Do NOT skip inconvenient data. Sources from DIFFERENT groups, DIFFERENT countries, DIFFERENT institutions. Never rely primarily on Wikipedia. Minimum: (1) ≥1 non-Wikipedia source per major claim cluster, (2) sources span ≥2-3 countries/organization types, (3) no single-source domination, (4) include dissenting/minority opinions alongside majority views.
  - **FAST research (only when user says "fast")**: Use at least 10 different websites. Cover opinions, facts, and how-to from each. Still diverse sources.

## Loop Engineering Format

When user says "loop", use this framework:

### 1. Define the Loop
- Goal: What are we trying to achieve?
- Stop Condition: When is it done? (success/fail/impossible)

### 2. Orchestration (Wiring)
- Trigger: What starts the loop?
- Actions: What steps run each iteration?
- Memory/State: What data persists between iterations?
- Sub-agents: What parallel work happens?

### 3. Control Structure (Safety)
- Verify: How do we check progress each iteration?
- Retry: What happens on failure?
- Escalate: When do we stop and ask for help?

### 4. The Cycle
Trigger → Plan → Execute → Verify → [Pass: ship | Fail: loop again | Impossible: escalate]

**Source**: User-provided images on Loop Engineering (Agent loops, Orchestration vs Control, PM→Agent workflow)

---

## Looksmaxxing Key Findings

### Origin
- Coined on Lookism.net (June 2015), spread from PSL forums (PUAhate, Sluthate, Lookism)
- TikTok mainstream adoption 2022-2023
- Tied to black pill ideology and incel communities

### "Ramus is Law"
- The ramus (vertical jawbone) is critical for facial aesthetics
- Jaw structure is a primary attractiveness determinant
- Forums debate whether eye area, jaw, or overall appeal is "law"

### Evidence-Based Priorities (What Actually Works)
1. **Body fat %**: #1 factor for jawline definition (12-15% for men)
2. **Skincare**: SPF + retinol = measurable results in weeks
3. **Sleep**: 7-9 hours, impacts collagen and hormones
4. **Resistance training**: Builds frame, improves posture
5. **Grooming**: Haircut, brows, dental hygiene (fastest visible change)

### What Doesn't Work
- Mewing in adults (limited bone change, but good breathing habit)
- Bonesmashing (dangerous, no evidence)
- Most "before/after" mewing photos = lighting + weight loss

### Risks
- Body dysmorphic disorder
- Eating disorders (starvmaxxing)
- Radicalization pipeline to incel culture
- Physical harm from extreme practices

---

## Agent Configuration Lessons

### 7-Provider Leaked Prompt Analysis (2026-09-07)
- **Sources**: Claude Code Desktop, Claude Fable 5, Claude Fable 5.1, Claude Code Fable 5.1, Gemini 3.1 Pro, Gemini 3.7 Flash, GPT-5.6 Sol, Kimi K3 (~20,000+ lines total)
- **Convergent patterns** (all providers agree):
  1. Lead with the answer — don't bury it
  2. Act when you have enough info — don't ask permission for obvious things
  3. Write for someone who didn't watch you work — no jargon, no assumptions
  4. Report what happened, not what you planned — honesty over confidence
  5. Match format to content — tables for comparisons, prose for explanations, lists for steps
  6. Don't end with plans — execute, don't promise
- **Communication discipline > technical sophistication**: "Lead with outcome", "write for a teammate who stepped away", and "don't end with plans" directly improve agent usefulness more than any tool or feature.
- **Memory systems converge**: Our wiki-based approach maps to Claude Code's file-based memory, Kimi's todo system, and GPT's context management. The pattern is universal.
- **Safety rules are platform-specific**: Claude's extensive refusal/safety rules, Gemini's LaTeX rules, GPT's content policy, Kimi's harness rules — all are provider-enforced and clash with low-safety preferences. Best to skip them entirely.
- **Formatting is context-dependent**: Gemini's "match format to question complexity" and Claude's "no headers under 500 words" are both valid. The right approach is to format based on what the content needs, not a fixed rule.
- **Autonomous operation = trust**: All providers agree: proceed without asking for reversible actions, stop only for destructive ones, and don't end with plans.

---
name: check-fix
description: "Checks your code for errors after every change, and finds the real cause of bugs before fixing them."
risk: critical
source: custom
date_added: "2026-08-06"
---

# Check & Fix Your Code

Two simple jobs:

1. **Check** - After you change code, make sure it has no errors.
2. **Fix** - When something is wrong, find the REAL cause before fixing it.

---

## Part 1: Check Your Code (Always Do This)

> After EVERY code change, run the checks below. Do not say a task is done until the code is error-free.

### For Python projects
1. `ruff check "path" --fix` - finds style/syntax problems
2. `mypy "path"` - checks types
3. `bandit -r "path" -ll` - checks for security problems

### For Node.js / TypeScript projects
1. `npm run lint` or `npx eslint "path" --fix` - finds style problems
2. `npx tsc --noEmit` - checks types
3. `npm audit --audit-level=high` - checks for security problems

### The Quality Loop
1. Write or edit code
2. Run the check for your project's language
3. Read the results
4. Fix any errors and check again

**If lint fails:** fix the style or syntax issues.
**If tsc/mypy fails:** correct the type mismatches.
**If no checker is set up:** look for `.eslintrc`, `tsconfig.json`, or `pyproject.toml` in the project root and suggest creating one.

---

## Part 2: Fix Bugs Properly (Find the Real Cause First)

> NEVER guess fixes. A quick guess makes new bugs. Find the root cause first.

### The Iron Law
```
NO FIXES UNTIL YOU KNOW THE ROOT CAUSE
```

### Phase 1: Investigate (before ANY fix)
1. **Read the error carefully** - line numbers, file paths, error codes
2. **Reproduce the bug** - can you trigger it every time?
3. **Check recent changes** - what did you change? (git diff, new files, config)
4. **Follow the data** - where does the bad value come from? Trace back to the source.

### Phase 2: Find the pattern
- Find similar working code and compare it to the broken code
- List every difference, even small ones
- Understand what the code depends on

### Phase 3: Test one idea at a time
- State ONE hypothesis: "I think X is the cause because Y"
- Make the SMALLEST possible change to test it
- Did it work? Great. Didn't work? Form a new hypothesis.
- Never change multiple things at once

### Phase 4: Fix and verify
- Fix the root cause, not the symptom
- Make ONE change at a time
- Verify the fix actually works and nothing else broke

### If 3+ fixes fail
- STOP. Question the whole approach/design.
- Talk to your teacher or partner before trying more fixes.

---

## Quick Rules to Remember
- Check code after every change
- Never guess the bug - investigate first
- One change at a time
- Verify before saying it's done
- If stuck after 3 tries, stop and rethink the design

## When to Use
Use this skill after any code change (check) or when you hit any bug, test failure, or unexpected behavior (fix).

## Limitations
- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

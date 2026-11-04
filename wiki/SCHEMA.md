# SCHEMA

Rules, templates, and workflows for this wiki.

---

## 1. Page Templates

### Feature Page (`wiki/features/<name>.md`)

```yaml
---
type: feature
status: active | abandoned | shipped
updated: YYYY-MM-DD
---
```

```markdown
# <Feature Name>

## Problem
<!-- What problem does this solve? -->

## Approach
<!-- How are we solving it? -->

## Status
<!-- Current state, blockers, next steps -->

## Notes
<!-- Implementation details, gotchas -->
```

### Concept Page (`wiki/concepts/<name>.md`)

```yaml
---
type: concept
updated: YYYY-MM-DD
---
```

```markdown
# <Concept Name>

<!-- One-paragraph definition. What does this mean in our project? -->

## Related
<!-- Links to features, other concepts -->
```

### Research Page (`wiki/research/<name>.md`)

```yaml
---
type: research
source: <URL or citation>
verdict: useful | partially useful | not useful
updated: YYYY-MM-DD
---
```

```markdown
# <Research Title>

## Summary
<!-- Key findings in 2-3 sentences -->

## Takeaways
<!-- What's actionable for us? -->
```

### Reference Page (`wiki/reference/<topic>.md`)

```yaml
---
type: reference
updated: YYYY-MM-DD
---
```

```markdown
# <Topic>

> This page links to the authoritative source. Do not duplicate content here.

## Links
- [Link text](URL) — description
```

---

## 2. Workflows

### After completing a unit of work:
1. Create `wiki/features/<name>.md` from the feature template
2. Add a line to `wiki/index.md` under Features
3. Append to `wiki/log.md`: `## [YYYY-MM-DD] feature | <name> | <outcome>`
4. Update `wiki/hot.md` (run `python wiki/update_hot.py` or equivalent)

### After abandoning an idea:
1. Add a row to `wiki/Failed Ideas/ledger.md`
2. Set the feature page status to `abandoned`
3. Append to `wiki/log.md`: `## [YYYY-MM-DD] abandoned | <name> | <reason>`

### After learning something new:
1. Create or update a concept page in `wiki/concepts/`
2. Add a lesson to `wiki/lessons.md` if it's cross-cutting
3. Append to `wiki/log.md`

### After reading external research:
1. Create `wiki/research/<name>.md` from the research template
2. Add a line to `wiki/index.md` under Research
3. Append to `wiki/log.md`

---

## 3. Lint (Self-Check)

Run periodically to catch wiki rot:

- **Orphan pages**: Find pages not linked from `index.md` or any other page.
- **Stale features**: Check if any `status: active` feature hasn't been updated in >7 days.
- **Missing concepts**: If a term appears in 2+ feature pages but has no concept page, create one.
- **Contradictions**: If two pages state conflicting facts, flag and reconcile.
- **Ledger check**: Before starting new work, confirm the idea isn't in the Failed Ideas ledger.

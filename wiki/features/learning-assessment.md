---
created: 2026-09-01
tags: [learning, education, assessment, self-improvement]
status: complete
---

# Learning Method Assessment Tool

> A Node.js program that tests different learning styles and finds what works best for YOU using promise-based loops.

## What It Does

Interactive learning assessment that:
1. **Preference Questionnaire** - Asks about your learning preferences across 6 methods
2. **Practical Learning Test** - Teaches the Pareto Principle using 4 different methods, then tests recall
3. **Capability Assessment** - Evaluates your study environment, time, and tech comfort
4. **Personalized Plan** - Generates rankings, time allocation, and daily schedule

## Learning Methods Tested

| Method | Emoji | Description |
|--------|-------|-------------|
| Visual | 👁️ | Diagrams, charts, mind maps, color coding |
| Auditory | 👂 | Listening, lectures, podcasts, talking out loud |
| Read/Write | 📖 | Reading texts, writing notes, lists, definitions |
| Kinesthetic | 🖐️ | Hands-on practice, experiments, building |
| Social | 👥 | Group study, teaching others, discussions |
| Solitary | 🧘 | Independent study, self-paced exploration |

## Technical Features

- Promise-based loops for sequential/parallel processing
- Async/await for interactive user input
- Scoring engine with capability modifiers
- JSON results export
- Promise.allSettled for error handling demo

## How to Run

```bash
node learning-assessment.js
```

## Promise Loop Concepts Demonstrated

1. **Sequential Loop** - Processes items one by one with `for...of` + `await`
2. **Parallel Loop** - Processes all items simultaneously with `Promise.all()`
3. **Error Handling** - Uses `Promise.allSettled()` to handle failures gracefully

## File Location

- `C:\Users\ZBook\Documents\Default Project\learning-assessment.js`

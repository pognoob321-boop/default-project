---
created: 2026-10-28
tags: [codehs, html, css, design, school-project, cornerstone]
status: done
---

# CodeHS Cornerstone — Login + Meet-Up Form (vitou aesthetic)

> Combined project: `index.html` (login) → `survey.html` (meet-up form). Shared `style.css` (vitou paper/ink/copper palette, Fraunces + Karla, centered cards, drop shadows) and shared `script.js` (guarded modules so each block runs only on its page).

## Deliverable files

- `index.html` — sign-in page
- `survey.html` — meet-up form with live preview ticket
- `style.css` — shared design system
- `script.js` — login validation + survey preview/submit

## Rubric mapping (Athena CSP9S1 Cornerstone Assessment 2, Part 2)

| Criterion | Where it lives |
|---|---|
| Mock Database (JS array) in login.html | `script.js` `users` array (lymeng/vitou/Kour) |
| Form validation | blank fields → error text; bad creds → "Invalid username or password" |
| Multi-page flow | login → `window.location.href = survey.html` after success |
| Dynamic survey output | `renderPreview()` live ticket; `submitMessage()` confirmation banner |
| At least 5 survey questions | name, time, place, subject, message |
| No reload on survey submit | DOM update only, `textContent` (no innerHTML injection) |
| Consistent CSS design | `style.css`, centered card layout, drop shadows, readable typography |
| vitou.html aesthetic | paper `#f6f1e8` / ink `#191c1b` / copper `#a8480e`, Fraunces headings, Karla body |

## DOM contract preserved (from codehs-input-buttons-redesign)

| Must keep | Value |
|---|---|
| Input ids | `nameInput`, `meetuptime`, `meetupplace`, `favsubject`, `messages` |
| Input type | `text` for all five |
| Placeholders | "Enter your name", "Enter time", "Enter place", "Enter subject", "Enter message" |
| Button | `onclick="submitMessage()"` |
| Output element | `id="outputMessage"` |
| Function | `submitMessage()` |

## Safety

`textContent` used instead of `innerHTML` for user-submitted output (no XSS injection).

Related: [[features/codehs-input-buttons-redesign]], [[features/csp9s1u1-cornerstone-part2]]

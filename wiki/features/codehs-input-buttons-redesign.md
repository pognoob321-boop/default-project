---
created: 2026-10-21
tags: [codehs, html, css, design, school-project]
status: active
---

# CodeHS "input buttons" Form Redesign

> Source file (canonical copy): `codehs-input-buttons/index.html`. The live version runs in the CodeHS sandbox `Input-buttons-SZ045X` (codehs.com/sandbox/id/Input-buttons-SZ045X). The user copies the file by hand into the sandbox — the repo copy is the source of truth, the sandbox is the deployment.

## What it is

The original was a bare-bones HTML form: five `<input type="text">` blocks, a `<button onclick="submitMessage()">`, and a `submitMessage()` function that concatenated the five values into one run-on sentence printed into `<p id="outputMessage">`.

The redesign keeps the exact DOM contract and rebuilds the presentation around it.

## Compatibility contract (do not break these)

The CodeHS rubric grades inputs and outputs, so these must survive any restyle:

| Must keep | Value |
|---|---|
| Input ids | `nameInput`, `meetuptime`, `meetupplace`, `favsubject`, `messages` |
| Input type | `text` for all five (not `time`/`date`/`textarea`) |
| Placeholders | "Enter your name", "Enter time", "Enter place", "Enter subject", "Enter message" |
| Button | `onclick="submitMessage()"` |
| Output element | `id="outputMessage"` |
| Function | `submitMessage()` |

Also preserved deliberately: the heading text "Student's Message and Meet Up" and all five question labels, in case the rubric checks for the original wording.

## Design decisions

Aesthetic: **editorial ticket on a dark board**. Matches the ink/paper/amber direction already used in `dream-destinations/styles.css` but pushes it dark, so a form that is mostly empty space stops looking like a form.

- **Typography** — Fraunces (display serif, weight 900) for headings + Karla for body. Google Fonts via `<link>`, with Georgia/Segoe UI fallbacks so the layout still holds if the sandbox blocks the font CDN.
- **Palette 60-30-10** — 60% `#0d1317` board, 30% `#16212a` panel, 10% `#f5a524` amber accent. No pure black, no pure white, no purple-blue gradient.
- **One radius family** (14px panels / 10-12px controls), one shadow style on the button only.
- **Hierarchy** — numbered field markers (`01`…`05`) in the accent serif set the reading order; the amber submit button is the only filled element on the form.
- **Backdrop** — a 46px grid at 3% white. Structure without decoration.

## The two features that carry the "cool" factor

1. **Live meet-up ticket** (`#ticket`) — a right-hand card that renders the five values as you type, with a dashed perforation before the message. On submit it stamps a rotated "Sent" badge.
2. **Output as a confirmation banner** — `#outputMessage` starts `display:none`, then fades in with a 3px amber left rule on submit.

Extra: Enter in any field submits (listener bound on `input` elements), and the original string's typos were fixed ("Your want too meet at" → "You want to meet at").

## Safety change

`innerHTML` → `textContent` for the output. The original injected user input as HTML, so a name of `<img onerror=...>` would execute. Same visible result, no injection.

Related: [[research/web-design-principles]], [[features/csp9s1u1-cornerstone-part2]]

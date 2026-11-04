---
created: 2026-10-01
tags: [school, assessment, html, css, codehs]
status: in-progress
---

# CSP9S1U1 Cornerstone 1 Assessment Part 2 — Dream Destinations Website

> HTML/CSS assignment for CodeHS: "My Top 3 Dream Destinations" with nav (Home / Destinations / About Me), 3 CSS box models side by side, and an About Me section.

## Deliverable Files

- `dream-destinations/index.html`
- `dream-destinations/styles.css`
- `dream-destinations/tokyo.jpg`, `rome.jpg`, `sydney.jpg` (local fallback images for CodeHS upload)

## Assignment Requirements (from Google Doc rubric)

1. **Nav menu** — 3 links: Home, Destinations, About Me + hover effect; links must jump to the right section.
2. **Main heading** — large "My Top 3 Dream Destinations".
3. **Three CSS box models side by side** — each box: photo, destination name, country, short "why I want to visit" description.
4. **CSS styling** — background/text colors, font styling, borders, padding, margin, proper image sizing, layout placing boxes next to each other.

## Rubric "Exceeds 4" mapping

| Criterion | Where it lives |
|---|---|
| HTML structure/content | `<header>` nav, `#home` heading, `#destinations` 3 `.destination-box`, `#about` |
| 3 box models w/ photo+name+country+desc | `.box-row` (flex) > `.destination-box` ×3 |
| Navigation menu | `.nav-menu a` + `:hover` + `#home/#destinations/#about` anchors |
| CSS styling & features | colors, `font-family/size`, `border`, `padding`, `margin`, `object-fit: cover` images, 2 `:hover` rules (nav + box) |

## Image Sources (all HTTP 200 verified)

- Tokyo: `images.unsplash.com/photo-1540959733332-eab4deabeeaf` (verified = Akihabara, Tokyo)
- Sydney: `images.unsplash.com/photo-1506973035872-a4ec16b8e8d9` (verified = Sydney harbour/Opera House)
- Rome: `commons.wikimedia.org/wiki/Special:FilePath/Colosseum,_Roma,_Italy_(Unsplash).jpg` (subject guaranteed by filename)

## Gotcha — model cannot read PDFs

`D:\CSP9S1U1 - Cornerstone 1 Assessment Part 2 .pdf` failed with "this model does not support pdf input". Workaround: user pasted Google Doc screenshots instead. Ask for screenshots/text, not PDFs.

## Remaining Submission Steps (not code)

CodeHS public link with "Show code" visible, screenshots of each section, Exit Ticket, HoM8 + EQ2 answers.

Related: [[features/learning-assessment]]

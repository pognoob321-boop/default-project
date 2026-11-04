---
created: 2026-10-01
tags: [design, web, css, aesthetics, reference]
status: active
---

# Web Design Principles & Aesthetic Catalog

> Source: user-pasted design guide (2026-10-01), condensed. Use as the standing quality bar for any HTML/CSS work in this repo.

## Part 1 — What makes a site look good (impact order)

1. **Typography** — 2 fonts max (display + body). Big size jumps (~3x heading vs body) and extreme weight contrast (200 vs 900, not 400 vs 600). Body ≥16px, line length 60–80 chars. Avoid Inter, Roboto, Poppins, Arial — they read as "nobody chose this".
2. **Color — 60-30-10** — 60% dominant bg, 30% secondary surface, 10% accent. One accent only. Never `#000` on `#fff` — tint both. Readable contrast, no gray-on-gray.
3. **Spacing** — 8px grid (8/16/24/32/48/64). inside-component < between-components < between-sections. Whitespace is a design element.
4. **Visual hierarchy** — one focal point per screen. Squint test: if everything is the same weight, hierarchy is broken.
5. **Consistency** — one radius, one shadow style, one button style. Everything from one family.
6. **Specific content** — real first-person concrete copy beats styling. Generic copy = #1 tell of a fake site. Every line must fail the "swap in a competitor's name" test.
7. **Purposeful motion** — hover must communicate "clickable", not decorate. One transition style, used consistently.

## Part 2 — Aesthetic catalog

| Aesthetic | Vibe | Fonts | Colors | Traits |
|---|---|---|---|---|
| Minimalist / Swiss | clean, nothing extra | Helvetica, Neue Haas | black, white, 1 red accent | huge whitespace, grid, no shadows |
| Editorial / Magazine | printed feature article | Playfair Display, Fraunces + serif body | cream paper, ink black, 1 accent | big serif heads, drop caps, columns, pull quotes |
| Brutalist | raw, anti-design | system/monospace | harsh contrast | thick borders, no radius, exposed structure |
| Retro / Vintage | 70s travel poster | slab serif, typewriter | burnt orange, avocado, brown, cream | textures, stamps, aged paper |
| Scrapbook / Zine | handmade journal | handwriting + serif | paper/tape tones | tilted photos, polaroids, tape |
| Glassmorphism | frosted glass | Inter (only paired well) | blur + white transparency | **overused by AI** |
| Neumorphism | soft extruded | light sans | subtle same-color shadows | pressed/raised |
| Dark / Neon | cyber, gaming | monospace, geometric | near-black + 1 neon | **AI overdoes this** |
| Playful / Cartoon | fun, approachable | Baloo, Fredoka | bright saturated | blobs, big buttons |
| Corporate / SaaS | trustworthy | IBM Plex, Source Sans | navy, blue, grays | **the AI default, hard to make distinctive** |
| Organic / Natural | calm, earthy | soft serif, humanist sans | sage, terracotta, cream | rounded, muted, breathing room |
| Luxury | expensive, sparse | Didot, Cormorant + tracking | black, gold, ivory | huge whitespace, tiny text |

**Pick rule:** match aesthetic to content. Travel journal → scrapbook or editorial. Tech → Swiss or dark. Bakery → organic or playful. The direction must feel inevitable, not random. **The single highest-leverage line in any build prompt is the aesthetic direction** — "make it look good" = average of every website; "make it look like a 1970s travel magazine" = a point of view.

## Standing build rules (from Part 3 prompt)

- State aesthetic choice, font pairing, palette **before** coding.
- No purple-blue gradients, no gradients on buttons/headlines.
- No pure black on pure white.
- Cards separated by whitespace or background shifts, **not** gray borders.
- Don't default to three identical centered cards — vary rhythm (tilts, offsets, sizes).
- No emojis in headings, no glassmorphism, no glow, no floating 3D blobs.
- One consistent border-radius + shadow style.
- Copy: first person, concrete, no buzzwords (seamless/amazing/explore the possibilities).

## Conflicts with CSP9S1U1 rubric (rubric wins)

Rubric **requires** borders around the 3 boxes and 3 boxes next to each other. So:
- Keep borders — use ink-colored 2px borders as a deliberate editorial choice, not gray card chrome.
- Keep 3 side-by-side — vary rhythm via offset/stagger and unequal internal emphasis instead of unequal placement.

Related: [[features/csp9s1u1-cornerstone-part2]]

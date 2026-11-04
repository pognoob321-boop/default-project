---
type: feature
status: active
updated: 2026-09-22
---

# 4 Pillars of Attractiveness

> Updated 2026-09-22 with the structured scoring system from
> looksmax.org "Definitive Facial Analysis Guide" (Jun 2026),
> a fix of BigBallsLarry's "2–10 Looks Scale" (Nov 2025).

## Scoring System (2026)

Four pillars, each scored 0–10, then combined into a TRUE_SCORE /10.

### Base weights
| Pillar | Weight | What it measures |
|--------|--------|------------------|
| **HARM** (Harmony) | **32%** | ratios/angles between features |
| **MISC** (Miscellaneous) | **26%** | skin, coloring, eyes, lips, nose quality, symmetry |
| **ANGU** (Angularity) | **22%** | sharpness: mandible visibility, 3D-ness, gonion, ogee curve, hollow cheeks |
| **DIMO** (Dimorphism) | **20%** | masculine signal: eye depth, brow ridge, chin, ramus, beard |

### Scaling constants (raw → 0–10)
```
HARM: MAX=389.74,  WORST=-409.92
MISC: MAX=1031,    WORST=-460
ANGU: MAX=149.83,  WORST=19.03
DIMO: MAX=120,     WORST=-67.44

pillar% = ((raw - WORST) / (MAX - WORST)) * 100
pillar/10 = pillar% / 10
```

### Dynamic penalty (replaces old spread×0.5 penalty)
2026 fix: old formula could make a *higher* HARM score produce a *lower*
final score when spread grew. New method: penalty **factor** per pillar score S,
then renormalize weights.

| Score S | Factor |
|---------|--------|
| ≥8.0 | 1.00 |
| ≥7.5 | 1.05 |
| ≥7.0 | 1.10 |
| ≥6.5 | 1.25 |
| ≥6.0 | 1.45 |
| ≥5.5 | 1.70 |
| ≥5.0 | 2.00 |
| ≥4.5 | 2.35 |
| ≥4.0 | 2.75 |
| ≥3.5 | 2.20 |
| ≥3.0 | 2.70 |
| ≥2.5 | 3.25 |
| <2.5 | 3.85 |

```
pen_i = (pillar/10)_i * base_weight_i * factor_i
weight_i' = pen_i / sum(pen)
TRUE = sum( (pillar/10)_i * weight_i' )
```
- If lowest pillar ≥8.0 → no adjustment (weights stay 32/26/22/20)
- Lower floor 2.5 → no additional penalty below
- Worse pillars get relatively more weight → progressive penalty for flaws

### Looks scale reference (0–10 male)
| Score | Meaning |
|-------|---------|
| 9+ | best in millions / near perfect |
| 9 | best in a million |
| 8.5 | best in hundreds of thousands |
| 8 | best in a couple thousand |
| 7.5 | best in hundreds |
| 7 | best in a hundred |
| 6.5 | best in 10s |
| 6 | best in 5 |
| 5.5 | best in 3 |
| 5 | average |
| 4.5 | ordinarily below average |
| 4 | solidly ugly |
| 3.5 | very ugly |
| 3 | extremely ugly |
| <2 | unquantifiably ugly |

Narrative bands: 0–2 unbelievably unattractive · 2–3 extremely · 3–4 very ·
4–5 below average · 5–6 slightly above · 6–7 noticeably · 7–8 very ·
8–9 extremely · 9–10 near perfect.

Worked example (Lorenzo Zurzolo, thread): HARM 8.70 · MISC 6.92 · ANGU 3.97 · DIMO 7.92

---

## 1st Pillar: Harmony (HARM) — 32%

Core facial harmony ratios and measurements. Full table: [Facial Ratios](facial-ratios.md).

Highest-weight HARM sub-metrics (2026 Definitive Guide tier points):
- Jaw Width 20.59 → ideal 87.5–91.5% bigonial/cheekbone
- Eye-to-Eyebrow distance / brow setness 19.83 → brows close to eyes, no droop
- Brow Ridge Inclination 19.83 → smooth but defined
- Facial Thirds 19.83 → U 30–32% · M 31.4–33.4% · L 33.9–37.0%
- Nasofrontal Angle 19.06 → 116–128°
- Neck Width 19.06 → 92–98% of bigonial
- Lower Third Proportion 18.30 → ~34–37% of total face height
- FWHR 18.30 → 1.95–2.05
- Eye Aspect Ratio 18.30 → 3–3.7×
- Gonial Angle 16.78 → ~115–121°
- Ramus Length 14.41 → long ramus, strong vertical jaw height
- Thirds of Jaw 17.54 → symmetric vertical jaw thirds
- Chin-to-Philtrum 12.96 → 2.1–2.5
- Lateral Canthal Tilt 12.35 → 6–8° positive
- Mouth-to-Nose 12.35 → 1.4–1.6×
- ESR 12.20 → 45–47% of bizygomatic
- Midface Ratio 11.90 → 0.98–1.02
- Jaw Frontal Angle 9.15 → 86.5–92.5°
- Cheekbone Setness 20 → high, projecting zygos with ogee curve
- Face Length 20 → 1.33–1.37×
- Bizygomatic Width 20 → wide and proportional
- Nose-to-Bizygomatic 7 → nose ~20% of cheekbone width
- Eyebrow Tilt 10 → 6.5–11°
- Medial Canthal Angle 7.5 → symmetric subtle inward angle
- Bitemporal Width 7.5 → 85–92% of bizygomatic
- Lower Third (nostril–commisure) 2.5 → 31–33.5% of lower third height

## 2nd Pillar: Miscellaneous (MISC) — 26%

Skin, eye area, coloring, lower-third soft tissue, lips, nose quality, ears, symmetry.

### Category ideal caps (Tier 1 sum → MAX 1031; WORST −460)
- Skin: 160
- Eyes: 231
- Colouring: 135
- Overall lower third: 170
- Lips: 110
- Nose: 110
- Other misc: 115

### Representative ideals
- **Skin**: no acne, blemishes, hyperpigmentation, moles, texture issues, scarring, folds/wrinkles
- **Eyes**: no UEE, straight/curved lids, no sclera show, thick dark lashes/brows, no periorbital darkening/circles/LEE, light eye colour, even scleral triangles, PFL 27mm+, white sclera, no unibrow
- **Colouring**: tanned (Fitzpatrick II–low IV), reddish-pink lips, contrasting lashes, light eyes, dark hair/eyebrows, white sclera
- **Lower third**: flared gonions, square wide chin, tall ramus, long straight mandible, minimal antegonial notch
- **Lips**: wide, short philtrum, defined ridges, full, healthy, slight upturn, prominent cupid's bow, straight seal
- **Nose**: narrow alar, low bulbosity, defined non-droopy tip, minimal nostril show/flare, straight dorsum, projected radix
- **Other**: pinned-back ears, minimal asymmetry (symmetry alone worth up to 100 pts)

## 3rd Pillar: Angularity (ANGU) — 22%

Sharp, defined bone structure — high cheekbones, hollow cheeks, strong jawline, clear facial planes.

| Feature | Tier-1 points | Ideal |
|---------|---------------|-------|
| Mandible Visibility (Front) | 24.75 | Broad flare, clear contour, no lower-face fat |
| Facial 3D-ness | 18.75 | Strong midface projection, sharp anterior depth |
| Gonion Sharpness | 18.75 | Well-defined gonial edge |
| Facial Depth | 17.25 | Strong maxilla + mandible forward projection |
| Mandible & Ramus Visibility | 16.74 | Long tall ramus, sharp rear-jaw contour |
| Ogee Curve | 15.75 | Defined midface S-curve, high cheekbone projection |
| Cheekbone Visibility | 15.11 | High wide-set malars, lateral projection, hollow cheeks |
| Chin Angularity | 12.30 | Squared chin pad, sharp pogonion |
| Lower-Midface Fat | 10.43 | Minimal buccal fat, lean jaw contour |

MAX 149.83 / WORST 19.03. Same scaling formula as other pillars.

## 4th Pillar: Dimorphism (DIMO) — 20%

Masculine signal: 0 = closest to female-ish features, 100 = "manly ogre".
Usually eyeballed against a DIMO chart; formula below for consistency.

| Feature | Tier-1 points | Ideal |
|---------|---------------|-------|
| Eye Depth | 22.32 | Very deep-set, supraorbital projection, orbital shadowing |
| Brow Ridge Shape | 13.44 | Pronounced brow bossing, sharp supraorbital margin |
| Chin Shape | 12.72 | Broad square chin, forward pogonion, minimal taper |
| Buccal Fat Size | 11.70 | Very low, hollowing under cheekbones |
| Ramus Length (Front) | 11.53 | Tall visible ramus, long lower face |
| Gonion Outward Growth | 11.04 | Wide gonial flare, V-to-square lower face |
| Narrowing Upper Third | 9.00 | Narrower upper third relative to mid/lower |
| Facial Hair Development | 7.80 | Dense coarse beard/stubble |
| Rough Skin Texture | 7.20 | Thicker textured dermis, visible pores |
| Cheekbone Size | 6.91 | High projecting malars, clear shadow lines |
| Lip Fullness | 6.34 | Relatively thin-to-average lips |

MAX 120 / WORST −67.44.

---

## Related
- [Facial Ratios](facial-ratios.md)
- [Facial Structure & Archetypes](facial-structure-archetypes.md)
- [Coloring & Style](coloring-style.md)
- [Facial Analysis Guides](../research/facial-analysis-guides.md)

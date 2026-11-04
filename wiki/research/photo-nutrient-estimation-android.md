# Free Photo → Nutrient Estimation (Android + Gemini + OpenCode)

Date: 2026-09-24
Question: Free Android (or mobile-browser) app that estimates nutrients from a food/drink photo (min: protein, sodium, potassium), safe, 100% free, works with Gemini AND OpenCode, table output with confidence.

## Bottom line

**No single product meets ALL 6 requirements.** Closest options + full workaround below.

## Ranked top 3 (closest)

### 1. Gemini API + `meal-analyzer-mcp` (OpenCode) [+ optional USDA FDC] — BEST overall path
- Link: https://github.com/ashurkina/meal-analyzer-mcp
- Free? Yes (own free Gemini API key from AI Studio; no card).
- Gemini/OpenCode: Built-in — MCP stdio server, default `gemini-2.5-flash`, photo base64 in → structured JSON out. Register in `opencode.json` under `mcp` (v1) / `mcp.servers` (v2).
- Safety: Open source Python, Docker, no phone install, key stays local.
- Sodium/potassium/protein from photo? Protein yes; **Na/K NOT in default schema** (calories + macros + confidence + warnings only). Extend prompt/schema or chain USDA FoodData Central (`api.nal.usda.gov`, free key, CC0) for verified Na/K.
- Android: run Docker web UI on a PC/LAN and open from Chrome on phone, or push photo to PC; not a native app.
- Verdict: **Best pick for OpenCode + Gemini**; Na/K needs one small extension.

### 2. OpenMeal (Android APK, Gemini key)
- Links: https://maximilianromer.github.io/OpenMeal · https://github.com/maximilianromer/OpenMeal
- Free? Yes 100% — bring your own free Gemini API key.
- Gemini/OpenCode: Uses Gemini multimodal for photo analysis; prompts public. No MCP; not callable from OpenCode as-is (could script same Gemini calls).
- Safety: Open source, single indie author (Stanford undergrad), **sideload APK not on Play Store** — install only from official GitHub/site link; permissions unknown (verify at install).
- Sodium/potassium/protein from photo? Prompt schema = kcal, carbs, protein, fat only. Sodium only appears as qualitative “excessive sodium” insight text — **no mg values, no potassium**.
- Verdict: **Best free Android+Gemini app; skip if Na/K numbers are hard requirements.**

### 3. SnapCalorie (Play Store)
- Link: https://play.google.com/store/apps/details?id=com.snapcalorie.alpha002
- Free? Partially — **free up to 3 AI photo logs/day**, no card; Premium ~$9.99/mo unlocks unlimited. Core usable free.
- Gemini/OpenCode: **No** — proprietary CV (ex-Google Lens team, CVPR research), not Gemini, no free public MCP/OpenCode hook.
- Safety: Strong — 4.7★ / 21k+ reviews, PerceptionLabs Inc, privacy policy, mainstream publisher.
- Sodium/potassium/protein from photo? **Yes** — claims 100+ nutrients incl. sodium, protein, potassium from photo + depth portioning; USDA-backed DB.
- Verdict: **Best native Android photo app for Na/K; fails Gemini/OpenCode req.**

## Honorable mentions (each fails ≥1 hard req)
- **Google Gemini app/site** (gem.gle / Play Store): free, photo→full nutrient table if prompted (incl. Na/K + confidence caveat), Google-published; OpenCode via Gemini API script, not a dedicated tracker.
- **FoodLens** (https://github.com/cakhiltej9001-source/foodlens-multimodal-ai): Gemini + USDA, reports sodium; Streamlit (browser), needs 2 free keys; educational only.
- **Open Food Facts** (F-Droid/Play): open source, free, Na/K on packaged goods via barcode/photo DB — not open-meal photo AI; has MCP servers (e.g. cyanheads/openfoodfacts-mcp-server).
- **Cronometer / Food You (F-Droid)**: full micros Na/K but manual/barcode, no photo AI + Gemini.
- Skipped sketchy: NutriPic (poor reviews), NutriSnap (1 scan/day free + ads), various zero-star GitHub demos.

## OpenMeal-like alternatives (BYOK photo → nutrition, free/OSS)

| App | Platform | Gemini? | Free | Na/K from photo? | Safety | Verdict |
|-----|----------|---------|------|------------------|--------|---------|
| **Chompass** | F-Droid + PWA browser | BYOK (Google AI Studio/OpenRouter) or on-device Gemma 4 | Yes, MIT | Photo→macros; barcode/OFF+USDA+Swiss DBs for full nutrients incl. Na/K | F-Droid signed, no ads/analytics/accounts, local-first, encrypted keys | **Best OpenMeal alternative overall** |
| **LazyCalAI** | Android/iOS (build from source) | Multi-provider BYOK (Gemini, OpenAI, Claude…) | Yes, MIT | kcal/protein/carbs/fat/fiber only — no Na/K | GitHub MIT, 0 stars (new), OTA CodePush caveat | Best multi-AI clone; no micronutrients |
| **MealSnap** | Web + Android (Flutter) | Gemini 2.5 + USDA FDC | Yes, MIT (self-host) | Confidence High/Med/Low; USDA lookup can return Na/K if queried | 0-star demo, Render free tier ~30s wake, has live demo | Best Gemini+USDA pattern; demo quality |
| **NutriSnap** (zanni098) | Mobile-first web (Vercel) | Gemini 2.5 Flash | Yes (own key; samples without key) | macros + confidence + health score; no Na/K fields | 0-star contest clone, browser-only | Quick try on phone Chrome |
| **FoodLens** (tejasnasre) | Expo/Android | Gemini | Yes | claims “micronutrients” in README | 1-star new repo, 404 at check time — verify | Unverified; treat as experimental |
| **Macro-Tracker** (dennisbrsv) | Web (React+Express) | Gemini | Yes | macros only | 0-star, no auth, demo | Self-host web only |
| **ai_calorie_tracker** (amirdora) | Flutter Android | Gemini 1.5 | Yes, MIT | kcal/protein/carbs/fat | 17★ old-ish, needs build | Solid small clone |
| **IntelliCal** | Android (Kotlin) | Gemini + Supabase | Build yourself | macros | 0-star, needs Supabase project | Too much setup |
| Skip: Cal AI (commercial, paid scans), NutriMind ($9 one-time / different Play app uses Gemma), random Streamlit demos |

**Pick order for “like OpenMeal”:** 1) Chompass (F-Droid + browser + micronutrient DBs) → 2) LazyCalAI (closest feature clone) → 3) MealSnap (Gemini+USDA+confidence pattern).

## Workaround that meets ALL requirements
1. Photo on Android → Gemini API vision call (script or MCP) identifies food + portion estimate.
2. Resolve item name → USDA FoodData Central search API (free key, CC0) for protein/sodium/potassium/kcal/sugar/carbs/fat per 100g × estimated grams.
3. Emit markdown table + confidence (Gemini self-rating + “hidden oil/sauce” warnings).
4. Wire as OpenCode MCP or plain CLI script OpenCode can run.

USDA docs: https://fdc.nal.usda.gov/api-guide · DEMO_KEY = 30/hr, 50/day; free signup for 3600/hr.

## Evidence (sample coconut water, USDA)
- Vita Coco 8 fl oz: 46 kcal, Na 36 mg, K 470 mg, protein 0 g (USDA branded).

## Play Store installs only (user could not sideload OpenMeal/Chompass APKs)

User failed to download both direct APKs (OpenMeal, Chompass). One-tap Play alternatives verified 2026-09-24:

| App | Play ID | Free? | Gemini/OpenCode | Na/K from photo? | Safety | Verdict |
|-----|---------|-------|-----------------|------------------|--------|---------|
| **Fud AI** | `com.apoorvdarshan.calorietracker` | 100% free, no ads/sub/IAP | BYOK Gemini (+13 other providers) | Photo AI can estimate Na/K/vitamins; barcode→OFF for verified | MIT OSS, 387★ GitHub, privacy-first, no account needed | **Best OpenMeal-style on Play** |
| **SnapCalorie** | `com.snapcalorie.alpha002` | Free 3 AI photo scans/day (Premium ~$9.99/mo) | No (proprietary CV) | Yes — 100+ nutrients incl. Na/K/protein (USDA-backed) | 4.6★/18K+, PerceptionLabs | **Easiest photo → Na/K numbers** |
| **OpenNutriTracker** | `com.opennutritracker.ont.opennutritracker` | Free, no ads/IAP/subscription | Optional BYOK photo AI (own API key) | Full nutrient tables (USDA/OFF); photo AI optional | GPL-3.0 OSS, privacy-focused | Best for verified Na/K lookup |

- Chompass: **NOT on Play** (404) — F-Droid client or PWA `https://chompass.app/app/` only.
- No-install fallback: Gemini app photo → "list sodium, potassium, protein in mg".

**Play pick order:** 1) SnapCalorie (instant photo result) → 2) Fud AI (Gemini + free forever) → 3) OpenNutriTracker (accurate Na/K DB).

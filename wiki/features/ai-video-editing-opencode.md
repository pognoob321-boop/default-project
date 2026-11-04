---
type: feature
status: shipped
updated: 2026-10-23
---

# AI Video Editing in OpenCode (Free)

## Problem

Telegram Saved Messages (2026-10-23) had 8 TikTok links captioned "Claude motion graphic". They show creators making/editing videos with coding agents (Claude Code, Remotion, HyperFrames). Question: can the same AI editing be done in OpenCode for $0?

## TikTok Links (resolved 2026-10-23)

| Short link | Creator | Full URL |
|---|---|---|
| ZSgmY3xBy | @rikibosso | tiktok.com/@rikibosso/video/7697990163909152032 |
| ZSgmYawhs | @storyboard.co.th | tiktok.com/@storyboard.co.th/video/7697937481471347975 |
| ZSgmYnXT4 | @storyboard.co.th | tiktok.com/@storyboard.co.th/video/7697144807822462260 |
| ZSgmYuyVB | @benkimball.ai | tiktok.com/@benkimball.ai/video/7698964404443909406 |
| ZSgmYpp31 | @marketerhub.ai | tiktok.com/@marketerhub.ai/video/7695763140797140238 |
| ZSgmYHVYB | @taki.gpt | tiktok.com/@taki.gpt/video/7698412619572481281 |
| ZSgmYxYBV | @nateherkai | tiktok.com/@nateherkai/video/7687261912828103949 |
| ZSgmYqKhH | @marcus_cryptosafe | tiktok.com/@marcus_cryptosafe/video/7688342198642953504 |

Topic cluster: Claude Motion / Remotion / HyperFrames — coding agents writing HTML/React that renders to MP4. @taki.gpt's viral clip: "Claude can now create and edit full videos with animations and sound." @benkimball.ai: Remotion + Codex/Claude for automated video editing.

## The Landscape (2026-10)

1. **Claude Motion** (Anthropic, beta 2026-10-08) — Team/Enterprise only ($25+/seat). NOT free. NOT on Pro/Max.
2. **HyperFrames** (HeyGen, Apache-2.0, 70k stars) — HTML → MP4. Free forever. Explicitly supports OpenCode. Local render = no HeyGen credits.
3. **Remotion** — React → MP4. Free for individuals / companies under $100k revenue. Agent skills published by remotion-dev.
4. **iart-ai TikTok skills** — 4 MIT skills for vertical short-form (hook/retention/loop grammar).

## What Was Implemented

Installed into `C:\Users\ZBook\.config\opencode\skills\`:

### HyperFrames core (primary — free, OpenCode-native)
- `hyperframes` — main contract + work loop
- `hyperframes-cli` — scaffold/check/preview/render
- `hyperframes-registry` — ~450 ready-made blocks
- `media-use` — free local TTS/SFX/transcripts

### Remotion agent skills (secondary)
- `remotion-create`, `remotion-render`, `remotion-captions`
- `remotion-best-practices`, `remotion-multimedia`, `remotion-markup`

### TikTok short-form (iart-ai, MIT)
- `short-form-video` — 9:16 hook→retention→loop
- `caption-animation`, `lower-thirds`, `countdown-video`

### CLI
- `hyperframes` npm package installed globally → v0.8.188
- FFmpeg 8.1.2 already present (from free-video-clipping research)
- Node v24.18.1

## How To Use

Restart OpenCode, then prompt:

```
Using /hyperframes, make a 10-second 9:16 product intro with a fade-in title and background music.
```

Or for TikTok-style talking-head edit:

```
Use /short-form-video and /hyperframes: edit my clip at D:\path\to\video.mp4 into a 30s vertical with captions and lower thirds.
```

First video project:

```powershell
hyperframes init my-video
hyperframes preview   # browser live reload
hyperframes render    # MP4
```

## Cost: $0

| Piece | Cost |
|---|---|
| HyperFrames | $0 (Apache-2.0) |
| Remotion (this use) | $0 (free tier) |
| TikTok skills | $0 (MIT) |
| FFmpeg / Node | $0 (already installed) |
| TTS (edge-tts / Kokoro) | $0 (local) |
| Claude Motion official | $25+/mo — skipped |

## Status

Shipped 2026-10-23. Skills on disk, CLI verified (`hyperframes --version` → 0.8.188). Not yet smoke-tested with a full render on this machine — first `hyperframes init` will download Puppeteer/Chrome on demand.

## Notes

- `npx hyperframes skills update` hangs on this machine (3 min timeout, no output). Manual sparse-clone into skills folder works instead.
- OpenCode auto-discovers skills from `~/.config/opencode/skills/<name>/SKILL.md`.
- Related: [TikTok Token Maxxing](tiktok-tokenmaxxing-free-tools.md), [Free Video Clipping](../research/free-video-clipping.md), [Meme Replication](../research/meme-replication.md), [Agentic AI](../research/agentic-ai.md)

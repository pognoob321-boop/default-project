# Free Automatic Video Clipping Tools

> Research: how an AI can automatically turn long videos into short clips, 100% free, no subscriptions, no watermarks, no trials.
> Generated: 2026-08-06 | Confidence: High

## Executive Summary

You can fully automate "long video → viral short clips" **for free on your own PC** using a stack of open-source tools: `yt-dlp` (download) + `faster-whisper` (transcribe) + an LLM scoring step + `ffmpeg` (cut/crop/captions). Your machine already has the hard parts installed: **Python 3.11.15**, **ffmpeg 8.1.2 full build with libass** (caption burning works), and **winget**. Only `deno` is missing (needed by the yt-dlp JS-challenge solver in some tools).

Two paths:

1. **Ready-made local tool (recommended): Chopify** — drop a YouTube URL, get scored 9:16 clips with burnt word-by-word captions + PNG posters. MIT license, zero paid APIs.
2. **Do it yourself with ffmpeg** — full control, no extra code needed. The AI (me) can drive ffmpeg directly from this machine.

## How the Pipeline Works (all tools)

| Step | Tool | Cost |
|------|------|------|
| Download video | `yt-dlp` | Free, open source |
| Transcribe audio → word timestamps | `faster-whisper` | Free, runs locally |
| Pick the best moments | LLM scoring (or manual) | Free if local |
| Cut + vertical crop + burn captions | `ffmpeg` | Free, installed |
| Face tracking reframe | OpenCV (MediaPipe/YuNet) | Free |

## Recommended: Chopify

- Repo: https://github.com/mehbul/chopify (MIT)
- Turns long videos into scored clips in 16:9 / 9:16 / 1:1 with AI virality scoring and CapCut-style word captions
- 100% local: no account, no watermark, no API keys
- Requirements: Windows, Python 3.11+, ffmpeg+ffprobe on PATH, `deno` on PATH
- Install: `winget install Gyan.FFmpeg` (done), `winget install DenoLand.Deno` (needed)
- Output goes to `C:\clips` (change `OUT_DIR` in `render_clips.py`)
- Note: faster-whisper CUDA is NVIDIA-only; on AMD/non-NVIDIA it runs on CPU (slower but works)

### Chopify workflow
1. `python download_and_transcribe.py "<YOUTUBE_URL>"` → writes `work/transcript.json`
2. Score segments → `work/segments.json` (LLM does this in-loop at zero cost; or score manually)
3. `python render_clips.py work` → cut + reframe + captions + poster → `C:\clips`

## Alternative: DIY with ffmpeg (I can do this directly)

Since ffmpeg is installed with libass, I can already:
- Cut clips: `ffmpeg -ss 134.2 -i in.mp4 -t 53.4 -c copy clip.mp4`
- Vertical 9:16: crop with face tracking or center-crop
- Burn captions: `ffmpeg -i in.mp4 -vf "subtitles=captions.srt" out.mp4`
- Add effects: `-vf eq=contrast=1.15:brightness=0.02`, fades, zoompan, etc.

## Other verified free local tools

| Tool | Link | License | Notes |
|------|------|---------|-------|
| OpenFang Auto Clip | github.com/outhsics/openfang-auto-clip | MIT | Fully customizable local pipeline, web UI |
| vid-clipper | github.com/anl331/vid-clipper | — | Paste URL → 9:16 clips, free Gemini model by default |
| OpenSource Clipping | github.com/naufalrizqullah/opensource-clipping | MIT | Karaoke subtitles, B-roll, BGM ducking, auto-thumbnails |
| AI-Youtube-Shorts-Generator | github.com/SamurAIGPT/AI-Youtube-Shorts-Generator | MIT | 4.1k stars, `--mode local` is free |
| VibeClip | github.com/oktaydbk54/vibeclip | AGPL-3.0 | Edit by chatting, needs one LLM key |
| clipperr | github.com/rasyiqi-code/clipperr | MIT | Windows exe, needs HuggingFace token for face tracking |
| echocut | github.com/skyconnfig/echocut | — | Node + Python CLI, brand overlays + publish kit |

## Free web tools (no watermark, no card) — but NOT for AI automation

| Tool | Free tier | Note |
|------|-----------|------|
| VidClean | 3 videos/day, 6 clips each, up to 90 min, no account, no watermark | No URL import |
| Klap | 1 video free, no watermark | After that paid |
| WayinVideo | 200 free credits on signup, no watermark | Credits based on length |
| Eklipse AI Clip Finder | Free, no login, in-browser | Uploaded MP4 only, local scan |

## Key facts / caveats
- Any tool whose caption burning fails with "No such filter: subtitles" needs libass in ffmpeg — your build has it (`--enable-libass` confirmed).
- Subtitle paths with colons on Windows need escaping: `subtitles=C\:\\Users\\...\\captions.srt`
- faster-whisper on Windows: CUDA libraries required for GPU; CPU works without.
- Only clip videos you own or have rights to process.

## Sources
1. Chopify README (github.com/mehbul/chopify) — free local alternative to Opus Clip/Vizard
2. auto-editor docs (github.com/WyattBlue/auto-editor) — silence detection automation
3. gyan.dev ffmpeg builds — full build includes libass
4. ffmpeg subtitles filter guide (ffmpeg-micro.com) — caption burning syntax
5. VidClean free tier page — no-account free clipping
6. MoviePy subtitle tutorials — programmatic caption overlays
7. AI-Youtube-Shorts-Generator README — local mode free pipeline
8. VibeClip / OpenSource Clipping / vid-clipper / OpenFang repos

## Methodology
Searched ~16 web queries across web/news. Deep-read 4 key sources (Chopify README, ffmpeg build config, gyan builds, MoviePy tutorials). Verified local environment: Python 3.11.15, ffmpeg 8.1.2-full-build with libass, winget present, deno missing.

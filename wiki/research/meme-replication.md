# "X is the Clip" Meme Replication

> Replicated the viral meme format from https://www.youtube.com/shorts/KByFAWUwpsc ("Stable Ronaldo is The Clip" by Haynx).
> Generated: 2026-08-06 | Confidence: High

## The Format (analyzed)

The original is an 18-second short:
- Deep dramatic AI voiceover narration over a streamer clip
- Word-by-word karaoke captions (CapCut style, yellow highlight on active word)
- Builds to a punchline: "Unless... you're Stable Ronaldo"
- 9:16 vertical, speaker-tracked

## How I Replicated It (100% free, local)

Pipeline:
1. **Source clip**: downloaded the original short with yt-dlp (already in `D:\chopify\work\source.mp4`)
2. **Script**: wrote a new dramatic script in the same style (script.txt)
3. **Voiceover**: `edge-tts` (free, no API key) with `en-US-ChristopherNeural` voice, -5% rate → `voiceover.mp3`
4. **Word timestamps**: transcribed the voiceover with faster-whisper (small model) → `vo_words.json` (52 words)
5. **Captions**: reused chopify's `build_ass()` → karaoke ASS with yellow active-word highlight
6. **Render**: ffmpeg — 9:16 crop, original audio ducked to 15% (volume=0.15), voiceover mixed on top (amix), word captions burnt in

Output: `D:\clips\stable-ronaldo-meme-replication.mp4` (1080x1920, ~18s, matches voiceover duration)

## Files

- `D:\chopify\replicate\script.txt` — the narration script
- `D:\chopify\replicate\voiceover.mp3` — edge-tts output
- `D:\chopify\replicate\vo_words.json` — word-level timestamps
- `D:\chopify\replicate\transcribe_audio.py` — helper to get word timestamps
- `D:\chopify\replicate\render_meme.py` — the render pipeline

## Key Learnings

1. **edge-tts is the free TTS solution** — no API key, works offline after install, has good dramatic male voices (ChristopherNeural, GuyNeural, etc.)
2. **Word captions**: faster-whisper word_timestamps=True gives the sync data; ASS karaoke style = yellow highlight on active word
3. **ffmpeg subtitles filter path escaping**: on Windows, drive-letter colons break `subtitles=`. Fix: use a relative path (`subtitles=_meme.ass`) and run ffmpeg with cwd=OUT_DIR (which chopify's render already does)
4. **Audio ducking**: `[0:a]volume=0.15[orig];[orig][1:a]amix=inputs=2` — original at 15%, voiceover at 100%
5. **Video length**: match `-t` to the voiceover duration so narration fully plays

## Related Formats (from research)

- "Kumar Method": deadpan talking head + cinematic AI shots + ironic punchline
- Reddit narration / brainrot: AI voice over gameplay (Subway Surfers), 165-180 wpm + dramatic pauses
- Meme compilation: rapid 1-3s cuts, loud music
- Sigma/motivational: dark cinematic, deep voice, phonk

## Sources
- Original video: youtube.com/shorts/KByFAWUwpsc (transcript: "You cannot always be the clip... unless you're stable, Ronaldo")
- Know Your Meme — Stable Ronaldo entry and "Stay In The Box" meme origin
- Kapwing Kumar Method guide — cinematic trend structure
- VidMuse brainrot guide — 5 core short-form styles
- GhostShorts — AI voiceover industry stats and formats

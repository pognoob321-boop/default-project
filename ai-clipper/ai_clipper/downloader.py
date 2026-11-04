"""Download YouTube videos and extract audio using yt-dlp."""

import subprocess
import sys
import shutil
import json
from pathlib import Path

YTDLP = [sys.executable, "-m", "yt_dlp", "--js-runtimes", "node"]
FFPROBE = shutil.which("ffprobe") or "ffprobe"


def download_video(url: str, output_dir: Path) -> dict:
    """Download video and extract audio.

    Returns dict with keys: video_path, audio_path, title, duration.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get video info first
    info_cmd = YTDLP + [
        "--dump-json",
        "--no-download",
        url,
    ]
    result = subprocess.run(info_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp info failed: {result.stderr}")
    info = json.loads(result.stdout)

    title = info.get("title", "video")
    duration = info.get("duration", 0)
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title).strip()
    safe_title = safe_title[:80] or "video"

    video_path = output_dir / f"{safe_title}.mp4"
    audio_path = output_dir / f"{safe_title}.wav"

    # Download video
    video_cmd = YTDLP + [
        "-f", "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best",
        "--merge-output-format", "mp4",
        "-o", str(video_path),
        url,
    ]
    result = subprocess.run(video_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp download failed: {result.stderr}")

    # Extract audio for whisper
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"
    audio_cmd = [
        ffmpeg, "-y",
        "-i", str(video_path),
        "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        str(audio_path),
    ]
    result = subprocess.run(audio_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg audio extraction failed: {result.stderr}")

    return {
        "video_path": video_path,
        "audio_path": audio_path,
        "title": title,
        "duration": duration,
    }

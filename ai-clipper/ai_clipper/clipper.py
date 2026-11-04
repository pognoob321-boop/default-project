"""Clip video segments using ffmpeg."""

import subprocess
import shutil
from pathlib import Path


def clip_segment(
    video_path: Path,
    start: float,
    end: float,
    output_path: Path,
    vertical: bool = True,
) -> Path:
    """Cut a segment from video and re-encode.

    If vertical=True, crops to 9:16 center crop.
    Returns output path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    duration = end - start
    ffmpeg = shutil.which("ffmpeg") or "ffmpeg"

    cmd = [
        ffmpeg, "-y",
        "-ss", str(start),
        "-i", str(video_path),
        "-t", str(duration),
    ]

    if vertical:
        # Center crop to 9:16 (1080x1920)
        cmd += [
            "-vf", (
                "crop=ih*9/16:ih,"
                "scale=1080:1920,"
                "setsar=1"
            ),
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
        ]
    else:
        cmd += [
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            "-c:a", "aac",
            "-b:a", "128k",
        ]

    cmd.append(str(output_path))

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg clip failed: {result.stderr}")

    return output_path

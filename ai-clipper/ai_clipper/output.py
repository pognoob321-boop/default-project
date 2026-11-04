"""Save clips and metadata to output directory."""

import json
from pathlib import Path

from .clipper import clip_segment


def save_clips(
    video_path: Path,
    highlights: list[dict],
    title: str,
    output_dir: Path,
    vertical: bool = True,
) -> list[dict]:
    """Clip all highlights and save with metadata.

    Returns list of saved clip info dicts.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in title).strip()
    safe_title = safe_title[:60] or "video"

    saved = []
    for i, h in enumerate(highlights, 1):
        clip_name = f"{safe_title}_clip{i}"
        clip_path = output_dir / f"{clip_name}.mp4"

        clip_segment(
            video_path=video_path,
            start=h["start"],
            end=h["end"],
            output_path=clip_path,
            vertical=vertical,
        )

        metadata = {
            "clip": clip_name,
            "source_title": title,
            "start": h["start"],
            "end": h["end"],
            "duration": round(h["end"] - h["start"], 2),
            "score": h.get("score", 0),
            "reason": h.get("reason", ""),
        }

        meta_path = output_dir / f"{clip_name}.json"
        meta_path.write_text(json.dumps(metadata, indent=2))

        saved.append({**metadata, "path": str(clip_path)})

    return saved

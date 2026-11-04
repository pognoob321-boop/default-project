"""Transcribe audio using faster-whisper."""

from pathlib import Path
from faster_whisper import WhisperModel


def transcribe(audio_path: Path, model_size: str = "base") -> dict:
    """Transcribe audio file.

    Returns dict with keys: text, segments (list of {start, end, text}).
    """
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments_iter, info = model.transcribe(
        str(audio_path),
        beam_size=5,
        word_timestamps=True,
    )

    segments = []
    full_text_parts = []
    for segment in segments_iter:
        segments.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip(),
        })
        full_text_parts.append(segment.text.strip())

    return {
        "text": " ".join(full_text_parts),
        "segments": segments,
        "language": info.language,
        "duration": info.duration,
    }

"""Analyze transcript and detect highlight moments using local heuristics."""

import re
import math


# Words that signal engaging content
HIGHLIGHT_WORDS = {
    "actually", "surprisingly", "amazing", "incredible", "unbelievable",
    "secret", "truth", "mistake", "wrong", "never", "always", "best",
    "worst", "love", "hate", "beautiful", "destroy", "insane", "crazy",
    "shocking", "hidden", "exclusive", "revealed", "finally", "listen",
    "important", "remember", "forget", "imagine", "think about",
    "game changer", "life changing", "blow your mind", "mind blown",
    "here's the thing", "the problem is", "the truth is",
}

TRANSITION_WORDS = {
    "but", "however", "actually", "wait", "no", "yes", "okay",
    "so", "now", "here", "look", "listen", "imagine", "think",
}


def _segment_score(segment: dict, total_duration: float, idx: int, total: int) -> float:
    """Score a single transcript segment."""
    text = segment["text"].lower()
    words = text.split()
    score = 0.0

    # Word density (more content = more interesting)
    duration = segment["end"] - segment["start"]
    if duration > 0:
        words_per_sec = len(words) / duration
        score += min(words_per_sec * 2, 3)

    # Highlight words
    highlight_count = sum(1 for w in words if w.strip(".,!?") in HIGHLIGHT_WORDS)
    score += highlight_count * 1.5

    # Exclamation / emphasis
    score += text.count("!") * 0.5

    # Questions (engaging)
    score += text.count("?") * 0.8

    # ALL CAPS words (emphasis in transcript)
    caps_words = sum(1 for w in segment["text"].split() if w.isupper() and len(w) > 1)
    score += caps_words * 0.5

    # Transition words (signal a shift = interesting)
    transition_count = sum(1 for w in words if w.strip(".,!?") in TRANSITION_WORDS)
    score += transition_count * 0.3

    # Position bonus: middle of video scores higher
    position = segment["start"] / total_duration if total_duration > 0 else 0.5
    position_score = 1.0 - abs(position - 0.5) * 1.5  # peaks at middle
    score += max(0, position_score)

    # Slight randomness for variety
    score += (idx % 3) * 0.1

    return round(score, 2)


def detect_highlights(
    transcript: dict,
    num_clips: int = 5,
    max_length: int = 60,
) -> list[dict]:
    """Analyze transcript and return ranked highlight segments.

    Uses local heuristics — no API key needed.
    Returns list of {start, end, score, reason}.
    """
    segments = transcript["segments"]
    total_duration = transcript["duration"]

    if not segments:
        return []

    # Score all segments
    scored = []
    for i, seg in enumerate(segments):
        s = _segment_score(seg, total_duration, i, len(segments))
        scored.append({**seg, "score": s})

    # Merge adjacent high-scoring segments into clips
    scored.sort(key=lambda x: x["start"])

    # Group into candidate clips by merging consecutive segments
    # that fall within max_length of each other
    candidates = []
    current_start = scored[0]["start"]
    current_end = scored[0]["end"]
    current_texts = [scored[0]["text"]]
    current_scores = [scored[0]["score"]]

    for seg in scored[1:]:
        gap = seg["start"] - current_end
        clip_len = seg["end"] - current_start

        if gap < 3.0 and clip_len <= max_length:
            # Merge
            current_end = seg["end"]
            current_texts.append(seg["text"])
            current_scores.append(seg["score"])
        else:
            # Save current and start new
            avg_score = sum(current_scores) / len(current_scores)
            candidates.append({
                "start": current_start,
                "end": current_end,
                "text": " ".join(current_texts),
                "score": round(avg_score, 2),
            })
            current_start = seg["start"]
            current_end = seg["end"]
            current_texts = [seg["text"]]
            current_scores = [seg["score"]]

    # Don't forget the last group
    avg_score = sum(current_scores) / len(current_scores)
    candidates.append({
        "start": current_start,
        "end": current_end,
        "text": " ".join(current_texts),
        "score": round(avg_score, 2),
    })

    # Sort by score and pick top N
    candidates.sort(key=lambda x: x["score"], reverse=True)
    top = candidates[:num_clips]

    # Sort by time for final output
    top.sort(key=lambda x: x["start"])

    # Generate reasons
    results = []
    for c in top:
        text_preview = c["text"][:80].strip()
        if "?" in c["text"]:
            reason = f"Engaging question: \"{text_preview}...\""
        elif any(w in c["text"].lower() for w in ["!", "amazing", "incredible", "shocking"]):
            reason = f"High-energy moment: \"{text_preview}...\""
        elif any(w in c["text"].lower() for w in ["but", "however", "actually", "wait"]):
            reason = f"Key transition: \"{text_preview}...\""
        else:
            reason = f"Dense content: \"{text_preview}...\""

        results.append({
            "start": round(c["start"], 2),
            "end": round(c["end"], 2),
            "score": c["score"],
            "reason": reason,
        })

    return results

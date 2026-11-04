#!/usr/bin/env python3
"""Regenerate wiki/hot.md from wiki/log.md.

Run from project root: python wiki/update_hot.py

Standard library only. Never crashes — silently handles missing files.
"""

import os
import re
from datetime import datetime
from pathlib import Path

WIKI_DIR = Path("wiki")
LOG_FILE = WIKI_DIR / "log.md"
HOT_FILE = WIKI_DIR / "hot.md"
FEATURES_DIR = WIKI_DIR / "features"
LEDGER_FILE = WIKI_DIR / "Failed Ideas" / "ledger.md"


def read_file(path: Path) -> str:
    """Read file contents, return empty string on error."""
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, PermissionError, OSError):
        return ""


def extract_next_actions(content: str) -> str:
    """Preserve the hand-editable Next Actions block."""
    match = re.search(r"## Next Actions\s*\n(.*)", content, re.DOTALL)
    return match.group(1).strip() if match else ""


def parse_log_entries(log_content: str, limit: int = 10) -> list[str]:
    """Extract recent log entries (## [date] lines)."""
    entries = []
    for line in log_content.splitlines():
        if re.match(r"^## \[\d{4}-\d{2}-\d{2}\]", line):
            entries.append(f"- {line}")
    return entries[-limit:]


def count_features() -> tuple[int, int]:
    """Count total and active features."""
    total = 0
    active = 0
    if FEATURES_DIR.is_dir():
        for f in FEATURES_DIR.glob("*.md"):
            total += 1
            content = read_file(f)
            if "status: active" in content:
                active += 1
    return total, active


def count_failed_ideas() -> int:
    """Count rows in the Failed Ideas ledger."""
    content = read_file(LEDGER_FILE)
    if not content:
        return 0
    count = 0
    for line in content.splitlines():
        if re.match(r"^\|.*\|.*\|.*\|.*\|", line):
            if not re.match(r"^\| Date", line) and not re.match(r"^\| —", line):
                count += 1
    return count


def main():
    # Read existing hot.md to preserve Next Actions
    existing = read_file(HOT_FILE)
    next_actions = extract_next_actions(existing)

    # Parse log
    log_content = read_file(LOG_FILE)
    recent = parse_log_entries(log_content)
    recent_text = "\n".join(recent) if recent else "_No log entries yet._"

    # Count
    total_features, active_features = count_features()
    failed_count = count_failed_ideas()

    # Generate
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    hot = f"""> **AUTO-GENERATED** — Do not hand-edit the sections between the banners.
> The script `wiki/update_hot.py` owns this file. Edit the "Next Actions" block only.

<!-- BEGIN AUTO -->

## Current State

- Updated: {timestamp}
- Features: {total_features} total, {active_features} active
- Failed ideas: {failed_count}

## Recent Log

{recent_text}

<!-- END AUTO -->

## Next Actions

{next_actions}
"""

    HOT_FILE.write_text(hot, encoding="utf-8")
    print("hot.md regenerated")


if __name__ == "__main__":
    main()

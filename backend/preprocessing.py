"""Text preprocessing utilities for novel input."""

from __future__ import annotations

import re


def clean_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph order."""
    if text is None:
        return ""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[\u0000-\u0008\u000b\u000c\u000e-\u001f]", "", normalized)
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    lines = [line.strip() for line in normalized.split("\n")]
    return "\n".join(lines).strip()


def split_paragraphs(text: str) -> list[str]:
    """Split cleaned text into non-empty paragraphs."""
    cleaned = clean_text(text)
    return [part.strip() for part in re.split(r"\n+", cleaned) if part.strip()]

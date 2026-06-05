"""Chapter recognition for common Chinese and English chapter headings."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .preprocessing import clean_text


class ChapterParseError(ValueError):
    """Raised when novel text cannot be split into valid chapters."""


@dataclass(frozen=True)
class Chapter:
    id: str
    title: str
    content: str
    order: int


CHAPTER_HEADING_RE = re.compile(
    r"^\s*(?:"
    r"第\s*[零〇一二三四五六七八九十百千两\d]+\s*章(?:\s+.*)?"
    r"|Chapter\s+\d+(?:\s*[:：.\-]\s*.*)?"
    r")\s*$",
    re.IGNORECASE,
)


def is_chapter_heading(line: str) -> bool:
    return bool(CHAPTER_HEADING_RE.match(line.strip()))


def parse_chapters(text: str, min_chapters: int = 3) -> list[Chapter]:
    """Parse text into chapters and require at least ``min_chapters`` chapters."""
    cleaned = clean_text(text)
    if not cleaned:
        raise ChapterParseError("Input text is empty.")

    chapters: list[Chapter] = []
    current_title: str | None = None
    current_lines: list[str] = []

    for line in cleaned.splitlines():
        if is_chapter_heading(line):
            if current_title is not None:
                chapters.append(_build_chapter(current_title, current_lines, len(chapters) + 1))
            current_title = line.strip()
            current_lines = []
        elif current_title is not None:
            current_lines.append(line)

    if current_title is not None:
        chapters.append(_build_chapter(current_title, current_lines, len(chapters) + 1))

    if len(chapters) < min_chapters:
        raise ChapterParseError(
            f"At least {min_chapters} chapters are required; found {len(chapters)}."
        )

    empty_titles = [chapter.title for chapter in chapters if not chapter.content.strip()]
    if empty_titles:
        joined = ", ".join(empty_titles)
        raise ChapterParseError(f"Chapter content is missing for: {joined}.")

    return chapters


def _build_chapter(title: str, lines: list[str], order: int) -> Chapter:
    content = "\n".join(line for line in lines).strip()
    return Chapter(
        id=f"chapter_{order:03d}",
        title=title.strip(),
        content=content,
        order=order,
    )

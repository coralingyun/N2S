"""Basic chapter-aware text chunking."""

from __future__ import annotations

from dataclasses import dataclass

from .chapter_parser import Chapter
from .preprocessing import split_paragraphs


@dataclass(frozen=True)
class TextChunk:
    chapter_id: str
    chunk_id: str
    text: str


def chunk_chapter(chapter: Chapter, max_chars: int = 6000) -> list[TextChunk]:
    """Chunk one chapter by paragraph without splitting natural paragraphs."""
    if len(chapter.content) <= max_chars:
        return [TextChunk(chapter_id=chapter.id, chunk_id=f"{chapter.id}_chunk_001", text=chapter.content)]

    chunks: list[TextChunk] = []
    current_parts: list[str] = []
    current_len = 0

    for paragraph in split_paragraphs(chapter.content):
        paragraph_len = len(paragraph)
        if current_parts and current_len + paragraph_len + 2 > max_chars:
            chunks.append(_build_chunk(chapter.id, len(chunks) + 1, current_parts))
            current_parts = []
            current_len = 0
        current_parts.append(paragraph)
        current_len += paragraph_len + 2

    if current_parts:
        chunks.append(_build_chunk(chapter.id, len(chunks) + 1, current_parts))

    return chunks


def chunk_chapters(chapters: list[Chapter], max_chars: int = 6000) -> list[TextChunk]:
    """Chunk all chapters while preserving chapter IDs."""
    chunks: list[TextChunk] = []
    for chapter in chapters:
        chunks.extend(chunk_chapter(chapter, max_chars=max_chars))
    return chunks


def _build_chunk(chapter_id: str, order: int, paragraphs: list[str]) -> TextChunk:
    return TextChunk(
        chapter_id=chapter_id,
        chunk_id=f"{chapter_id}_chunk_{order:03d}",
        text="\n\n".join(paragraphs),
    )

"""End-to-end conversion pipeline for the MVP."""

from __future__ import annotations

import logging
import os

from .chapter_parser import Chapter, parse_chapters
from .llm_adapter import LLMAdapter, get_llm_adapter
from .preprocessing import clean_text
from .text_chunker import chunk_chapter
from .yaml_validator import repair_and_validate_screenplay_data

logger = logging.getLogger(__name__)


def convert_novel_to_screenplay_yaml(
    input_text: str,
    llm_adapter: LLMAdapter | None = None,
    max_repair_attempts: int = 2,
) -> dict:
    """Convert novel text into a validated screenplay YAML-compatible dict."""
    cleaned = clean_text(input_text)
    chapters = parse_chapters(cleaned)
    llm = llm_adapter or get_llm_adapter()
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower() or "mock"

    logger.info("Starting conversion: chapters=%s provider=%s", len(chapters), provider)

    chapter_analyses = [_analyze_chapter_with_chunks(llm, chapter) for chapter in chapters]
    logger.info("Chapter analysis completed: chapters=%s", len(chapter_analyses))

    characters = llm.extract_characters(chapter_analyses)
    logger.info("Character extraction completed: characters=%s", len(characters))

    scenes: list[dict] = []
    for chapter, analysis in zip(chapters, chapter_analyses, strict=True):
        scenes.extend(llm.split_scenes(chapter, analysis, characters))
    logger.info("Scene splitting completed: scenes=%s", len(scenes))

    screenplay = llm.generate_screenplay(chapters, chapter_analyses, characters, scenes)
    logger.info("Screenplay YAML generation completed.")

    validated = repair_and_validate_screenplay_data(
        screenplay,
        llm,
        max_attempts=max_repair_attempts,
    )
    logger.info("YAML schema validation completed.")
    return validated


def _analyze_chapter_with_chunks(llm: LLMAdapter, chapter: Chapter) -> dict:
    chunks = chunk_chapter(chapter)
    logger.info("Prepared chunks for %s: chunks=%s", chapter.id, len(chunks))
    if len(chunks) == 1:
        analysis = llm.analyze_chapter(chapter)
        logger.info("Chapter analysis completed: chapter_id=%s", chapter.id)
        return analysis

    chunk_analyses: list[dict] = []
    for index, chunk in enumerate(chunks, start=1):
        chunk_chapter_obj = Chapter(
            id=chapter.id,
            title=f"{chapter.title} chunk {index}",
            content=chunk.text,
            order=chapter.order,
        )
        chunk_analyses.append(llm.analyze_chapter(chunk_chapter_obj))

    merged = _merge_chunk_analyses(chapter, chunk_analyses)
    logger.info("Chunked chapter analysis completed: chapter_id=%s chunks=%s", chapter.id, len(chunks))
    return merged


def _merge_chunk_analyses(chapter: Chapter, chunk_analyses: list[dict]) -> dict:
    def unique_values(field: str) -> list:
        values = []
        seen = set()
        for analysis in chunk_analyses:
            for value in analysis.get(field, []):
                key = repr(value)
                if key not in seen:
                    values.append(value)
                    seen.add(key)
        return values

    emotional_start = ""
    emotional_end = ""
    if chunk_analyses:
        emotional_start = chunk_analyses[0].get("emotional_shift", {}).get("start", "")
        emotional_end = chunk_analyses[-1].get("emotional_shift", {}).get("end", "")

    return {
        "chapter_id": chapter.id,
        "title": chapter.title,
        "summary": " ".join(str(item.get("summary", "")) for item in chunk_analyses).strip(),
        "locations": unique_values("locations"),
        "characters": unique_values("characters"),
        "events": unique_values("events"),
        "conflicts": unique_values("conflicts"),
        "emotional_shift": {"start": emotional_start, "end": emotional_end},
        "unresolved_issues": unique_values("unresolved_issues"),
    }

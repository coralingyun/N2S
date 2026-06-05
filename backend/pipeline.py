"""End-to-end conversion pipeline for the MVP."""

from __future__ import annotations

from .chapter_parser import parse_chapters
from .llm_adapter import MockLLMAdapter
from .preprocessing import clean_text
from .screenplay_generator import generate_screenplay
from .yaml_validator import validate_screenplay_data


def convert_novel_to_screenplay_yaml(input_text: str) -> dict:
    """Convert novel text into a validated screenplay YAML-compatible dict."""
    cleaned = clean_text(input_text)
    chapters = parse_chapters(cleaned)
    llm = MockLLMAdapter()
    chapter_analyses = [llm.analyze_chapter(chapter) for chapter in chapters]
    screenplay = generate_screenplay(chapters, chapter_analyses, llm)
    validate_screenplay_data(screenplay)
    return screenplay

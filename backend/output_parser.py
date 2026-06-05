"""Utilities for parsing structured LLM output."""

from __future__ import annotations

import json
import re
from typing import Any

import yaml
from yaml import YAMLError


class OutputParseError(ValueError):
    """Raised when an LLM output cannot be parsed as the expected format."""

    def __init__(self, message: str, raw_output: str) -> None:
        super().__init__(message)
        self.raw_output = raw_output


def extract_code_block(text: str, preferred_languages: tuple[str, ...] = ("yaml", "yml", "json")) -> str:
    """Extract a fenced code block, or return stripped text when no block exists."""
    stripped = text.strip()
    blocks = re.findall(r"```([A-Za-z0-9_-]*)\s*(.*?)```", stripped, flags=re.DOTALL)
    if not blocks:
        return stripped

    normalized = {language.lower(): content.strip() for language, content in blocks}
    for language in preferred_languages:
        if language in normalized:
            return normalized[language]
    return blocks[0][1].strip()


def parse_json_output(text: str) -> Any:
    """Parse JSON from an LLM output, including fenced code blocks."""
    candidate = extract_code_block(text, preferred_languages=("json",))
    try:
        return json.loads(candidate)
    except json.JSONDecodeError as exc:
        raise OutputParseError(f"Failed to parse LLM output as JSON: {exc}", text) from exc


def parse_yaml_output(text: str) -> Any:
    """Parse YAML from an LLM output, including fenced code blocks."""
    candidate = extract_code_block(text, preferred_languages=("yaml", "yml", "json"))
    try:
        return yaml.safe_load(candidate)
    except YAMLError as exc:
        raise OutputParseError(f"Failed to parse LLM output as YAML: {exc}", text) from exc


def parse_mapping_output(text: str, format_hint: str = "yaml") -> dict[str, Any]:
    """Parse YAML or JSON output and require a mapping root."""
    parsed = parse_json_output(text) if format_hint == "json" else parse_yaml_output(text)
    if not isinstance(parsed, dict):
        raise OutputParseError("Parsed LLM output must be a mapping/object.", text)
    return parsed

"""YAML parsing and schema validation."""

from __future__ import annotations

import logging
from typing import Any

import yaml
from pydantic import ValidationError
from yaml import YAMLError

from .schemas import Screenplay
from .output_parser import OutputParseError, parse_mapping_output

logger = logging.getLogger(__name__)


class ScreenplayValidationError(ValueError):
    """Raised when screenplay YAML cannot be validated or repaired."""

    def __init__(self, message: str, errors: list[dict[str, Any]] | None = None) -> None:
        super().__init__(message)
        self.errors = errors or []


def validate_screenplay_data(data: dict[str, Any]) -> Screenplay:
    """Validate a screenplay dictionary and return its Pydantic model."""
    try:
        return Screenplay.model_validate(data)
    except ValidationError as exc:
        raise ScreenplayValidationError("Screenplay schema validation failed.", format_validation_errors(exc)) from exc


def validate_screenplay_yaml(yaml_text: str) -> Screenplay:
    """Parse and validate screenplay YAML text."""
    loaded = load_yaml_mapping(yaml_text)
    return validate_screenplay_data(loaded)


def load_yaml_mapping(yaml_text: str) -> dict[str, Any]:
    """Load YAML text and require a mapping root."""
    try:
        loaded = parse_mapping_output(yaml_text, format_hint="yaml")
    except (YAMLError, OutputParseError) as exc:
        raise ScreenplayValidationError(
            "YAML parsing failed.",
            [{"path": "$", "reason": str(exc)}],
        ) from exc
    return loaded


def dump_screenplay_yaml(data: dict[str, Any]) -> str:
    """Serialize screenplay data as readable UTF-8 YAML."""
    validate_screenplay_data(data)
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def dump_raw_yaml(data: dict[str, Any]) -> str:
    """Serialize data without validating it first."""
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def format_validation_errors(exc: ValidationError) -> list[dict[str, Any]]:
    """Convert Pydantic errors into stable API-friendly path/reason objects."""
    formatted: list[dict[str, Any]] = []
    for error in exc.errors():
        loc = ".".join(str(part) for part in error.get("loc", ()))
        formatted.append(
            {
                "path": f"$.{loc}" if loc else "$",
                "reason": error.get("msg", "Invalid value."),
                "type": error.get("type", "value_error"),
            }
        )
    return formatted


def repair_and_validate_screenplay_data(data: dict[str, Any], llm_adapter, max_attempts: int = 2) -> dict[str, Any]:
    """Validate data, then try bounded LLM repair if validation fails."""
    current_data = data
    last_errors: list[dict[str, Any]] = []

    for attempt in range(max_attempts + 1):
        try:
            validate_screenplay_data(current_data)
            if attempt:
                logger.info("YAML schema validation succeeded after repairs: repair_attempts=%s", attempt)
            else:
                logger.info("YAML schema validation succeeded without repair.")
            return current_data
        except ScreenplayValidationError as exc:
            last_errors = exc.errors
            if attempt >= max_attempts:
                break
            logger.info("YAML schema validation failed; requesting repair: attempt=%s", attempt + 1)
            repaired_yaml = llm_adapter.repair_yaml(dump_raw_yaml(current_data), last_errors)
            current_data = load_yaml_mapping(repaired_yaml)

    logger.error("YAML schema validation failed after repair attempts: attempts=%s", max_attempts)
    raise ScreenplayValidationError(
        f"Screenplay schema validation failed after {max_attempts} repair attempts.",
        last_errors,
    )

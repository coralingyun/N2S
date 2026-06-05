"""YAML parsing and schema validation."""

from __future__ import annotations

from typing import Any

import yaml
from pydantic import ValidationError

from .schemas import Screenplay


def validate_screenplay_data(data: dict[str, Any]) -> Screenplay:
    """Validate a screenplay dictionary and return its Pydantic model."""
    return Screenplay.model_validate(data)


def validate_screenplay_yaml(yaml_text: str) -> Screenplay:
    """Parse and validate screenplay YAML text."""
    loaded = yaml.safe_load(yaml_text)
    if not isinstance(loaded, dict):
        raise ValidationError("YAML root must be an object.")
    return validate_screenplay_data(loaded)


def dump_screenplay_yaml(data: dict[str, Any]) -> str:
    """Serialize screenplay data as readable UTF-8 YAML."""
    validate_screenplay_data(data)
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)

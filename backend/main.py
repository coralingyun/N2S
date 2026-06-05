"""FastAPI app and CLI entry point for the local MVP demo."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .chapter_parser import ChapterParseError
from .llm_adapter import LLMConfigurationError, LLMRequestError
from .pipeline import convert_novel_to_screenplay_yaml
from .yaml_validator import (
    ScreenplayValidationError,
    dump_screenplay_yaml,
    validate_screenplay_yaml,
)


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "examples" / "sample_novel.txt"
OUTPUT_PATH = ROOT / "examples" / "sample_screenplay.yaml"
FRONTEND_DIR = ROOT / "frontend"

app = FastAPI(title="Novel to Screenplay AI", version="0.2")


class ConvertRequest(BaseModel):
    input_text: str


class ValidateRequest(BaseModel):
    yaml_text: str


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/sample-novel")
def sample_novel() -> dict[str, str]:
    return {"text": INPUT_PATH.read_text(encoding="utf-8")}


@app.post("/convert")
def convert(request: ConvertRequest) -> dict[str, Any]:
    try:
        screenplay = convert_novel_to_screenplay_yaml(request.input_text)
        return {"ok": True, "data": screenplay, "yaml": dump_screenplay_yaml(screenplay)}
    except ChapterParseError as exc:
        raise HTTPException(status_code=400, detail={"message": str(exc), "errors": []}) from exc
    except (ScreenplayValidationError, LLMConfigurationError, LLMRequestError) as exc:
        raise HTTPException(
            status_code=422,
            detail={"message": str(exc), "errors": getattr(exc, "errors", [])},
        ) from exc


@app.post("/validate")
def validate(request: ValidateRequest) -> dict[str, Any]:
    try:
        validate_screenplay_yaml(request.yaml_text)
        return {"ok": True, "errors": []}
    except ScreenplayValidationError as exc:
        return {"ok": False, "errors": exc.errors, "message": str(exc)}


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    input_text = INPUT_PATH.read_text(encoding="utf-8")
    screenplay = convert_novel_to_screenplay_yaml(input_text)
    yaml_text = dump_screenplay_yaml(screenplay)
    OUTPUT_PATH.write_text(yaml_text, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

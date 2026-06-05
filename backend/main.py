"""CLI entry point for the local MVP demo."""

from __future__ import annotations

from pathlib import Path

from .pipeline import convert_novel_to_screenplay_yaml
from .yaml_validator import dump_screenplay_yaml


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "examples" / "sample_novel.txt"
OUTPUT_PATH = ROOT / "examples" / "sample_screenplay.yaml"


def main() -> None:
    input_text = INPUT_PATH.read_text(encoding="utf-8")
    screenplay = convert_novel_to_screenplay_yaml(input_text)
    yaml_text = dump_screenplay_yaml(screenplay)
    OUTPUT_PATH.write_text(yaml_text, encoding="utf-8")
    print(f"Generated {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

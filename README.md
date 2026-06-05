# Novel to Screenplay AI

This project is an MVP for converting multi-chapter novel text into a structured, editable screenplay draft expressed as YAML.

The current implementation is deliberately small. It does not call a real LLM API. Instead, it uses a deterministic `MockLLMAdapter` so the complete pipeline can be run, validated, and tested locally.

## Current Capabilities

- Read a Chinese sample novel with at least three chapters.
- Clean and normalize text.
- Detect common chapter headings, including `第一章`, `第1章`, `第 一 章`, and `Chapter 1`.
- Generate mock chapter analysis.
- Generate screenplay YAML as a Python dictionary.
- Validate the YAML structure with Pydantic.
- Save the result to `examples/sample_screenplay.yaml`.

## Installation

Create and use a local virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run the Demo

```powershell
.\.venv\Scripts\python.exe -m backend.main
```

This reads `examples/sample_novel.txt` and writes `examples/sample_screenplay.yaml`.

## Run Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Project Structure

```text
README.md
PLAN.md
requirements.txt
docs/
  yaml_schema.md
  prompt_design.md
examples/
  sample_novel.txt
  sample_screenplay.yaml
backend/
  main.py
  pipeline.py
  preprocessing.py
  chapter_parser.py
  scene_splitter.py
  screenplay_generator.py
  yaml_validator.py
  llm_adapter.py
  schemas.py
tests/
  test_chapter_parser.py
  test_yaml_validator.py
  test_pipeline.py
```

## MVP Boundaries

Not implemented yet:

- Real LLM API integration.
- Frontend editor or export UI.
- Streaming progress updates.
- Long-context chunking.
- Human-in-the-loop revision workflow.
- Advanced scene splitting based on semantic analysis.

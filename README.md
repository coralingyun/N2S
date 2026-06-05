# Novel to Screenplay AI

This project is an MVP for converting multi-chapter novel text into a structured, editable screenplay draft expressed as YAML.

The current implementation is deliberately small. It supports a deterministic `MockLLMAdapter` for local tests and an OpenAI-compatible adapter for real LLM calls when environment variables are configured.

The tool is intended for novel authors and screenplay creators who need an editable first draft rather than a simple summary. It analyzes chapters, characters, conflicts, scenes, and beats, then produces YAML that can be reviewed and revised by a human author.

## Current Capabilities

- Read a Chinese sample novel with at least three chapters.
- Clean and normalize text.
- Detect common chapter headings, including `第一章`, `第1章`, `第 一 章`, and `Chapter 1`.
- Run chapter-level analysis, character extraction, scene splitting, screenplay YAML generation, validation, and bounded repair.
- Generate screenplay YAML as a Python dictionary.
- Validate the YAML structure with Pydantic.
- Try a bounded YAML repair loop when validation fails.
- Expose FastAPI endpoints for conversion and validation.
- Serve a minimal Web demo for input, conversion, validation, copy, and YAML download.
- Save the result to `examples/sample_screenplay.yaml`.

The current chunking strategy is intentionally basic. It uses chapters as the main unit and splits overlong chapters by paragraph without cutting natural paragraphs. It is not a semantic chunking, RAG, or retrieval system.

## Installation

Create and use a local virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` or set variables in PowerShell before running:

```powershell
$env:LLM_PROVIDER = "mock"
```

Supported variables:

```text
LLM_PROVIDER=mock
LLM_API_KEY=
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=
```

For real LLM calls:

```powershell
$env:LLM_PROVIDER = "openai"
$env:LLM_API_KEY = "your-api-key"
$env:LLM_BASE_URL = "https://api.openai.com/v1"
$env:LLM_MODEL = "your-model"
```

No API key is required for `LLM_PROVIDER=mock`. If `LLM_PROVIDER=openai` is selected without `LLM_API_KEY` or `LLM_MODEL`, the backend raises a clear configuration error.

In real LLM mode, the conversion chain calls the model for chapter analysis, character extraction, scene splitting, full screenplay YAML generation, and YAML repair. Output quality depends on the configured model and the input novel. Generated results should be reviewed and edited by a human author.

## Run the Demo

```powershell
.\.venv\Scripts\python.exe -m backend.main
```

This reads `examples/sample_novel.txt` and writes `examples/sample_screenplay.yaml`.

## Run FastAPI

```powershell
.\.venv\Scripts\uvicorn.exe backend.main:app --reload
```

Open the Web demo after the server starts:

```text
http://127.0.0.1:8000/
```

For a complete Web Demo run:

1. Start FastAPI.
2. Open `http://127.0.0.1:8000/`.
3. Click `加载示例小说`.
4. Click `生成剧本 YAML`.
5. Click `校验 YAML`.
6. Copy the YAML or download `screenplay.yaml`.

Available endpoints:

- `GET /health`
- `GET /sample-novel`
- `POST /convert`
- `POST /validate`

Example `/convert` request:

```powershell
$body = @{ input_text = Get-Content examples\sample_novel.txt -Raw } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/convert -ContentType "application/json" -Body $body
```

Example `/validate` request:

```powershell
$body = @{ yaml_text = Get-Content examples\sample_screenplay.yaml -Raw } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/validate -ContentType "application/json" -Body $body
```

## Web Demo Features

The minimal browser demo supports:

- loading `examples/sample_novel.txt`;
- pasting novel text into a textarea;
- generating screenplay YAML through `/convert`;
- editing the YAML output;
- validating YAML through `/validate`;
- copying YAML to the clipboard;
- downloading `screenplay.yaml`.

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
  acceptance_checklist.md
examples/
  sample_novel.txt
  sample_screenplay.yaml
frontend/
  index.html
  app.js
  style.css
backend/
  main.py
  pipeline.py
  preprocessing.py
  chapter_parser.py
  scene_splitter.py
  screenplay_generator.py
  yaml_validator.py
  llm_adapter.py
  output_parser.py
  text_chunker.py
  prompts.py
  schemas.py
tests/
  conftest.py
  test_api.py
  test_chapter_parser.py
  test_output_parser.py
  test_text_chunker.py
  test_yaml_validator.py
  test_pipeline.py
```

## MVP Boundaries

Not implemented yet:

- Rich frontend editor, syntax highlighting, or multi-file project workspace.
- Streaming progress updates.
- Advanced semantic chunking or retrieval.
- Human-in-the-loop revision workflow.
- Advanced scene splitting based on semantic analysis.

## Documentation

- YAML schema: `docs/yaml_schema.md`
- Prompt design: `docs/prompt_design.md`
- Acceptance checklist: `docs/acceptance_checklist.md`

## Suggested Next Stage

The next practical upgrade is a lightweight YAML editing experience with syntax highlighting and better validation navigation, followed by progress reporting for real LLM conversions.

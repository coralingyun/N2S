# MVP Acceptance Checklist

This checklist defines the minimum acceptance scope for the AI novel-to-screenplay MVP.

## Functional Acceptance

- The backend can start with FastAPI.
- `GET /health` returns service status.
- `GET /sample-novel` returns a sample novel with at least three chapters.
- `POST /convert` accepts novel text and returns screenplay YAML.
- `POST /validate` accepts YAML text and returns validation results.
- Inputs with fewer than three chapters return a clear error.
- The command-line demo can generate `examples/sample_screenplay.yaml`.

## YAML Schema Acceptance

- YAML contains `project`, `metadata`, `story`, `characters`, `structure`, `scenes`, `transitions`, and `notes`.
- `metadata.source_chapter_count` is at least 3.
- `characters` contains stable character IDs.
- `scenes` contains at least one scene.
- Each scene contains `scene_id`, `source_chapter`, `scene_heading`, `purpose`, `conflict`, `characters_present`, `emotional_arc`, and `beats`.
- Each scene has at least one beat.
- Dialogue beats include a valid `character`.
- Character references use stable IDs rather than inconsistent names.
- YAML can pass Pydantic validation.

## Web Demo Acceptance

- `http://127.0.0.1:8000/` opens the demo page.
- The page shows backend availability via `/health`.
- The user can load `examples/sample_novel.txt`.
- The user can paste novel text into the input area.
- The user can generate YAML through `/convert`.
- The user can validate edited YAML through `/validate`.
- The user can copy YAML to the clipboard.
- The user can download `screenplay.yaml`.
- Validation errors show field paths and reasons on the page.
- Generation and validation buttons show loading states and avoid duplicate clicks.

## Real LLM Mode Acceptance

- `LLM_PROVIDER=mock` works without an API key.
- `LLM_PROVIDER=openai` requires `LLM_API_KEY` and `LLM_MODEL`.
- No API key is hard-coded or displayed in logs.
- The real LLM chain calls chapter analysis, character extraction, scene splitting, screenplay YAML generation, validation, and repair.
- YAML repair is bounded to at most two attempts.
- Real LLM output remains subject to human review.

## Current MVP Boundaries

- No login or authentication.
- No database or persistent project storage.
- No asynchronous task queue.
- No rich YAML editor or syntax highlighting.
- No long-form project version management.
- No production-grade prompt evaluation.
- No advanced semantic chunking or retrieval.

## Recommended Next Extensions

- Add a lightweight YAML editor with syntax highlighting.
- Add request progress reporting for long conversions.
- Add structured export formats such as Markdown screenplay view.
- Improve prompts with model-specific examples and regression tests.
- Add human revision notes and before/after comparison.
- Add optional project save/load once persistence is required.

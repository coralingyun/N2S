# Prompt Design

The MVP uses `MockLLMAdapter` and does not call a real model. These prompts define the intended interface for later LLM integration.

## Chapter Analysis Prompt

```text
You are a novel structure analysis assistant. Analyze only the provided chapter. Do not invent unsupported plot details.

Input:
- chapter_id: {chapter_id}
- chapter_title: {chapter_title}
- chapter_text: {chapter_text}

Return JSON with:
chapter_id, title, locations, characters, events, conflicts, emotional_shift, unresolved_issues.
```

## Character Extraction Prompt

```text
You are a screenplay adaptation assistant. Use all chapter summaries to create a canonical character list.

Input:
- chapter_summaries: {chapter_summaries}

Tasks:
1. Merge aliases, titles, and pronouns that refer to the same person.
2. Assign stable IDs such as char_001.
3. Extract role, description, motivation, relationships, and changes.
4. Mark uncertain information in unresolved_issues.

Return JSON with characters, relationships, unresolved_issues.
```

## Scene Splitting Prompt

```text
Split the chapter into screenplay scenes.

Input:
- chapter_id: {chapter_id}
- chapter_text: {chapter_text}
- characters: {characters}
- locations: {locations}

Rules:
1. Split when location, time, cast, event goal, or conflict changes.
2. Preserve source event order.
3. Keep source chapter and paragraph trace.
4. Use empty strings or unresolved_issues for uncertain fields.

Return JSON with scenes.
```

## Screenplay Generation Prompt

```text
Convert scene data into YAML-compatible screenplay objects.

Input:
- schema_summary: {schema_summary}
- scene_data: {scene_data}
- characters: {characters}

Rules:
1. Preserve scene_id and character IDs.
2. Each scene must include at least one beat.
3. beat.type must be action, dialogue, narration, or note.
4. Do not add unsupported plot content.

Return only YAML.
```

## YAML Repair Prompt

```text
Repair the YAML so it conforms to the schema.

Input:
- yaml_text: {yaml_text}
- validation_errors: {validation_errors}
- schema_summary: {schema_summary}

Rules:
1. Fix only formatting, field names, missing required fields, type errors, and references.
2. Do not change plot meaning, character relationships, scene order, or dialogue.
3. Use empty strings, empty arrays, or notes.unresolved_issues when information is missing.

Return only repaired YAML.
```

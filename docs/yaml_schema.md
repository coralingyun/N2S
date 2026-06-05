# YAML Schema Design

This document defines the MVP YAML structure for converting novel chapters into an editable screenplay draft. The schema is intentionally compact so that the first implementation can be validated, tested, and extended without relying on a real LLM API.

## Top-Level Structure

```yaml
project: {}
metadata: {}
story: {}
characters: []
structure:
  acts: []
scenes: []
transitions: []
notes: {}
```

## Field Definitions

| Field | Type | Required | Purpose |
| --- | --- | --- | --- |
| `project` | object | yes | Basic project identity and adaptation target. |
| `metadata` | object | yes | Version, author, creation time, and source chapter count. |
| `story` | object | yes | Global story understanding, including logline, synopsis, themes, tone, and perspective. |
| `characters` | array | yes | Canonical character list with stable IDs. |
| `structure` | object | yes | Act-level organization for later screenplay revision. |
| `scenes` | array | yes | Core screenplay content. Each scene contains heading, conflict, cast, emotional arc, and beats. |
| `transitions` | array | yes | Scene-to-scene connection information. |
| `notes` | object | yes | Adaptation notes and unresolved issues requiring author review. |

## Scene Object

Each scene must contain:

- `scene_id`: stable scene identifier, such as `scene_001`.
- `source_chapter`: source chapter identifier, such as `chapter_001`.
- `scene_heading`: object with `location`, `time`, and `interior_exterior`.
- `purpose`: the dramatic function of the scene.
- `conflict`: the central conflict in the scene.
- `characters_present`: character IDs appearing in the scene.
- `emotional_arc`: object with `start` and `end`.
- `beats`: ordered list of scene beats.

## Beat Object

`beats` preserve the internal order of a scene. Supported MVP beat types are:

- `action`: visible action or staging.
- `dialogue`: spoken line; must include `character`.
- `narration`: voice-over, narration, or retained prose information.
- `note`: adaptation note embedded at beat level.

## Example

```yaml
project:
  title: "手稿之夜"
  source_type: "novel"
  language: "zh-CN"
  adaptation_goal: "screenplay_draft"
metadata:
  author: ""
  created_at: "2026-06-05T00:00:00+00:00"
  version: "0.1"
  source_chapter_count: 3
story:
  logline: "A writer investigates altered manuscript pages."
  synopsis: "The protagonist follows clues across three chapters."
  themes: ["authorship", "memory"]
  tone: "suspenseful"
  narrative_perspective: "third_person_limited"
characters:
  - id: "char_001"
    name: "林舟"
    role: "protagonist"
    description: "A young writer."
    motivation: "Recover the missing pages."
    relationship_to_others: []
structure:
  acts:
    - act_id: "act_1"
      title: "发现"
      function: "setup"
      chapters_covered: ["chapter_001"]
scenes:
  - scene_id: "scene_001"
    source_chapter: "chapter_001"
    scene_heading:
      location: "旧书店"
      time: "night"
      interior_exterior: "INT"
    purpose: "Introduce the altered manuscript."
    conflict: "The protagonist cannot prove who changed the manuscript."
    characters_present: ["char_001"]
    emotional_arc:
      start: "calm"
      end: "uneasy"
    beats:
      - beat_id: "beat_001_001"
        type: "action"
        content: "林舟翻开手稿。"
transitions: []
notes:
  adaptation_notes: []
  unresolved_issues: []
```

## Design Rationale

`project` records basic project properties so the schema can later support different source types or adaptation goals.

`metadata` supports reproducibility by recording version, author, creation time, and source chapter count.

`story` keeps global narrative understanding so the screenplay does not become a list of disconnected scenes.

`characters` provides stable IDs and reduces ambiguity caused by names, aliases, titles, and pronouns.

`structure` stores act-level organization. It supports three-act and multi-act revisions without forcing all stories into one fixed structure.

`scenes` is the core level because a screenplay is primarily organized as scenes.

`beats` represent ordered internal scene units, including action, dialogue, narration, and notes.

`transitions` records how scenes connect and can later support richer editing or shot-level planning.

`notes` separates uncertain or unresolved AI output from verified story content.

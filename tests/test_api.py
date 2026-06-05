from fastapi.testclient import TestClient

from backend.main import app
from backend.pipeline import convert_novel_to_screenplay_yaml
from backend.yaml_validator import dump_screenplay_yaml


client = TestClient(app)


def test_frontend_root_is_served() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "AI 小说转剧本工具" in response.text


def test_sample_novel_endpoint_returns_text() -> None:
    response = client.get("/sample-novel")
    assert response.status_code == 200
    text = response.json()["text"]
    assert "第一章" in text
    assert "第二章" in text
    assert "第三章" in text


def test_convert_rejects_less_than_three_chapters() -> None:
    response = client.post(
        "/convert",
        json={
            "input_text": """
第一章
只有第一章。

第二章
只有第二章。
"""
        },
    )
    assert response.status_code == 400
    assert "At least 3 chapters" in response.json()["detail"]["message"]


def test_validate_accepts_valid_yaml() -> None:
    data = convert_novel_to_screenplay_yaml(
        """
第一章
林舟发现手稿被替换。

第二章
许澄找到旧登记表。

第三章
两人在天台公开证据。
"""
    )
    response = client.post("/validate", json={"yaml_text": dump_screenplay_yaml(data)})
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_convert_mock_returns_valid_yaml() -> None:
    response = client.post(
        "/convert",
        json={
            "input_text": """
第一章
林舟在旧书店发现手稿被替换。

第二章
许澄找到旧登记表。

第三章
两人在天台公开证据。
"""
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body["ok"] is True
    validate_response = client.post("/validate", json={"yaml_text": body["yaml"]})
    assert validate_response.json()["ok"] is True


def test_validate_rejects_invalid_yaml() -> None:
    response = client.post("/validate", json={"yaml_text": "project: ["})
    body = response.json()
    assert response.status_code == 200
    assert body["ok"] is False
    assert body["errors"]


def test_validate_rejects_missing_scenes() -> None:
    response = client.post(
        "/validate",
        json={
            "yaml_text": """
project:
  title: x
  source_type: novel
  language: zh-CN
  adaptation_goal: screenplay_draft
metadata:
  author: ''
  created_at: '2026-06-05T00:00:00+00:00'
  version: '0.1'
  source_chapter_count: 3
story:
  logline: x
  synopsis: x
  themes: []
  tone: x
  narrative_perspective: x
characters:
  - id: char_001
    name: 林舟
    role: protagonist
    description: x
    motivation: x
    relationship_to_others: []
structure:
  acts: []
transitions: []
notes:
  adaptation_notes: []
  unresolved_issues: []
"""
        },
    )
    body = response.json()
    assert body["ok"] is False
    assert any("scenes" in error["path"] for error in body["errors"])


def test_validate_rejects_scene_without_beat() -> None:
    response = client.post(
        "/validate",
        json={
            "yaml_text": """
project:
  title: x
  source_type: novel
  language: zh-CN
  adaptation_goal: screenplay_draft
metadata:
  author: ''
  created_at: '2026-06-05T00:00:00+00:00'
  version: '0.1'
  source_chapter_count: 3
story:
  logline: x
  synopsis: x
  themes: []
  tone: x
  narrative_perspective: x
characters:
  - id: char_001
    name: 林舟
    role: protagonist
    description: x
    motivation: x
    relationship_to_others: []
structure:
  acts: []
scenes:
  - scene_id: scene_001
    source_chapter: chapter_001
    scene_heading:
      location: 旧书店
      time: night
      interior_exterior: INT
    purpose: x
    conflict: x
    characters_present: [char_001]
    emotional_arc:
      start: calm
      end: tense
    beats: []
transitions: []
notes:
  adaptation_notes: []
  unresolved_issues: []
"""
        },
    )
    body = response.json()
    assert body["ok"] is False
    assert any("beats" in error["path"] for error in body["errors"])


def test_validate_rejects_dialogue_without_character() -> None:
    response = client.post(
        "/validate",
        json={
            "yaml_text": """
project:
  title: x
  source_type: novel
  language: zh-CN
  adaptation_goal: screenplay_draft
metadata:
  author: ''
  created_at: '2026-06-05T00:00:00+00:00'
  version: '0.1'
  source_chapter_count: 3
story:
  logline: x
  synopsis: x
  themes: []
  tone: x
  narrative_perspective: x
characters:
  - id: char_001
    name: 林舟
    role: protagonist
    description: x
    motivation: x
    relationship_to_others: []
structure:
  acts: []
scenes:
  - scene_id: scene_001
    source_chapter: chapter_001
    scene_heading:
      location: 旧书店
      time: night
      interior_exterior: INT
    purpose: x
    conflict: x
    characters_present: [char_001]
    emotional_arc:
      start: calm
      end: tense
    beats:
      - beat_id: beat_001
        type: dialogue
        content: 这不是我写的。
transitions: []
notes:
  adaptation_notes: []
  unresolved_issues: []
"""
        },
    )
    body = response.json()
    assert body["ok"] is False
    assert any("Dialogue beat" in error["reason"] for error in body["errors"])


def test_mock_yaml_uses_chinese_content_without_english_template() -> None:
    data = convert_novel_to_screenplay_yaml(
        """
第一章
林舟在旧书店发现手稿被替换。

第二章
许澄找到旧登记表。

第三章
两人在天台公开证据。
"""
    )
    yaml_text = dump_screenplay_yaml(data)
    assert "Adapt the central event" not in yaml_text
    assert "This output is generated" not in yaml_text
    assert "林舟" in yaml_text
    assert "手稿" in yaml_text

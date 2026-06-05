import pytest

from backend.llm_adapter import MockLLMAdapter
from backend.pipeline import convert_novel_to_screenplay_yaml
from backend.yaml_validator import ScreenplayValidationError, repair_and_validate_screenplay_data, validate_screenplay_data


def test_pipeline_outputs_required_top_level_sections() -> None:
    text = """
第一章
旧书店即将打烊，林舟发现自己的手稿被人换走。

第 一 章
许澄在图书馆档案室找出一张旧登记表，登记表上有林舟父亲的名字。

Chapter 1
雨落在天台边缘，两人争执后决定保留证据并公开真相。
"""
    data = convert_novel_to_screenplay_yaml(text)

    assert {"project", "story", "characters", "scenes"}.issubset(data)
    assert data["scenes"]
    assert data["scenes"][0]["beats"]
    validate_screenplay_data(data)


def test_pipeline_runs_with_mock_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    text = """
第一章
林舟在旧书店发现手稿被替换。

第二章
许澄带他去档案室查找旧记录。

第三章
两人在天台决定公开证据。
"""
    data = convert_novel_to_screenplay_yaml(text)
    assert data["metadata"]["source_chapter_count"] == 3


def test_mock_repair_loop_is_bounded() -> None:
    invalid = {
        "project": {
            "title": "x",
            "source_type": "novel",
            "language": "zh-CN",
            "adaptation_goal": "screenplay_draft",
        }
    }
    with pytest.raises(ScreenplayValidationError, match="after 2 repair attempts"):
        repair_and_validate_screenplay_data(invalid, MockLLMAdapter(), max_attempts=2)


def test_pipeline_logs_do_not_leak_api_key(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("LLM_API_KEY", "secret-test-key")
    caplog.set_level("INFO")
    text = """
第一章
林舟在旧书店发现手稿被替换。

第二章
许澄带他去档案室查找旧记录。

第三章
两人在天台决定公开证据。
"""
    convert_novel_to_screenplay_yaml(text)
    assert "secret-test-key" not in caplog.text
    assert "provider=mock" in caplog.text

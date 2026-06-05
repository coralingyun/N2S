from backend.pipeline import convert_novel_to_screenplay_yaml
from backend.yaml_validator import validate_screenplay_data


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

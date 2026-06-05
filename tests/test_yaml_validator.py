from backend.pipeline import convert_novel_to_screenplay_yaml
from backend.yaml_validator import dump_screenplay_yaml, validate_screenplay_yaml


def test_generated_yaml_can_be_validated() -> None:
    text = """
第一章
林舟在旧书店发现手稿缺页，心中开始不安。

第二章
许澄带他进入档案室，两人找到被涂改的登记表。

第三章
雨夜天台上，他们决定公开秘密。
"""
    data = convert_novel_to_screenplay_yaml(text)
    yaml_text = dump_screenplay_yaml(data)
    validated = validate_screenplay_yaml(yaml_text)
    assert validated.project.source_type == "novel"
    assert len(validated.scenes) == 3

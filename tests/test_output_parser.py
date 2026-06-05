import pytest

from backend.output_parser import OutputParseError, parse_json_output, parse_yaml_output


def test_parse_yaml_code_block() -> None:
    parsed = parse_yaml_output(
        """
模型输出如下：
```yaml
project:
  title: 手稿之夜
```
"""
    )
    assert parsed["project"]["title"] == "手稿之夜"


def test_parse_json_code_block() -> None:
    parsed = parse_json_output(
        """
```json
{"chapter_id": "chapter_001", "locations": ["旧书店"]}
```
"""
    )
    assert parsed["chapter_id"] == "chapter_001"


def test_parse_failure_keeps_raw_output() -> None:
    raw = "```json\n{not valid json}\n```"
    with pytest.raises(OutputParseError) as exc_info:
        parse_json_output(raw)
    assert exc_info.value.raw_output == raw

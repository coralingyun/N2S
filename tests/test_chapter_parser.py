import pytest

from backend.chapter_parser import ChapterParseError, parse_chapters


def test_parse_chapters_supports_common_headings() -> None:
    text = """
第一章
旧书店里，林舟发现手稿少了一页。

第1章
许澄在档案室找到被改动的登记表。

Chapter 1
雨夜里，两人决定公开线索。
"""
    chapters = parse_chapters(text)
    assert len(chapters) == 3
    assert chapters[0].title == "第一章"
    assert chapters[1].title == "第1章"
    assert chapters[2].title == "Chapter 1"


def test_parse_chapters_rejects_less_than_three_chapters() -> None:
    text = """
第一章
只有第一章。

第二章
只有第二章。
"""
    with pytest.raises(ChapterParseError, match="At least 3 chapters"):
        parse_chapters(text)

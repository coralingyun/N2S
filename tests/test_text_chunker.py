from backend.chapter_parser import Chapter
from backend.text_chunker import chunk_chapter


def test_long_chapter_is_chunked_by_paragraph() -> None:
    chapter = Chapter(
        id="chapter_001",
        title="第一章",
        content="\n\n".join(["第一段内容很长。" * 20, "第二段内容也很长。" * 20, "第三段内容继续推进。" * 20]),
        order=1,
    )
    chunks = chunk_chapter(chapter, max_chars=180)
    assert len(chunks) >= 2
    assert all(chunk.chapter_id == "chapter_001" for chunk in chunks)
    assert all(chunk.chunk_id.startswith("chapter_001_chunk_") for chunk in chunks)
    assert all("\n\n" not in chunk.text.strip("\n").split("\n\n")[0] for chunk in chunks)

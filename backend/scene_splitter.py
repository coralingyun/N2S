"""Deterministic scene splitter for the MVP pipeline."""

from __future__ import annotations

from .chapter_parser import Chapter


def split_chapter_into_scenes(chapter: Chapter, analysis: dict) -> list[dict]:
    """Create one concise scene per chapter for the MVP."""
    location = analysis["locations"][0] if analysis.get("locations") else ""
    conflict = analysis["conflicts"][0] if analysis.get("conflicts") else ""
    return [
        {
            "scene_id": f"scene_{chapter.order:03d}",
            "source_chapter": chapter.id,
            "scene_heading": {
                "location": location,
                "time": "night" if chapter.order in {1, 3} else "afternoon",
                "interior_exterior": "EXT" if chapter.order == 3 else "INT",
            },
            "purpose": f"将{chapter.title}的核心事件转化为可表演的剧本场景。",
            "conflict": conflict,
            "characters_present": ["char_001", "char_002"],
            "emotional_arc": analysis.get("emotional_shift", {"start": "", "end": ""}),
            "beats": [
                {
                    "beat_id": f"beat_{chapter.order:03d}_001",
                    "type": "action",
                    "content": _first_sentence(chapter.content),
                },
                {
                    "beat_id": f"beat_{chapter.order:03d}_002",
                    "type": "dialogue",
                    "character": "char_001",
                    "content": "这不是我留下的那一页。",
                },
                {
                    "beat_id": f"beat_{chapter.order:03d}_003",
                    "type": "narration",
                    "content": "沉默让线索显得更加明确，也更加危险。",
                },
            ],
        }
    ]


def _first_sentence(text: str) -> str:
    compact = " ".join(part.strip() for part in text.splitlines() if part.strip())
    for marker in ("。", "！", "？", ".", "!", "?"):
        if marker in compact:
            return compact.split(marker, 1)[0].strip() + marker
    return compact[:120]

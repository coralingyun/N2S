"""LLM adapter layer.

The MVP uses a deterministic mock adapter. No external model API is called.
"""

from __future__ import annotations

from .chapter_parser import Chapter


class MockLLMAdapter:
    """Return stable, plausible analysis structures for local tests and demos."""

    def analyze_chapter(self, chapter: Chapter) -> dict:
        return {
            "chapter_id": chapter.id,
            "title": chapter.title,
            "summary": f"{chapter.title} introduces a focused story event for adaptation.",
            "locations": [self._location_for_order(chapter.order)],
            "characters": ["林舟", "许澄"],
            "events": [
                {
                    "order": 1,
                    "summary": f"Key conflict escalates in {chapter.title}.",
                }
            ],
            "conflicts": [self._conflict_for_order(chapter.order)],
            "emotional_shift": {
                "start": self._emotion_for_order(chapter.order, start=True),
                "end": self._emotion_for_order(chapter.order, start=False),
            },
            "unresolved_issues": [],
        }

    def extract_characters(self, chapter_analyses: list[dict]) -> list[dict]:
        return [
            {
                "id": "char_001",
                "name": "林舟",
                "role": "protagonist",
                "description": "A young writer trying to protect an unfinished manuscript.",
                "motivation": "Recover the missing pages and understand who altered them.",
                "relationship_to_others": [
                    {
                        "character_id": "char_002",
                        "type": "ally_with_tension",
                        "description": "林舟 trusts 许澄 but questions how much she knows.",
                    }
                ],
            },
            {
                "id": "char_002",
                "name": "许澄",
                "role": "supporting",
                "description": "An editor who helps trace the manuscript's origin.",
                "motivation": "Find the truth behind the anonymous annotations.",
                "relationship_to_others": [
                    {
                        "character_id": "char_001",
                        "type": "ally_with_tension",
                        "description": "许澄 supports 林舟 while withholding one relevant detail.",
                    }
                ],
            },
        ]

    def build_story(self, chapter_analyses: list[dict]) -> dict:
        tone = "suspenseful"
        return {
            "logline": "A young writer and an editor investigate altered manuscript pages before the story is taken from them.",
            "synopsis": "Across three chapters, the protagonist discovers missing pages, follows clues through a library archive, and confronts the immediate cost of preserving the manuscript.",
            "themes": ["authorship", "memory", "trust"],
            "tone": tone,
            "narrative_perspective": "third_person_limited",
        }

    def _location_for_order(self, order: int) -> str:
        locations = {
            1: "旧书店",
            2: "市图书馆档案室",
            3: "雨夜天台",
        }
        return locations.get(order, "未知地点")

    def _conflict_for_order(self, order: int) -> str:
        conflicts = {
            1: "林舟发现手稿被替换，但无法证明是谁动过它。",
            2: "档案线索指向许澄曾隐瞒的旧记录。",
            3: "两人必须决定是否公开手稿中的秘密。",
        }
        return conflicts.get(order, "章节冲突尚需人工确认。")

    def _emotion_for_order(self, order: int, start: bool) -> str:
        shifts = {
            1: ("calm", "uneasy"),
            2: ("doubtful", "tense"),
            3: ("fearful", "resolved"),
        }
        return shifts.get(order, ("uncertain", "uncertain"))[0 if start else 1]

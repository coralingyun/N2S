"""LLM adapter layer with mock and OpenAI-compatible implementations."""

from __future__ import annotations

import json
import os
from typing import Protocol
from urllib import error, request

from .chapter_parser import Chapter
from .output_parser import OutputParseError, parse_json_output, parse_mapping_output
from .prompts import (
    CHAPTER_ANALYSIS_PROMPT,
    CHARACTER_EXTRACTION_PROMPT,
    SCHEMA_SUMMARY,
    SCENE_SPLIT_PROMPT,
    SCREENPLAY_YAML_PROMPT,
    YAML_REPAIR_PROMPT,
)
from .scene_splitter import split_chapter_into_scenes
from .screenplay_generator import generate_screenplay_from_parts


class LLMConfigurationError(RuntimeError):
    """Raised when a requested real LLM provider is not configured."""


class LLMRequestError(RuntimeError):
    """Raised when a real LLM request fails."""


class LLMAdapter(Protocol):
    def analyze_chapter(self, chapter: Chapter) -> dict:
        ...

    def extract_characters(self, chapter_analyses: list[dict]) -> list[dict]:
        ...

    def build_story(self, chapter_analyses: list[dict]) -> dict:
        ...

    def split_scenes(self, chapter: Chapter, chapter_analysis: dict, characters: list[dict]) -> list[dict]:
        ...

    def generate_screenplay(
        self,
        chapters: list[Chapter],
        chapter_analyses: list[dict],
        characters: list[dict],
        scenes: list[dict],
    ) -> dict:
        ...

    def repair_yaml(self, yaml_text: str, validation_errors: list[dict]) -> str:
        ...


class MockLLMAdapter:
    """Return stable, plausible analysis structures for local tests and demos."""

    def analyze_chapter(self, chapter: Chapter) -> dict:
        return {
            "chapter_id": chapter.id,
            "title": chapter.title,
            "summary": f"{chapter.title}围绕手稿异常与人物追查推进主要情节。",
            "locations": [self._location_for_order(chapter.order)],
            "characters": ["林舟", "许澄"],
            "events": [
                {
                    "order": 1,
                    "summary": f"{chapter.title}中的关键冲突进一步升级。",
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
                "description": "年轻作者，试图保护被篡改的未完成手稿。",
                "motivation": "找回缺失页面，并查清是谁改动了手稿。",
                "relationship_to_others": [
                    {
                        "character_id": "char_002",
                        "type": "ally_with_tension",
                        "description": "林舟信任许澄，但怀疑她隐瞒了与手稿有关的信息。",
                    }
                ],
            },
            {
                "id": "char_002",
                "name": "许澄",
                "role": "supporting",
                "description": "编辑，协助林舟追查手稿来源，同时背负旧事。",
                "motivation": "查明匿名改写背后的真相，并弥补过去的隐瞒。",
                "relationship_to_others": [
                    {
                        "character_id": "char_001",
                        "type": "ally_with_tension",
                        "description": "许澄帮助林舟调查，但起初没有说出全部线索。",
                    }
                ],
            },
        ]

    def build_story(self, chapter_analyses: list[dict]) -> dict:
        tone = "悬疑、克制、紧张"
        return {
            "logline": "年轻作者与编辑追查被篡改的手稿，在旧档案和隐瞒中重新夺回故事的解释权。",
            "synopsis": "林舟发现手稿结尾被人改写，许澄在追查过程中暴露出与旧手稿有关的隐瞒。两人从旧书店追到图书馆档案室，最终在雨夜天台决定公开证据。",
            "themes": ["创作权", "记忆", "信任"],
            "tone": tone,
            "narrative_perspective": "第三人称有限视角",
        }

    def split_scenes(self, chapter: Chapter, chapter_analysis: dict, characters: list[dict]) -> list[dict]:
        return split_chapter_into_scenes(chapter, chapter_analysis)

    def generate_screenplay(
        self,
        chapters: list[Chapter],
        chapter_analyses: list[dict],
        characters: list[dict],
        scenes: list[dict],
    ) -> dict:
        return generate_screenplay_from_parts(
            chapters=chapters,
            chapter_analyses=chapter_analyses,
            story=self.build_story(chapter_analyses),
            characters=characters,
            scenes=scenes,
            adaptation_note="当前 YAML 由 mock LLM 适配器生成，用于本地演示和测试。",
        )

    def repair_yaml(self, yaml_text: str, validation_errors: list[dict]) -> str:
        """Return input unchanged; validation loop remains bounded by caller."""
        return yaml_text

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


class OpenAICompatibleLLMAdapter:
    """Minimal adapter for OpenAI-compatible chat completion APIs."""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        timeout_seconds: int = 60,
    ) -> None:
        if not api_key:
            raise LLMConfigurationError("LLM_API_KEY is required when LLM_PROVIDER=openai.")
        if not model:
            raise LLMConfigurationError("LLM_MODEL is required when LLM_PROVIDER=openai.")

        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def analyze_chapter(self, chapter: Chapter) -> dict:
        prompt = CHAPTER_ANALYSIS_PROMPT.format(
            chapter_id=chapter.id,
            chapter_title=chapter.title,
            chapter_text=chapter.content,
        )
        return self._chat_json(prompt)

    def extract_characters(self, chapter_analyses: list[dict]) -> list[dict]:
        prompt = CHARACTER_EXTRACTION_PROMPT.format(
            chapter_analyses=json.dumps(chapter_analyses, ensure_ascii=False)
        )
        result = self._chat_json(prompt)
        characters = result.get("characters", result.get("items", []))
        if not isinstance(characters, list):
            raise LLMRequestError("Character extraction response must contain a characters list.")
        return characters

    def build_story(self, chapter_analyses: list[dict]) -> dict:
        prompt = (
            "你是剧本改编助手。请根据章节分析生成 story 对象，只输出 JSON，不要解释。\n"
            "JSON 字段必须为 logline, synopsis, themes, tone, narrative_perspective。\n"
            f"章节分析：{json.dumps(chapter_analyses, ensure_ascii=False)}"
        )
        return self._chat_json(prompt)

    def split_scenes(self, chapter: Chapter, chapter_analysis: dict, characters: list[dict]) -> list[dict]:
        prompt = SCENE_SPLIT_PROMPT.format(
            chapter_id=chapter.id,
            chapter_text=chapter.content,
            characters=json.dumps(characters, ensure_ascii=False),
            chapter_analysis=json.dumps(chapter_analysis, ensure_ascii=False),
        )
        result = self._chat_json(prompt)
        scenes = result.get("scenes", result.get("items", []))
        if not isinstance(scenes, list):
            raise LLMRequestError("Scene split response must contain a scenes list.")
        return scenes

    def generate_screenplay(
        self,
        chapters: list[Chapter],
        chapter_analyses: list[dict],
        characters: list[dict],
        scenes: list[dict],
    ) -> dict:
        prompt = SCREENPLAY_YAML_PROMPT.format(
            schema_summary=SCHEMA_SUMMARY,
            source_chapter_count=len(chapters),
            chapter_analyses=json.dumps(chapter_analyses, ensure_ascii=False),
            characters=json.dumps(characters, ensure_ascii=False),
            scenes=json.dumps(scenes, ensure_ascii=False),
        )
        return self._chat_yaml_mapping(prompt)

    def repair_yaml(self, yaml_text: str, validation_errors: list[dict]) -> str:
        prompt = YAML_REPAIR_PROMPT.format(
            yaml_text=yaml_text,
            validation_errors=json.dumps(validation_errors, ensure_ascii=False),
            schema_summary=SCHEMA_SUMMARY,
        )
        return self._chat_text(prompt)

    def _chat_json(self, prompt: str) -> dict:
        text = self._chat_text(prompt)
        try:
            parsed = parse_json_output(text)
        except OutputParseError as exc:
            raise LLMRequestError(str(exc)) from exc
        if isinstance(parsed, dict):
            return parsed
        if isinstance(parsed, list):
            return {"items": parsed}
        raise LLMRequestError("LLM response must be a JSON object or array.")

    def _chat_yaml_mapping(self, prompt: str) -> dict:
        text = self._chat_text(prompt)
        try:
            return parse_mapping_output(text, format_hint="yaml")
        except OutputParseError as exc:
            raise LLMRequestError(str(exc)) from exc

    def _chat_text(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是严谨的小说转剧本结构化处理助手。"},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                response_body = response.read().decode("utf-8")
        except error.URLError as exc:
            raise LLMRequestError(f"LLM request failed: {exc}") from exc

        data = json.loads(response_body)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMRequestError("LLM response does not match chat completions format.") from exc


def get_llm_adapter() -> LLMAdapter:
    """Create an adapter from environment variables."""
    provider = os.getenv("LLM_PROVIDER", "mock").strip().lower()
    if provider in {"", "mock"}:
        return MockLLMAdapter()
    if provider in {"openai", "real"}:
        return OpenAICompatibleLLMAdapter(
            api_key=os.getenv("LLM_API_KEY", ""),
            base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
            model=os.getenv("LLM_MODEL", ""),
        )
    raise LLMConfigurationError(f"Unsupported LLM_PROVIDER: {provider}")

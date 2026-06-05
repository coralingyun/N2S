"""Prompt templates for real LLM integration."""

CHAPTER_ANALYSIS_PROMPT = """\
你是小说结构分析助手。请只根据输入章节进行分析，不要补充原文没有支持的情节。

输入：
- 章节 ID：{chapter_id}
- 章节标题：{chapter_title}
- 章节正文：
{chapter_text}

任务：
1. 提取本章出现的地点。
2. 提取本章出现的人物及其行动。
3. 概括本章主要事件，按发生顺序排列。
4. 识别本章主要冲突。
5. 描述本章情绪变化，包括 start 和 end。
6. 对不确定内容写入 unresolved_issues，不要伪造事实。

只输出 JSON，不要输出解释文字。JSON 字段必须为：
chapter_id, title, summary, locations, characters, events, conflicts, emotional_shift, unresolved_issues。
"""

CHARACTER_EXTRACTION_PROMPT = """\
你是剧本改编的人物分析助手。请根据全部章节摘要统一人物信息。

输入章节分析 JSON：
{chapter_analyses}

任务：
1. 合并同一人物的不同称谓、昵称或代称。
2. 为每个主要人物分配稳定 ID，例如 char_001。
3. 提取人物 role、description、motivation 和 relationship_to_others。
4. relationship_to_others 中使用 character_id, type, description。
5. 对不确定内容写入 unresolved_issues，不要伪造事实。

只输出 JSON，不要输出解释文字。JSON 根字段必须包含 characters。
"""

SCENE_SPLIT_PROMPT = """\
你是剧本场景拆分助手。请将输入章节拆分为适合剧本改编的场景。

输入：
- 章节 ID：{chapter_id}
- 章节正文：
{chapter_text}
- 已知人物表：
{characters}
- 章节分析：
{chapter_analysis}

拆分原则：
1. 地点变化、时间变化、人物组合变化、事件目标变化或冲突变化通常意味着新场景。
2. 不要改变原文事件顺序。
3. 每个场景必须保留 source_chapter。
4. 如果无法确定地点或时间，使用空字符串或 unresolved_issues 说明。

只输出 JSON，不要输出解释文字。JSON 根字段必须包含 scenes。
"""

SCREENPLAY_YAML_PROMPT = """\
你是剧本 YAML 生成助手。请将章节分析、人物表和场景拆分结果合并为完整 screenplay YAML。

Schema 摘要：
{schema_summary}

来源章节数量：
{source_chapter_count}

章节分析：
{chapter_analyses}

人物表：
{characters}

场景拆分结果：
{scenes}

要求：
1. 只输出 YAML，不输出解释文字。
2. 输出必须包含顶层字段 project, metadata, story, characters, structure, scenes, transitions, notes。
3. metadata.source_chapter_count 必须等于来源章节数量。
4. 保持 scene_id 和 character id 稳定。
5. 每个场景至少包含一个 beat。
6. beat.type 只能使用 action、dialogue、narration、camera、transition。
7. dialogue 类型 beat 必须包含 character 字段。
8. 不要新增输入中没有依据的剧情。
"""

YAML_REPAIR_PROMPT = """\
你是 YAML Schema 修复助手。请修复输入 YAML，使其符合给定 Schema。

原始 YAML：
{yaml_text}

Schema 错误列表：
{validation_errors}

Schema 摘要：
{schema_summary}

要求：
1. 只修复格式、字段名、字段类型、缺失必填字段和引用一致性问题。
2. 不改变剧情含义、人物关系、场景顺序或对白内容。
3. 对无法从原 YAML 推断的缺失字段，使用空字符串、空数组或 notes.unresolved_issues。
4. beat.type 只能是 action、dialogue、narration、camera、transition。
5. dialogue 类型 beat 必须包含 character 字段。
6. 只输出修复后的 YAML，不输出解释文字。
"""

SCHEMA_SUMMARY = """\
顶层字段：project, metadata, story, characters, structure, scenes, transitions, notes。
metadata.source_chapter_count >= 3。
characters 至少 1 个，每个角色必须有 id, name, role, description, motivation。
scenes 至少 1 个。每个 scene 必须有 scene_id, source_chapter, scene_heading, purpose, conflict, characters_present, emotional_arc, beats。
scene_heading 必须包含 location, time, interior_exterior；interior_exterior 只能是 INT 或 EXT。
characters_present 至少 1 个。
beats 至少 1 个。beat.type 只能是 action, dialogue, narration, camera, transition。
dialogue beat 必须包含 character。
"""

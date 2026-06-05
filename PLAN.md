# AI 小说转剧本工具开发计划

## 1. 产品目标

本项目旨在开发一款面向小说作者和剧本创作者的 AI 辅助剧本创作工具。系统目标不是对小说文本进行简单摘要，而是完成“小说文本 -> 剧本结构化初稿”的转换：用户输入不少于 3 个章节的小说文本后，系统自动识别章节、场景、人物、动作、对白、旁白、情绪变化和冲突推进，并输出可编辑、可校验、可进一步打磨的 YAML 剧本草稿。

该工具应保留原小说的主要叙事信息，同时将其重组为适合剧本创作的结构化表达。输出结果应服务于后续人工编辑，而不是直接替代编剧创作。因此，系统设计需要强调可追溯性、可修改性、字段语义清晰性和格式稳定性。

核心产品目标包括：

- 将多章节小说文本转换为结构化剧本初稿。
- 自动分析故事结构、人物关系、场景推进和戏剧冲突。
- 以 YAML 格式输出可编辑的剧本草稿。
- 提供 Schema 文档，明确 YAML 字段、层级、类型、示例和设计理由。
- 支持用户查看、修改并导出剧本草稿，便于后续编剧工作流接入。

## 2. 用户与使用场景

目标用户包括：

- 希望将小说改编为短剧、影视剧、广播剧或互动剧本的小说作者。
- 需要快速整理小说结构和场景草稿的编剧。
- 需要将长篇文本转化为结构化创作素材的内容工作者。

典型流程如下：

1. 用户粘贴不少于 3 个章节的小说文本。
2. 系统识别章节标题并检查输入完整性。
3. 系统对小说进行预处理、结构分析和场景拆分。
4. 系统生成符合 YAML Schema 的剧本初稿。
5. 用户在编辑界面检查和修改 YAML。
6. 用户导出 `.yaml`、`.md` 或 `.txt` 文件。

## 3. 核心功能模块

### 3.1 输入模块

输入模块负责接收用户粘贴的小说文本，并完成基础输入检查。

功能要求：

- 支持用户粘贴长篇小说文本。
- 要求输入文本至少包含 3 个章节。
- 自动识别章节标题，例如“第 1 章”“第一章”“Chapter 1”“1.”等常见形式。
- 显示识别到的章节数量和章节标题列表。
- 如果章节数量不足 3 个，需要阻止继续转换，并给出明确提示。
- 保留原始输入文本，用于后续追溯和重新分析。

关键校验：

- 输入文本不能为空。
- 有效章节数不得少于 3。
- 每个章节需要包含正文内容，不能仅有标题。
- 对异常格式章节给出可读提示，而不是静默失败。

### 3.2 文本预处理模块

文本预处理模块负责将原始小说文本转换为适合 AI 分析的规范化文本片段。

功能要求：

- 清洗连续空行、首尾空白和异常控制字符。
- 统一常见中英文标点，降低解析歧义。
- 按段落切分文本，保留段落顺序。
- 根据章节标题切分章节。
- 对长章节进行语义尽量连续的文本切块，避免超过模型上下文限制。
- 为每个文本块记录来源章节、段落范围和字符范围。

设计原则：

- 不改变原文叙事顺序。
- 不主动改写小说内容。
- 预处理结果应可追溯到原始章节和段落。
- 长文本切块应优先按段落边界进行，避免截断对白或关键动作描写。

### 3.3 小说结构分析模块

小说结构分析模块负责从整体层面理解小说内容，并生成后续剧本转换所需的全局信息。

功能要求：

- 提取或推断故事标题。
- 生成章节列表，包括章节标题、摘要、主要事件和情绪变化。
- 提取主要人物，包括姓名、身份、性格特征、目标、人物弧光和首次出现章节。
- 分析人物关系，包括亲属、同盟、对立、情感、师徒、利益关系等。
- 识别核心冲突，包括外部冲突、内部冲突和关系冲突。
- 梳理故事时间线，包括明确时间、相对时间和事件顺序。
- 提取主要地点和地点功能。
- 识别叙事视角，例如第一人称、第三人称有限视角、第三人称全知视角等。
- 分析整体情绪基调，例如悬疑、压抑、轻松、悲剧、热血等。

输出要求：

- 结构分析结果应作为 YAML 剧本输出的元信息。
- 对不确定内容应使用 `null`、空数组或 `notes` 字段记录，而不是编造事实。
- 需要区分原文明确给出的事实和模型推断结果。

### 3.4 场景拆分模块

场景拆分模块负责将每个小说章节转换为若干剧本场景。

功能要求：

- 按地点、时间、人物组合、事件目标和戏剧冲突变化拆分场景。
- 为每个场景识别场景地点、时间、出场人物和场景目标。
- 提取或改写为剧本动作描述。
- 提取原文对白，并在必要时转换为剧本对白格式。
- 标注旁白、内心独白或叙述性信息。
- 识别场景内的戏剧冲突、情绪起点、情绪转折和情绪终点。
- 记录场景在原章节中的来源范围，便于人工回查。

场景字段应覆盖：

- 稳定场景编号 `scene_id`。
- 来源章节 `source_chapter`。
- 场景标题。
- 场景标题信息 `scene_heading`，包括地点、时间和内外景。
- 出场人物 `characters_present`。
- 场景目的 `purpose`。
- 冲突描述。
- 情绪变化。
- 场景内部节拍 `beats`，包括动作、对白、旁白和说明。
- 改编备注和未解决问题。

### 3.5 YAML 输出模块

YAML 输出模块负责根据项目定义的 YAML Schema 生成结构化剧本初稿，并执行格式校验。

功能要求：

- 按固定 Schema 输出 YAML。
- 支持 `project`、`metadata`、`story`、`characters`、`structure`、`scenes`、`transitions` 和 `notes` 等顶层字段。
- 对必要字段进行存在性校验。
- 对字段类型进行校验，例如字符串、数组、对象、枚举值。
- 对场景编号、人物引用、来源章节和场景转场引用进行一致性检查。
- 校验失败时返回可读错误信息，指出字段路径和错误原因。

输出原则：

- YAML 应适合人工阅读和编辑。
- 字段命名应稳定、清晰、可扩展。
- 不确定内容不得被包装为确定事实。
- 对模型生成内容应保留 `confidence` 或 `notes` 等辅助字段，便于后续审阅。

### 3.6 编辑与导出模块

编辑与导出模块负责提供用户查看、修改和保存剧本初稿的能力。

功能要求：

- 提供 YAML 查看与编辑界面。
- 支持基础语法高亮和缩进辅助。
- 支持 YAML 格式校验。
- 支持将 YAML 导出为 `.yaml` 文件。
- 支持将剧本内容导出为 `.md` 文件，便于阅读和审阅。
- 支持将剧本内容导出为 `.txt` 文件，便于简单文本流转。
- 编辑后可重新校验 Schema。

设计原则：

- 编辑器不应隐藏 YAML 的真实结构。
- 导出结果应与当前编辑内容一致。
- 校验错误应定位到具体字段，避免只显示笼统失败信息。

### 3.7 Schema 文档模块

Schema 文档模块负责生成 `docs/yaml_schema.md`，系统性说明剧本 YAML Schema 的字段、层级、类型、示例和设计理由。

文档内容要求：

- Schema 总体设计目标。
- 顶层字段说明。
- 人物、关系、章节、场景、对白、动作、旁白、情绪变化等字段定义。
- 每个字段的类型、是否必填、允许值和示例。
- 完整 YAML 示例。
- 字段设计理由。
- Schema 扩展策略，例如后续支持分集剧本、镜头语言、分镜、角色弧光版本管理等。

该文档是项目的必要交付物，应与实际 YAML 输出保持一致。

## 4. 初版 YAML Schema 草案

初版 YAML 结构先在 `PLAN.md` 中确定顶层层级、核心字段和字段意图。后续应在 `docs/yaml_schema.md` 中进一步展开字段类型、必填规则、枚举值、示例和设计原因。

```yaml
project:
  title: ""
  source_type: "novel"
  language: "zh-CN"
  adaptation_goal: "screenplay_draft"

metadata:
  author: ""
  created_at: ""
  version: "0.1"
  source_chapter_count: 3

story:
  logline: ""
  synopsis: ""
  themes: []
  tone: ""
  narrative_perspective: ""

characters:
  - id: "char_001"
    name: ""
    role: "protagonist"
    description: ""
    motivation: ""
    relationship_to_others: []

structure:
  acts:
    - act_id: "act_1"
      title: ""
      function: "setup"
      chapters_covered: []

scenes:
  - scene_id: "scene_001"
    source_chapter: ""
    scene_heading:
      location: ""
      time: ""
      interior_exterior: "INT"
    purpose: ""
    conflict: ""
    characters_present: []
    emotional_arc:
      start: ""
      end: ""
    beats:
      - beat_id: "beat_001"
        type: "action"
        content: ""
      - beat_id: "beat_002"
        type: "dialogue"
        character: ""
        content: ""
      - beat_id: "beat_003"
        type: "narration"
        content: ""

transitions:
  - from_scene: "scene_001"
    to_scene: "scene_002"
    type: "cut"

notes:
  adaptation_notes: []
  unresolved_issues: []
```

### 4.1 Schema 层级设计原因

`project` 用于定义项目基本属性，包括标题、来源类型、语言和改编目标。该层级使同一套 Schema 可以支持后续不同来源文本或不同剧本目标，而不需要修改核心场景结构。

`metadata` 用于追踪作者、创建时间、版本和来源章节数量。这些字段服务于版本管理、复现实验和输入完整性检查，尤其是在同一小说多次生成或多轮修订时需要保留明确记录。

`story` 用于保存整体故事理解，包括一句话梗概、总体摘要、主题、基调和叙事视角。该层级可以避免输出结果只剩离散场景，使编剧在修改场景时仍能参考整体叙事目标。

`characters` 用于统一人物 ID、姓名、角色功能、描述、动机和关系信息。剧本生成和场景引用应优先使用稳定 ID，避免同一人物因姓名、称谓、昵称或模型输出差异而产生混乱。

`structure` 用于保存三幕式或多幕式结构。该层级不强制所有作品都套用固定结构，而是为后续改编、节奏调整、分集拆分和结构重排提供可编辑依据。

`scenes` 是核心层级，因为剧本本质上由场景组成。每个场景必须记录来源章节、场景标题、地点、时间、出场人物、目的、冲突、情绪弧和内部节拍，便于人工审阅和继续改写。

`beats` 用于表达场景内部的动作、对白、旁白和镜头节奏。相比把动作和对白分散到多个平行数组，统一 beat 列表更接近剧本推进顺序，也更便于后续插入、删除和重排。

`transitions` 用于表达场景之间的连接方式，例如 `cut`、`fade`、`match_cut` 或 `montage`。MVP 阶段可以只保留基础类型，后续再扩展为更细的镜头语言或剪辑语义。

`notes` 用于保存 AI 无法确定、需要作者进一步打磨的问题，包括改编说明、未解决问题、事实不确定项和建议人工复核内容。该层级明确区分确定输出与待审阅内容，降低模型编造被误认为事实的风险。

## 5. 推荐技术架构

主方案采用 `Next.js + React + TypeScript` 前端和 `Python FastAPI` 后端。AI 调用层独立封装在 `llm_adapter.py`，YAML 处理使用 `PyYAML`，Schema 校验优先使用 `Pydantic`，测试使用 `pytest`，文档使用 Markdown。

选择该方案的原因是：Next.js 适合构建小说输入、生成进度、YAML 编辑、Schema 校验和导出的一体化演示界面；FastAPI 适合承载文本预处理、分阶段 AI 编排、Schema 校验和导出转换。Streamlit 可用于内部快速验证，但不作为主 MVP，因为本项目需要更明确的前后端边界、可编辑 YAML 体验和后续扩展能力。

前端核心页面包括小说输入页、章节识别与预处理预览页、分析进度页、YAML 剧本编辑页和 Schema 文档查看页。YAML 编辑器建议使用 Monaco Editor 或 CodeMirror，导出功能使用浏览器 Blob API 实现。

后端核心模块包括 `chapter_parser`、`preprocessing`、`pipeline`、`scene_splitter`、`screenplay_generator`、`yaml_validator`、`llm_adapter` 和 `schemas`。后端不应直接依赖前端状态，所有可复现中间结果应通过结构化对象传递。

## 6. 系统架构与数据流

文字版系统架构如下：

```text
用户输入小说文本
  -> 文本预处理
  -> 章节识别
  -> 小说结构分析
  -> 场景拆分
  -> 剧本生成
  -> YAML Schema 校验
  -> 可编辑 YAML 输出
  -> 导出文件
```

各层输入、输出和职责如下：

| 层级 | 输入 | 输出 | 职责 |
| --- | --- | --- | --- |
| 用户输入小说文本 | 用户粘贴的原始小说文本 | 原始文本字符串 | 接收不少于 3 个章节的小说文本，并保留原始输入用于追溯。 |
| 文本预处理 | 原始文本字符串 | 规范化文本、段落列表、清洗日志 | 清理空白、异常控制字符和明显格式噪声，按段落保留原始顺序，不改写叙事内容。 |
| 章节识别 | 规范化文本和段落列表 | 章节对象列表 | 识别章节标题、章节正文、段落范围和字符范围；校验章节数量不少于 3。 |
| 小说结构分析 | 章节对象列表 | 故事摘要、人物候选、地点、冲突、情绪变化和章节摘要 | 从整体层面建立故事理解，为人物统一、结构设计和场景拆分提供依据。 |
| 场景拆分 | 章节内容、章节摘要、人物和地点信息 | 场景候选列表 | 按地点、时间、人物组合、事件目标和冲突变化拆分场景，并记录来源章节。 |
| 剧本生成 | 场景候选、人物表、故事结构 | 符合目标 Schema 的剧本结构对象 | 将场景转换为剧本字段，生成场景标题、目的、冲突、情绪弧、beats 和 transitions。 |
| YAML Schema 校验 | 剧本结构对象或 YAML 字符串 | 校验结果、错误路径、警告列表 | 校验 YAML 可解析性、字段完整性、类型正确性和引用一致性。 |
| 可编辑 YAML 输出 | 合法 YAML 和校验结果 | 前端编辑器中的 YAML 文本 | 向用户展示可修改的 YAML 初稿，并支持编辑后再次校验。 |
| 导出文件 | 当前编辑器 YAML 文本 | `.yaml`、`.md` 或 `.txt` 文件 | 将当前编辑内容导出为稳定编码的文件，保证导出内容与编辑区一致。 |

关键中间数据应尽量结构化保存，避免仅依赖不可追踪的自然语言中间结果。

## 7. AI Prompt 设计方案

AI 调用应采用分阶段 prompt，而不是一次性要求模型输出完整剧本。每个 prompt 都应要求模型区分原文明确事实、合理推断和不确定项，并避免编造未由输入支持的情节。

### 7.1 章节分析 prompt

目标：输入单章小说，输出该章的地点、人物、事件、冲突和情绪变化。

```text
你是小说结构分析助手。请只根据输入章节进行分析，不要补充原文没有支持的情节。

输入：
- 章节 ID：{chapter_id}
- 章节标题：{chapter_title}
- 章节正文：{chapter_text}

任务：
1. 提取本章出现的地点。
2. 提取本章出现的人物及其行动。
3. 概括本章主要事件，按发生顺序排列。
4. 识别本章主要冲突。
5. 描述本章情绪变化，包括起点、转折和终点。
6. 对不确定内容写入 unresolved_issues，不要伪造事实。

输出 JSON，字段包括：
chapter_id, title, locations, characters, events, conflicts, emotional_shift, unresolved_issues。
```

### 7.2 人物抽取 prompt

目标：输入全部章节摘要，输出主要人物、人物关系、动机和变化。

```text
你是剧本改编的人物分析助手。请根据全部章节摘要统一人物信息。

输入：
- 章节摘要列表：{chapter_summaries}

任务：
1. 合并同一人物的不同称谓、昵称或代称。
2. 为每个主要人物分配稳定 ID，例如 char_001。
3. 提取人物角色功能、描述、动机和变化。
4. 提取人物关系，说明关系类型和依据。
5. 标注信息是原文明确事实还是基于上下文的合理推断。

输出 JSON，字段包括：
characters, relationships, unresolved_issues。
```

### 7.3 场景拆分 prompt

目标：输入章节内容，输出若干剧本场景。

```text
你是剧本场景拆分助手。请将输入章节拆分为适合剧本改编的场景。

输入：
- 章节 ID：{chapter_id}
- 章节正文：{chapter_text}
- 已知人物表：{characters}
- 已知地点表：{locations}

拆分原则：
1. 地点变化、时间变化、人物组合变化、事件目标变化或冲突变化通常意味着新场景。
2. 不要改变原文事件顺序。
3. 每个场景必须保留来源章节和段落范围。
4. 如果无法确定地点或时间，使用空字符串或 unresolved_issues 说明。

输出 JSON，字段包括：
scenes，每个 scene 包含 scene_id, source_chapter, scene_heading, purpose, conflict, characters_present, emotional_arc, source_trace。
```

### 7.4 剧本生成 prompt

目标：输入场景信息，输出符合 YAML Schema 的剧本片段。

```text
你是剧本 YAML 生成助手。请将场景信息转换为符合给定 Schema 的 YAML 片段。

输入：
- YAML Schema 摘要：{schema_summary}
- 场景信息：{scene_data}
- 人物表：{characters}

要求：
1. 只输出 YAML，不输出解释。
2. 保持 scene_id 和 character id 稳定。
3. 每个场景至少包含一个 beat。
4. beat.type 只能使用 action、dialogue、narration 或 note。
5. 不要新增输入中没有依据的剧情。

输出：
符合 scenes 字段结构的 YAML 片段。
```

### 7.5 校验修复 prompt

目标：当 YAML 不符合 Schema 时，要求 AI 修复格式，不改变剧情含义。

```text
你是 YAML Schema 修复助手。请修复输入 YAML，使其符合给定 Schema。

输入：
- 原始 YAML：{yaml_text}
- Schema 错误列表：{validation_errors}
- Schema 摘要：{schema_summary}

要求：
1. 只修复格式、字段名、字段类型、缺失必填字段和引用一致性问题。
2. 不改变剧情含义、人物关系、场景顺序或对白内容。
3. 对无法从原 YAML 推断的缺失字段，使用空字符串、空数组或 notes/unresolved_issues。
4. 只输出修复后的 YAML，不输出解释。
```

## 8. 校验与质量控制

### 8.1 输入校验

- 输入为空时禁止提交。
- 章节数少于 3 时提示用户补充文本。
- 章节标题重复时提示用户检查。
- 章节正文过短时标记为潜在异常。

### 8.2 YAML 校验

- 校验 YAML 是否可解析。
- 校验必填字段是否存在。
- 校验字段类型是否符合 Schema。
- 校验 `scene_id`、`character id`、`source_chapter` 和 transition 引用是否一致。
- 校验场景顺序是否与章节顺序一致。
- 校验每个场景是否包含 `scene_heading`、`purpose`、`conflict`、`characters_present` 和至少一个 `beat`。

### 8.3 内容质量检查

- 检查是否存在没有出场人物的关键场景。
- 检查对白角色是否出现在该场景人物列表中。
- 检查核心人物是否缺少目标或描述。
- 检查冲突字段是否为空。
- 检查过长的 `action` beat，必要时建议拆分。

质量检查结果应以警告形式呈现，不应默认阻止导出。

## 9. 开发里程碑

### 阶段 1：项目骨架与文档

创建目录结构，生成 `README.md`、`PLAN.md`、`docs/yaml_schema.md`、`examples/sample_novel.txt` 和 `examples/sample_screenplay.yaml`。

交付物：

- 基础项目目录。
- `README.md`。
- `PLAN.md`。
- `docs/yaml_schema.md`。
- `examples/sample_novel.txt`。
- `examples/sample_screenplay.yaml`。

验证重点：

- 文档明确说明系统是“小说文本 -> 结构化剧本初稿”工具，而不是摘要器。
- 示例 YAML 与初版 Schema 字段保持一致。

### 阶段 2：核心转换管线

完成章节识别、文本预处理、AI 调用封装和 YAML 生成。

交付物：

- `backend/chapter_parser.py`。
- `backend/preprocessing.py`。
- `backend/llm_adapter.py`。
- `backend/pipeline.py`。
- `backend/screenplay_generator.py`。

验证重点：

- 不少于 3 个章节时允许进入转换流程。
- 少于 3 个章节时返回明确错误。
- 后端可以从样例小说生成初步 YAML 结构。

### 阶段 3：Schema 校验与错误修复

完成 YAML Schema 校验、缺失字段检查、错误提示和自动修复流程。

交付物：

- `backend/yaml_validator.py`。
- `backend/schemas.py`。
- 校验错误格式定义。
- 校验修复 prompt 接入点。

验证重点：

- YAML 可解析。
- 必填字段完整。
- 引用字段一致。
- 自动修复只修复格式和结构问题，不改变剧情含义。

### 阶段 4：前端或交互界面

完成输入框、生成按钮、YAML 预览、编辑区和导出按钮。

交付物：

- 前端输入页面。
- YAML 预览和编辑组件。
- Schema 校验结果展示。
- `.yaml`、`.md`、`.txt` 导出按钮。

验证重点：

- 用户可以粘贴 3 章以上小说文本并触发生成。
- 用户可以编辑 YAML 并重新校验。
- 导出文件内容与编辑区内容一致。

### 阶段 5：测试与演示样例

添加测试用例，准备一个 3 章小说样例，并生成对应 YAML 剧本样例。

交付物：

- 至少 3 个基础测试。
- 可运行 demo。
- 3 章小说样例。
- 对应 YAML 剧本样例。

验证重点：

- 章节识别测试通过。
- YAML 校验测试通过。
- 核心 pipeline 测试通过。
- Demo 可以从样例小说生成合法 YAML。

## 10. 文件结构规划

建议项目结构如下：

```text
novel-to-screenplay-ai/
  README.md
  PLAN.md
  requirements.txt
  docs/
    yaml_schema.md
    prompt_design.md
  examples/
    sample_novel.txt
    sample_screenplay.yaml
  backend/
    main.py
    pipeline.py
    preprocessing.py
    chapter_parser.py
    scene_splitter.py
    screenplay_generator.py
    yaml_validator.py
    llm_adapter.py
    schemas.py
  frontend/
    package.json
    src/
      app/
      components/
      lib/
  tests/
    test_chapter_parser.py
    test_yaml_validator.py
    test_pipeline.py
```

该结构采用前后端分离但保持 MVP 轻量。`backend/` 负责核心转换与校验，`frontend/` 负责交互体验，`docs/` 和 `examples/` 保证 Schema 与演示样例可复核，`tests/` 覆盖最小可验证行为。

## 11. 测试计划

建议测试覆盖：

- 章节识别单元测试。
- 文本清洗与分段测试。
- 长文本切块边界测试。
- YAML Schema 校验测试。
- 人物、场景和 transition 引用一致性测试。
- 导出格式测试。
- 少于 3 个章节的输入提示测试。
- 异常 YAML 的错误提示测试。

测试样例应包含：

- 标准中文章节标题。
- 阿拉伯数字章节标题。
- 英文章节标题。
- 章节标题缺失或重复的异常文本。
- 包含大量对白的小说片段。
- 包含多地点切换的章节。

MVP 阶段至少需要包含以下 3 个基础测试：

- `tests/test_chapter_parser.py`：验证不少于 3 章的识别与少于 3 章的错误提示。
- `tests/test_yaml_validator.py`：验证样例 YAML 能通过 Schema 校验，异常 YAML 能返回字段路径。
- `tests/test_pipeline.py`：验证样例小说经过核心 pipeline 后包含 `project`、`story`、`characters`、`scenes` 和 `beats`。

## 12. 主要风险与应对

### 12.1 长文本上下文丢失

风险：一次性处理长篇小说可能导致章节信息缺失或人物关系混乱。

应对：采用章节级和全局级分阶段分析，并保留来源追踪。

### 12.2 YAML 格式错误

风险：AI 直接生成 YAML 时可能出现缩进、转义或类型错误。

应对：使用结构化中间对象生成 YAML，并在输出前执行 Schema 校验。

### 12.3 人物命名不一致

风险：同一人物可能以姓名、昵称、称谓等多种方式出现。

应对：建立人物规范名和别名字段，并在场景生成时统一引用稳定人物 ID。

### 12.4 改编过度或事实编造

风险：模型可能生成原文未支持的情节或人物动机。

应对：要求关键分析字段记录依据；对推断内容使用 `notes` 或置信度标记；不确定内容不得伪装为原文事实。

### 12.5 Schema 与实际输出不一致

风险：文档定义和代码输出逐渐偏离。

应对：将 Schema 文档、JSON Schema 和示例输出纳入测试，后续变更时同步更新。

## 13. GitHub 工作流要求

当前工作区需要绑定到对应 GitHub 代码仓库后，才能执行拉取、提交和推送。推荐工作流如下：

1. 确认远端仓库地址。
2. 克隆或初始化本地 Git 仓库。
3. 在开始开发前执行 `git pull` 或等价同步操作。
4. 在独立分支上进行文档和代码变更。
5. 提交前运行相关测试或校验命令。
6. 提交信息应清晰说明变更范围。
7. 将变更推送到对应 GitHub 仓库。

本次任务只生成 `PLAN.md`，不编写具体业务代码。当前目录已检测到 Git 仓库，并已绑定远端仓库 `origin`：`https://github.com/coralingyun/N2S.git`。后续开发应在同步远端代码后创建独立分支，并在完成文档、Schema、代码和测试变更后按上述流程提交与推送。

## 14. 验收标准

项目 MVP 的验收标准如下：

- 输入不少于 3 个章节的小说文本后，系统可以生成合法 YAML。
- YAML 中必须包含项目信息、故事概述、人物列表、场景列表和场景 beats。
- 每个场景必须包含地点、时间、人物、冲突和至少一个 beat。
- YAML 能通过 Schema 校验。
- 项目必须包含 `docs/yaml_schema.md`，并解释 Schema 的设计原因。
- 项目必须提供一个可运行 demo。
- 项目必须包含至少 3 个基础测试。
- 生成结果应保留可编辑性和可追溯性，不应把不确定推断伪装为原文事实。

---
name: project-memory-read
description: Read project memory selectively through task routing, exact-first retrieval and minimal context. Use for project facts, constraints, plans, lessons, shared references or history. Keep retrieval read-only and hand verified discoveries or stale facts to project-memory-maintenance in the same task; do not initialize or write memory during retrieval.
---

# 项目记忆读取

通过任务路由和渐进式披露取得完成当前任务所需的最小证据。本 Skill 只读记忆，不写入正文、索引、manifest、数据库或缓存。

只读边界针对检索阶段。项目任务按“索引定位 → 按需读取 → 缺口探索 → 核验事实 → 接续维护”执行；满足分层写入条件后，同一 Agent 在当前轮次切换到 `project-memory-maintenance`，不等待用户另行要求记录。用户明确禁止写入时只返回会话内候选，不切换写入阶段。

## 定位与起点

1. 按“用户指定目录 > 当前工作目录”确定项目目录；不要自动切换到更宽的工作区根目录或上溯 Git 根目录。
2. 从 `<项目目录>/.codex/memory/INDEX.md` 开始。
3. 根索引不存在时，`FALLBACK`：依据当前代码、配置、数据库和用户材料完成任务，并说明项目记忆尚未初始化。

不要一开始遍历整个 `memory/`，也不要把根索引当作完整知识库。

用户原始材料默认位于 `<项目目录>/.codex/source-materials/`。需要使用 `user_material` 证据时按任务精确读取对应文件；原始材料不是记忆条目，不把它当作已验证的当前事实，也不因读取而修改它。

读取 Skill 是严格只读流程：不得创建预览目录、临时文件、缓存、索引数据库或任何项目根目录条目。解析 SQL、表格或原始材料时使用内存、终端或系统临时目录；不得调用 PowerShell `md`、`mkdir`、`ni`、`New-Item` 别名或重定向命令。运行 Python 读取辅助脚本加 `-B`，防止导入产生 `__pycache__`。若某个读取工具有写入副作用，停止使用并回退到文本读取或报告工具不可用。

## 任务路由

| 任务信号 | 首读 | 其次读取 | 默认跳过 |
| --- | --- | --- | --- |
| 修改文件、配置、依赖或数据 | `guardrails` | 精确匹配的 `modules` | `library`、`changes` 全量 |
| 开发具体功能、页面、接口或数据流 | `modules` | `lessons`、已有且关联的 `plans` | 无关层 |
| 执行大需求、恢复复杂问题或核对需求进度 | `plans/INDEX.md` 对应的当前有效版本 | `guardrails`、`modules` | 无关计划、`changes` 全量 |
| 排查回归、历史原因或回滚 | `changes` | `modules`、`lessons` | 无关层 |
| 接入共享组件或规范 | `library` | 当前项目 `modules` | `changes` |
| 修改样式、组件或技术规范 | 当前项目 `modules` | 相关 `library` 条目 | 无关层 |

修改类任务必须先检查匹配的 `guardrails`。项目现有实现与共享规范冲突时，以当前实现和已验证的 `modules` 为事实来源；约束冲突则以用户当前明确指令和匹配的 `guardrails` 为操作依据。

`modules` 采用“业务域目录 → 页面文档”结构，并按 [modules-format.md](../project-memory-maintenance/references/modules-format.md) 区分全局业务总述、页面事实、接口事实和表结构事实。用户询问具体页面、业务节点或独立配置界面时，若对应业务域存在 `INDEX.md` 先读取它；没有域级索引时按目录和文件名精确定位页面，再读取页面文档。顶层业务域概览不能替代页面级事实。若页面没有独立条目，返回 `missing` 或 `partial`，不得把域级摘要扩写成页面事实。变更历史、测试过程和回滚线索按需读取 `changes`，不从页面模块的历史段落推断。

`changes` 使用按日期保存的 JSONL 时间线：文件名为 `YYYY-MM-DD.jsonl`，同日一行一条记录。需要历史追踪、回归或回滚时，先按日期文件、`change_id` 或 `issue` 精确定位，再读取必要的记录行；`changes/INDEX.md` 不承担单条记录索引。

`plans` 只保存材料中的大需求和需要分阶段处理的复杂问题，文件名为 `YYYY-MM-DD-vN.md`。先按 `plans/INDEX.md` 的文件级需求简介、`plan_id` 或日期定位，再读取当前有效版本中的来源、需求清单、待补充和实施计划；仅在版本比较或历史决策需要时读取旧版本，不因某个文件日期更近就认定它属于同一需求。执行前核对需求是否明确、是否可立即实施及依赖；未解决 P0 禁止实施其影响及依赖部分。普通小修改不要求先找到计划，也不因计划缺失而自动生成文件。

## 检索升级顺序

按以下顺序逐级升级，命中充分证据后立即停止：

1. **工作集命中**：当前会话已有相关证据且来源仍新鲜时直接复用。
2. **精确命中**：按 `memory_id`、计划的 `plan_id`、文件路径、接口、路由、模块名或唯一标题定位。
3. **词法命中**：按关键词、别名、错误信息和状态筛选少量候选。
4. **派生全文索引**：若存在且新鲜，使用 manifest 或 SQLite/FTS5；不存在、过期或损坏时，普通记忆回退分层 `INDEX.md`，`changes` 回退日期文件名和 JSONL 文本搜索。
5. **项目记忆新鲜度**：若项目存在 Git 和 `check_memory_freshness.py`，先读取其结果。优先运行 `.codex/skills/project-memory-maintenance/scripts/check_memory_freshness.py`；`fresh` 才能按当前事实使用；`stale` 必须触发模块刷新或报告过期原因；`unknown`、`needs_review` 或缺少 `verified_commit` 时不得把代码事实条目当作可靠当前事实。需求计划使用轻量头，代码新鲜度为 `not_applicable`；按正文来源、依赖、待补充和验收结果核对，不将缺少普通元数据/Git 字段当作过期或旧格式，也不把计划当成已实现事实。
6. **父上下文补全**：命中子节点后最多补充直接父节点的定位、状态、限制和必要来源，不默认读取整页。
7. **关系扩展**：问题明确涉及调用、依赖、约束、影响范围或数据流时，默认只扩展一跳；每次最多返回 3 个关系节点、总证据最多 8 个条目。证据不足才扩展第二跳，并说明原因；第二跳仍不足即停止。
8. **向量或受限 Agent**：只有精确和词法路径无法形成充分证据，且问题确实是模糊、多跳或跨模块时才启用。仅在当前运行时已提供且项目已启用时使用；不可用则返回 `missing`。默认最多两轮，并输出证据 ID 和缺口。

稳定 ID 存在时，禁止用模糊语义结果替代唯一精确命中。候选结果应按类型、状态、项目范围和来源新鲜度过滤，`deprecated` 默认排除。模块审计字段位于 `modules/.audit.json`；查询默认返回轻量元数据，需要证据路径、提交号或哈希时再请求审计字段。

启用机器索引时，使用项目内的查询脚本：

```text
python -B .codex/.knowledge/scripts/query_index.py --query "<任务关键词>"
```

脚本返回 `fallback_required`、`missing` 或 `stale` 时，立即回退 Markdown 索引、文件名和文本搜索。读取 Skill 不运行 `sync_index.py`、不修复数据库，也不修改任何记忆文件。

如果项目启用了 `.codex/.runtime/session-state.json`，会话开始时可以先读取其中的任务目标、已完成步骤、变更文件、测试结果和待确认项。该文件只提供运行上下文，必须用当前代码和记忆来源核实，不得当作项目事实，也不得在读取过程中修改它。

## 读取预算和停止条件

- 每次优先读取 1 至 3 个高相关条目。
- 每个命中节点只补最小必要父上下文。
- 关系扩展默认一跳；跨两跳必须存在证据缺口。
- 关系查询返回关系边及目标节点；它是轻量关系图，不代表完整 GraphRAG 结论。
- 证据已覆盖当前任务所需的事实类型、约束和来源后立即停止。
- 不因为“还可以找到更多内容”继续扩大上下文。

如果候选冲突、来源过期、证据不足或命中为空，停止扩大猜测并报告缺口。

## 缺口探索与维护交接

记忆中 `missing`、`partial` 或 `stale` 不等于实际项目没有信息。先按当前任务的缺口精确检查必要的代码、配置、可访问的数据库信息或用户材料；不得因为读取 Skill 只读就直接结束任务，也不得为补记忆全量扫描无关代码。

- 记忆新鲜、事实够用且没有新增知识：复用后停止，维护为 `none`。
- 缺口已由本轮来源核验，形成未记录或需要修正的持续事实：交接为 `ready`，答复前必须接续维护 Skill，自动写入 `modules` 并同步索引。即使只要求“了解一下”或“先列计划”，也按项目自动维护规则执行。
- 部分链路已核验：已知内容可交接为 `ready`，页面保持 `partial`；实库、运行效果或未找到的链路记录为未确认，不因缺少整页验证而丢弃已核验事实。
- 仅命中空索引、推断或冲突，尚无可核验事实：先补必要证据；仍不足时交接为 `blocked` 并说明缺口，不生成虚构页面事实。
- 用户禁止写入、架构未初始化或写入工具不可用：保留核验结论与候选，说明维护未执行，不自行初始化或制造索引。

交接只留在当前会话，包含拟写层级/路径、事实或差异、来源路径与锚点、覆盖范围及未确认项；不创建新的队列文件或会话缓存。`library`、`guardrails` 的修订建议只有对应用户授权才能写入；重要变更、有效经验和当前轮次计划由维护 Skill 按各自触发条件处理。

## 证据结果格式

读取结果应优先整理为以下结构，而不是只给无来源的摘要：

```yaml
intent: modify_behavior
subject_ids: [MOD-ORDER-SAVE-001]
evidence:
  - memory_id: MOD-ORDER-SAVE-001
    role: primary
    status: verified
    record: modules/order/overview.md#save-behavior
    evidence_sources:
      - kind: code
        path: src/order/save.ts
        anchor: saveOrder
        evidence_hash: sha256:...
        verified_at: 2026-09-23
    summary: 只有 draft 状态允许保存
constraints:
  - memory_id: RULE-ORDER-DRAFT-001
    role: constraint
conflicts: []
missing: []
maintenance_handoff:
  state: none # none、ready 或 blocked；不写为持久队列
  candidates: [] # 包含目标层/路径、事实差异、来源、覆盖范围和未确认项
  reason: 已有记忆仍有效且没有新增事实
```

如果旧条目没有正文头或侧车审计元数据，标记 `metadata_state: legacy` 或审计缺失，保留来源路径；不要因为缺少元数据就自动判定事实无效，也不要因读取而改写文件。

## 冲突和新鲜度

- 事实可信度：运行结果和有效数据 > 当前代码、配置及数据库 > `modules` > `changes` > `plans` > `library`。
- `modules` 是当前事实，`plans` 是预期；计划不得覆盖实际实现。
- `library` 仅作共享参考，不覆盖当前项目风格、代码或配置。
- `modules/.audit.json` 中 `evidence_sources` 的路径、锚点或 `evidence_hash` 不一致时，标记为 stale，优先检查实际来源；`record_hash` 只用于确认记忆正文是否变化。
- 侧车审计中的 `verified_commit` 之后若 `impact_paths` 或证据文件发生代码提交或未提交变更，标记为 stale。可自动刷新的模块由维护流程重新核验；跨模块或高风险变更进入 `needs_review`。
- 同一事实存在多个版本时，不静默选择；列出冲突来源、状态和需要确认的项。

## CHECKPOINT

返回读取结果前确认：

- 是否检查了当前任务适用的约束。
- 是否使用了精确优先的检索顺序。
- 是否只读取了必要父上下文和关系。
- 是否列出来源、状态、哈希或 legacy 标记。
- 是否明确报告冲突、缺口和停止原因。
- 是否区分“记忆缺失”和“实际证据不足”，并把已核验增量交接给维护流程。

本 Checkpoint 只确认检索完成；有 `ready` 候选时，整轮任务仍需接续维护并报告实际结果。

## 失败处理

| 触发条件 | 处理 |
| --- | --- |
| 根索引不存在 | 回退实际项目材料，报告未初始化，不创建记忆。 |
| 分层索引缺失 | 普通记忆用分层索引、文件名和关键词定位；`changes` 用日期文件名、`change_id`、`issue` 和文本搜索定位，报告索引缺口。 |
| manifest/FTS5 缺失、过期、损坏或 schema 未知 | 回退 Markdown 索引与文本搜索，不把工具错误当作无知识。 |
| 精确命中多个冲突条目 | 停止静默选择，返回冲突列表和确认项。 |
| 记忆没有充分证据 | 按任务缺口读取实际来源；仍不足时返回 `missing`，不得用模型猜测补齐。 |
| 关系扩展超过一跳仍不足 | 停止并报告证据缺口，不无限扩大搜索。 |
| 记忆与实际代码不一致 | 以已核验的实际代码为事实，本 Skill 不写回；在同轮接续维护 Skill 更新对应条目，禁止写入时仅报告候选。 |

## 不要做

- 不要默认读取整个 `library`、`changes` 或所有模块。
- 不要用摘要、旧会话记忆或向量相似度替代可定位原文。
- 不要在没有来源和验证状态时输出确定性业务结论。
- 不要因派生索引不可用而阻断任务。
- 不要在读取 Skill 中修改正文、索引、缓存或数据库。
- 不要启用向量检索来替代精确检索、FTS5 或原文证据。

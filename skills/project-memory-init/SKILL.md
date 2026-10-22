---
name: project-memory-init
description: Initialize a project's `memory` authority files, six memory layers, sparse navigation indexes, and routing metadata when the user asks to create the project-memory architecture. Use for first-time setup or filling missing scaffold files; do not use for routine retrieval, content discovery, or machine-index rebuilds.
---

# 项目记忆初始化

仅创建项目记忆骨架和导航规则。初始化阶段不得扫描代码、总结业务、生成历史记录或猜测项目事实。

## 项目位置

按以下顺序确定目标目录：

1. 用户明确指定的目录。
2. 当前工作目录。

不要自动切换到更宽的工作区根目录或上溯 Git 根目录。用户明确指定项目根目录时，才切换到该目录。

默认目标为 `<项目目录>/memory/`。如果项目目录无法确定，使用当前工作目录并在结果中报告。

## 创建结构

创建以下六层目录和最小路由索引：

```text
source-materials/
memory/
    |-- INDEX.md
    |-- library/
    |   `-- INDEX.md
    |-- guardrails/
    |   `-- INDEX.md
    |-- modules/
    |   `-- INDEX.md
    |-- changes/
    |   `-- INDEX.md
    |-- lessons/
    |   `-- INDEX.md
    `-- plans/
        `-- INDEX.md
```

如果目标已存在，先检查现有结构，只补充缺失目录或文件。不得覆盖、清空或重排已有内容。

初始化完成后调用本 Skill 的 `scripts/generate_agents_md.py`：

```text
python <project-memory-init>/scripts/generate_agents_md.py --project-root "<项目目录>"
```

该脚本在项目根目录创建或幂等更新 `AGENTS.md` 的受管区块。该文件用于让 Codex 在后续任务中自动遵守本项目记忆架构；它不是六层记忆，不进入 `memory` 索引。若已有 `AGENTS.md`，只替换受管标记区块，保留区块外的用户指令；标记不完整或文件无法按 UTF-8 读取时停止并报告，不覆盖原文件。

`source-materials/` 是用户原始材料目录。初始化只创建目录，不扫描、摘要、改写、移动或删除其中的材料；用户可以将 DDL、设计文档、数据字典、需求材料和其他原始文件放入其中。原始材料不是记忆条目，不进入六层 `memory/` 的导航索引，也不直接作为当前事实，后续维护时必须按来源核验后再写入对应记忆层。

`memory/` 是人类可读的权威来源：普通记忆使用 Markdown，`changes` 使用按日期追加的 JSONL。Markdown 索引只做导航，不复制正文；默认只创建根索引和六层索引，不为每个主题、业务域或空目录预建 `INDEX.md`。只有条目规模或检索边界确实需要时，才按需增加一层主题索引。可选的机器派生目录（例如 `.knowledge/`、manifest、SQLite/FTS5、证据缓存）不在初始化阶段默认创建；只有用户启用机器索引或维护流程确实需要时才建立。会话运行状态也不默认创建，只有用户启用会话恢复时才复制 `.runtime/session_state.py`。

## 写入边界与副作用限制

初始化本身只允许写入以下位置：

- `<项目目录>/source-materials/`：只创建目录，不写入用户材料；
- `<项目目录>/memory/`：创建骨架和缺失索引；
- 用户明确启用机器索引后，才允许创建 `.knowledge/` 及其派生文件；
- 用户明确启用会话恢复后，才允许创建 `.runtime/` 及其状态文件。

初始化时允许额外创建或更新项目根目录的 `AGENTS.md` 受管区块；除此之外，初始化不得写入项目根目录。

除受管 `AGENTS.md` 外，初始化不得在项目根目录、源码目录、配置目录或数据库目录创建临时文件、预览目录、备份目录或脚本输出。分析、列目录、解析 SQL 和生成预览必须使用内存、终端或系统临时目录；不得把原始字段名、表注释、类型值等数据拼接为 shell 命令或路径。

不得使用 PowerShell 的 `md`、`mkdir`、`ni`、`New-Item` 别名或 `>`/`>>` 重定向承载未转义数据。需要写入时使用结构化文件 API，并先验证目标路径位于允许目录内；遇到无法验证的目标路径，停止并报告，不用猜测路径。

## 启用 SQLite/FTS5 加速

当用户明确要求启用机器索引时，在完成 Markdown 骨架后，从本 Skill 的 `templates/knowledge/` 复制以下模板到项目：

```text
.knowledge/
├── manifest.yaml
└── scripts/
    ├── index_lib.py
    ├── sync_index.py
    ├── query_index.py
    ├── check_index.py
    ├── check_layout.py
    ├── check_memory_freshness.py
    ├── workspace_guard.py
    └── safe_write.py
```

此时只创建脚本和初始 manifest，不要求立即创建 `index.sqlite`。首次维护时由 `sync_index.py` 创建数据库。复制模板后运行一次 `check_index.py` 和 `check_layout.py`；索引不存在属于正常的 `missing` 状态，不应阻断初始化。

`workspace_guard.py` 仅用于执行前后工作区快照、未授权路径审计和写入目标校验；它不会自动删除异常文件。初始化创建 `AGENTS.md` 时，审计命令必须显式传入 `--allow-project-instructions`，该例外只允许根目录这个文件。`safe_write.py` 只允许原子写入 `memory/**/*.md`，维护时优先使用它写入普通正文和索引；`changes` 由维护 Skill 的 `append_change.py` 追加并由 `validate_changes.py` 校验。

`check_memory_freshness.py` 只读检查项目记忆与 Git 当前提交、证据文件和证据哈希的关系。它输出 `fresh`、`stale`、`unknown` 和可自动刷新的模块队列，不直接修改记忆。初始化复制该脚本后，后续维护可在拉取协作者代码或合并代码变更后运行它。

Git 新鲜度检查不依赖 SQLite/FTS5；项目应同时安装 `skills/project-memory-maintenance/scripts/check_memory_freshness.py` 包装入口。即使项目采用 Markdown-first，也必须保留该入口，不能因为未启用机器索引而跳过代码变更后的记忆失效检查。

不要让 Agent 临时编写 SQL，也不要把未知 schema 的现有数据库直接覆盖。机器索引脚本不可用时继续使用普通 Markdown 和日期 JSONL，并报告机器索引未启用或需要重建。

## 根索引要求

新建的 `memory/INDEX.md` 必须包含：

- “先索引、后正文”的渐进读取原则。
- 六层职责、读取条件和写入权限。
- 各层自动维护触发条件：`library`、`guardrails` 需用户明确授权；`modules`、`changes`、`lessons` 按维护 Skill 的条件自动接续；`plans` 仅为材料中的大需求或需分阶段处理的复杂问题创建，不为普通对话、小修改或日常任务创建计划。
- 缺口探索闭环：索引缺失或过期时只核验任务内必要来源，已验证的增量在本轮答复前写入对应层并同步索引；已有且一致的事实不重复写入。
- 任务路由表：任务信号、首读层、其次读取层、默认跳过层。
- 事实优先级和操作约束优先级。
- 普通记忆 Markdown 和 `changes/*.jsonl` 是权威来源；任何 manifest、全文索引、缓存和摘要都是可重建派生物。
- 派生索引缺失、过期或损坏时，普通记忆回退到导航 `INDEX.md` 和文本搜索，`changes` 回退到日期文件名和 JSONL 文本搜索，不阻断任务。

## 页面级模块记忆

正常任务中渐进积累页面事实：先查索引，没有目标信息时才按需了解代码，核验完成后自动接续维护。初始化本身仍只搭骨架；用户明确禁止写入时，后续任务也不得自动沉淀。`AGENTS.md` 受管区块必须同时说明自动维护条件与检索阶段只读边界。

模块职责、全局业务总述、页面事实、接口文档、数据库表文档和变更边界见 `skills/project-memory-maintenance/references/modules-format.md`。页面模块只记录当前状态，不建立 dated change sections；变更原因、测试和回滚回到 `changes`。

当用户要求“整体了解项目”“按功能模块搭建记忆”或“梳理页面地图”时，不得直接把若干顶层业务域摘要当作完成结果。必须先建立覆盖清单；默认按以下结构写入，业务域索引只在同域页面较多或需要独立检索边界时增加：

```text
modules/<业务域>/<页面或独立配置界面>.md
# 可选：modules/<业务域>/INDEX.md
```

独立路由页面、独立配置界面或具有独立权限/数据流的业务节点各有一个 Markdown 条目；页面内普通按钮、弹窗和局部组件记录在页面文档中。共享页面实现可放在 `shared/` 并由页面关系引用。每个路由/页面必须在覆盖清单中标记 `covered`、`partial` 或 `excluded`，只有没有未说明项时才能报告整体完成。

## 轻量关系图与会话恢复

项目记忆只启用轻量关系图：条目 frontmatter 中的 `parent_id` 和 `relations` 由维护 Skill 写入 SQLite 关系表，读取时最多扩展一跳并返回关系目标节点。不要初始化图数据库、自动实体抽取或完整 GraphRAG。

当用户明确启用会话恢复时，从本 Skill 的 `templates/runtime/session_state.py` 复制到：

```text
.runtime/session_state.py
```

该脚本只维护 `.runtime/session-state.json`，记录任务目标、完成步骤、变更文件、测试结果和待确认项。它不是记忆层，不进入导航索引，也不得自动写入 `library`、`guardrails` 或 `modules`。具体 Hook 事件由运行环境接入，脚本本身保持可独立调用。

建议将 `.runtime/session-state.json` 加入项目忽略规则；如果项目需要跨设备恢复，再由项目自行决定是否纳入版本控制。

向量检索只保留后续扩展位；初始化阶段不安装 embedding 模型、向量库或外部服务。

推荐任务路由：

| 任务信号 | 首读 | 其次读取 | 默认跳过 |
| --- | --- | --- | --- |
| 修改文件、配置、依赖或数据 | `guardrails` | `modules` | `library`、`changes` |
| 开发具体功能、页面、接口或数据流 | `modules` | `lessons`、已有且关联的 `plans` | `changes` |
| 执行大需求、恢复复杂问题或核对需求进度 | `plans/INDEX.md` 对应的当前有效版本 | `guardrails`、`modules` | 无关计划、`changes` |
| 排查回归、历史原因或回滚 | `changes` | `modules`、`lessons` | 其他无关层 |
| 接入共享组件或规范 | `library` | `modules` | `changes` |

## 稀疏索引要求

每个已创建的分层或主题 `INDEX.md` 必须包含职责、读取条件、写入权限和直接条目表。空层保留六层索引作为路由入口，但不继续预建下级索引。`plans` 只说明大需求/复杂问题的创建门槛、`YYYY-MM-DD-vN.md` 命名、详细格式入口和 P0 实施阻塞规则；直接条目只登记文件、需求简介、计划编号、版本、状态和更新时间，不展开文件内的需求清单。初始化不创建实际计划，详细格式见维护 Skill 的 `references/plans-format.md`。其他普通记忆条目表使用稳定字段：

```markdown
| ID | 触发词 | 摘要 | 适用范围 | 路径 | 优先级 | 状态 | 更新时间 |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

索引路径统一相对于 `memory/`。每个索引只记录直接子条目或直接子索引，不展开后代内容。

默认索引深度最多为三层：根索引、分层/主题索引、正文。只有直接条目超过 30 至 50 个、索引超过约 100 行，或需要独立检索边界时，才增加主题索引；不为单条记录创建索引。正文变更先更新直接索引，祖先索引在一批写入结束时或显式刷新时更新，避免每条记录产生祖先索引写放大。

## 条目元数据模板

初始化时不创建虚构条目。`plans/` 下的需求正文文件仅要求 `plan_id`、`plan_state`、`updated_at`，替代旧版时加 `supersedes`；日期/版本从文件名读取，其他信息放正文，派生索引推导唯一节点和哈希。不要套用普通元数据或将缺少 Git 字段的计划判为 legacy/unknown；`plans/INDEX.md` 保留导航索引元数据。`modules/INDEX.md` 和按需创建的 `modules/<domain>/INDEX.md` 按 modules-format 使用 `memory_id`、`type`、`updated_at` 轻量头，不要求审计字段。其他事实条目的最低元数据为：

```yaml
memory_id: MOD-EXAMPLE-001
type: module
status: verified
coverage: partial
updated_at: 2026-09-23
```

`memory_id` 一经使用不得因标题、文件名或路径变化而修改。模块事实正文统一使用 `type: module`；页面、共享文档、接口和数据表的 `record_level` 保存在 `modules/.audit.json` 中。`scope`、`aliases`、`record_path`、`record_anchor`、`parent_id`、`relations`、`evidence_sources`、`verified_commit`、`impact_paths`、`working_tree_verified` 和 `record_hash` 不再写入事实文档头，统一由侧车保存。旧 Markdown 记忆使用 `metadata_state: legacy` 时，在侧车文件中保留该状态；不得为了补字段而恢复重型 YAML 头。

`record_hash` 仍对 UTF-8、LF 规范化后的正文计算，避免自引用；侧车文件缺失时应报告审计字段不完整，不把页面事实自动判为错误。

`modules/.audit.json` 中的 `verified_commit` 记录本条事实最后一次核验所依据的 Git 提交，`impact_paths` 列出会使本条记忆失效的代码、配置、迁移或数据路径，使用项目相对路径和 glob。代码事实记忆缺少侧车审计字段时，不得报告为可靠的 `fresh`，应标记为 `unknown` 并在首次维护时补齐。需求计划不适用这组代码核验要求，新鲜度输出为 `not_applicable`；来源和实施条件仍按正文核对。

协作者可以直接修改代码，不要求其手工维护记忆。代码拉取或合并后运行 `check_memory_freshness.py`；对 `refreshable: true` 的 `modules`/页面记录，维护流程应重新读取受影响来源，只更新对应记录，写入当前 `verified_commit` 和新的证据哈希，再更新直接索引，并按需批量刷新祖先索引和派生索引。跨模块、高风险、历史分叉、来源缺失或证据不足的记录进入 `needs_review`，不得自动猜测。

## CHECKPOINT

初始化完成前检查：

- `memory/` 是否位于用户指定或当前工作目录下。
- `source-materials/` 是否已创建，并且未被扫描或改写。
- `AGENTS.md` 是否已通过生成脚本创建或更新，且保留了受管区块之外的原有内容。
- 是否只补缺失项，未覆盖已有正文和索引。
- 是否没有虚构项目事实。
- 根索引是否包含任务路由和派生索引回退规则。
- 新建根/分层索引和 `AGENTS.md` 是否明确分层自动维护条件，未把维护限定为用户单独触发。
- 现有索引不完整时，是否报告迁移建议而非未经授权重排。

## 失败处理

| 触发条件 | 处理 |
| --- | --- |
| 目标目录不存在 | 创建目录和索引骨架。 |
| 目标目录已有内容 | 只补缺失项，保留现有内容。 |
| 现有索引格式不一致 | 不重排正文；报告冲突，补充兼容说明。 |
| 目标路径无法确定 | 使用当前工作目录并报告。 |
| 派生索引工具不可用 | 不创建伪索引，保留 Markdown 骨架并报告可选后续。 |

## 完成条件

- 六个分层目录及其 `INDEX.md` 存在。
- `source-materials/` 存在，并与 `memory/` 保持职责分离。
- 根索引包含任务路由、优先级、回退规则和权限边界。
- 索引路径有效且使用相对路径。
- 没有生成业务事实、虚构条目或默认机器数据库。
- 已有不完整索引允许“部分完成并报告”，不宣称已完成迁移。
- 向用户报告创建项、保留项、冲突和未启用的可选派生层。

## 不要做

- 不要扫描整个项目来“顺便填充”记忆。
- 不要把 `source-materials/` 中的原始材料自动转换为记忆条目。
- 不要把原始材料目录放入 `memory/`，避免被机器索引误收录。
- 不要把完整知识库放入根索引。
- 不要默认创建 SQLite、向量库、GraphRAG 或会话缓存。
- 不要把索引摘要当作权威事实。

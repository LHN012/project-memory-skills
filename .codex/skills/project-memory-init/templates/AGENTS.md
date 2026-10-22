# 项目记忆工作规则

<!-- BEGIN CODEX PROJECT MEMORY MANAGED BLOCK -->

本项目启用了 `.codex/memory` 项目记忆架构。以下区块由 `project-memory-init` 初始化 Skill 管理；不要把它当作业务事实，普通记忆必须回到 `.codex/memory` 的 Markdown 记录中核验，`changes` 历史必须回到日期 JSONL 文件中核验。

## Skill 路由

- 首次创建或补齐架构：使用 `.codex/skills/project-memory-init/SKILL.md`。
- 读取项目记忆：使用 `.codex/skills/project-memory-read/SKILL.md`；检索阶段只读，不创建缓存、预览目录或索引。
- 自动沉淀、修订和同步记忆：满足下方条件后在同一轮次接续 `.codex/skills/project-memory-maintenance/SKILL.md`，无需用户单独调用。
- 用户要求“整体了解项目”“按功能模块搭建记忆”“梳理页面地图”时，必须执行完整清单和覆盖检查，不得只写几个业务域摘要。

## 渐进式披露与自动维护

每轮按“先索引 → 读匹配记忆 → 按缺口查看必要来源 → 核验增量 → 接续维护并同步索引”执行。不要把“记忆没有记录”误判为“实际项目无法了解”，也不要为补一条记忆扫描整个项目。

| 层级 | 维护触发 |
| --- | --- |
| `library` | 仅用户明确授权纳入或修订；共享经验先提议 |
| `guardrails` | 仅用户明确授权保存或修订项目约束 |
| `modules` | 任务内核验出缺失、过期或变化的持续事实后自动新增/修订 |
| `changes` | 本轮实际发生重要业务、接口、数据或架构变更后自动记录 |
| `lessons` | 出现有证据且可复用的经验后自动记录或合并，不逐次记录临时错误 |
| `plans` | 仅为材料中的大需求或需要分阶段处理的复杂问题创建；已有计划按实际进度维护 |

- “了解一下”“先列计划”“不改业务代码”不关闭记忆自动维护。发现页面记忆缺失并已核验源码事实时，答复前新增 `modules/<业务域>/<页面>.md` 并同步索引，不等待用户追问。
- 仅列计划时，现状写入 `modules`；拟实施内容仅在满足大需求或复杂问题条件时写入 `plans` 并标明待确认，其他步骤留在会话中，不写成已发生的变更或已存在的新页面；实施后更新实际事实和已有计划进度。
- `plans` 仅记录材料中的大需求或需要分阶段处理的复杂问题，普通问答、按钮/文案/样式小修改和简单修复不创建计划文件或日计划。文件名为 `YYYY-MM-DD-vN.md`；进度更新沿用当前版本，实质性范围/方案变化才新建版本。详细格式见 `.codex/skills/project-memory-maintenance/references/plans-format.md`。`plans/INDEX.md` 只登记文件级需求简介；P0 未解决时禁止实施其影响及依赖部分。
- 已有且一致的信息不重复写入、不仅刷新时间戳；部分已知事实可沉淀，页面保持 `partial` 并列出未确认项。
- 用户明确说“不要修改任何文件”“不要写入记忆”或“严格只读”时，本轮只读并报告维护候选；未初始化时不自动搭架构。自动维护不授权业务实施或启用可选服务。
- 每批正文写入后更新直接索引；祖先索引在一批写入结束、路由信息变化或显式刷新时批量更新。没有达到拆分阈值的目录不预建下级 `INDEX.md`。再同步已启用且兼容的派生索引、校验与审计。工具不可用或证据不足时报告维护未完成，不声称已沉淀。

## 页面级模块记忆

`modules` 的组织粒度固定为“业务域目录 → 页面或独立配置界面文档”：

```text
.codex/memory/modules/
├── INDEX.md
└── <domain>/
    ├── INDEX.md
    ├── <page-a>.md
    └── <page-b>.md
```

- 业务域 `INDEX.md` 只在同域页面较多或需要独立检索边界时创建，负责导航和概览，不能替代页面记忆。
- 每个独立路由页面、独立配置界面或具有独立权限/数据流的业务节点必须有单独 Markdown 文档。
- 页面内普通弹窗、按钮和局部组件默认记录在页面文档中；只有它具有独立路由、独立权限、独立数据流或可复用业务契约时，才另建节点并建立关系。
- `modules` 只记录当前事实：全局业务对象、状态、系统协作、数据权威和通用安全规则集中在 `modules/shared/`；页面只记录目的与边界、当前行为、页面权限、接口用途、兼容契约和未决项；接口和数据库表分别按接口族、单表权威文件放入 `modules/interfaces/`、`modules/data/`。
- `modules` 不记录按日期排列的变更、实施过程、测试过程或回滚步骤；变更历史统一回到 `changes/YYYY-MM-DD.jsonl`，页面只在必要时引用 `change_id`。
- 共享页面实现可以建立 `shared/` 节点；多个页面通过关系引用，不复制整段事实。
- 旧的扁平模块摘要只能作为概览或迁移来源，不得把它当作所有页面均已覆盖。

## 整体了解的完成条件

开始写入前先建立覆盖清单，至少核对：

`路由 → 页面文件 → 页面功能 → API → Controller/Service → Mapper/SQL → 数据表`。

每个路由或页面必须标记 `covered`、`partial` 或 `excluded`，`excluded` 必须有原因。只有清单中没有未说明项时，才能报告“整体了解完成”。事实状态 `verified` 只表示已有证据支持，不表示覆盖完整；页面文档还应记录 `coverage` 状态和未确认项。

## 项目记忆新鲜度与自动刷新

代码事实记忆的 `verified_commit`、`impact_paths` 和证据哈希统一保存在 `modules/.audit.json`，正文头只保留 `memory_id`、`type`、`status`、`coverage`、`updated_at`。需求计划正文只用 `plan_id`、`plan_state`、`updated_at` 三字段头，替代旧版本时增加 `supersedes`；日期和版本从文件名读取，其他内容在正文。不得为计划补回普通元数据或 Git 字段，代码新鲜度返回 `not_applicable`，来源和实施条件仍按正文核对。代码被其他协作者直接修改后，先运行 `python -B .codex/skills/project-memory-maintenance/scripts/check_memory_freshness.py --project-root .`。对 `refreshable: true` 的模块或页面，重新读取当前代码并直接更新对应记忆、侧车证据和提交号；同步直接索引，祖先索引按需批量刷新；不要只修改更新时间。跨模块、权限/安全、数据库迁移、来源缺失或证据不足的变化标记为 `needs_review`，不得猜测。普通记忆 Markdown 是权威来源，`changes/*.jsonl` 是变更历史权威来源，SQLite/FTS5 只在 Markdown 正文更新后按需同步。

## 数据库表创建

新建表或设计表结构时，先检查当前项目已有表、迁移脚本和 SQL 风格；有可比表时沿用实际项目风格，没有可比表时才采用精简的阿里规范基线。按当前功能选择字段组，并解释每个字段组的作用和本表创建目的。没有当前需求或证据的租户、审计、逻辑删除、状态、乐观锁和扩展字段组不自动创建。详细规则见 `.codex/skills/project-memory-maintenance/references/database-table-creation.md`。

## 记忆权限和事实优先级

- `.codex/source-materials/` 是用户原始材料，只读，不自动转为记忆。
- `library` 和 `guardrails` 只有用户明确授权才能写入。
- `modules` 记录当前代码、配置、数据库和运行结果验证出的事实。
- `plans` 记录预期，不得覆盖实际实现；实际代码优先于旧记忆和计划。
- 普通记忆 Markdown 和 `changes/*.jsonl` 是权威来源；SQLite/FTS5、摘要和其他索引都是可重建派生物。

## 写入安全

记忆维护阶段只允许写入 `.codex/memory/`、已启用的 `.codex/.knowledge/` 和 `.codex/.runtime/`。初始化时仅允许额外创建或更新项目根目录的本 `AGENTS.md` 受管区块。该边界不禁止用户另行授权的业务代码修改；先完成该批业务修改，再为独立的记忆写入阶段建立快照和审计，中间不穿插业务改动。禁止把 SQL 字段、表注释或用户材料拼接进 PowerShell 命令、路径或 `md`/`mkdir`/`ni`/重定向；发现未声明路径立即停止，不自动删除异常文件。

<!-- END CODEX PROJECT MEMORY MANAGED BLOCK -->

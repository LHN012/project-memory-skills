# Project Memory

一套面向 AI 辅助软件工程和长期项目协作的通用记忆架构。它把长期知识、项目约束、业务事实、变更历史、排错经验和复杂需求计划分层保存，并通过索引、按需检索和自动维护减少上下文冗余与错误记忆。

本仓库根据《记忆结构设计》整理，保留记忆系统的核心目录与配套自动化规则。架构本身不依赖某个 AI 平台，目录已直接展开为 `memory/` 和 `skills/`。`memory/library/` 是跨项目共享知识库，按本次发布要求不纳入仓库。

## 解决的问题

- 让 AI 先查索引，再读取与当前任务相关的最小正文。
- 区分当前事实、历史变更、经验总结和未来计划，避免把计划当成实现结果。
- 对 `changes` 使用按日期追加的 JSONL，便于追溯、检索和机器处理。
- 通过读取、核验和维护流程形成“检索 → 核验 → 沉淀”的闭环。
- 保留可选的 SQLite/FTS5、工作区审计和会话恢复模板，但默认不依赖外部服务。

## 目录结构

```text
memory/
├── INDEX.md              # 总路由：先索引、后正文
├── guardrails/           # 当前项目的规则与约束
├── modules/              # 已核验的业务模块、页面、接口和数据事实
├── changes/              # YYYY-MM-DD.jsonl 变更时间线
├── lessons/              # 可复用的排错与实施经验
└── plans/                # 大需求和复杂问题的分阶段计划
skills/
├── project-memory-init/        # 初始化骨架与导航索引
├── project-memory-read/         # 按需读取记忆
└── project-memory-maintenance/ # 写入、修订、去重与索引维护
```

### 六层记忆

| 层级 | 主要职责 | 默认写入方式 |
| --- | --- | --- |
| `library` | 跨项目共享知识 | 需要用户明确授权；本仓库不包含该层内容 |
| `guardrails` | 当前项目的规则、约束和模板 | 需要用户明确授权 |
| `modules` | 当前项目已核验的业务、页面、接口和数据事实 | 任务内核验后可自动维护 |
| `changes` | 重要行为、接口、数据、架构或依赖变更 | 发生重要变更后按日期 JSONL 追加 |
| `lessons` | 有证据、可复用的排错与实施经验 | 形成持续价值经验后维护 |
| `plans` | 大需求或复杂问题的范围、依赖、验收和回滚计划 | 满足大需求门槛后创建或修订 |

层级优先级和读取条件以 `memory/INDEX.md` 为准。`library` 与 `guardrails` 属于受保护层，不会因为普通检索或建议自动写入。

## 核心工作流

1. **定位**：从 `memory/INDEX.md` 开始，按任务路由选择首读层。
2. **精确读取**：优先按 `memory_id`、文件路径、接口、模块名或唯一标题定位，再按关键词扩大范围。
3. **核验缺口**：记忆不足时，只检查当前任务需要的代码、配置、数据库或用户材料；不以摘要替代事实。
4. **维护**：把本轮已核验且具有持续价值的增量写入合适层级，并同步直接索引。
5. **校验**：检查 JSONL 格式、文件布局、稳定 ID、来源和可选派生索引状态。

事实优先级为：运行结果和有效数据 > 当前代码、配置及数据库 > `modules` > `changes` > `plans` > `library`。普通 Markdown 和 `changes/*.jsonl` 是权威来源；manifest、SQLite/FTS5、缓存和摘要都可以重建。

## 配套自动化流程

### `project-memory-init`

初始化 `memory` 六层目录、根索引和分层索引，并提供可选的知识索引、工作区审计和会话状态模板。初始化阶段只创建骨架，不扫描业务代码，也不生成虚构事实。该流程可以迁移到其他 Agent 或自动化工具。

### `project-memory-read`

按“索引定位 → 精确读取 → 必要的缺口探索”获取最小证据。它保持读取阶段只读，遇到已核验的新事实时，将维护候选交接给维护流程；检索策略不依赖特定模型。

### `project-memory-maintenance`

负责记忆正文、直接索引、`changes` JSONL、稳定 ID、来源和审计信息的维护。它会区分自动维护层与需要明确授权的 `library`、`guardrails` 层，并在派生索引不可用时回退到 Markdown 和 JSONL。

## `changes` 格式

每行一条记录，文件名为 `YYYY-MM-DD.jsonl`，字段固定为：

```json
{
  "change_id": "CHG-20261009-001",
  "timestamp": "2026-10-09T13:13:20+08:00",
  "issue": "changes_jsonl_maintenance_workflow",
  "observation": "记录变更现象、原因、处理方式、验证结果和未确认事项"
}
```

`change_id` 用于唯一引用和去重，`timestamp` 保留完整时区，`issue` 用于搜索归类，`observation` 保存完整变更事实。不要为单条变更记录创建 Markdown 文件或索引行。

## 快速开始

### 1. 选择版本

当前版本和前两代版本按顺序放在 Git 分支和 Releases 中：

| 版本 | 分支 | Release |
| --- | --- | --- |
| v1 | [`v1`](https://github.com/LHN012/project-memory-skills/tree/v1) | [`v1.0.0`](https://github.com/LHN012/project-memory-skills/releases/tag/v1.0.0) |
| v2 | [`v2`](https://github.com/LHN012/project-memory-skills/tree/v2) | [`v2.0.0`](https://github.com/LHN012/project-memory-skills/releases/tag/v2.0.0) |
| v3 / current | [`main`](https://github.com/LHN012/project-memory-skills/tree/main) | [`v3.0.0`](https://github.com/LHN012/project-memory-skills/releases/tag/v3.0.0) |

优先使用最新版本；需要复现历史项目时，切换对应分支或下载对应 Release 的 zip 包。

### 2. 安装 Skills

从 [Releases](https://github.com/LHN012/project-memory-skills/releases) 下载对应版本的 `project-memory-skills-*.zip`，解压后将 `skills/` 下的 Skill 目录复制到所使用的 Agent 的 Skill 目录。不同 Agent 的安装目录名称可能不同，保持每个 Skill 目录的完整结构即可。

当前版本包含 `project-memory-init`、`project-memory-read` 和 `project-memory-maintenance` 三个核心流程。v1、v2 的安装包保留各自时代的 Skill 集合。

### 3. 初始化项目记忆

将本仓库的 `memory/` 目录复制到目标项目根目录，或让初始化 Skill 在目标项目中创建同样的结构。初始化阶段只创建索引骨架，不扫描业务代码，也不生成虚构事实。

### 4. 按任务读取和维护

从 `memory/INDEX.md` 开始，根据任务选择 `guardrails`、`modules`、`changes`、`lessons` 或 `plans`。先精确读取，再按缺口核验必要来源；本轮形成持续价值的事实、变更、经验或计划按规则写回对应层。

### 5. 运行校验

在项目根目录执行只读校验：

```powershell
python -B skills/project-memory-maintenance/scripts/validate_changes.py --project-root .
python -B skills/project-memory-init/templates/knowledge/scripts/check_layout.py --project-root .
python -B skills/project-memory-init/templates/knowledge/scripts/check_index.py --project-root .
```

没有启用 SQLite/FTS5 时，`check_index.py` 返回 `database_missing` 属于预期状态；Markdown 记忆和日期 JSONL 仍然可以独立使用。

## Releases

Skills 压缩包按版本顺序发布在 [Releases](https://github.com/LHN012/project-memory-skills/releases)。每个压缩包只包含对应版本的 `skills/`，不包含项目 `memory/`、跨项目 `library/` 或额外文档。

## 发布边界

本仓库明确不包含：

- `memory/library/` 跨项目共享知识库；
- `docs/` 设计文档；
- `.codex/` 工作区包装目录和 PPT 修订产物；
- 其他与记忆系统无关的本地工作区文件。

如果未来需要公开仓库，请先检查 `guardrails`、`changes` 和 `modules` 中是否包含项目名称、内部地址、业务代码或其他不宜公开的上下文。

## 许可

当前仓库未声明开源许可证。若要公开分发，请先补充合适的 `LICENSE` 文件。


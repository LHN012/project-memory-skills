---
name: project-memory-maintenance
description: Automatically maintain an existing project's `.codex/memory` after task-scoped discovery, verified fact corrections, meaningful changes, reusable lessons, or major requirement plan updates. Plans are limited to major requirements from source materials and complex problems needing phased work. Library and guardrails require explicit authorization; explicit no-write tasks remain read-only. Do not initialize the architecture.
---

# 项目记忆维护

负责记忆写入、修订、去重、状态管理和稀疏导航索引同步。各层按自身格式确定权威来源：普通记忆正文和导航索引使用 Markdown，`changes/*.jsonl` 使用按日期追加的 JSONL；manifest、SQLite/FTS5、向量索引、证据缓存和会话清单均为可重建派生物。

## 自动接续与增量沉淀

维护是项目任务的内置收尾阶段，不要求用户另说“记录一下”或单独调用本 Skill。已启用本架构的项目中，了解、解释、诊断、列计划和实施任务都按下方分层条件判断是否需要维护；仅检索已有且仍有效的记忆，没有新增事实或状态变化时不写入。

1. 接收 `project-memory-read` 的会话内缺口和维护交接，或本轮实施中形成的事实、变更、经验与计划状态；不要求生成交接文件。
2. 只对本轮已核验、具有持续价值且尚未记录或已经过期的内容维护。信息已有且一致时复用，不重复建条目或仅刷新时间戳。
3. 按分层条件筛选可自动写入项；`library`、`guardrails` 未获授权的候选只报告，不阻断其他层的正常维护。用户已给出的对应授权无需再次询问。
4. 复用当前会话的新鲜证据和现有 ID，只补必要的来源定位、哈希与缺口核验，不为写记忆重新遍历项目。页面只核对当前任务涉及的链路，未知部分保留 `partial` 和待确认项。
5. 在一批事实核验完成、实施结束或当前轮次答复前，集中写入对应 Markdown 正文或 `changes` JSONL；正文写入后即时更新直接索引，祖先索引只在一批写入结束、路由信息变化或显式刷新时更新。随后按需同步派生索引并校验与审计。`changes` 不创建单条索引行。不得只口头总结后等待用户追问才补写。
6. 简要报告实际新增或修订的记忆路径及未完成原因。不能安全写入时保留任务结论，明确报告维护未完成；不得宣称已自动沉淀。

用户明确要求“不要修改任何文件”“不要写入记忆”或“严格只读”时，本轮不写入正文、索引、缓存或会话状态，仅返回会话内维护候选。“了解一下”“先列计划”“不改业务代码”仅限制业务实施，不自动关闭已启用的记忆维护。自动维护不授权修改业务代码、执行数据库变更或启用可选服务。

## 前置检查

1. 按“用户指定目录 > 当前工作目录”定位项目目录；不要自动切换到更宽的工作区根目录或上溯 Git 根目录。
2. 查找 `<项目目录>/.codex/memory/INDEX.md`。
3. 若记忆架构不存在，`STOP`：报告需要先运行初始化 Skill，不自行创建整套架构。
4. 读取根索引、目标层索引和拟修改条目，确认路由、权限和已有 ID。
5. 若存在机器派生索引，检查其版本或新鲜度；缺失、过期或损坏时，普通记忆回退 Markdown，`changes` 回退日期文件和 JSONL 文本，不阻断维护。
6. 若项目存在 Git，先运行 `check_memory_freshness.py`。需求计划返回 `not_applicable`，按正文来源、依赖和待补充检查，不自动补 Git 核验字段。代码变更命中条目的 `impact_paths` 或证据文件时，条目必须先进入刷新流程；没有 `verified_commit`、来源哈希不匹配或历史分叉的条目不得继续作为当前事实使用。

用户原始材料默认位于 `<项目目录>/.codex/source-materials/`。该目录只作为 `user_material` 证据来源，不属于六层记忆，不写入导航索引，也不得在维护过程中改写原文件。

## 写入边界与副作用防护

记忆维护是受限写入流程。默认只允许修改：

- `.codex/memory/`：普通记忆 Markdown 正文、稀疏 `INDEX.md` 和 `changes/YYYY-MM-DD.jsonl`；
- `.codex/.knowledge/`：由已启用的索引脚本维护的 manifest、SQLite/FTS5 等派生物；
- `.codex/.runtime/`：已启用的会话状态和临时文件。

`.codex/source-materials/` 永远只读。项目根目录、源码目录、配置目录、业务数据库目录以及其他未声明路径均禁止写入。不要为了预览、解析 SQL、整理表结构或生成备份在这些位置创建目录或文件。

每次涉及写入的维护操作都应遵循以下顺序。若同轮还要实施业务变更，先完成该批已授权的业务变更，再对独立的记忆写入阶段建立快照；快照至审计之间不穿插业务代码修改，避免把正常实施误判为记忆副作用。

1. 写入前用项目内 `workspace_guard.py snapshot` 保存工作区快照；快照文件放在 `.codex/.runtime/tmp/` 或系统临时目录。
2. Markdown 正文和索引使用结构化文件 API 或 `safe_write.py` 写入；`changes` 使用本 Skill 的 `scripts/append_change.py` 追加并用 `scripts/validate_changes.py` 校验。目标路径先执行 `workspace_guard.py check-write`。`safe_write.py` 仍只负责 `.codex/memory/**/*.md`，不得用它替换 JSONL 时间线。
3. 写入、索引同步和校验完成后执行 `workspace_guard.py audit --before ...`。结果为 `blocked` 时立即停止，不自动删除或“顺手整理”异常路径，并报告完整路径和变更类型。

若项目尚未复制 `.codex/.knowledge/scripts/workspace_guard.py`，使用同项目 `.codex/skills/project-memory-init/templates/knowledge/scripts/workspace_guard.py` 并传入 `--project-root`；同目录的 `safe_write.py`、`check_layout.py` 负责 Markdown 记忆，`changes` 由本 Skill 的 JSONL 脚本负责，不需要先启用机器索引。不得为了补齐工具而在项目根目录临时创建脚本。若当前环境连审计脚本也不可用，只能进行只读检查或停止写入，不得宣称已完成副作用审计，并应把该项列为未完成。

调用 Python 辅助脚本统一加 `-B`，避免导入同目录模块时在 Skill 模板目录生成 `__pycache__`，导致记忆维护越界。

禁止使用 PowerShell `md`、`mkdir`、`ni`、`New-Item` 别名、`>`/`>>` 重定向或字符串拼接命令承载字段名、类型、表注释、用户材料内容。SQL 和表格分析默认只读，预览输出到终端或内存；临时文件只能写入 `.codex/.runtime/tmp/` 或系统临时目录。无法确认目标路径、命令是否有副作用或快照审计失败时，必须 `STOP`，不得继续写入。

工作区审计只报告异常，不代替用户决定删除、恢复或移动文件。若审计发现与本次维护无关的并发改动，保留现场并请求确认。

## SQLite/FTS5 同步

只有项目已启用 `.codex/.knowledge/manifest.yaml` 和脚本时才调用机器索引。Markdown 记忆写入和直接/按需祖先索引更新后执行：

```text
python -B .codex/.knowledge/scripts/sync_index.py --changed <相对文件路径>...
```

规则：

- 小范围修改使用 `--changed` 增量更新；删除的路径也可以传入，脚本负责移除对应节点。
- 首次建立、schema 变化、索引损坏或无法确认变化范围时使用 `--rebuild`。
- 脚本返回 `fresh` 才更新索引状态；返回 `stale`、`missing` 或执行失败时保留 Markdown，报告派生层状态，不阻断记忆维护。
- 只在 manifest 声明的 `schema_version` 和脚本版本兼容时更新数据库；未知 schema 不得直接修改。
- 完成后可执行 `check_index.py` 校验重复 ID、失效来源、父子关系、文件和证据哈希、关系数据及 FTS5 状态；可执行 `check_layout.py` 校验根目录平铺、`record_path` 和重复稳定 ID。

若脚本目录不存在或运行时没有可用 Python/SQLite，跳过派生索引并报告“普通 Markdown 已更新，派生索引未启用”。维护 Skill 不临时生成替代 SQL。

`changes/*.jsonl` 不参与 Markdown 导航索引或 SQLite/FTS5 Markdown 同步。写入 `changes` 后运行 `python -B .codex/skills/project-memory-maintenance/scripts/validate_changes.py --project-root .`；读取时按日期文件名、`change_id`、`issue` 和文本内容定位记录。

## 备份与恢复

`.codex/memory/` 下的 Markdown、稀疏 `INDEX.md` 和 `changes/*.jsonl` 应纳入项目版本控制或其他可恢复备份。批量整理、目录迁移或大范围重写前，先创建版本节点或备份副本。恢复普通记忆时以 Markdown 和索引为准，再使用 `sync_index.py --rebuild` 重建 SQLite/FTS5；恢复 `changes` 时先运行 `validate_changes.py`。不要把 `index.sqlite` 当作唯一备份，也不要手工修复派生数据库。

## 轻量关系图与会话状态

`parent_id` 和 `relations` 是当前唯一的关系图来源。维护正文时同步关系边；读取只做一跳扩展，最多返回 3 条关系边和对应目标节点。不要自动创建图数据库或把未验证的模型推断写成关系。

若项目已启用 `.codex/.runtime/session_state.py`，在一轮工作结束后可以保存任务目标、完成步骤、变更文件、测试结果和待确认项。会话状态只用于恢复工作，不进入六层记忆，也不替代 `changes`、`plans` 或 `lessons`。Hook 或脚本失败不得阻断记忆维护。

示例：

```text
python -B .codex/.runtime/session_state.py save --goal "完成订单状态流转" --step "已核对接口" --changed src/order.ts --test "unit tests"
python -B .codex/.runtime/session_state.py show
```

向量检索当前关闭。不得因维护任务安装 embedding 模型、向量库或外部服务；未来启用时只能把它作为 FTS5 之后的候选召回层，并以 `record_hash` 判断是否过期。

## 知识库目录归档

写入 `library` 时必须先按内容分类，禁止把具体知识条目直接放在 `library/` 根目录。当前分类约定为：

| 内容类型 | 归档目录 |
| --- | --- |
| 代码、SQL、数据库和操作规则 | `library/规则库/` |
| 样式、视觉和交互规范 | `library/样式库/` |
| 可复用组件及其接入资料 | `library/组件库/` |

新增主题只有在条目规模、索引长度或独立检索边界确实需要时才创建主题目录和对应 `INDEX.md`；小主题直接挂在已有层级，由上级索引导航。归档路径必须反映内容分类，`record_path`、索引链接和 Skill 引用必须同步更新。

## 分层路由与授权

| 层级 | 触发方式 | 写入条件与边界 |
| --- | --- | --- |
| `library` | 用户明确授权 | 用户确定纳入、修订或删除某项共享知识后写入；跨项目经验只能先提议，不自动归档或改动共享组件 |
| `guardrails` | 用户明确授权 | 用户确定保存或修订某条项目约束后写入；不得把 Agent 的建议或临时做法升级为强制规则 |
| `modules` | 条件满足后自动 | 索引缺失、条目部分覆盖、信息过期或实际实现变化，且任务内已从代码、配置、数据库或运行结果核验出有持续价值的事实时，自动新增或修订；用户材料按来源核验，未知内容不补猜测 |
| `changes` | 条件满足后自动 | 本轮实际造成重要行为、接口、数据、架构或依赖变化后记录；只读了解、仅列计划、普通记忆补写和无实质影响的小改动不创建变更日志 |
| `lessons` | 条件满足后自动 | 实施、调试或工具使用中获得有证据、能避免重复踩坑的经验时记录或合并；不逐次记录临时错误和重复尝试，有共享价值时可提议归档到 `library` |
| `plans` | 条件满足后自动 | 仅为材料中的大需求，或需要分阶段处理且有依赖、待确认项或验收安排的复杂问题创建详细计划；普通对话、小修改和日常任务不创建计划或日计划。已有需求更新原计划，具体规则见 references/plans-format.md |

用户明确说“加入 library”或“加入 guardrails”即构成对应写入授权；只说“记录一下”“更新记忆”不构成受保护层授权。若用户意图是建议而非授权，仅停止对应受保护项并报告，继续其他已满足条件的自动维护。已授权条目写入后，同步其索引属于该次维护的一部分；不得顺带重排受保护层其他内容。

## 稳定元数据

需求计划正文使用 `plan_id`、`plan_state`、`updated_at` 三字段头，仅替代旧版本时加 `supersedes`；日期/版本从文件名读取，来源/范围/进度在正文。不得套用下方普通元数据或自动补回冗余字段；唯一版本节点 ID 与哈希由索引推导。`plans/INDEX.md` 仍是普通导航索引。具体格式见 [plans-format.md](references/plans-format.md)。

除 `plans/` 下的需求正文文件和 `modules/` 导航索引外，`modules` 事实文档也使用轻量头；导航索引和事实文档按 [modules-format.md](references/modules-format.md) 区分，不把机器审计字段塞回正文头。

```yaml
memory_id: MOD-ORDER-SAVE-001
type: module
status: verified
coverage: partial
updated_at: 2026-09-23
```

规则：

- 优先复用已有 `memory_id`；没有时先对 `.codex/memory` 的索引和元数据做精确 ID 搜索，确认无冲突后再创建稳定、可预测且唯一的 ID。
- ID 不因标题、文件名或路径变化而修改。
- 旧 Markdown 没有元数据时使用 `metadata_state: legacy`，只在首次触碰时补充，不批量重写历史内容。
- `status` 使用 `draft`、`derived`、`verified` 或 `deprecated`；`metadata_state` 使用 `native` 或 `legacy`，二者不得混用。
- `draft` 和 `derived` 不得作为高风险修改的唯一证据；`deprecated` 默认不进入证据包。
- `modules` 事实文档的头部只保留 `memory_id`、`type: module`、`status`、`coverage`、`updated_at`；页面、共享文档、接口和数据表的 `record_level` 写入 `modules/.audit.json`，不再把层级字段塞回正文头。
- `metadata_state`、`record_anchor`、`record_path`、`scope`、`aliases`、`parent_id`、`relations`、`evidence_sources`、`verified_commit`、`impact_paths`、`working_tree_verified` 和 `record_hash` 写入 `modules/.audit.json`，按相对路径关联；不得重新塞回正文头。
- `evidence_sources` 记录代码、配置、数据库、原始文档、运行结果或用户决策等事实来源；`evidence_hash` 哈希原始证据，`record_hash` 哈希 UTF-8、LF 规范化后的正文。两者由维护脚本生成或更新，不手工伪造。
- `verified_commit` 指向最后一次核验事实的 Git 提交；`impact_paths` 描述代码、配置、迁移或数据路径。命中变更后不得只改时间戳，必须重新读取来源、更新侧车审计和事实正文。

## 写入标准

每条 Markdown 记忆必须有持续价值、可指认来源、适用范围、状态和更新时间；普通记忆还应有关键词或别名，需求计划的来源和范围记录在正文，不为此增加文件头字段。未验证内容必须标记为 `draft` 或“待确认”；`changes` 记录按日期 JSONL 规则校验，不使用这组 Markdown 元数据。

事实可信度依次为：运行结果和有效数据 > 当前代码、配置及数据库 > `modules` > `changes` > `plans` > `library`。

`modules` 描述当前事实，`plans` 描述预期；计划未实施的内容不得写入 `modules`。项目实际采用的组件版本和配置写入 `modules`，不得自动回写 `library`。

## 页面级模块记录

详细规则见 [modules-format.md](references/modules-format.md)。`modules` 只记录当前事实：跨页面业务对象、状态、系统地图、数据权威和通用安全规则集中在 `modules/shared/`；页面文档只记录页面目的与边界、当前行为与数据链路、页面权限、接口用途、当前兼容契约和未决项。页面按业务域目录归档，业务域 `INDEX.md` 仅在同域页面较多或需要独立检索边界时创建。接口按接口族整理到 `modules/interfaces/`，数据库表按表整理到 `modules/data/`。

`modules` 不维护按日期排列的变更记录，不记录实施过程、测试过程或回滚步骤；这些内容写入 `changes/YYYY-MM-DD.jsonl`。历史原因只引用 `change_id`，不复制变更正文。

整体梳理写入前必须生成覆盖清单，至少对照路由、页面文件、API、后端边界和数据表。单页面任务只核对该页面涉及的链路，可将已知范围与未确认项放在页面正文，不为一次补写建立全项目清单。每个候选页面标记 `covered`、`partial` 或 `excluded` 及原因；不得因为顶层摘要已有内容就跳过页面文档。`verified` 只表示该条事实有证据，不表示页面覆盖完整；页面条目应另记录 `coverage` 和未确认项。新建页面条目不得直接放在 `modules/` 根目录；`check_layout.py` 从 `modules/.audit.json` 的 `record_level: page` 判断页面布局。已有域级摘要可以暂时保留在根目录，但应视为迁移候选，不能计入页面覆盖完成度。

## 业务数据库表结构记录

业务数据库表结构属于 `modules`。记录时遵循 `library/规则库/数据库规范/数据库表结构记录规范.md` 和 `guardrails/数据库表结构记录约束.md`：

当用户要求新建表或设计表结构时，先读取 `references/database-table-creation.md`。决策顺序是“当前项目已有表风格优先；没有可比表时采用精简的阿里规范基线；按当前功能选择必要字段组”。建表前必须解释每个选中字段组的作用和本表创建目的；未选中的常见字段组说明不创建的原因。不得为了完整性自动加入租户、审计、逻辑删除、状态或乐观锁字段。

- 信息来源只分为 `user_material`（`.codex/source-materials/` 中的用户原始材料）和 `code_sql`（代码、迁移脚本、Mapper/XML、注解或可定位 SQL）；
- 最低记录表名、表注释、表作用、字段名、字段类型、字段注释，以及字段关联的目标表、目标字段和关联用途；
- 表作用可以基于证据理解后补充，但推断内容必须标记为 `derived` 或待确认；没有证据不得创建表关联；
- 项目业务表总量超过 200 张时，才按功能模块拆分表目录；同一张表只保留一个权威条目，跨模块使用稳定 `memory_id` 引用；
- 当前结构写入 `modules`，变更原因、影响范围和回滚线索写入 `changes`，敏感数据不得写入记忆。

## 变更、经验与计划

`changes` 使用独立的日期 JSONL 时间线，详细格式见 [references/changes-format.md](references/changes-format.md)：文件名为 `YYYY-MM-DD.jsonl`，同日记录追加到同一文件，每行只包含 `change_id`、`timestamp`、`issue`、`observation` 四个字段。使用 `scripts/append_change.py` 写入，使用 `scripts/validate_changes.py` 校验，不为单条记录创建 Markdown 文件或索引行。

经验条目至少包括：触发条件、问题表现、根因、有效解决方式、不适用场景和验证依据。

创建、更新或修订大需求计划时，读取 [references/plans-format.md](references/plans-format.md)，使用 [assets/requirement-plan-template.md](assets/requirement-plan-template.md) 的详细结构。文件名固定为 `YYYY-MM-DD-vN.md`，进度维护不新增版本；范围、方案或关键约束实质变化时保留旧版本并建立版本关系。`plans/INDEX.md` 只登记文件级需求简介和版本/状态，不展开需求清单。实施前检查清单的可立即实施标记、依赖和 P0/P1 待补充事项；存在未解决 P0 时禁止实施其影响及依赖部分。

仅列计划时，已核验的现状自动沉淀到 `modules`；拟实施方案只有满足大需求或复杂问题条件时才写入 `plans`，小任务的步骤留在会话中。“先列计划”本身不触发计划文件。计划不额外授予实施权限，沿用当前会话已有授权；不生成 `changes`，也不把拟新增页面写成现有事实。实施完成后，按实际实现更新受影响的 `modules`、已有且关联的大需求 `plans` 的进度，以及满足重要变更条件的 `changes`。

## 派生索引与失效

### 代码变更后的自动刷新

代码协作者不需要手工维护项目记忆。拉取或合并代码后，先运行：

```text
python -B .codex/skills/project-memory-maintenance/scripts/check_memory_freshness.py --project-root .
```

对输出中 `refreshable: true` 且类型为 `module` 或 `page` 的条目，可以在当前维护轮次自动刷新：

1. 读取该条目的父级索引、正文和 `refresh_queue` 中列出的变更文件。
2. 以当前代码、配置、数据库或运行结果为证据，只更新受影响的模块/页面事实。
3. 将 `verified_commit` 更新为当前 HEAD，重新计算 `evidence_hash`，必要时调整 `coverage` 和未确认项。
4. 更新直接索引；若本批写入已结束、路由信息发生变化或收到显式刷新要求，再更新受影响的祖先索引。不要因为单条正文变化重写整条索引链。
5. 运行 `check_index.py`、`check_layout.py` 和工作区审计，并报告自动刷新条目及未解决项。

以下情况不得自动改写事实，应进入 `needs_review`：跨模块重构、权限/安全变更、数据库迁移、删除或重命名导致的历史分叉、来源文件缺失、证据哈希无法核验、没有稳定 `verified_commit`，以及无法判断代码意图的行为变化。自动刷新只允许更新 `modules` 和页面记录，不得顺手修改 `guardrails`、`plans` 或 `library`。

写入 Markdown 正文后：

1. 更新条目所在目录的 `INDEX.md`；目录没有索引且规模未达到拆分阈值时，不为单条记录新建索引。
2. 在本批写入结束、路由字段变化或显式刷新时，逐级更新受影响的祖先索引；普通小修改允许暂缓祖先摘要刷新，但必须在维护结果中标记待刷新状态。
3. 若 manifest 或 SQLite/FTS5 存在，按上面的同步命令，仅在其声明的 schema、版本和更新器兼容时更新受影响节点；否则不直接修改未知数据库。机器索引默认不启用。
4. 若派生索引无法安全更新，使用既定 `stale` 标记；没有标记协议时只报告 stale，不假装已更新。
5. 普通记忆正文、标题、路径或关系变化时，更新 `modules/.audit.json` 中对应记录的 `record_path`、`record_anchor`、`record_hash`、`evidence_hash` 和关系边；需求计划只维护轻量头、正文和文件级导航，索引所需字段由脚本推导。
6. 对失效链接、重复 ID、无来源节点和不一致状态进行检查。

派生索引不存在时不得因缺少数据库或向量依赖而失败；继续维护普通 Markdown，并报告“派生索引未启用”。`changes` 仍按 JSONL 规则独立校验，不因 Markdown 派生索引缺失而失败。

## CHECKPOINT

写入结束前必须确认：

- 是否写入了正确层级。
- 是否已接续本轮缺口探索的增量沉淀，或明确说明不写入的原因，而不是等待用户另行触发。
- `library`/`guardrails` 是否有明确授权。
- 普通记忆是否复用了或创建了唯一 `memory_id`；需求计划是否保持稳定 `plan_id` 与唯一日期-vN文件名。
- 正文、原始证据、状态、哈希和索引是否一致。
- 对整体梳理任务，是否有页面级覆盖清单，且没有未说明的路由或页面。
- 页面条目是否位于 `modules/<业务域>/`，而不是 `modules/` 根目录。
- 工作区前后快照审计是否为 `fresh`；若为 `blocked`、缺失或未执行，是否已停止写入并报告。
- 是否存在冲突、失效链接、待确认项或 stale 派生索引。

## 失败处理

| 触发条件 | 一线处理 | 仍失败时 |
| --- | --- | --- |
| 记忆架构不存在 | `STOP`，要求初始化 | 不写入任何层 |
| ID 已存在但指向不同事实 | 停止合并，保留候选 | 报告 ID 冲突，等待确认 |
| 找不到来源或验证依据 | 标记 `draft`/待确认 | 不得写成 `verified` |
| Markdown 索引损坏或格式不一致 | 局部修复并保留原文 | 报告冲突，不重排无关索引 |
| `changes` JSONL 格式错误或重复 ID | 停止追加，报告日期文件和记录行 | 不覆盖历史记录，修复后再追加 |
| 派生索引缺失/过期/损坏 | 回退 Markdown；兼容时标记 `stale` | 不阻断正文写入 |
| 索引出现失效链接 | 修正直接受影响的索引 | 无法确认正文时不得删除条目 |
| 受保护层授权不清 | 跳过对应项并列出待确认项 | 不写入 `library`/`guardrails`，继续其他已授权或可自动维护层 |
| 工作区审计发现未授权路径 | `STOP`，保留现场并报告路径、类型和时间 | 不自动删除、移动或恢复 |
| 审计脚本缺失或执行失败 | 只读维护或停止写入，并报告未完成审计 | 不用 PowerShell 临时替代 |

## 稀疏索引格式

每个目录只索引直接子条目或子索引，字段统一为：

```markdown
| ID | 触发词 | 摘要 | 适用范围 | 路径 | 优先级 | 状态 | 更新时间 |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

默认 Markdown 索引深度最多三层；直接条目超过 30 至 50 个、索引超过约 100 行或需要独立检索边界时才按主题拆分。`changes` 不按主题、月份或记录条目继续拆目录，始终使用 `YYYY-MM-DD.jsonl` 日期文件；规模变大时通过日期文件和文本检索定位。`plans` 的大需求文件直接保存为 `YYYY-MM-DD-vN.md`，按文件级简介检索，历史版本留在原目录并标明被替代关系，不创建日计划或逐条需求索引。单次关系扩展最多返回 3 个关系节点、总证据最多 8 个条目；超出的候选进入缺口列表，不继续扩大上下文。

## 不要做

- 不要因一次小修改而读取或重建全库。
- 不要把摘要、向量结果或缓存当作权威事实。
- 不要未经授权修改 `library` 或 `guardrails`。
- 不要只更新正文而遗漏直接索引；祖先索引若被暂缓，必须在本批结束或维护报告中标明待刷新。
- 不要因 SQLite、向量库或脚本不可用而阻断普通记忆或 `changes` 维护。
- 不要把未验证 AI 生成内容写成 `verified`。
- 不要为每次检索创建记忆、复制整段对话或重复记录相同事实。
- 不要把读取阶段只读误解为整轮禁止自动维护，也不要越过用户明确的禁止写入指令。

## 完成条件

正文、元数据和直接索引一致；已触发刷新的祖先索引一致，暂缓项有明确待刷新标记；受保护层授权明确；来源和状态可追溯；派生索引状态明确；无重复 ID、失效链接、敏感信息或无关改写。向用户报告写入、修订、未写入、冲突和 stale 项。

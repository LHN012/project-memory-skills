---
name: model-implement
description: "优先调用 model-context-rag 定位初始化报告、模块报告和历史记忆，再结合原型目录/图片、已有代码风格和 knowledge-library 命中资料，为指定模块生成逐页面详细前后端实施方案以及模块关联文档。适用于初始化已产出初始化契约、代码及框架信息、已有功能模块信息、待办清单、业务理解、数据库审查报告、待确认点和 module-readiness 后，开展模块级详细规划。触发词：页面方案、模块规划、frontend-plan、backend-plan、module-relations、生成实施方案、RAG辅助规划。不要用它做项目初始化、直接写代码或自动进入 executor；后续 model-implement-executor 必须由用户另行明确触发。"
---

# Model Implement

## 概述

这个 skill 用于把已经准备好的初始化上下文、目标模块原型、RAG 检索定位结果和可复用知识，转化为可直接供 Codex/executor 阅读的页面级详细实施方案。它属于流程中的详细规划阶段，只应在 `model-implement-init` 完成前期准备后再启动。

RAG 只负责定位候选上下文，不能替代原文精读。最终方案中的事实、判断和引用必须来自命中的原始报告、原型材料、代码或知识库原文。

## 触发与交付速查

- 触发词：页面方案、模块规划、详细实施方案、前后端方案、`frontend-plan.md`、`backend-plan.md`、`module-relations.md`。
- 必要输入：目标模块名、已完成的新版初始化报告、`module-readiness.md`、目标模块原型或需求材料、`model-context-rag` 状态/检索结果、知识库入口或缺失说明。
- 必须产出：`module-relations.md`、每个目标界面的 `frontend-plan.md` 和 `backend-plan.md`，以及业务闭环检查清单。
- 交付出口：方案完成后停止；只写清 executor 后续实施建议，不自动调用、不自动交给 `model-implement-executor`。用户明确再次触发实施时，才进入 `model-implement-executor`。

## 工作区

统一使用 `.codex/model-implement/` 作为共享工作区：

- `prototypes/<模块名>/`：用户提供的原型图、说明文档和模块补充材料。
- `.sql/`：由初始化阶段优先评估过的共享 SQL 目录。
- `library/定义规则.md`：知识库入口；若 `.codex/model-implement/library/` 存在，本 skill 应先读取该入口，并按当前模块命中的规则、组件、样式或特殊资料继续读取相关路径，不默认读取 `library/README.md`，也不递归全量读取知识库。
- `reports/init-airead/source-manifest.json`：初始化阶段生成的输入指纹清单，本 skill 将其视为输入而不是自己刷新。
- `reports/init-read/初始化契约.md`：初始化输入、输出、脱敏、严重等级和下游交接规则。
- `reports/init-read/代码及框架信息.md`：项目技术栈、框架版本、工程约定、代码风格、权限/请求/数据库方言等事实。
- `reports/init-read/已有功能模块信息.md`：已有模块、界面名、入口、动作、接口和可复用能力。
- `reports/init-read/待办清单.md`：目标模块或任务是否属于新增页面、已有界面改造、批量问题修复或待归类材料。
- `reports/init-read/业务理解.md`：业务流程、页面穿透、弹窗/详情/编辑链路和跨模块流转。
- `reports/init-read/数据库审查报告.md`：数据库覆盖、必须/建议补充的表字段、索引和严重等级。
- `reports/init-read/待确认点.md`：仍会影响实现方向的确认点和严重等级。
- `reports/modules/<模块名>/module-readiness.md`：控制详细页面规划是否允许继续的模块准备度文档。
- `reports/modules/<模块名>/module-relations.md`：本 skill 生成的模块级界面/业务/数据关联文档。
- `reports/modules/<模块名>/<界面名>/frontend-plan.md`：本 skill 为单个界面生成的前端实施方案。
- `reports/modules/<模块名>/<界面名>/backend-plan.md`：本 skill 为单个界面生成的后端实施方案。
- `reports/context-rag/`：`model-context-rag` 生成的机器检索索引和质量报告；本 skill 只通过 `rag-status.ps1`、`rag-search.ps1` 使用它，并且只把搜索结果当作原文定位线索。
- `memory/model-implement.jsonl`：页面规划阶段的观察、经验和规则候选。
- `memory/model-implement-rules.md`：页面规划阶段的私有稳定规则。
- `memory/init-rules.md`、`memory/executor-rules.md`、`memory/shared-memory.md` 与 `memory/shared-rules.md`：本 skill 只读使用，用于保持与其他阶段对齐。

## 工作流程

1. 若存在，先读取 `memory/model-implement-rules.md`、`memory/shared-rules.md` 和 `memory/shared-memory.md`。
2. 按 `model-context-rag/references/integration-contract.md` 的契约优先调用 RAG：先运行 `rag-status.ps1 -ModelRoot ".codex/model-implement" -Json`；若索引不存在或明显过期，可先运行 `rag-index.ps1` 后再检查状态。
3. 若 RAG 状态为 `healthy`，围绕目标模块、界面名、任务类型、待办、业务流程、数据库缺口、待确认点、已有可复用功能和框架风格执行多组 `rag-search.ps1`；若为 `warning`，允许搜索但必须扩大原文读取范围；若为 `blocked`，不要依赖检索结果，回退直接读取原始报告。
4. 按 RAG 结果中的 `source_path`、`heading`、`suggested_read` 打开原始报告精读，并在方案文档中记录“检索词、命中原文路径、精读结论”。不要把 `chunks.jsonl` 当作事实来源。
5. 确认目标模块已具备新版初始化产物：`reports/init-read/初始化契约.md`、`代码及框架信息.md`、`已有功能模块信息.md`、`待办清单.md`、`业务理解.md`、`数据库审查报告.md`、`待确认点.md`、`reports/init-airead/source-manifest.json`、`reports/modules/<模块名>/module-readiness.md`。若旧项目尚未迁移，可把旧的 `reports/init-airead/shared-context.md`、`business-flows.md`、`db-assessment.md` 作为历史辅助输入，但不能替代新版主报告。
6. 优先读取 `reports/modules/<模块名>/module-readiness.md`；如果状态是 `draft` 或 `blocked`，停止并暴露初始化阶段未解决的问题，不要继续生成详细方案。
7. 当 `module-readiness.md` 指向确认项时，读取 `reports/init-read/待确认点.md`，理解会影响当前模块的阻塞点、严重等级或兜底假设；旧路径 `reports/init-read/待人工确认.md` 仅作为历史兼容辅助。
8. 检查 `.codex/model-implement/library/` 是否存在：存在则读取 `library/定义规则.md`，再按目标模块、页面类型、组件类型、接口/权限/SQL/样式关键词调用 `knowledge-library` 的本地检索；只读取命中的规则、组件、样式或特殊资料路径，并在方案文档中列出实际参考路径和影响点；不存在则继续规划，但在相关文档里注明本轮未使用知识库。
9. 只为当前目标模块使用 `scripts/module_doc_bootstrap.py --module <模块名>` 创建或刷新页面方案目录。
10. 把初始化阶段原始文档作为主要事实来源；只有在解决该模块细节时，才补充查看原始代码、现有页面、组件实现、样式文件或 SQL，避免重新做一次项目级初始化。
11. 对目标模块目录下的每一张原型图，都生成一个界面目录，并在其中维护 `frontend-plan.md` 和 `backend-plan.md`；若原型目录还有说明文档、表格或截图命名线索，也要纳入“原型对照”。
12. 为目标模块生成唯一一份 `module-relations.md`，总结模块内部界面关系，以及与其他模块、其他界面的业务和数据关联。
13. 对每个界面的前端方案，必须写清样式依据：未额外说明时，默认以当前项目已有框架、设计系统、组件库和同类页面样式为主；原型用于校准布局结构、组件组合、相对位置、业务差异和明确标注的新视觉要求；不要脱离当前框架自行设计替代样式。
14. 对每个界面的后端方案，必须把表、字段、接口和状态写成带业务含义的人能读懂的描述，不要只抛字段名、表名或路由名。
15. 在完成模块与页面文档前，必须补齐业务闭环检查清单；若某项未知且会实质影响实施，则保持相关文档为 `draft` 或 `blocked`。
16. 本 skill 只负责文档和方案，不负责编码实施。产出完成后停止，等待用户决定是否另行触发 `model-implement-executor`。
17. 结束前，将有价值的规划观察或规则候选写入 `memory/model-implement.jsonl`，把稳定规则提升到 `memory/model-implement-rules.md`；共享规则合成默认仍由 `model-implement-init` 负责。

## 🔴 CHECKPOINT · 启动门禁

遇到以下任一情况，必须停止生成页面级方案，先把阻塞项写清楚并等待用户确认：

- `module-readiness.md` 不存在，或状态为 `draft`、`blocked`。
- 初始化产物缺失，且兼容旧路径也找不到可用上下文。
- `model-context-rag` 为 `blocked` 且直接读取原始报告也无法确认当前模块关键上下文。
- 知识库入口 `library/定义规则.md` 存在但无法读取，或命中资料路径缺失。
- 原型、方案依据、当前框架样式之间存在冲突，且用户没有明确优先级。
- 用户要求直接写代码、跳过初始化、跳过准备度或自动进入 `model-implement-executor`；应提示实施必须由用户另行明确触发。

## 失败分支与兜底

| 触发条件 | 一线处理 | 仍失败兜底 |
|---|---|---|
| 初始化文档缺失 | 检查新版 6 份报告和 `初始化契约.md` 是否存在；旧报告只能作历史辅助 | 停止并提示先运行新版 `model-implement-init` |
| RAG 状态异常 | 先运行 `rag-status`，必要时运行 `rag-index` 后复查；`warning` 时扩大原文精读，`blocked` 时回退原文 | 若原文也不足以支撑规划，停止并写清缺口 |
| `module-readiness.md` 为 `draft`/`blocked` | 读取其中的未决项和 `init-read/待确认点.md` | 只输出阻塞摘要，不生成页面方案 |
| 知识库命中资料缺失 | 在方案中列出缺失路径和影响范围 | 将相关文档保持为 `blocked` |
| 原型与当前框架视觉冲突 | 写成差异点和待确认项 | 不自行选择新视觉，不标记 `confirmed` |
| 页面业务闭环未知 | 标出缺失的状态、权限、接口、验收或索引信息 | 对应页面方案保持 `draft` 或 `blocked` |

## 反模式黑名单

- 不要把初始化阶段重新做一遍；只读取与当前模块规划直接相关的事实。
- 不要把 RAG chunk 当作事实来源；RAG 只定位原文，方案事实必须来自原始报告、原型、代码或知识库原文。
- 不要在 `draft` 或 `blocked` 状态下伪造 `confirmed` 方案。
- 不要脱离当前框架、同类页面和知识库规则自由设计新视觉。
- 不要把页面方案写成空泛提示；必须落到界面目录、字段、接口、状态和验收清单。
- 不要自动调用实施或修复 skill；下一阶段必须由用户明确选择。

## 报告约束

- 初始化阶段文档是前置条件，不是可选参考。
- 模块级关联关系统一写到 `reports/modules/<模块名>/module-relations.md`。
- 界面级前端和后端细节统一写到 `reports/modules/<模块名>/<界面名>/frontend-plan.md` 与 `backend-plan.md`。
- 不要在生成目标模块文档前先额外生成模块列表或模块索引。
- 页面级方案文档要被视为后续实施的主依据。
- 页面级方案必须记录 RAG 检索词、命中的原始报告路径、实际精读结论和未命中的关键问题；如果没有使用 RAG，要说明原因和兜底读取范围。
- 页面级前端方案必须写清样式来源：当前框架/设计系统/同类页面/组件库/知识库样式资料/原型图分别提供了哪些依据。
- 未额外说明时，默认以当前项目已有框架、设计系统、组件库和同类页面样式为主；原型图用于校准布局结构、组件组合、相对位置、业务差异和明确的新视觉要求。
- 如果原型样式明显不同于当前框架，不能默认照搬，也不能自行裁决；应写成差异点和待确认项，等待用户确认是否引入新视觉。
- 不要自动调用、默认进入或声称已经交给 `model-implement-executor`；只写清后续实施建议，是否开始实施由用户再次明确触发。
- 模块和页面方案状态必须遵循 `references/status-contract.md`；`module-relations.md`、`frontend-plan.md`、`backend-plan.md` 只能使用 `draft`、`blocked`、`confirmed`、`implementing`、`done`。
- 如果还有会影响实施方向的未决问题，相关文档必须保持 `draft` 或 `blocked`，不要假装已确认。
- 每个模块和页面文档都要补齐业务闭环检查清单：状态枚举、权限/数据范围、写操作事务与幂等、关联模块影响、接口契约、验收用例、测试数据、性能/索引说明、待确认项。
- 不要在本 skill 中重写 `init-read/初始化契约.md`、`代码及框架信息.md`、`已有功能模块信息.md`、`待办清单.md`、`业务理解.md`、`数据库审查报告.md`、`待确认点.md` 或 `library/定义规则.md`；如果这些输入已过期或不足，应该停下来并建议先刷新 `model-implement-init` 或维护知识库。

## 规划深度要求

每一份 `frontend-plan.md` 都应细到足以让前端工程师直接开工，至少包含：

- RAG 检索记录、命中原文路径和精读结论。
- 原型对照：原型区域、当前系统同类页面、需要照原型实现的差异、需要沿用现有框架的部分、冲突待确认项。
- 布局分区与相对位置。
- 组件类型、数量和层级关系。
- 颜色、样式、视觉重点与状态差异。
- 样式依据优先级：用户明确要求 > 当前项目已有框架/设计系统/同类页面 > 已命中的知识库样式或组件规则 > 原型中的明确差异；若原型和当前框架冲突，只能写成待确认项，不能擅自补一套新视觉。
- 交互行为、显隐条件、校验提示、联动关系。
- 数据绑定、接口触发点、初始化加载逻辑。
- 推荐的前端实施步骤。

每一份 `backend-plan.md` 都应细到足以让后端工程师直接开工，至少包含：

- RAG 检索记录、命中原文路径和精读结论。
- 原型对照：界面动作、表单/列表字段、状态按钮和后端能力的映射。
- 页面涉及的业务动作。
- 所用表、字段、状态位、关联关系。
- 接口清单、请求/响应结构。
- 权限、数据范围、校验规则。
- 事务、幂等、并发或状态流转要求。
- 视图、存储过程、触发器、索引或性能注意事项。
- 推荐的后端实施步骤。

模块和页面文档中的业务闭环检查清单，要填写成稳定事实，而不是空泛提醒。若某项主要属于别的文档，应明确指向对应文档，而不是留空。

## 记忆规则

参见 `references/memory-cycle.md`。简要规则如下：

- 页面规划阶段的观察、经验和规则候选写入 `memory/model-implement.jsonl`。
- 只有重复出现、用户确认或经验证稳定的规划偏好，才提升到 `memory/model-implement-rules.md`。
- 读取初始化和实施阶段的记忆与规则用于对齐，但不要在本 skill 中重写它们的私有规则文件。
- 只有确实会影响初始化或实施阶段的规划规则，才标记 `shared_candidate=true`，并且要谨慎使用，因为它可以绕过普通私有规则提升阈值。
- 共享规则合成默认仍交给 `model-implement-init`，除非用户明确要求当前就刷新共享记忆。
- 不要把密钥、账号、连接串、生产数据或原始隐私数据写入记忆。

## 参考资料

- 需要详细页面规划流程时，读取 `references/workflow.md`。
- 需要报告格式规范时，读取 `references/report-format.md`。
- 需要设置或解释文档状态时，读取 `references/status-contract.md`。
- 在完成任何模块或页面报告前，读取 `references/business-closure-checklist.md`。
- 进行规则提升或共享记忆对齐前，读取 `references/memory-cycle.md`。

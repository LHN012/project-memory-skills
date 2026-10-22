---
name: model-implement
description: "基于已完成初始化的项目上下文、原型目录/图片和需求说明，为指定模块生成逐页面的详细前后端实施方案以及模块关联文档。适用于 model-implement-init 已产出共享上下文、业务流程、数据库评估、模块准备度和审查报告后，再开展模块级详细规划。触发词：页面方案、模块规划、frontend-plan、backend-plan、module-relations、生成实施方案。不要用它做项目初始化或直接写代码。"
---

# Model Implement

## 概述

这个 skill 用于把已经准备好的初始化上下文和目标模块原型，转化为可直接交给前后端工程师使用的页面级详细实施方案。它属于流程中的详细规划阶段，只应在 `model-implement-init` 完成前期准备后再启动。

## 触发与交付速查

- 触发词：页面方案、模块规划、详细实施方案、前后端方案、`frontend-plan.md`、`backend-plan.md`、`module-relations.md`。
- 必要输入：目标模块名、已完成的初始化报告、`module-readiness.md`、目标模块原型或需求材料、知识库入口或缺失说明。
- 必须产出：`module-relations.md`、每个目标界面的 `frontend-plan.md` 和 `backend-plan.md`，以及业务闭环检查清单。
- 交接出口：方案完成后停止；用户明确选择实施时，才交给 `model-implement-executor`。

## 工作区

统一使用 `.codex/model-implement/` 作为共享工作区：

- `prototypes/<模块名>/`：用户提供的原型图、说明文档和模块补充材料。
- `.sql/`：由初始化阶段优先评估过的共享 SQL 目录。
- `library/定义规则.md`：知识库入口；若 `.codex/model-implement/library/` 存在，本 skill 应先读取该入口，并按当前模块命中的规则、组件、样式或特殊资料继续读取相关路径，不默认读取 `library/README.md`，也不递归全量读取知识库。
- `reports/init-airead/source-manifest.json`：初始化阶段生成的输入指纹清单，本 skill 将其视为输入而不是自己刷新。
- `reports/init-airead/shared-context.md`：来自 `model-implement-init` 的 AI 读取版项目共享上下文。
- `reports/init-airead/business-flows.md`：来自 `model-implement-init` 的 AI 读取版跨模块业务流程文档。
- `reports/init-airead/db-assessment.md`：来自 `model-implement-init` 的 AI 读取版数据库评估文档。
- `reports/init-airead/input-materials.md`：来自 `model-implement-init` 的 AI 读取版输入材料清单、归类依据和未归类项。
- `reports/init-read/待人工确认.md`：来自 `model-implement-init` 的中文审查报告。
- `reports/init-read/功能模块清单.md`：来自 `model-implement-init` 的人读模块/菜单/页面层级目录，必要时用于确认页面归属。
- `reports/modules/<模块名>/module-readiness.md`：控制详细页面规划是否允许继续的模块准备度文档。
- `reports/modules/<模块名>/module-relations.md`：本 skill 生成的模块级界面/业务/数据关联文档。
- `reports/modules/<模块名>/<界面名>/frontend-plan.md`：本 skill 为单个界面生成的前端实施方案。
- `reports/modules/<模块名>/<界面名>/backend-plan.md`：本 skill 为单个界面生成的后端实施方案。
- `memory/model-implement.jsonl`：页面规划阶段的观察、经验和规则候选。
- `memory/model-implement-rules.md`：页面规划阶段的私有稳定规则。
- `memory/init-rules.md`、`memory/executor-rules.md`、`memory/shared-memory.md` 与 `memory/shared-rules.md`：本 skill 只读使用，用于保持与其他阶段对齐。

## 工作流程

1. 若存在，先读取 `memory/model-implement-rules.md`、`memory/shared-rules.md` 和 `memory/shared-memory.md`。
2. 确认目标模块已具备初始化产物：`reports/init-airead/shared-context.md`、`reports/init-airead/business-flows.md`、`reports/init-airead/db-assessment.md`、`reports/init-airead/input-materials.md`、`reports/init-airead/source-manifest.json`、`reports/modules/<模块名>/module-readiness.md`。若旧项目尚未迁移，可把 `reports/shared-context.md`、`reports/business-flows.md`、`reports/db-assessment.md`、`reports/source-manifest.json` 作为兼容回退。
3. 优先读取 `reports/modules/<模块名>/module-readiness.md`；如果状态是 `draft` 或 `blocked`，停止并暴露初始化阶段未解决的问题，不要继续生成详细方案。
4. 当 `module-readiness.md` 指向人工审查项时，读取 `reports/init-read/待人工确认.md`，理解会影响当前模块的阻塞点或兜底假设；旧路径 `reports/review-needed.zh.md` 仅作为兼容回退。
5. 检查 `.codex/model-implement/library/` 是否存在：存在则读取 `library/定义规则.md`，按当前模块命中的规则、组件、样式或特殊资料路径补充参考，并在方案文档中列出实际参考路径；不存在则继续规划，但在相关文档里注明本轮未使用知识库。
6. 只为当前目标模块使用 `scripts/module_doc_bootstrap.py --module <模块名>` 创建或刷新页面方案目录。
7. 把初始化阶段的文档作为主要事实来源；只有在解决该模块细节时，才补充查看原始代码、现有页面、组件实现、样式文件或 SQL，避免重新做一次项目级初始化。
8. 对目标模块目录下的每一张原型图，都生成一个界面目录，并在其中维护 `frontend-plan.md` 和 `backend-plan.md`。
9. 为目标模块生成唯一一份 `module-relations.md`，总结模块内部界面关系，以及与其他模块、其他界面的业务和数据关联。
10. 对每个界面的前端方案，必须写清样式依据：未额外说明时，默认以当前项目已有框架、设计系统、组件库和同类页面样式为主；原型用于校准布局结构、组件组合、相对位置、业务差异和明确标注的新视觉要求；不要脱离当前框架自行设计替代样式。
11. 在完成模块与页面文档前，必须补齐业务闭环检查清单；若某项未知且会实质影响实施，则保持相关文档为 `draft` 或 `blocked`。
12. 本 skill 只负责文档和方案，不负责编码实施。产出完成后停止，等待用户决定是否进入实施阶段。
13. 结束前，将有价值的规划观察或规则候选写入 `memory/model-implement.jsonl`，把稳定规则提升到 `memory/model-implement-rules.md`；共享规则合成默认仍由 `model-implement-init` 负责。

## 🔴 CHECKPOINT · 启动门禁

遇到以下任一情况，必须停止生成页面级方案，先把阻塞项写清楚并等待用户确认：

- `module-readiness.md` 不存在，或状态为 `draft`、`blocked`。
- 初始化产物缺失，且兼容旧路径也找不到可用上下文。
- 知识库入口 `library/定义规则.md` 存在但无法读取，或命中资料路径缺失。
- 原型、方案依据、当前框架样式之间存在冲突，且用户没有明确优先级。
- 用户要求直接写代码、跳过初始化、跳过准备度或自动进入 `model-implement-executor`。

## 失败分支与兜底

| 触发条件 | 一线处理 | 仍失败兜底 |
|---|---|---|
| 初始化文档缺失 | 检查旧路径 `reports/shared-context.md`、`reports/business-flows.md`、`reports/db-assessment.md` | 停止并提示先运行 `model-implement-init` |
| `module-readiness.md` 为 `draft`/`blocked` | 读取其中的未决项和 `init-read/待人工确认.md` | 只输出阻塞摘要，不生成页面方案 |
| 知识库命中资料缺失 | 在方案中列出缺失路径和影响范围 | 将相关文档保持为 `blocked` |
| 原型与当前框架视觉冲突 | 写成差异点和待确认项 | 不自行选择新视觉，不标记 `confirmed` |
| 页面业务闭环未知 | 标出缺失的状态、权限、接口、验收或索引信息 | 对应页面方案保持 `draft` 或 `blocked` |

## 反模式黑名单

- 不要把初始化阶段重新做一遍；只读取与当前模块规划直接相关的事实。
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
- 页面级前端方案必须写清样式来源：当前框架/设计系统/同类页面/组件库/知识库样式资料/原型图分别提供了哪些依据。
- 未额外说明时，默认以当前项目已有框架、设计系统、组件库和同类页面样式为主；原型图用于校准布局结构、组件组合、相对位置、业务差异和明确的新视觉要求。
- 如果原型样式明显不同于当前框架，不能默认照搬，也不能自行裁决；应写成差异点和待确认项，等待用户确认是否引入新视觉。
- 不要自动调用或默认进入 `model-implement-executor`；是否开始实施由用户决定。
- 模块和页面方案状态必须遵循 `references/status-contract.md`；`module-relations.md`、`frontend-plan.md`、`backend-plan.md` 只能使用 `draft`、`blocked`、`confirmed`、`implementing`、`done`。
- 如果还有会影响实施方向的未决问题，相关文档必须保持 `draft` 或 `blocked`，不要假装已确认。
- 每个模块和页面文档都要补齐业务闭环检查清单：状态枚举、权限/数据范围、写操作事务与幂等、关联模块影响、接口契约、验收用例、测试数据、性能/索引说明、待确认项。
- 不要在本 skill 中重写 `init-airead/shared-context.md`、`init-airead/business-flows.md`、`init-airead/db-assessment.md`、`init-airead/input-materials.md`、`init-read/待人工确认.md` 或 `library/定义规则.md`；如果这些输入已过期或不足，应该停下来并建议先刷新 `model-implement-init` 或维护知识库。

## 规划深度要求

每一份 `frontend-plan.md` 都应细到足以让前端工程师直接开工，至少包含：

- 布局分区与相对位置。
- 组件类型、数量和层级关系。
- 颜色、样式、视觉重点与状态差异。
- 样式依据优先级：用户明确要求 > 当前项目已有框架/设计系统/同类页面 > 已命中的知识库样式或组件规则 > 原型中的明确差异；若原型和当前框架冲突，只能写成待确认项，不能擅自补一套新视觉。
- 交互行为、显隐条件、校验提示、联动关系。
- 数据绑定、接口触发点、初始化加载逻辑。
- 推荐的前端实施步骤。

每一份 `backend-plan.md` 都应细到足以让后端工程师直接开工，至少包含：

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

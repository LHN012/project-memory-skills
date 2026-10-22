---
name: model-implement-init
description: "通过扫描当前项目框架、已有模块、知识库 library、原型/非标准材料、需求说明和 SQL，初始化项目级实施上下文，产出共享上下文、业务流程、数据库评估、模块准备度、输入清单和待人工审查报告。适用于页面级方案前的项目初始化、材料归类、SQL 覆盖评估和模块 ready 判断。触发词：初始化、项目上下文、module-readiness、source-manifest、SQL评估、功能模块清单。不要生成页面方案或写业务代码。"
---

# Model Implement Init

## 概述

这个 skill 用于在页面级规划开始前，先准备可复用的项目级与模块级初始化上下文。它负责框架扫描、已有模块理解、业务流程提取、数据库评估、准备度判断、人工审查报告，以及共享记忆合成。

## 触发与交付速查

- 触发词：初始化、项目上下文、材料归类、SQL评估、模块准备度、`source-manifest.json`、`module-readiness.md`、功能模块清单。
- 必要输入：项目代码、`.codex/model-implement/prototypes/` 或用户指定材料、`.sql/`、`library/定义规则.md` 或缺失事实、目标模块范围。
- 必须产出：`init-airead/`、`init-read/`、`sql-schema-digest.*`、`input-materials.md`、各模块 `module-readiness.md`。
- 交接出口：模块达到 `ready` 后停止；用户要求页面方案时，再交给 `model-implement`。

## 工作区

统一使用 `.codex/model-implement/` 作为共享工作区：

- `prototypes/<模块名>/`：用户提供的原型图、说明文档和模块相关补充材料。
- `prototypes/`：原型和需求材料输入根目录；材料不一定按 `<模块名>/` 标准拆分，也可能是根目录 PPT/PPTX、Excel、PDF、Word、Markdown、HTML、导出的图片、混合目录或人工给定路径。
- `.sql/`：工作区内共享 SQL 目录，存放完整数据库定义。
- `library/`：知识库根目录；若存在，初始化阶段应先读取 `library/定义规则.md`，并按索引把相关规则、组件、样式、特殊资料纳入参考；若不存在，应在初始化输出中提醒用户当前缺少知识库。
- `reports/init-airead/source-manifest.json`：用于判断原型、文档、SQL、知识库是否变化的输入指纹清单。
- `reports/init-airead/shared-context.md`：后续规划与实施使用的项目共享上下文主文档。
- `reports/init-airead/business-flows.md`：跨模块业务流程主文档。
- `reports/init-airead/db-assessment.md`：数据库覆盖度与风险评估主文档。
- `reports/init-airead/sql-schema-digest.json` 与 `reports/init-airead/sql-schema-digest.md`：由 `scripts/sql_schema_digest.py` 从 SQL 中抽取的表、字段、注释、索引、主键、外键和疑似枚举摘要。
- `reports/init-airead/input-materials.md`：AI 快速读取的输入材料清单、归类依据和模块/页面来源。
- `reports/init-read/初始化总结.md`：给使用人看的初始化总结报告，宽泛总结业务流程路线、页面关联穿透、可复用代码能力和原型可抽象公共实现。
- `reports/init-read/功能模块清单.md`：给使用人看的模块/菜单/页面层级目录，记录每个大模块下有哪些页面，有几级就分几级。
- `reports/init-read/共享上下文.md`：共享上下文的中文阅读版。
- `reports/init-read/业务流程.md`：业务流程中文阅读版。
- `reports/init-read/数据库评估.md`：数据库评估中文阅读版。
- `reports/init-read/待人工确认.md`：给人看的中文审查报告，记录阻塞项、待确认项与建议。
- `reports/modules/<模块名>/module-readiness.md`：某模块是否已具备进入详细页面规划阶段的判断结果。
- `memory/init.jsonl`：初始化阶段的观察、经验和规则候选。
- `memory/init-rules.md`：初始化阶段沉淀出的私有稳定规则。
- `memory/model-implement.jsonl` 与 `memory/model-implement-rules.md`：页面规划阶段私有记忆与规则，仅在共享合成时读取。
- `memory/executor.jsonl` 与 `memory/executor-rules.md`：实施阶段私有记忆与规则，仅在共享合成时读取。
- `memory/fix.jsonl` 与 `memory/fix-rules.md`：问题修复阶段私有记忆与规则，仅在共享合成时读取。
- `memory/review.jsonl` 与 `memory/review-rules.md`：代码审查阶段私有记忆与规则，仅在共享合成时读取。
- `memory/reuse.jsonl` 与 `memory/reuse-rules.md`：复用沉淀阶段私有记忆与规则，仅在共享合成时读取。
- `memory/shared-memory.md` 与 `memory/shared-rules.md`：跨 skill 合成后的共享记忆与共享规则。

## 工作流程

1. 若存在，先读取 `memory/init-rules.md`、`memory/shared-rules.md` 和 `memory/shared-memory.md`。
2. 检查 `.codex/model-implement/library/` 是否存在：存在则只读取 `library/定义规则.md` 作为初始化参考入口，并按任务命中的索引读取相关知识；不存在则在 `init-read/初始化总结.md`、`init-airead/shared-context.md` 或 `init-read/待人工确认.md` 中提醒用户缺少知识库。
3. 使用 `scripts/init_doc_bootstrap.py` 创建缺失的初始化阶段文档；能按模块收敛就按模块处理；如果原型材料不是标准模块文件夹结构，应先生成未归类输入的准备度文档并在报告中说明归类依据。
4. 使用 `scripts/source_fingerprint.py` 刷新或对比 `reports/init-airead/source-manifest.json`，默认纳入 `prototypes/`、`.sql/` 和 `library/定义规则.md`；若 `定义规则.md` 命中特定知识库资料，可把命中的路径作为额外 sources 加入指纹，当输入指纹未变化时优先复用已有初始化产物。
5. 扫描当前代码库的前后端框架、路由、组件约定、接口组织、数据访问方式、权限模型与已有模块能力；识别数据库方言时，必须同时扫描运行 datasource 配置（如 `application*.properties` / `application*.yml`、`driver-class-name`、JDBC 协议、显式 dialect 配置），以 active datasource 作为主要证据，DDL 风格和 Maven 驱动依赖只能作为辅助证据。若只能看到多个驱动依赖或 DDL 风格，不能直接判定方言，必须标记 `待确认`。
6. 扫描目标原型目录及说明材料，先建立“输入材料清单”和“材料归类判断”：材料可能来自模块文件夹、根目录 PPT/PPTX、Excel 功能清单、PDF/Word 说明、Markdown、HTML 导出、图片散落文件、压缩包解压目录或用户指定路径；不要假设一定是 `prototypes/<模块名>/图片`。
7. 从多样化原型材料中整理业务角色、端到端流程、页面清单、页面穿透、跨模块依赖以及不明确点；对从文件名、PPT 页标题、Excel 功能项或目录名推断出的模块归属，要标注为“推断”而非确定事实。
8. 优先读取 `.codex/model-implement/.sql/`，并将其视为主要数据库来源；先运行 `scripts/sql_schema_digest.py` 生成 `reports/init-airead/sql-schema-digest.json` 和 `reports/init-airead/sql-schema-digest.md`，再结合业务流程评估 SQL 对模块需求的覆盖度。
9. 更新 `reports/init-read/初始化总结.md`，用宽泛易懂的中文总结业务流程路线、页面关联穿透跳转、已有可复用能力、知识库可参考能力、原型可提取公共实现和建议下一步；其中业务流程路线和页面关联穿透应使用 Mermaid 图表达。
10. 更新 `reports/init-read/功能模块清单.md`，按大模块/子模块/页面层级记录页面目录、来源材料、归类状态和待确认项。
11. 更新 `reports/init-airead/shared-context.md` 与 `reports/init-read/共享上下文.md`，沉淀稳定的框架事实、已有模块能力、知识库命中情况、共享假设与风险。
12. 更新 `reports/init-airead/business-flows.md` 与 `reports/init-read/业务流程.md`，沉淀角色、流程、状态与模块间依赖分析。
13. 更新 `reports/init-airead/db-assessment.md` 与 `reports/init-read/数据库评估.md`，沉淀数据库覆盖情况、缺口、风险和建议。
14. 更新 `reports/init-airead/input-materials.md`，记录 AI 可快速读取的输入材料清单、模块/页面归类依据、未归类输入和知识库命中路径。
15. 更新 `reports/init-read/待人工确认.md`，输出给人看的阻塞项、不清晰点、原型材料归类问题、知识库缺失或索引缺失提醒、建议确认项与默认兜底假设。
16. 更新 `reports/modules/<模块名>/module-readiness.md`，判断该模块是否可以安全进入详细页面规划。
17. 不要在这个阶段生成页面级 `frontend-plan.md`、`backend-plan.md` 或 `module-relations.md`。
18. 结束前，将有价值的初始化观察或规则候选写入 `memory/init.jsonl`，把稳定规则提升到 `memory/init-rules.md`，并在合适时机负责初始化、页面规划、实施、问题修复、代码审查和复用沉淀六侧记忆的共享合成。

## 🔴 CHECKPOINT · 初始化门禁

开始生成或刷新初始化产物前，必须先确认输入范围和变更来源。遇到以下情况要停止并写入待人工确认：

- 原型、需求、SQL 或知识库路径无法访问。
- 非标准原型材料无法可靠归类到模块或页面。
- SQL 与业务流程明显不匹配，且缺少用户给出的兜底决定。
- 知识库入口存在但无法读取，或命中资料缺失。
- 用户要求在初始化阶段直接生成页面方案或业务代码。

## 失败分支与兜底

| 触发条件 | 一线处理 | 仍失败兜底 |
|---|---|---|
| 输入材料非标准结构 | 建立 `input-materials.md`，按文件名、页标题、目录和用户说明标注归类依据 | 将无法归类项写入 `待人工确认.md` |
| 指纹未变化 | 复用已有初始化产物，只刷新明确受影响的报告 | 在总结中写明复用依据和未刷新范围 |
| SQL 摘要生成失败 | 记录失败命令、错误和涉及文件 | 继续业务材料整理，但数据库评估标为 `blocked` |
| 知识库缺失 | 在共享上下文和人读报告中说明未发现知识库 | 不把“无知识库”当作已验证规则 |
| 准备度证据不足 | 列出缺失的流程、页面、库表、权限或验收依据 | `module-readiness.md` 保持 `draft` 或 `blocked` |

## 反模式黑名单

- 不要假设原型一定按 `prototypes/<模块名>/图片` 标准组织。
- 不要把从文件名、PPT 标题或目录名推断出的归属写成确定事实。
- 不要在初始化阶段生成页面级前后端方案或直接改业务代码。
- 不要把 SQL 缺口、知识库缺口或人工待确认项静默吞掉。
- 不要只依据 DDL 风格或 Maven 驱动依赖判断数据库方言；必须交叉检查运行 datasource 配置，并且不得把 datasource URL、账号、密码或内部地址写入报告。
- 不要把六套私有规则简单拼接成共享规则。

## 输出约束

- 面向使用人的宽泛总结、业务流程路线图、页面关联穿透图、可复用能力摘要和原型公共实现建议放到 `reports/init-read/初始化总结.md`。
- 面向使用人的模块/菜单/页面层级目录放到 `reports/init-read/功能模块清单.md`，用中文命名和层级结构表达。
- 给 AI 读取的框架信息、已有模块能力、知识库存在性、知识库命中路径、跨项目稳定约定放到 `reports/init-airead/shared-context.md`，中文阅读版放到 `reports/init-read/共享上下文.md`。
- 给 AI 读取的跨模块业务流程、角色、状态与交接关系放到 `reports/init-airead/business-flows.md`，中文阅读版放到 `reports/init-read/业务流程.md`。
- 给 AI 读取的 SQL 结构摘要放到 `reports/init-airead/sql-schema-digest.json` 和 `reports/init-airead/sql-schema-digest.md`；数据库覆盖度、库表缺口、索引风险与建议放到 `reports/init-airead/db-assessment.md`，中文阅读版放到 `reports/init-read/数据库评估.md`。
- 给 AI 读取的输入材料清单、归类依据、未归类项、知识库命中路径放到 `reports/init-airead/input-materials.md`。
- 给人看的不清晰点、阻塞项、原型材料归类问题、知识库缺失或索引缺失、待补充内容和兜底假设放到 `reports/init-read/待人工确认.md`。
- 模块是否具备进入详细规划条件，只写到 `reports/modules/<模块名>/module-readiness.md`。
- 不要在本 skill 中生成 `frontend-plan.md`、`backend-plan.md` 或 `module-relations.md`。
- 如果关键输入仍不明确，不要硬猜；保持 `module-readiness.md` 为 `draft` 或 `blocked`。

## 准备度规则

只有在以下条件都满足时，才可以把 `module-readiness.md` 标记为 `ready`：

- 目标模块的原型和材料足以支撑页面级详细规划。
- 若原型材料为非标准结构，模块归属、页面清单和页面来源已经有明确证据，或已把不确定项写入非阻塞兜底假设。
- 业务流程已经清楚到可以枚举主要角色、状态和模块交互。
- 数据库评估要么显示覆盖基本足够，要么已有明确且不阻塞的兜底决定。
- 中文审查报告中不存在影响该模块继续推进的未解决阻塞项。

状态含义与允许状态以 `references/status-contract.md` 为准。`module-readiness.md` 只能使用 `draft`、`blocked`、`ready`、`done`。

## 记忆规则

参见 `references/memory-cycle.md`。简要规则如下：

- 初始化观察、经验和规则候选写入 `memory/init.jsonl`。
- 只有被重复验证、用户明确确认或确实稳定的初始化偏好，才提升到 `memory/init-rules.md`。
- 读取页面规划、实施、问题修复、代码审查和复用沉淀阶段的私有规则用于共享合成，但不要在本 skill 中重写它们的私有规则文件。
- 只有明确跨阶段有效的规则，才在记录时标记 `shared_candidate=true`，并且要谨慎使用，因为它可以绕过普通私有规则提升阈值。
- 共享结论只写入 `memory/shared-memory.md` 与 `memory/shared-rules.md`，而且共享规则不能当作六套私有规则的简单并集。
- 不要把密钥、账号、连接串、生产数据或原始隐私数据写入记忆。

## 参考资料

- 需要完整初始化流程时，读取 `references/workflow.md`。
- 需要初始化文档格式时，读取 `references/report-format.md`。
- 需要设置或解释文档状态时，读取 `references/status-contract.md`。
- 涉及 SQL 或库表评估时，先运行 `scripts/sql_schema_digest.py`，再读取 `references/db-evaluation.md`。
- 进行规则提升或共享记忆合成前，读取 `references/memory-cycle.md`。

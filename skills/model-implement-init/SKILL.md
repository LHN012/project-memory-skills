---
name: model-implement-init
description: "按真实接手新项目的顺序初始化项目：先创建 AGENTS.md 并执行 knowledge-library 的 kb-init-project.ps1，建立初始化契约；再扫描前后端 VS/Vue/Spring 等框架版本、代码风格和工程约定；再通过路由、菜单、页面和接口扫描已有功能模块与可复用能力；最后结合 prototypes/、已有模块和 .sql/ 生成待办清单、业务理解、数据库审查报告、待确认点和 module-readiness。适用于项目初始化、材料归类、已有模块理解、SQL 审查、任务拆分、用户补充 SQL/清单/确认点后的报告刷新，以及进入页面方案前的 ready 判断。用户提示已补充、已回答、已修改报告或直接进入下一阶段时，优先调用 model-context-rag 刷新 reports/memory 上下文索引。不要生成页面方案或写业务代码。"
---

# Model Implement Init

## 概述

这个 skill 用于在页面级规划和编码前，按工程师真实接手项目的顺序建立项目认知。它不再产出旧的 `shared-context.md`、`business-flows.md`、`db-assessment.md` 作为必读输入；这些上下文由 6 份新的人读报告替代：

- `reports/init-read/代码及框架信息.md`
- `reports/init-read/已有功能模块信息.md`
- `reports/init-read/待办清单.md`
- `reports/init-read/业务理解.md`
- `reports/init-read/数据库审查报告.md`
- `reports/init-read/待确认点.md`

第一层还必须创建 `reports/init-read/初始化契约.md`，用于固定输入、输出、状态、脱敏、人话表达和下游交接规则。`source-manifest.json` 与 `sql-schema-digest.*` 仍作为机器辅助产物保留。

## 触发与交付速查

- 触发词：初始化、项目接手、框架扫描、已有功能模块、待办清单、业务理解、数据库审查、待确认点、module-readiness、已补充、已回答、SQL 已补完、清单已调整、报告已修改、进入下一阶段。
- 必要输入：项目代码、`.codex/model-implement/prototypes/` 或用户指定材料、`.codex/model-implement/.sql/`、`.codex/model-implement/library/定义规则.md` 或缺失事实、目标模块范围。
- 必须产出：`初始化契约.md`、`代码及框架信息.md`、`已有功能模块信息.md`、`待办清单.md`、`业务理解.md`、`数据库审查报告.md`、`待确认点.md`、`source-manifest.json`、`sql-schema-digest.*`、各模块 `module-readiness.md`。
- 交接出口：模块达到 `ready` 后停止；若用户已补充 SQL、清单、确认点或报告并要求进入下一阶段，先刷新 `model-context-rag` 索引且确认不是 `blocked`，再交给 `model-implement`。

## 工作区

统一使用 `.codex/model-implement/` 作为共享工作区：

- `prototypes/`：原型和需求材料输入根目录；可包含模块文件夹、根目录 PPT/PPTX、Excel、PDF、Word、Markdown、HTML、图片、导出原型目录或用户指定材料。
- `.sql/`：共享 SQL 目录，存放完整数据库定义或补充 SQL。
- `library/定义规则.md`：知识库入口；初始化阶段只读入口和命中资料，不全量扫描 `library/`。
- `reports/init-read/初始化契约.md`：初始化阶段契约，记录输入范围、输出路径、状态规则、脱敏规则、人话表达规则和下游交接边界。
- `reports/init-read/代码及框架信息.md`：前后端框架版本、VS/Vue/Spring 等技术栈、构建方式、配置、代码风格、权限/请求/分页/路由等工程事实。
- `reports/init-read/已有功能模块信息.md`：通过路由、菜单、页面、Controller/API 和已有代码梳理当前功能模块、界面用途、页面动作和可复用封装。
- `reports/init-read/待办清单.md`：按材料把需求分为新增模块/新增页面、已有界面新增功能、批量 bug/问题修复、待归类任务，并跟踪进度。
- `reports/init-read/业务理解.md`：按材料和已有功能理解业务流程、页面穿透、弹窗/详情/编辑链路，并使用 Mermaid 绘制流程图。
- `reports/init-read/数据库审查报告.md`：结合 SQL、业务材料和已有模块审查数据库是否支撑后续实现，列出必须新增/建议新增字段或表，并标严重等级。
- `reports/init-read/待确认点.md`：只记录已经尽力从代码、材料、SQL、知识库中查找后仍影响实现方向的问题，并标严重等级。
- `reports/init-airead/source-manifest.json`：输入指纹清单，用于判断原型、SQL、知识库入口和命中资料是否变化。
- `reports/init-airead/sql-schema-digest.json` 与 `sql-schema-digest.md`：由 `scripts/sql_schema_digest.py` 抽取的 SQL 摘要，供数据库审查报告引用。
- `reports/context-rag/index-status.json`：由 `model-context-rag` 生成的 reports/memory 上下文索引状态，用于补充后或交接前判断索引是否可被下游检索使用。
- `reports/modules/<模块名>/module-readiness.md`：某模块是否具备进入详细页面规划阶段的判断结果。
- `memory/init.jsonl`、`memory/init-rules.md`、`memory/shared-memory.md`、`memory/shared-rules.md`：初始化观察、稳定规则和跨阶段共享记忆。

## 四层工作流程

### 第一层：准备工作

1. 若存在，先读取 `memory/init-rules.md`、`memory/shared-rules.md` 和 `memory/shared-memory.md`。
2. 若项目根目录缺少 `AGENTS.md`，创建它；无论是否已存在，都执行 `knowledge-library/scripts/kb-init-project.ps1`，把知识库读取规则写入 `AGENTS.md` 的标记块。
3. 读取 `.codex/model-implement/library/定义规则.md`；若知识库缺失或入口不可读，在 `初始化契约.md` 和 `待确认点.md` 记录。
4. 使用 `scripts/init_doc_bootstrap.py` 创建缺失的初始化报告和模块准备度文档。
5. 创建或更新 `reports/init-read/初始化契约.md`，明确本次初始化输入、输出、状态、脱敏规则、严重等级、人话表达规则和禁止事项。
6. 使用 `scripts/source_fingerprint.py` 刷新或对比 `reports/init-airead/source-manifest.json`。默认纳入 `prototypes/`、`.sql/`、`library/定义规则.md`；命中的知识库资料可作为额外 sources 纳入。

### 第二层：扫描代码及框架信息

1. 扫描前端依赖和配置，识别 Vue 版本、VS/VSUI 组件或框架版本、构建工具、路由方式、状态管理、请求封装、权限入口、代码目录和页面风格。
2. 扫描后端依赖和配置，识别 Spring/Spring Boot 版本、MyBatis 或 ORM、分页组件、权限组件、模块分包、Controller/Service/Mapper/XML 结构、日志和异常处理。
3. 识别数据库方言时，必须同时扫描运行 datasource 配置，如 `application*.properties` / `application*.yml`、`driver-class-name`、JDBC 协议、显式 dialect 配置。以 active datasource 作为主要证据，DDL 风格和 Maven 驱动依赖只能作为辅助证据。
4. 不得把 datasource URL、账号、密码、内部地址或密钥写入报告。
5. 更新 `reports/init-read/代码及框架信息.md`。报告必须用人能看懂的语言描述，技术标识后要解释它对开发有什么影响。

### 第三层：扫描已有功能模块

1. 通过前端路由、菜单配置、页面目录、页面标题、API 文件、后端 Controller/API 和已有模块目录识别当前已有功能模块。
2. 对每个模块写清：界面名、菜单/路由/文件路径、主要用途、页面动作、关联接口、关联表、权限/数据范围、可复用点。
3. 不要单独抛出路由；路由必须配合界面名、菜单位置或页面用途说明。
4. 识别可复用能力：列表页模式、查询/重置、分页、弹窗/抽屉、详情/编辑穿透、附件上传、导入导出、码表、权限、当前登录人、流程组件、公共工具或同类页面。
5. 更新 `reports/init-read/已有功能模块信息.md`。

### 第四层：材料、业务、数据库和待办整理

1. 扫描 `prototypes/` 中已有材料，建立材料清单和归类依据。材料可能是标准模块目录，也可能是根目录 PPT/PPTX、Excel、PDF/Word、Markdown、HTML、图片或导出目录。
2. 结合 `已有功能模块信息.md` 判断每份材料属于：
   - 新增功能模块或新增页面，没有已有界面，需要后续生成页面方案。
   - 在已有界面上新增功能、改交互、加字段、加按钮、加弹窗或调整流程。
   - 批量修改 bug、接口偏差、UI 偏差、权限/数据范围/状态流转问题。
   - 无法可靠归类，需进入 `待确认点.md`。
3. 运行 `scripts/sql_schema_digest.py`，生成 `sql-schema-digest.json/md`，再结合原始 SQL、业务流程、已有模块和待办任务进行数据库审查。
4. 更新 `待办清单.md`，用于任务分类和进度掌控。
5. 更新 `业务理解.md`，对每条业务流程绘制 Mermaid 流程图；页面穿透、详情、编辑、弹窗、跨模块跳转也用图表达。
6. 更新 `数据库审查报告.md`，用业务语言说明缺口。不得只丢表字段；必须写清字段中文含义、业务用途、建议位置和严重等级。
7. 更新 `待确认点.md`。先尽力从代码、原型、SQL、知识库和已有模块中找答案，找不到且确实影响实现再提出。
8. 更新 `reports/modules/<模块名>/module-readiness.md`，判断模块是否可以进入 `model-implement`。
9. 不要在初始化阶段生成页面级 `frontend-plan.md`、`backend-plan.md` 或 `module-relations.md`。

### 补充后索引门禁

当用户根据初始化报告补充 SQL、修改待办清单、回答待确认点、修正业务理解、补充数据库建议，或明确表示“已补充”“已回答”“可以进入下一阶段”“开始页面方案”时，必须先调用 `model-context-rag` 对已有 `reports/` 与 `memory/` 重新切分和建索引。

执行顺序：

1. 运行 `.codex/skills/model-context-rag/scripts/rag-index.ps1 -ModelRoot .codex/model-implement`。若 skill 路径不同，先在 `.codex/skills/` 下定位 `model-context-rag/scripts/rag-index.ps1`。
2. 运行 `.codex/skills/model-context-rag/scripts/rag-status.ps1 -ModelRoot .codex/model-implement -Json`。
3. 若状态为 `healthy`，继续准备度判断或交接到下一阶段。
4. 若状态为 `warning`，允许继续，但必须说明索引存在轻微质量风险，并要求下游精读命中的原始报告。
5. 若状态为 `blocked`，停止交接；先重建索引、修复报告/记忆，或回退为直接读取原始报告，不要让下游依赖旧检索结果。

## 严重等级

初始化报告中的业务、数据库和待确认项统一使用：

- `P0 阻塞`：不解决就无法继续规划或实现核心流程，或存在数据/权限/真实业务风险。
- `P1 高风险`：可以继续分析，但会明显影响接口、字段、状态、权限、数据一致性或验收。
- `P2 建议处理`：不阻塞当前实现，但会影响性能、可维护性、体验或后续扩展。
- `P3 记录观察`：低风险提醒或后续可优化事项。

## CHECKPOINT · 初始化门禁

遇到以下情况必须停止或保持相关产物为 `blocked`，并写入 `待确认点.md`：

- `AGENTS.md` 无法创建或 `kb-init-project.ps1` 无法执行，且项目要求知识库门禁。
- 原型、需求、SQL 或知识库路径无法访问。
- 非标准材料无法可靠归类到新增任务、已有界面改造或问题修复。
- 无法确认 active datasource，却需要判断 SQL 方言或 SQL 兼容规则。
- SQL 与业务流程明显不匹配，且缺少用户给出的兜底决定。
- 知识库入口存在但无法读取，或命中资料缺失。
- 用户要求在初始化阶段直接生成页面方案或业务代码。
- 用户补充 SQL、清单、确认点或报告后准备进入下一阶段，但 `model-context-rag` 的 `index-status.json` 为 `blocked`。

## 输出约束

- 所有报告默认写中文，面向人阅读。
- 表、字段、接口、路由、文件路径都要配合业务解释；不要只堆技术名词。
- 页面引用必须优先写界面名和用途，再补路由或文件路径。
- 数据库建议必须写清“哪个业务动作需要它、建议在哪张表或新表上补、字段中文含义是什么、严重等级是什么”。
- `待确认点.md` 只放影响实现方向的问题；不把普通 TODO、可自行查证的问题或泛泛提醒丢给用户。
- 旧的 `reports/init-airead/shared-context.md`、`business-flows.md`、`db-assessment.md` 不再作为必需产物；若旧项目存在，可作为历史兼容输入读取，但不得继续作为新初始化主报告。

## 准备度规则

只有在以下条件都满足时，才可以把 `module-readiness.md` 标记为 `ready`：

- 目标模块或任务已在 `待办清单.md` 中归类清楚。
- 若是新增模块/页面，原型和材料足以支撑页面级详细规划。
- 若是已有界面改造或问题修复，已在 `已有功能模块信息.md` 中定位到界面名、入口、代码范围或关联接口。
- 业务流程和页面穿透关系已在 `业务理解.md` 中说明，阻塞问题已进入 `待确认点.md`。
- 数据库审查要么显示覆盖基本足够，要么已有明确且不阻塞的兜底决定。
- `待确认点.md` 中不存在影响该模块继续推进的 P0 阻塞项。
- 若用户在初始化报告生成后补充过 SQL、清单、确认点、业务理解或数据库审查，`model-context-rag` 已刷新索引，且 `reports/context-rag/index-status.json` 不是 `blocked`。

状态含义与允许状态以 `references/status-contract.md` 为准。`module-readiness.md` 只能使用 `draft`、`blocked`、`ready`、`done`。

## 记忆规则

参见 `references/memory-cycle.md`。简要规则如下：

- 初始化观察、经验和规则候选写入 `memory/init.jsonl`。
- 只有被重复验证、用户明确确认或确实稳定的初始化偏好，才提升到 `memory/init-rules.md`。
- 读取页面规划、实施、问题修复和代码审查阶段的私有规则用于共享合成，但不要在本 skill 中重写它们的私有规则文件。
- 共享结论只写入 `memory/shared-memory.md` 与 `memory/shared-rules.md`，而且共享规则不能当作私有规则的简单并集。
- 不要把密钥、账号、连接串、生产数据或原始隐私数据写入记忆。

## 参考资料

- 需要完整初始化流程时，读取 `references/workflow.md`。
- 需要初始化文档格式时，读取 `references/report-format.md`。
- 需要设置或解释文档状态时，读取 `references/status-contract.md`。
- 涉及 SQL 或库表评估时，先运行 `scripts/sql_schema_digest.py`，再读取 `references/db-evaluation.md`。
- 进行规则提升或共享记忆合成前，读取 `references/memory-cycle.md`。

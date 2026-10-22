# Report Format

## Purpose

`model-implement-init` now produces human-readable initialization reports that replace the old `shared-context.md`, `business-flows.md`, and `db-assessment.md` main inputs. Keep the writing concrete, readable, and connected to business meaning.

Technical names are allowed, but never alone:

- Table and field names must include Chinese meaning and business use.
- Routes must include interface/page name and purpose.
- APIs must include the user action or page interaction that triggers them.
- Uncertainty must be classified by impact, not dumped as generic TODOs.

## Initialization Contract

Create:

- `reports/init-read/初始化契约.md`

Keep these sections:

- `状态`
- `本次初始化范围`
- `输入目录与材料来源`
- `输出文档清单`
- `知识库与 AGENTS 约定`
- `扫描边界`
- `脱敏规则`
- `状态与严重等级`
- `人话表达规则`
- `下游交接规则`
- `禁止事项`

The contract must mention whether `AGENTS.md` exists, whether `kb-init-project.ps1` ran successfully, which knowledge-library entry was read, and where generated reports will be written.

## Code And Framework Report

Create:

- `reports/init-read/代码及框架信息.md`

Keep these sections:

- `状态`
- `一句话结论`
- `前端框架与版本`
- `后端框架与版本`
- `VS 或组件框架信息`
- `构建与启动方式`
- `路由、菜单与页面组织`
- `请求封装与接口组织`
- `权限、登录人与数据范围`
- `数据库连接与方言判断`
- `代码目录与分层结构`
- `已有代码风格与约定`
- `可复用工程能力`
- `风险与待确认项`

Do not expose datasource URL, usernames, passwords, tokens, internal hosts, or production data. For database dialect, state evidence such as active datasource config, driver, dialect config, or uncertainty.

## Existing Feature Module Report

Create:

- `reports/init-read/已有功能模块信息.md`

Keep these sections:

- `状态`
- `模块总览`
- `路由与菜单来源`
- `已有模块清单`
- `界面与功能动作`
- `模块接口与后端入口`
- `关联数据对象`
- `权限与数据范围观察`
- `已封装可复用功能`
- `可作为新需求参考的同类页面`
- `未识别或需确认的模块`

For each existing module or page, prefer this shape:

```text
### 模块/界面名称

- 界面用途：...
- 菜单或入口：界面名 + 路由/文件路径
- 主要动作：查询、新增、编辑、删除、提交、审核、导入、导出、上传等
- 关联接口：动作 + method/path + 后端入口
- 关联数据对象：业务对象中文名 + 表/字段线索
- 可复用点：页面结构、组件、接口模式、权限写法、公共工具
- 备注：...
```

## Todo List Report

Create:

- `reports/init-read/待办清单.md`

The purpose is task classification and progress control. It must classify prototype/material requirements into:

- `新增功能模块或新增页面`
- `已有界面新增功能或调整`
- `批量 bug 或问题修复`
- `待归类材料`

Keep these sections:

- `状态`
- `任务总览`
- `材料来源清单`
- `新增功能模块或新增页面`
- `已有界面新增功能或调整`
- `批量 bug 或问题修复`
- `待归类材料`
- `进度状态表`
- `建议执行顺序`
- `阻塞与依赖`

Suggested progress labels inside this report:

- `未开始`
- `已归类`
- `待确认`
- `可进入页面方案`
- `可进入修复`
- `已交接`

These are task progress labels, not lifecycle statuses.

## Business Understanding Report

Create:

- `reports/init-read/业务理解.md`

Keep these sections:

- `状态`
- `业务总体理解`
- `角色与参与方`
- `业务对象说明`
- `业务流程清单`
- `业务流程图`
- `界面穿透与弹窗关系`
- `跨模块流转`
- `状态与关键规则`
- `与已有功能模块的关系`
- `业务风险与待确认项`

Every identified business flow should have a short description and a Mermaid diagram. Page penetration, detail/edit pages, dialogs, drawers, popups, and cross-module jumps should also be shown with Mermaid when there is enough evidence.

Use interface names rather than raw routes in diagrams. Routes or files may be added in parentheses when helpful.

## Database Review Report

Create:

- `reports/init-read/数据库审查报告.md`

Before writing this report, generate and read:

- `reports/init-airead/sql-schema-digest.json`
- `reports/init-airead/sql-schema-digest.md`

Keep these sections:

- `状态`
- `审查结论`
- `SQL 输入来源`
- `数据库方言与证据`
- `业务对象覆盖情况`
- `已有表结构可支撑的功能`
- `必须补充的表或字段`
- `建议补充的表或字段`
- `关系、状态与字典审查`
- `查询、分页、统计与索引风险`
- `数据质量与约束风险`
- `严重等级汇总`
- `待确认数据库问题`

For each database gap, use this shape:

```text
### P1-001 标题

- 严重等级：P1 高风险
- 涉及业务：哪个页面/流程/动作需要它
- 当前证据：已有表、字段、SQL 摘要或材料来源
- 缺口说明：用业务语言解释缺什么
- 建议位置：建议在哪张表补字段，或建议新增哪张表
- 字段/表含义：中文含义 + 技术名建议
- 影响：不处理会影响什么
```

Do not output bare field lists without business explanation.

## Confirmation Points Report

Create:

- `reports/init-read/待确认点.md`

Keep these sections:

- `状态`
- `确认点处理原则`
- `P0 阻塞确认点`
- `P1 高风险确认点`
- `P2 建议确认点`
- `P3 记录观察`
- `已自行查证并关闭的问题`
- `建议向用户提问的最小问题集`

Only include questions after checking available code, prototypes, SQL, knowledge-library entries, existing module reports, and reasonable inference. Avoid pushing questions to the user when the answer can be found locally.

For each open question:

```text
### P1-001 标题

- 严重等级：P1 高风险
- 涉及范围：模块/界面/接口/表/流程
- 已查找证据：查过哪些材料和结论
- 仍不确定的问题：...
- 为什么必须确认：...
- 默认兜底建议：如果用户暂不确认，是否可继续以及怎么继续
```

## Module Readiness Report

For one target module or task group, create:

- `reports/modules/<module-name>/module-readiness.md`

Keep these sections:

- `状态`
- `模块或任务范围`
- `对应待办项`
- `输入材料清单`
- `材料归类依据`
- `关联已有界面或新增判断`
- `知识库参考项`
- `业务理解摘要`
- `可复用已有能力`
- `数据库覆盖判断`
- `页面方案前置检查`
- `阻塞项`
- `建议先确认事项`
- `下一步建议`

The readiness report should reference the six new initialization reports, especially `待办清单.md`, `业务理解.md`, `数据库审查报告.md`, `待确认点.md`, and `已有功能模块信息.md`.

## Legacy Compatibility

Do not create these as new primary reports:

- `reports/init-airead/shared-context.md`
- `reports/init-airead/business-flows.md`
- `reports/init-airead/db-assessment.md`
- `reports/init-read/共享上下文.md`
- `reports/init-read/业务流程.md`
- `reports/init-read/数据库评估.md`

If they already exist in a migrated project, they may be read as historical context only. New initialization output must use the documents above.

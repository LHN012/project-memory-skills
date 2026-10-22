# Report Format

## Initialization Summary Report

`reports/init-read/初始化总结.md` is the concise Chinese entry report for human readers. It should summarize the initialization result without copying all detailed reports. Keep these sections:

- `状态`
- `一句话结论`
- `本轮覆盖范围`
- `知识库参考情况`
- `业务逻辑层面`
- `业务流程路线`
- `页面关联穿透跳转情况`
- `代码层面`
- `已有可复用的方法与能力`
- `知识库可参考能力`
- `原型需求可提取公共实现的地方`
- `重点风险与待确认项`
- `建议下一步`

Use Mermaid diagrams inside this report for:

- business-flow routes,
- page associations, drill-through paths, redirects, and cross-module page jumps.

Keep the diagrams broad and readable. Do not replace detailed business-flow or module planning reports with this summary.

## Human Module Directory

`reports/init-read/功能模块清单.md` is the human-facing module/menu/page directory. Keep it Chinese and easy to scan. It should record:

- `状态`
- `说明`
- `模块层级目录`
- `未归类材料`
- `页面来源索引`
- `待确认项`

The `模块层级目录` section should look like a menu tree. Use as many levels as the prototype material supports:

```text
大模块
  子模块
    页面
      子页面/弹窗/详情/编辑
```

Every page item should record its source evidence when known, such as PPT file, page title, Excel row, image path, document heading, or user instruction.

## Shared Context

`reports/init-airead/shared-context.md` is the canonical AI-facing shared project report for framework, conventions, and stable cross-module context. Keep these sections:

- `Status`
- `Source Manifest`
- `Project Understanding`
- `Framework Scan`
- `Existing Module Inventory`
- `Knowledge Library References`
- `Prototype and Requirement Inputs`
- `Shared Assumptions`
- `Shared Risks`
- `Next Update Notes`

`reports/init-read/共享上下文.md` mirrors the same information in user-facing Chinese.

`Knowledge Library References` should state whether `.codex/model-implement/library/` exists, whether `library/定义规则.md` was read, which paths were matched for this initialization pass, and which library entries are missing or not yet indexed.

`Prototype and Requirement Inputs` must not assume only `prototypes/<module-name>/`. It should list root-level PPT/PPTX, Excel, PDF/Word, Markdown, HTML, scattered images, exported prototype folders, and user-specified paths when present. Mark module ownership as `confirmed`, `inferred`, or `unclassified`.

## Business Flow Report

`reports/init-airead/business-flows.md` is the canonical AI-facing cross-module business-flow report. Keep these sections:

- `Status`
- `Scope`
- `Input Sources`
- `Prototype Material Inventory`
- `Roles and Actors`
- `Module Flow Summary`
- `Cross-Module Flow Details`
- `State and Process Dependencies`
- `Shared Data Hand-offs`
- `Reusable Existing Capabilities`
- `Ambiguities and Gaps`
- `Next Update Notes`

`reports/init-read/业务流程.md` mirrors the same information in user-facing Chinese.

`Prototype Material Inventory` should explain how business flows were extracted from module folders, root-level files, PPT pages, Excel function rows, documents, screenshots, or inferred naming.

## Database Assessment Report

`reports/init-airead/db-assessment.md` is the canonical AI-facing database coverage and risk report. Keep these sections:

- `Status`
- `Source SQL Inputs`
- `Business Flow Coverage`
- `Entity and Attribute Coverage`
- `Relationship and State Coverage`
- `Write Operation Support`
- `Query and Reporting Support`
- `Constraints and Data Quality`
- `Performance and Index Notes`
- `Risks and Recommendations`
- `Open Questions`

`reports/init-read/数据库评估.md` mirrors the same information in user-facing Chinese.

Before writing database assessment, generate and read:

- `reports/init-airead/sql-schema-digest.json`
- `reports/init-airead/sql-schema-digest.md`

These files are produced by `scripts/sql_schema_digest.py` and should summarize tables, fields, comments, primary keys, foreign keys, indexes, and enum-like comment hints.

## AI Input Materials

`reports/init-airead/input-materials.md` is the AI-facing material inventory and classification report. Keep these sections:

- `Status`
- `Prototype Root`
- `Material Inventory`
- `Module and Page Classification`
- `Unclassified Inputs`
- `Knowledge Library Matches`
- `Source Evidence Rules`
- `Open Questions`

This file should be optimized for downstream AI reading. It may be more structured than the human reports.

## Human Review Report

`reports/init-read/待人工确认.md` is the Chinese report intended for human review. Keep these sections:

- `状态`
- `本轮结论摘要`
- `需人工确认的阻塞项`
- `建议补充的业务信息`
- `原型或文档不清晰点`
- `原型材料归类待确认`
- `知识库待确认点`
- `数据库待确认点`
- `默认兜底假设`
- `建议下一步`

Keep this file concise, decision-oriented, and easy for a human reviewer to act on.

## Module Readiness Report

For one target module, create:

- `reports/modules/<module-name>/module-readiness.md`

`module-readiness.md` should capture whether the module is ready to enter detailed screen planning. Keep these sections:

- `状态`
- `模块范围`
- `输入材料清单`
- `输入材料归类依据`
- `知识库参考项`
- `业务理解摘要`
- `现有模块复用点`
- `数据库覆盖判断`
- `页面方案前置检查`
- `阻塞项`
- `建议先确认事项`
- `下一步建议`

The `页面方案前置检查` section should explicitly cover:

- source material completeness,
- source material classification and module ownership,
- knowledge-library existence and matched reference paths,
- business-flow clarity,
- role and status clarity,
- reusable capability clarity,
- database coverage sufficiency,
- and whether screen planning can proceed safely.

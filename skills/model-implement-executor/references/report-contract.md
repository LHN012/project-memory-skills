# Report Contract

`model-implement-executor` should treat the new `reports/init-read/` initialization reports and confirmed module/page plans as canonical implementation contracts, then verify execution details against RAG-located original reports, prototypes, SQL/database evidence, knowledge-library rules, and real code.

Prototype images remain required implementation references for the target screen. Reports define the implementation contract. When the report does not fully specify style details, current framework, design-system, component-library, and similar-page styles are the default style source; the matching prototype calibrates layout structure, component grouping, relative positions, and explicit visual differences.

RAG is a locator, not a source of truth. The executor may use RAG to find relevant initialization reports, module plans, confirmation points, database review items, and memory entries, but must read the original files before making implementation decisions.

SQL/database evidence is mandatory for data persistence work. `backend-plan.md` explains intended behavior; `数据库审查报告.md`, `.sql`, and real backend code confirm whether the schema and codebase can support it.

## Initialization Contract

Before implementation, `model-implement-executor` should read:

- `model-context-rag` status and matched original report paths
- `reports/init-read/初始化契约.md`
- `reports/init-read/代码及框架信息.md`
- `reports/init-read/已有功能模块信息.md`
- `reports/init-read/待办清单.md`
- `reports/init-read/业务理解.md`
- `reports/init-read/数据库审查报告.md`
- `reports/init-read/待确认点.md`
- `reports/modules/<module-name>/module-readiness.md`
- `library/定义规则.md`
- matched knowledge-library paths required by `library/定义规则.md`
- `prototypes/<module-name>/` materials that match the target screen when visual or interaction details need calibration
- `.sql` files relevant to target tables, fields, views, procedures, triggers, indexes, or seed data

Knowledge-library references are mandatory before implementation. If the knowledge library exists, `library/定义规则.md` is the gate. The executor must read it, follow the priority and lookup rules, read matched concrete documents, and stop before code changes if required knowledge files are missing or conflicts cannot be resolved.

RAG references are mandatory before implementation when the RAG skill is available in the Workbench. Use `rag-status` first, then `rag-search`, then open matched original report sections. If RAG is `blocked`, read the original report folders directly and record that fallback.

When evidence conflicts, use this priority unless the user explicitly says otherwise:

1. Direct user instruction for this run.
2. Knowledge-library mandatory rule or AGENTS.md project rule.
3. Confirmed `model-implement` plan and module relation contract.
4. Current real code conventions and framework constraints.
5. SQL/database evidence and database review feasibility.
6. Prototype layout and explicit visual/interaction differences.
7. Historical memory or older reports.

If this priority still leaves a material conflict, apply the risk deferral policy: skip high-risk non-blocking work and list it for manual confirmation; stop only the subtask that cannot safely close without the answer.

`初始化契约.md` should explain:

- initialization scope, outputs, status rules, severity labels, desensitization rules, and downstream handoff rules.

`代码及框架信息.md` should explain:

- frontend and backend framework versions, VS/component framework, routing, request wrappers, permissions, datasource dialect evidence, and code style.

`已有功能模块信息.md` should explain:

- existing modules, interface/page names, menu or route entries, actions, APIs, data objects, permissions, and reusable capabilities.

`待办清单.md` should explain:

- whether the target is a new module/page, existing page feature addition, batch bug fix, or unclassified material.

`业务理解.md` should explain:

- roles, business flows, page penetration, dialogs/drawers, cross-module flow, states, and key business rules.

`数据库审查报告.md` should explain:

- whether the schema supports the target module,
- required or suggested table/field changes,
- business meaning of database gaps,
- performance or index concerns,
- severity levels.

`.sql` and real backend code should confirm:

- whether the required tables, fields, indexes, views, procedures, triggers, seed data, Mapper SQL, Entity/DTO/VO mappings, and status enums already exist,
- whether new schema work is required,
- whether the proposed change affects only the target module or also shared/cross-module queries.

`待确认点.md` should explain:

- unresolved P0/P1/P2/P3 questions that still affect implementation direction or acceptance.

`module-readiness.md` should explain whether detailed screen planning and execution can proceed for the target module. If it is `draft` or `blocked`, stop unless the user explicitly overrides it.

## Module Planning Contract

For one target module, `model-implement-executor` should read:

- `reports/modules/<module-name>/module-relations.md`
- `reports/modules/<module-name>/<screen-name>/frontend-plan.md`
- `reports/modules/<module-name>/<screen-name>/backend-plan.md`

`module-relations.md` should explain internal screen flow, screen penetration, cross-module relations, shared data, and synchronization risks.

Each `frontend-plan.md` should describe the screen structure, components, styles, interactions, initialization inputs, data binding, and implementation steps.

When `frontend-plan.md` does not fully define styles, spacing, visual hierarchy, alignments, grouping, or component emphasis, `model-implement-executor` should first follow current framework, design-system, component-library, and similar-page styles, then refer back to the matching prototype image for layout structure, component grouping, relative positions, and explicit visual differences.

Each `backend-plan.md` should describe the screen's business actions, initialization inputs, tables, fields, interfaces, rules, and implementation steps.

Only implement screens whose plan status is `confirmed`, `implementing`, or directly approved by the user, and only after the module readiness report allows the module to proceed.

If the confirmed plan and the prototype disagree on a material implementation detail, classify the risk. If the conflict is non-blocking, keep current project conventions, skip the risky difference, and list it for manual confirmation. If it blocks the target screen's core closure, stop that subtask and ask for clarification unless the user has already stated which source overrides the other.

## Implementation Record Contract

When code changes are made, create or update:

- `reports/modules/<module-name>/<screen-name>/implementation-record.md`

The record should summarize:

- implementation scope,
- model-implement plans read,
- RAG status and original files read,
- prototype and SQL references used,
- knowledge-library paths read,
- code files changed,
- validation commands and results,
- skipped high-risk items and manual confirmation needs,
- residual risk for review/fix.

Use `references/implementation-record-format.md` for the recommended structure.


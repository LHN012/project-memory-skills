# Report Format

## Required Initialization Inputs

Before generating page plans for a module, read these initialization outputs:

- `model-context-rag` status via `rag-status.ps1`; if usable, run `rag-search.ps1` and then open the matched original files
- `reports/init-read/初始化契约.md`
- `reports/init-read/代码及框架信息.md`
- `reports/init-read/已有功能模块信息.md`
- `reports/init-read/待办清单.md`
- `reports/init-read/业务理解.md`
- `reports/init-read/数据库审查报告.md`
- `reports/init-read/待确认点.md`
- `reports/modules/<module-name>/module-readiness.md`
- `reports/init-read/待确认点.md` when confirmation findings affect the target module
- `library/定义规则.md` when the knowledge library exists, plus only the matched knowledge-library paths for this module

If any required new initialization report is missing, or the module readiness report is missing, `draft`, or `blocked`, stop and refresh initialization first.

RAG results are context locators only. Every report must list the original files actually read from RAG hits, not `reports/context-rag/chunks.jsonl`.

## Module Output Layout

Do not create a module list or module index before producing a module.

For one target module, `model-implement` creates:

- `reports/modules/<module-name>/module-relations.md`
- `reports/modules/<module-name>/<screen-name>/frontend-plan.md`
- `reports/modules/<module-name>/<screen-name>/backend-plan.md`

`reports/modules/<module-name>/module-readiness.md` is created by `model-implement-init` and treated as a prerequisite, not an output of this skill.

If legacy module-level files already exist, preserve them under:

- `reports/modules/<module-name>/_legacy/legacy-module-plan.md`
- `reports/modules/<module-name>/_legacy/legacy-module-plan.zh.md`

## Business Closure Checklist

Every module and screen report must explicitly cover these items before the report can be marked `confirmed`:

- `Status Enums`
- `Permissions and Data Scope`
- `Write Transactions and Idempotency`
- `Related Module Impact`
- `Interface Contract`
- `Acceptance Use Cases`
- `Test Data`
- `Performance and Index Notes`
- `Open Questions`

If an item belongs mainly to another report, point to that report and summarize the dependency instead of leaving the item blank.

## Module Relations Report

`module-relations.md` should capture the module as a whole. Keep these sections:

- `Status`
- `RAG Context Trail`
- `Initialization Inputs`
- `Knowledge Library References`
- `Module Scope`
- `Prototype Sources`
- `Prototype Comparison Summary`
- `Module Screen Inventory`
- `Internal Flow Relations`
- `Internal Navigation and Screen Penetration`
- `Cross-Module Business Relations`
- `Cross-Module Navigation Relations`
- `Shared Data, Tables, Fields, and Interfaces`
- `State Transitions and Process Dependencies`
- `Business Closure Checklist`
- `Risks and Synchronization Points`
- `Open Questions`
- `Executor Follow-Up Notes`

In the module-level checklist, summarize cross-screen or cross-module status dependencies, permissions/data scope dependencies, write-impact boundaries, shared interface contracts, acceptance scenarios, shared test data, performance hot spots, and unresolved questions.

This report is module-level, not screen-level.

In `RAG Context Trail`, list the search terms, status (`healthy`, `warning`, `blocked`, or fallback), matched original report paths, headings, and the planning conclusions taken after reading the original files.

In `Prototype Comparison Summary`, describe what the prototypes add compared with existing project screens: new pages, changed interactions, changed fields, visual differences, and conflicts requiring confirmation.

In `Executor Follow-Up Notes`, write implementation order and files/areas to inspect later. Do not say the executor has been called; the user must trigger it separately.

## Frontend Screen Report

`frontend-plan.md` should be detailed enough for a frontend engineer to start implementation. Keep these sections:

- `Status`
- `RAG Context Trail`
- `Source Prototype`
- `Initialization Inputs`
- `Knowledge Library References`
- `Prototype Comparison`
- `Screen Purpose and Entry Position`
- `Layout Regions and Relative Positioning`
- `Component Inventory and Estimated Counts`
- `Region-by-Region Component Breakdown`
- `Visual Style Plan`
- `Color, Typography, Spacing, and Density`
- `Interaction Behavior and Page States`
- `Validation, Feedback, and Empty/Error States`
- `Data Binding and Interface Consumption`
- `Business Closure Checklist`
- `Responsive and Compatibility Notes`
- `Frontend Implementation Steps`
- `Open Questions and Risks`
- `Acceptance Checklist`
- `Executor Follow-Up Notes`

In the frontend checklist, cover at least:

- status display and state-dependent UI behavior,
- permission-dependent UI visibility or disabled states,
- related module impact and navigation penetration,
- interface contract alignment with backend plan,
- acceptance use cases,
- required test data or fixture assumptions,
- frontend performance concerns such as large tables, waterfall requests, chart refresh, image loading, and caching,
- unresolved questions.

Be explicit about component types, approximate counts, button groups, forms, tables, tabs, cards, dialogs, drawers, lists, charts, uploaders, colors, spacing, and relative placement.

In `Knowledge Library References`, list `library/定义规则.md` and every actually-read knowledge-library path, or state that no library exists/no matching entry was used.

In `Prototype Comparison`, compare prototype regions to current project style and similar existing pages. State which layout decisions come from the prototype, which visual or component decisions should follow the current project, and which conflicts need confirmation.

In `Visual Style Plan` and `Color, Typography, Spacing, and Density`, state the style source priority for this screen. When the user has not explicitly requested a new visual style, default to the current project framework, design system, component library, and similar existing pages. Use the prototype for layout structure, component grouping, relative positioning, screen-specific differences, and explicit new visual requirements. If prototype styling conflicts with existing framework style, record the conflict in `Open Questions and Risks`.

In `Executor Follow-Up Notes`, include frontend file areas, existing pages/components to compare, and implementation sequence. Do not state that executor has started.

## Backend Screen Report

`backend-plan.md` should be detailed enough for a backend engineer to start implementation. Keep these sections:

- `Status`
- `RAG Context Trail`
- `Source Prototype`
- `Initialization Inputs`
- `Knowledge Library References`
- `Prototype-to-Backend Mapping`
- `Screen Business Goal`
- `Business Actions Triggered by This Screen`
- `Related Tables and Their Roles`
- `Field Mapping`
- `Read and Write Operations`
- `Interface Plan`
- `Request and Response Notes`
- `Validation and Business Rules`
- `Permissions and Data Scope`
- `Transactions, Views, Procedures, and Triggers`
- `Logging, Auditing, and Idempotency Notes`
- `Business Closure Checklist`
- `Backend Implementation Steps`
- `Open Questions and Risks`
- `Acceptance Checklist`
- `Executor Follow-Up Notes`

In the backend checklist, cover all required items in implementation detail. If the screen is read-only, explicitly state which checklist items are not applicable and why.

Be explicit about which tables and fields are read, written, filtered, aggregated, or joined; which endpoints are required; and which SQL objects or service-layer rules are needed.

In `Knowledge Library References`, list `library/定义规则.md` and every actually-read knowledge-library path, especially component, permission, SQL, API, or special business references that affect backend planning.

In `Prototype-to-Backend Mapping`, map visible prototype controls, fields, buttons, dialogs, and status labels to backend business actions, read/write models, and interface needs.

In `Related Tables and Their Roles` and `Field Mapping`, never dump raw table or field names alone. Add a short human-readable business meaning, usage, and whether the item is query-only, display-only, writable, filterable, sortable, aggregated, or used for state control.

In `Executor Follow-Up Notes`, include backend packages/files/SQL areas to inspect later and implementation sequence. Do not state that executor has started.


# Report Format

## Required Initialization Inputs

Before generating page plans for a module, read these initialization outputs:

- `reports/init-airead/shared-context.md`
- `reports/init-airead/business-flows.md`
- `reports/init-airead/db-assessment.md`
- `reports/init-airead/input-materials.md`
- `reports/modules/<module-name>/module-readiness.md`
- `reports/init-read/待人工确认.md` when human-review findings affect the target module
- `library/定义规则.md` when the knowledge library exists, plus only the matched knowledge-library paths for this module

If the module readiness report is missing, `draft`, or `blocked`, stop and refresh initialization first.

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
- `Initialization Inputs`
- `Knowledge Library References`
- `Module Scope`
- `Prototype Sources`
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

In the module-level checklist, summarize cross-screen or cross-module status dependencies, permissions/data scope dependencies, write-impact boundaries, shared interface contracts, acceptance scenarios, shared test data, performance hot spots, and unresolved questions.

This report is module-level, not screen-level.

## Frontend Screen Report

`frontend-plan.md` should be detailed enough for a frontend engineer to start implementation. Keep these sections:

- `Status`
- `Source Prototype`
- `Initialization Inputs`
- `Knowledge Library References`
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

In `Visual Style Plan` and `Color, Typography, Spacing, and Density`, state the style source priority for this screen. When the user has not explicitly requested a new visual style, default to the current project framework, design system, component library, and similar existing pages. Use the prototype for layout structure, component grouping, relative positioning, screen-specific differences, and explicit new visual requirements. If prototype styling conflicts with existing framework style, record the conflict in `Open Questions and Risks`.

## Backend Screen Report

`backend-plan.md` should be detailed enough for a backend engineer to start implementation. Keep these sections:

- `Status`
- `Source Prototype`
- `Initialization Inputs`
- `Knowledge Library References`
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

In the backend checklist, cover all required items in implementation detail. If the screen is read-only, explicitly state which checklist items are not applicable and why.

Be explicit about which tables and fields are read, written, filtered, aggregated, or joined; which endpoints are required; and which SQL objects or service-layer rules are needed.

In `Knowledge Library References`, list `library/定义规则.md` and every actually-read knowledge-library path, especially component, permission, SQL, API, or special business references that affect backend planning.


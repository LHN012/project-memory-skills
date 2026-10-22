# Business Closure Checklist

Use this checklist before marking a module, frontend screen plan, or backend screen plan as `confirmed`.

## Goal

The checklist exists to reduce business gaps between prototype understanding and real implementation. It is not a perfunctory appendix. Fill it with concise, durable conclusions that another Codex or engineer can execute against.

Treat `model-implement-init` outputs as prerequisite context. Use `shared-context.md`, `business-flows.md`, `db-assessment.md`, and `module-readiness.md` to ground the checklist instead of rediscovering the project from scratch.

## Required Items

Every target module and screen must cover these items somewhere in its reports:

1. `Status Enums`
2. `Permissions and Data Scope`
3. `Write Transactions and Idempotency`
4. `Related Module Impact`
5. `Interface Contract`
6. `Acceptance Use Cases`
7. `Test Data`
8. `Performance and Index Notes`
9. `Open Questions`

## How To Fill Them

### Status Enums

- List the business statuses that affect this module or screen.
- Explain the trigger for each transition.
- If the screen is read-only, state that explicitly instead of leaving the item blank.
- If a status dictionary is missing, record the current fallback rule and mark the gap.

### Permissions and Data Scope

- State who can see or operate this screen or action.
- State which org, tenant, user, supplier, budget unit, or other data scope filters apply.
- State whether data scope is inherited from login context, route params, or explicit filters.

### Write Transactions and Idempotency

- For write flows, identify the transactional boundary.
- State whether repeated submit, repeated callback, or browser refresh can duplicate data.
- Record anti-duplicate strategy such as unique keys, version fields, request tokens, or state guards.
- For read-only screens, explicitly write `Read-only; no transaction or idempotency requirement`.

### Related Module Impact

- Identify upstream modules that provide required data.
- Identify downstream modules, pages, states, reminders, statistics, or reports that will change after this screen acts.
- Record whether the impact is navigation-only, business-only, data-only, or multi-dimensional.

### Interface Contract

- List required APIs with method, path, purpose, core request fields, core response fields, and error/empty-state behavior.
- Keep frontend and backend report wording aligned. If a field name is provisional, mark it as provisional in both reports.

### Acceptance Use Cases

- Write concrete verification cases, not generic statements.
- Cover normal flow, boundary flow, empty/error flow, permission denial, and state-transition flow when applicable.

### Test Data

- Describe the minimum data set needed for development and verification.
- Include representative statuses, roles, org scopes, empty data, and exceptional data when applicable.
- Prefer table-level or entity-level descriptions over large copied SQL snippets.

### Performance and Index Notes

- State expected high-frequency queries, aggregations, sorts, or joins.
- Note whether the current SQL obviously supports them or whether indexes/views/materialized summaries may be needed.
- If the module is not performance-sensitive, say why.

### Open Questions

- Record only unresolved items that materially affect implementation or acceptance.
- If an item is non-blocking, say so and document the temporary fallback.

## Report Placement

- `module-relations.md`: summarize cross-screen and cross-module checklist items, especially status dependencies, permissions/data scope dependencies, related module impact, shared interfaces, shared test data, and shared open questions.
- `frontend-plan.md`: capture interface-contract alignment, UI acceptance use cases, UI test data assumptions, and screen-level impact notes.
- `backend-plan.md`: capture the full checklist in implementation detail, especially status enums, permissions/data scope, transactions/idempotency, interface contract, test data, and performance/index notes.

## Confirmation Rule

Do not mark a report `confirmed` when any blocking checklist item is still:

- unknown,
- contradictory,
- copied as placeholder text, or
- deferred without a fallback decision.

Use lifecycle statuses according to `references/status-contract.md`. In this checklist context, use `draft` when analysis is still in progress and `blocked` when the missing answer prevents a safe implementation plan.


# Report Contract

`model-implement-executor` should treat non-`.zh.md` report files as canonical.

Prototype images remain required implementation references for the target screen. Reports define the implementation contract. When the report does not fully specify style details, current framework, design-system, component-library, and similar-page styles are the default style source; the matching prototype calibrates layout structure, component grouping, relative positions, and explicit visual differences.

## Initialization Contract

Before implementation, `model-implement-executor` should read:

- `reports/init-airead/shared-context.md`
- `reports/init-airead/business-flows.md`
- `reports/init-airead/db-assessment.md`
- `reports/modules/<module-name>/module-readiness.md`
- `library/定义规则.md`
- matched knowledge-library paths required by `library/定义规则.md`
- `prototypes/<module-name>/` materials that match the target screen when visual or interaction details need calibration

Knowledge-library references are mandatory before implementation. If the knowledge library exists, `library/定义规则.md` is the gate. The executor must read it, follow the priority and lookup rules, read matched concrete documents, and stop before code changes if required knowledge files are missing or conflicts cannot be resolved.

`shared-context.md` should contain:

- project understanding,
- framework scan,
- existing module inventory,
- shared assumptions,
- shared risks.

`business-flows.md` should explain:

- roles,
- cross-module flow,
- state dependencies,
- shared data hand-offs,
- reusable existing capabilities,
- flow ambiguities.

`db-assessment.md` should explain:

- whether the schema supports the target module,
- key schema risks,
- fallback assumptions,
- performance or index concerns,
- open schema questions.

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

If the confirmed plan and the prototype disagree on a material implementation detail, stop and ask for clarification unless the user has already stated which one overrides the other.


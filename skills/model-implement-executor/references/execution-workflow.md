# Execution Workflow

## Required Reading

Before editing code, read:

- `model-context-rag` status and search results, then the matched original report sections
- `.codex/model-implement/reports/init-read/初始化契约.md`
- `.codex/model-implement/reports/init-read/代码及框架信息.md`
- `.codex/model-implement/reports/init-read/已有功能模块信息.md`
- `.codex/model-implement/reports/init-read/待办清单.md`
- `.codex/model-implement/reports/init-read/业务理解.md`
- `.codex/model-implement/reports/init-read/数据库审查报告.md`
- `.codex/model-implement/reports/init-read/待确认点.md`
- `.codex/model-implement/reports/modules/<module-name>/module-readiness.md`
- `.codex/model-implement/reports/modules/<module-name>/module-relations.md`
- `.codex/model-implement/reports/modules/<module-name>/<screen-name>/frontend-plan.md`
- `.codex/model-implement/reports/modules/<module-name>/<screen-name>/backend-plan.md`
- `.codex/model-implement/prototypes/<module-name>/` prototype image or notes that match the target screen
- `.codex/model-implement/.sql/` SQL files related to the target module, tables, interfaces, or fields
- `.codex/model-implement/library/定义规则.md`
- matched knowledge-library paths under `.codex/model-implement/library/`
- `.codex/model-implement/memory/shared-rules.md`
- `.codex/model-implement/memory/executor-rules.md`

Use the reports as the implementation contract, but still inspect the target prototype image and similar existing pages as calibration sources. When style details are missing from `frontend-plan.md`, default to the current framework, design system, component library, and similar existing pages for colors, spacing, typography, density, and component styling. Use the prototype to calibrate layout structure, component grouping, relative positions, and explicit visual differences instead of inventing a new style.

Use RAG only as a locator. Run `rag-status.ps1 -ModelRoot ".codex/model-implement" -Json` first. If status is `healthy`, search normally; if `warning`, search and read wider original sections; if `blocked`, do not rely on search results and directly read original reports. Implementation facts must come from original reports, plans, SQL files, prototypes, knowledge-library docs, or real code.

Knowledge-library reading is mandatory before editing code. Read `library/定义规则.md`, identify all matched required and lookup-on-use entries for the implementation task, read those specific files, and obey them strictly. Do not treat the knowledge library as optional background. If `library/` exists but `定义规则.md` is missing, matched files cannot be read, or rule priority is unclear, stop before editing code.

SQL/database reading is mandatory for backend or data-binding work. Compare `backend-plan.md`, `数据库审查报告.md`, `.sql` files, and real backend code before editing Mapper, Entity, DTO, VO, migration SQL, or status enums. Do not silently add or reinterpret fields.

## Steps

1. Confirm the target module readiness report allows implementation.
2. Confirm the target screen plans and the module relation plan allow implementation.
3. Run the RAG gate:
   - `scripts/rag-status.ps1 -ModelRoot ".codex/model-implement" -Json`
   - Search by module name, screen name, page title, interface name, table name, field business meaning, database gap, confirmation issue, and reusable existing feature.
   - Open matched original files and record paths used.
4. Enforce the knowledge-library gate: read `library/定义规则.md`, search/read all matched specific knowledge files, and record the actual paths used.
5. Locate the target screen prototype before editing UI code, and inspect notes or supplemental documents under the same prototype module folder.
6. Read `.sql`, `数据库审查报告.md`, and backend plan sections that mention target tables, fields, status values, indexes, procedures, triggers, or views.
7. Inspect the relevant existing code paths named in the screen plans, including similar pages, shared components, style files, API clients, route/menu configuration, permission checks, backend controllers, services, mappers, entities, DTOs, VOs, and tests.
8. Build a short implementation checklist from the confirmed plans:
   - frontend files and visible behavior,
   - backend interfaces and data operations,
   - SQL/schema assumptions,
   - permissions and validation,
   - verification commands,
   - risky items to skip or confirm.
9. Implement the necessary bounded frontend and backend changes that satisfy the chosen screen plans, follow the matched knowledge-library rules, follow current framework style where the plan is visually underspecified, use the prototype for layout and explicit differences, and do not break module relations.
10. When style details are not explicitly specified, default to current framework/style-system consistency and do not invent replacement styling.
11. Preserve framework conventions discovered in the codebase.
12. If a plan, prototype, SQL evidence, knowledge-library rule, and current framework style conflict, classify the issue:
   - Safe and necessary: implement.
   - High-risk but not necessary for the current safe closure: skip and add to manual confirmation.
   - Blocking for the current closure: stop that subtask and report why.
13. Run relevant checks or tests.
14. Update the relevant screen or module relation report only with durable facts when the user wants the reports kept in sync.
15. Create or update `reports/modules/<module-name>/<screen-name>/implementation-record.md` when the implementation changes code.
16. Append useful execution observations to `.codex/model-implement/memory/executor.jsonl`.
17. Promote stable implementation rules to `.codex/model-implement/memory/executor-rules.md` when repeated or user-confirmed.
18. Use `shared_candidate=true` only for execution lessons that should also constrain initialization or planning, because it can bypass the normal private-rule score threshold; otherwise keep them private to executor memory.

## Risk Deferral Policy

Prefer deferring high-risk non-blocking changes over making broad speculative edits.

Defer and list for manual confirmation when the change would:

- alter shared framework, request, permission, route, menu, auth, or state-management foundations,
- add or reinterpret unconfirmed database fields, indexes, status enums, or migrations,
- change SQL used by unrelated modules,
- refactor reusable components beyond the target page's need,
- migrate or rewrite historical data,
- overwrite unrelated user work,
- choose between conflicting plan/prototype/knowledge-library/SQL evidence without a stated priority.

Do not defer silently. Put every deferred item in `implementation-record.md` and in the final response with impact, severity, suggested owner, and whether acceptance is blocked.

## Stop Conditions

Stop and ask for clarification when:

- the target module readiness report is `draft` or `blocked`,
- the target screen plan or module relation report is `draft` or `blocked`,
- `library/` exists but `library/定义规则.md` is missing,
- a matched required knowledge-library file is missing or unreadable,
- knowledge-library rules conflict with user instructions, project rules, or confirmed plans and priority cannot be determined,
- the implementation would contradict `shared-rules.md`,
- the plan depends on a missing API, schema, route decision, or initialization decision,
- the plan, prototype, SQL evidence, knowledge-library rule, and current framework style disagree on a material layout, style, interaction, data-display, status, permission, or persistence behavior and the issue blocks the current implementation closure,
- the requested change risks overwriting unrelated user work.

If the disagreement is high-risk but not required for the current closure, skip that part and list it for manual confirmation instead of stopping the entire safe implementation.


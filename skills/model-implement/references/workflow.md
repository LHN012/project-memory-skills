# Model Implement Workflow

## Purpose

Use this workflow to convert initialized project context, RAG-located original reports, knowledge-library matches, and one target module's raw screens into reusable screen-level implementation plans before code is written.

## Inputs

- `reports/init-read/初始化契约.md`
- `reports/init-read/代码及框架信息.md`
- `reports/init-read/已有功能模块信息.md`
- `reports/init-read/待办清单.md`
- `reports/init-read/业务理解.md`
- `reports/init-read/数据库审查报告.md`
- `reports/init-read/待确认点.md`
- `reports/init-airead/source-manifest.json`
- `reports/modules/<module-name>/module-readiness.md`
- `reports/init-read/待确认点.md` when confirmation findings affect the target module
- `model-context-rag` status and search results for target module context location
- `library/定义规则.md` when `.codex/model-implement/library/` exists, plus only the matched knowledge-library paths for the target module
- `.codex/model-implement/prototypes/<module-name>/` raw prototype images, notes, and module-specific source files
- Existing detailed module reports under `.codex/model-implement/reports/modules/<module-name>/`

## Steps

1. Load stable rules from `memory/model-implement-rules.md` and `memory/shared-rules.md`.
2. Run `model-context-rag` status first:
   - Preferred command: `scripts/rag-status.ps1 -ModelRoot ".codex/model-implement" -Json`.
   - If no index exists or the source manifest is stale, run `scripts/rag-index.ps1 -ModelRoot ".codex/model-implement"` and then rerun status.
   - If status is `healthy`, use search normally.
   - If status is `warning`, use search only as a locator and read wider original-report sections.
   - If status is `blocked`, do not rely on search results; fall back to direct original report reading.
3. Search RAG with several small queries instead of one broad query. Include the target module name, screen names, task category, business objects, known route/page names, database gaps, confirmation points, reusable existing pages, and framework/style keywords.
4. Open original files from RAG `source_path`, `heading`, or `suggested_read`. Record the search terms, original paths read, and conclusions in the generated reports. Never cite `chunks.jsonl` as a human-readable source.
5. Confirm the required new initialization reports exist and are current enough for the target module.
6. Read `reports/modules/<module-name>/module-readiness.md` and stop if it is `draft` or `blocked`.
7. If `.codex/model-implement/library/` exists, read `library/定义规则.md`; then use `knowledge-library` local search for target module terms, page type, component names, permission/API/SQL/style keywords, and read only matched rule, component, style, or special-reference paths. Do not read `library/README.md` by default and do not recursively scan the whole library.
8. Run `scripts/module_doc_bootstrap.py --module <module-name>` to create missing module and screen report files.
9. Analyze the target module's raw prototype screens and notes using the initialization reports as the primary shared context. For every screen, write a prototype comparison: prototype regions, existing similar screen, copied layout decisions, project-style decisions, business differences, and conflicts.
10. Inspect current code only as needed to resolve target-module route, component, API, existing screen style, component-library usage, and implementation-pattern conventions.
11. Update `reports/modules/<module-name>/module-relations.md` with internal and cross-module relations, RAG source trail, knowledge-library references, and executor implementation order suggestions.
12. Update each target `frontend-plan.md` with detailed frontend planning. When style details are not otherwise specified, use the current project framework, design system, component library, and similar existing pages as the default style source.
13. Use prototypes to calibrate layout structure, component combinations, relative positioning, business-specific differences, and explicitly marked new visual requirements. If prototype styling conflicts with the current framework, record the conflict as an open question instead of silently copying it.
14. Update each target `backend-plan.md` with detailed backend planning. Describe tables, fields, routes, interfaces, and statuses with business meaning so the executor can implement without guessing.
15. Complete the business-closure checklist in every affected report.
16. Capture unresolved questions in the relevant screen or relation report and keep status as `draft` or `blocked` when answers are required. Reference `待确认点.md` issue IDs when possible.
17. Append useful planning observations to `memory/model-implement.jsonl`.
18. Promote only repeated or user-confirmed planning rules to `memory/model-implement-rules.md`.
19. Stop after plans are written. Do not invoke, hand off to, or claim completion by `model-implement-executor`; write only what a later user-triggered executor run should read and do.

## Reuse Policy

Do not redo framework-wide or SQL-wide initialization here. If `代码及框架信息.md`, `已有功能模块信息.md`, `待办清单.md`, `业务理解.md`, `数据库审查报告.md`, or `待确认点.md` are stale, refresh `model-implement-init` instead.

Do not treat RAG output as source truth. RAG output is a table of contents for large memory and reports. Read the original Markdown report, module report, or memory file before writing implementation decisions.

Do not redo a full knowledge-library indexing pass here. Use `library/定义规则.md` as the entry and read only matched paths needed by the target module.

If only one target module changes, update only that module folder, its screen reports, and its `module-relations.md`.

## Confirmation Policy

Do not mark a report `confirmed` when the business-closure checklist still contains blocking unknowns, contradictory assumptions, or placeholder text.

Use lifecycle statuses according to `references/status-contract.md`. In planning reports, use `draft` when analysis is still in progress and `blocked` when the missing answer prevents safe implementation planning.

## Boundary Policy

Do not hand off automatically to `model-implement-executor`.

Do not state that implementation has started or has been assigned to executor. The plan can include a section named "给后续 executor 的实施顺序建议", but the next skill must be triggered by the user in a separate step.

Do not rewrite initialization reports such as `代码及框架信息.md`, `已有功能模块信息.md`, `待办清单.md`, `业务理解.md`, `数据库审查报告.md`, or `待确认点.md` from this skill.

Finish after module relations, screen plans, and planning memory updates are written. The user decides whether to run `model-implement-executor` in a separate step.


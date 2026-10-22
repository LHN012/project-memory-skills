# Model Implement Init Workflow

## Purpose

Prepare project-level and module-level initialization context before any screen-specific implementation plan is generated. The workflow follows a real project handover sequence:

1. Prepare project instructions and initialization contract.
2. Understand code and framework information.
3. Understand existing feature modules and reusable capabilities.
4. Classify prototype/material requirements and review business/database gaps.

The old `shared-context.md`, `business-flows.md`, and `db-assessment.md` are replaced by the six human-readable initialization reports under `reports/init-read/`.

## Inputs

- Existing application framework and codebase.
- `.codex/model-implement/library/定义规则.md` as the knowledge-library entry.
- `.codex/skills/knowledge-library/scripts/kb-init-project.ps1` for AGENTS initialization.
- `.codex/model-implement/prototypes/` as the prototype and requirement input root.
- `.codex/model-implement/.sql/` as the primary shared SQL source.
- Additional requirement descriptions from user messages or local documents.
- Existing reports and memory under `.codex/model-implement/`.
- `.codex/skills/model-context-rag/scripts/` for refreshing reports/memory context indexes after user supplementation or before downstream handoff.

## Layer 1: Preparation

1. Load stable rules from `memory/init-rules.md` and `memory/shared-rules.md`.
2. Ensure project `AGENTS.md` exists. Run:

```powershell
powershell -ExecutionPolicy Bypass -File ".codex/skills/knowledge-library/scripts/kb-init-project.ps1" -ProjectRoot "." -LibraryRoot ".codex/model-implement/library"
```

If the script path differs, locate it under `.codex/skills/knowledge-library/scripts/`.

3. Read `.codex/model-implement/library/定义规则.md` if it exists.
4. Run `scripts/init_doc_bootstrap.py` to create missing initialization reports and module readiness reports.
5. Write `reports/init-read/初始化契约.md` with input scope, output list, status rules, severity rules, desensitization rules, human-readable reporting rules, and downstream handoff rules.
6. Refresh `reports/init-airead/source-manifest.json` with `scripts/source_fingerprint.py`. Default sources include `prototypes/`, `.sql/`, and `library/定义规则.md`; add matched knowledge-library paths only when used.

## Layer 2: Code And Framework Scan

Write `reports/init-read/代码及框架信息.md`.

Scan and summarize:

- Frontend dependencies and versions, including Vue, VS/VSUI libraries, build tools, router, state management, request wrapper, and permission entry.
- Backend dependencies and versions, including Spring/Spring Boot, MyBatis or ORM, pagination, permission integration, Controller/Service/Mapper/XML layering, exception and logging conventions.
- Active datasource evidence. Use runtime datasource config as primary evidence; DDL style and dependencies are supporting evidence only.
- Existing code style: naming, directory structure, comments, loading states, dialog reset, pagination, date handling, MyBatis dynamic conditions.
- Project-specific reusable engineering capabilities.

Do not report secrets, passwords, tokens, datasource URLs, internal hosts, or production data.

## Layer 3: Existing Feature Module Scan

Write `reports/init-read/已有功能模块信息.md`.

Use:

- Frontend routes and menu config.
- Page directories and page titles.
- Frontend API files and hardcoded request paths.
- Backend Controller/API paths, DTO/VO, Service, Mapper/XML.
- Permission and data-scope code.

For each module, write the page name and business purpose before route/file path. Identify reusable implementations such as list pages, table pagination, filters, dialogs/drawers, detail/edit penetration, upload, import/export, dicts, permission, current user retrieval, workflow components, and shared utilities.

## Layer 4: Materials, Business, Database, Todo

1. Inventory `.codex/model-implement/prototypes/`. Inputs may be module folders, root-level PPT/PPTX, Excel function lists, PDF/Word documents, Markdown, HTML exports, images, extracted prototype folders, or user-specified paths.
2. Classify each material or requirement into:
   - New feature module or new page.
   - Existing page feature addition or behavior adjustment.
   - Batch bug/problem fix.
   - Unclassified material.
3. Write `reports/init-read/待办清单.md` as the task classification and progress-control document.
4. Extract business flows, roles, business objects, state changes, page penetration, dialogs/drawers, details/edit flows, and cross-module navigation. Write `reports/init-read/业务理解.md` with Mermaid diagrams.
5. Run `scripts/sql_schema_digest.py` against `.codex/model-implement/.sql/` and write:
   - `reports/init-airead/sql-schema-digest.json`
   - `reports/init-airead/sql-schema-digest.md`
6. Read SQL digest and original SQL as needed. Write `reports/init-read/数据库审查报告.md` with human-readable business explanations, required/suggested table or field changes, and severity levels.
7. Write `reports/init-read/待确认点.md`. Include only questions that remain after checking code, prototypes, SQL, knowledge-library, and reasonable inference.
8. Update `reports/modules/<module-name>/module-readiness.md` with readiness judgement for each target module or task group.
9. Append useful initialization observations to `memory/init.jsonl`, promote stable rules to `memory/init-rules.md`, and synthesize shared memory when useful.

## Post-Supplement Context RAG Gate

Use this gate when the user updates or answers based on initialization reports, including SQL supplementation, todo-list changes, answered confirmation points, business-flow corrections, database-review updates, or messages such as "已补充", "已回答", "SQL 已补完", "清单已调整", "报告已修改", "可以进入下一阶段", or "开始页面方案".

Before readiness handoff or downstream planning, refresh the reports/memory context index:

```powershell
powershell -ExecutionPolicy Bypass -File ".codex/skills/model-context-rag/scripts/rag-index.ps1" -ModelRoot ".codex/model-implement"
powershell -ExecutionPolicy Bypass -File ".codex/skills/model-context-rag/scripts/rag-status.ps1" -ModelRoot ".codex/model-implement" -Json
```

If the skill path differs, locate `model-context-rag/scripts/rag-index.ps1` under `.codex/skills/`.

Status handling:

- `healthy`: continue readiness judgement or handoff.
- `warning`: continue only after noting the quality risk; downstream work must read matched original reports, not only chunks.
- `blocked`: do not hand off to downstream skills based on the stale or broken index. Rebuild the index, fix the reports/memory, or fall back to direct original-report reading.

## Library Policy

If `library/` exists:

- Always read `library/定义规则.md`.
- Do not read `library/README.md` by default unless maintaining the library.
- Use `定义规则.md` and `kb-search.ps1` to locate matched rule, component, style, or special-reference documents.
- Record the actual paths used in `初始化契约.md`, `代码及框架信息.md`, or the relevant report.
- Do not recursively read all of `library/`.

If `library/` does not exist, initialization can continue, but `初始化契约.md` and `待确认点.md` must record the missing knowledge library.

## Prototype Material Policy

Do not require users to reorganize materials before initialization.

When module/page ownership is inferred from filenames, PPT page titles, Excel rows, document headings, screenshots, or directories, mark it as inferred. If ownership is unclear, record it under unclassified materials in `待办清单.md` and `待确认点.md`.

## Database Policy

Use `.codex/model-implement/.sql/` as the primary schema source. Before database review, run `scripts/sql_schema_digest.py`.

Database review must explain gaps in business language:

- Which page or business action needs the data.
- What existing table/field evidence exists.
- What is missing.
- Where to add a field or table.
- What the field/table means in Chinese.
- Severity and impact.

Do not output bare technical field lists without explanation.

## Reuse Policy

Do not reanalyze unchanged sources unnecessarily. Compare `source-manifest.json` and update only affected reports when possible.

If one prototype module or one root-level material changes, update affected sections in:

- `待办清单.md`
- `业务理解.md`
- `数据库审查报告.md`
- `待确认点.md`
- affected `module-readiness.md`

After these updates, run the Post-Supplement Context RAG Gate before marking a module ready for downstream planning.

Refresh `代码及框架信息.md` or `已有功能模块信息.md` only when project code, routes, menus, dependencies, or reusable capabilities changed.

## Readiness Policy

Do not mark `module-readiness.md` as `ready` when any blocking initialization condition remains unresolved.

For new modules/pages, readiness requires clear source material, business flow, database support or fallback, and no P0 confirmation point.

For existing page modifications or bug batches, readiness requires locating the target page/interface/code range in `已有功能模块信息.md`, classifying the task in `待办清单.md`, and documenting any unresolved P0/P1 risks.

If reports or memory were supplemented after initial report generation, readiness also requires `reports/context-rag/index-status.json` to exist and not be `blocked`.

## Boundary Policy

Do not generate per-screen `frontend-plan.md` or `backend-plan.md`.

Do not implement frontend or backend code. Finish after initialization reports, readiness decisions, and memory updates are written.

The user decides whether to run `model-implement`, `model-implement-executor`, `model-implement-fix`, or `model-implement-review` later.

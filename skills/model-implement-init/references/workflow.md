# Model Implement Init Workflow

## Purpose

Use this workflow to prepare project-level and module-level initialization context before any screen-specific implementation plan is generated.

## Inputs

- Existing application framework and codebase.
- `.codex/model-implement/library/` when present. Read only `library/定义规则.md` as the knowledge-library entry, then load only the matched rule, component, style, or special-reference paths.
- `.codex/model-implement/prototypes/` as the prototype and requirement input root. Inputs may be standard module folders, root-level PPT/PPTX files, Excel function lists, PDF/Word documents, Markdown, HTML exports, scattered images, extracted prototype folders, or user-specified paths.
- `.codex/model-implement/.sql/` as the primary shared SQL source, typically containing one complete SQL file with tables, views, triggers, procedures, and other database objects.
- Additional SQL files or database documentation found in the workspace.
- Requirement descriptions from user messages or local documents.
- Existing reports and memory under `.codex/model-implement/`.

## Steps

1. Load stable rules from `memory/init-rules.md` and `memory/shared-rules.md`.
2. Check whether `.codex/model-implement/library/` exists. If it is missing, record a user-facing reminder in the initialization outputs. If it exists, read `library/定义规则.md` and record matched knowledge paths as initialization reference material.
3. Load `reports/init-airead/source-manifest.json` and decide whether existing initialization reports can be reused. The default manifest sources should include `prototypes/`, `.sql/`, and `library/定义规则.md`; add matched knowledge-library paths as extra sources only when they are used.
4. Identify the requested initialization scope. Prefer a requested module folder when it exists, but do not assume prototype inputs are always split by module folder.
5. Build an input-material inventory before business analysis. Classify files by evidence source: folder name, root-level file name, PPT/PPTX page title, Excel function item, document heading, image name, HTML export path, or explicit user instruction.
6. Run `scripts/init_doc_bootstrap.py` to create missing initialization reports and module readiness reports. When no standard module folder exists, create an `_unclassified-inputs` readiness report so the material can still be reviewed and assigned.
7. Scan the current framework and summarize stable facts in `reports/init-airead/shared-context.md`.
8. Scan existing code modules and note reusable capabilities, routes, permissions, tables, APIs, and UI patterns.
9. Run `scripts/sql_schema_digest.py` against `.codex/model-implement/.sql/` and write `reports/init-airead/sql-schema-digest.json` plus `reports/init-airead/sql-schema-digest.md`.
10. Read `.codex/model-implement/.sql/` and the generated schema digest, evaluate the shared SQL against business-flow and module needs, and write the result into `reports/init-airead/db-assessment.md`.
11. Extract cross-module business flows, roles, states, page associations, drill-through paths, and hand-offs into `reports/init-airead/business-flows.md`.
12. Write `reports/init-read/初始化总结.md` as the concise human-facing entry report, including broad business-flow and page-association Mermaid diagrams and any knowledge-library reference summary.
13. Write `reports/init-read/功能模块清单.md` as the human-facing module/menu/page directory. It should record each major module, nested submodules, pages, page source material, and unresolved classification questions.
14. Write AI-facing canonical reports in `reports/init-airead/shared-context.md`, `reports/init-airead/business-flows.md`, `reports/init-airead/db-assessment.md`, and `reports/init-airead/input-materials.md`.
15. Write user-facing Chinese reports in `reports/init-read/共享上下文.md`, `reports/init-read/业务流程.md`, `reports/init-read/数据库评估.md`, and `reports/init-read/待人工确认.md`.
16. For the requested module or inferred material group, update `reports/modules/<module-name>/module-readiness.md` with a readiness judgement and clear blocking or non-blocking conditions.
17. Append useful initialization observations to `memory/init.jsonl`.
18. Promote repeated or user-confirmed initialization rules to `memory/init-rules.md`.
19. Synthesize shared memory from init, planning, and execution rules into `memory/shared-memory.md` and `memory/shared-rules.md` when useful.

## Library Policy

If `library/` exists, treat it as initialization reference material, not as raw source code to scan exhaustively:

- Always read `library/定义规则.md` when present.
- Do not read `library/README.md` by default; it overlaps with `定义规则.md` and should only be used if the user explicitly asks for knowledge-library maintenance context.
- Use `定义规则.md` to decide which rule, component, style, or special-reference documents are relevant.
- Record the existence, missing entry file, matched paths, and any conflicts in `init-airead/shared-context.md` or `init-read/待人工确认.md`.
- Do not recursively read all of `library/`; some entries may contain large demos, images, generated assets, or vendor files.

If `library/` does not exist, initialization should continue, but the human-facing reports should remind the user that no knowledge library was found.

## Prototype Material Policy

Prototype and requirement material may be diverse. Do not require users to reorganize it before initialization.

Supported inputs include:

- standard `prototypes/<module-name>/` folders,
- root-level `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.pdf`, `.doc`, `.docx`, `.md`, `.html`,
- scattered `.png`, `.jpg`, `.jpeg`, `.webp`, `.gif`,
- exported prototype folders,
- manually provided paths or descriptions.

When module ownership is inferred from filenames, PPT page titles, Excel rows, document headings, or screenshots, mark it as inferred. If module ownership is unclear, use `_unclassified-inputs` and list the exact evidence needed from the user.

## Reuse Policy

Do not reanalyze unchanged sources. Refresh the source manifest and compare the combined hash before spending context on repeated prototype, `.codex/model-implement/.sql/`, or matched knowledge-library parsing.

If only one prototype module or one root-level material file changes, update only the affected `module-readiness.md` or `_unclassified-inputs` report, any affected flow or database sections, `init-read/初始化总结.md`, `init-read/功能模块清单.md`, and `init-read/待人工确认.md` if its blocking conditions change.

## Readiness Policy

Do not mark `module-readiness.md` as `ready` when any blocking initialization condition is still unresolved.

For non-standard prototype material, do not mark a module as `ready` until the source files, page list, and module ownership are either confirmed or documented as non-blocking assumptions.

Use lifecycle statuses according to `references/status-contract.md`. In initialization reports, use `draft` when analysis is still in progress, `blocked` when a missing answer prevents safe screen planning, and `done` only when the initialization context is mature for the current source fingerprint.

## Boundary Policy

Do not generate per-screen `frontend-plan.md` or `backend-plan.md`.

Do not implement frontend or backend code. Finish after initialization reports, readiness decisions, and memory updates are written. The user decides whether to run `model-implement` or `model-implement-executor` later.

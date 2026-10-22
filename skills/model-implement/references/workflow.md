# Model Implement Workflow

## Purpose

Use this workflow to convert initialized project context plus one target module's raw screens into reusable screen-level implementation plans before code is written.

## Inputs

- `reports/init-airead/shared-context.md`
- `reports/init-airead/business-flows.md`
- `reports/init-airead/db-assessment.md`
- `reports/init-airead/source-manifest.json`
- `reports/modules/<module-name>/module-readiness.md`
- `reports/init-read/待人工确认.md` when human-review findings affect the target module
- `library/定义规则.md` when `.codex/model-implement/library/` exists, plus only the matched knowledge-library paths for the target module
- `.codex/model-implement/prototypes/<module-name>/` raw prototype images, notes, and module-specific source files
- Existing detailed module reports under `.codex/model-implement/reports/modules/<module-name>/`

## Steps

1. Load stable rules from `memory/model-implement-rules.md` and `memory/shared-rules.md`.
2. Confirm the required initialization reports exist and are current enough for the target module.
3. Read `reports/modules/<module-name>/module-readiness.md` and stop if it is `draft` or `blocked`.
4. If `.codex/model-implement/library/` exists, read `library/定义规则.md`; then read only matched rule, component, style, or special-reference paths for the target module. Do not read `library/README.md` by default and do not recursively scan the whole library.
5. Run `scripts/module_doc_bootstrap.py --module <module-name>` to create missing module and screen report files.
6. Analyze the target module's raw prototype screens and notes using the initialization reports as the primary shared context.
7. Inspect current code only as needed to resolve target-module route, component, API, existing screen style, component-library usage, and implementation-pattern conventions.
8. Update `reports/modules/<module-name>/module-relations.md` with internal and cross-module relations.
9. Update each target `frontend-plan.md` with detailed frontend planning. When style details are not otherwise specified, use the current project framework, design system, component library, and similar existing pages as the default style source.
10. Use prototypes to calibrate layout structure, component combinations, relative positioning, business-specific differences, and explicitly marked new visual requirements. If prototype styling conflicts with the current framework, record the conflict as an open question instead of silently copying it.
11. Update each target `backend-plan.md` with detailed backend planning.
12. Complete the business-closure checklist in every affected report.
13. Capture unresolved questions in the relevant screen or relation report and keep status as `draft` or `blocked` when answers are required.
14. Append useful planning observations to `memory/model-implement.jsonl`.
15. Promote only repeated or user-confirmed planning rules to `memory/model-implement-rules.md`.

## Reuse Policy

Do not redo framework-wide or SQL-wide initialization here. If the shared initialization reports are stale, refresh `model-implement-init` instead.

Do not redo a full knowledge-library indexing pass here. Use `library/定义规则.md` as the entry and read only matched paths needed by the target module.

If only one target module changes, update only that module folder, its screen reports, and its `module-relations.md`.

## Confirmation Policy

Do not mark a report `confirmed` when the business-closure checklist still contains blocking unknowns, contradictory assumptions, or placeholder text.

Use lifecycle statuses according to `references/status-contract.md`. In planning reports, use `draft` when analysis is still in progress and `blocked` when the missing answer prevents safe implementation planning.

## Boundary Policy

Do not hand off automatically to `model-implement-executor`.

Do not rewrite shared context, business-flow, or database-assessment reports from this skill.

Finish after module relations, screen plans, and planning memory updates are written. The user decides whether to run `model-implement-executor` in a separate step.


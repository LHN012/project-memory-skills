# Status Contract

## Purpose

Use this contract whenever a report, plan, issue, review, or knowledge-library capture needs a lifecycle status. Keep status values stable and do not invent new lifecycle statuses inside individual reports.

This contract separates lifecycle statuses from classification labels:

- Lifecycle statuses describe progress and whether the next action is safe.
- Classification labels describe evidence or type, such as `confirmed`, `inferred`, `unclassified`, `P0`, `P1`, `component`, or `feature`.

## Global Lifecycle Statuses

- `draft`: Work is being analyzed or prepared. The document is not reliable enough for downstream execution.
- `blocked`: Work cannot safely continue until a missing input, conflict, or decision is resolved.
- `ready`: The current artifact is ready for the next stage, but the next stage has not started.
- `confirmed`: A plan or decision has been accepted as the implementation contract.
- `implementing`: Confirmed work is actively being executed.
- `done`: The current stage is complete for the current input fingerprint or confirmed scope.

## Stage-Specific Statuses

Use these only in the listed stage:

- `reproducing`: `model-implement-fix` is reproducing or gathering proof for an issue.
- `diagnosed`: `model-implement-fix` has identified the root cause but has not completed the fix.
- `fixing`: `model-implement-fix` is actively applying a fix.
- `fixed`: `model-implement-fix` has completed the fix and verification for the stated issue.
- `study-only`: `knowledge-library` has produced a learning/reference entry and should not extract code.
- `ready-for-extract`: `knowledge-library` has enough evidence and permission to extract or refactor.
- `extracted`: `knowledge-library` has completed an approved extraction/refactor.

## Allowed Statuses By Artifact

| Artifact | Allowed lifecycle statuses |
|---|---|
| `reports/init-airead/source-manifest.json` / `sql-schema-digest.*` | `draft`, `blocked`, `done` |
| `reports/init-read/初始化契约.md` | `draft`, `blocked`, `done` |
| `reports/init-read/代码及框架信息.md` | `draft`, `blocked`, `done` |
| `reports/init-read/已有功能模块信息.md` | `draft`, `blocked`, `done` |
| `reports/init-read/待办清单.md` | `draft`, `blocked`, `done` |
| `reports/init-read/业务理解.md` | `draft`, `blocked`, `done` |
| `reports/init-read/数据库审查报告.md` | `draft`, `blocked`, `done` |
| `reports/init-read/待确认点.md` | `draft`, `blocked`, `done` |
| `reports/modules/<module>/module-readiness.md` | `draft`, `blocked`, `ready`, `done` |
| `reports/modules/<module>/module-relations.md` | `draft`, `blocked`, `confirmed`, `implementing`, `done` |
| `frontend-plan.md` / `backend-plan.md` | `draft`, `blocked`, `confirmed`, `implementing`, `done` |
| `reports/issues/<issue>/issue.md` | `draft`, `blocked`, `reproducing`, `diagnosed`, `fixing`, `fixed` |
| `reports/issues/<issue>/fix-result.md` | `draft`, `blocked`, `fixing`, `fixed` |
| `reports/reviews/<review>/接口契约对齐判断.md` | `draft`, `blocked`, `done` |
| `reports/reviews/<review>/运行时待审查清单.md` | `draft`, `blocked`, `done` |
| `reports/reviews/<review>/审查问题清单.md` | `draft`, `blocked`, `done` |
| `library/**` knowledge capture entry | `draft`, `blocked`, `study-only`, `ready-for-extract`, `extracted`, `done` |

## Transition Rules

- `draft` may move to `blocked`, `ready`, `confirmed`, `study-only`, `diagnosed`, or `done`, depending on artifact type.
- `blocked` may only move forward after the blocking reason is resolved or the user explicitly approves a documented fallback.
- `ready` may move to `confirmed` only when the user or current workflow accepts the artifact as a contract.
- `confirmed` may move to `implementing` only when the user starts execution.
- `implementing` may move to `done` after implementation and required verification are complete.
- `reproducing` may move to `diagnosed` after the issue is proven and root cause is known.
- `diagnosed` may move to `fixing` when code changes begin.
- `fixing` may move to `fixed` only after the fix validation checklist passes or documented residual risks are accepted.
- `study-only` may move to `ready-for-extract` only after the user explicitly allows extraction/refactor and dependencies are clear.
- `ready-for-extract` may move to `extracted` only after the approved extraction/refactor is complete and validated.

## Blocking Rules

Use `blocked` instead of guessing when any of these are true:

- Required input files, SQL, prototypes, knowledge-library entries, or confirmed plans are missing.
- Business rules, permission/data scope, status transitions, or interface contracts are unclear.
- A report conflicts with the prototype, current framework, database schema, or knowledge-library rules.
- A downstream stage would need to invent implementation details that should be user-confirmed.
- Knowledge-library rules are required but missing, unreadable, or have unresolved priority conflicts.

## Non-Lifecycle Labels

Do not use these as lifecycle statuses:

- Evidence labels: `confirmed`, `inferred`, `unclassified` when used for module/page/source classification.
- Review severity labels: `P0`, `P1`, `P2`, `P3`.
- Asset type labels: `component`, `feature`, `logic`, `mixed`.
- Issue type labels: `visual`, `interaction`, `data`, `permission`, `api`, `state`, `performance`, `regression`.

When a word such as `confirmed` is used as an evidence label, write it in a field like `归类状态` or `evidence_status`; do not place it in the document lifecycle `状态` field unless the artifact itself is confirmed as a contract.

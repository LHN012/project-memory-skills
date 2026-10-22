# Runtime Checklist Builder

## Purpose

Use this checklist to generate `运行时待审查清单.md` after interface contract alignment is complete. The checklist is a progress tracker, not the final issue report.

## Required Checklist Fields

Each item should include:

- `编号`
- `页面`
- `交互项`
- `关联接口`
- `验收标准`
- `验收方式`
- `测试状态`
- `是否报错`
- `是否阻塞`
- `问题编号`
- `复测策略`

Allowed `测试状态` values:

- `未测`
- `已测通过`
- `已测有报错`
- `阻塞未测`
- `不适用`

Allowed `验收方式` values:

- `完整测试`
- `微测试`
- `静态确认`
- `人工确认`

Allowed `复测策略` values:

- `完整测试`
- `微测试`
- `本轮跳过`
- `阻塞未测`
- `人工确认`

An item can be marked `已测通过` only when its acceptance criteria are satisfied. A click without visible errors is not enough.

## Sources

Generate items from these sources:

- Frontend API calls.
- Backend interface actions.
- Page buttons and row actions.
- Search filters and reset controls.
- Tables, pagination, sorting, selection, expand rows.
- Forms, validation rules, input fields, date controls, dictionary selects, tree selects.
- Dialogs, drawers, popovers, tabs, steps, details pages.
- Upload, preview, download, import, export.
- Route jumps, detail jumps, back buttons, cross-module navigation.
- Empty, loading, error, disabled, and no-permission states.
- Accepted plans, interface contracts, review config, module-specific requirements, and default acceptance rules.

## Acceptance Criteria

Every checklist item must have a concrete `验收标准`. Derive it from:

1. Confirmed `frontend-plan.md`, `backend-plan.md`, and `module-relations.md`.
2. `接口契约对齐判断.md`.
3. Optional `reports/review-config/测试流程与要求.md` and `<模块名>-测试要求.md`.
4. Current implementation and interface behavior.
5. Default rules below when no explicit standard exists.

Default acceptance rules:

- Query: request succeeds, optional empty fields are handled correctly, list result matches visible filters, pagination total and current page are correct.
- Reset: filters return to default values and query result refreshes according to defaults.
- Add: required validation works, save request succeeds, new record can be found by list or detail query.
- Edit: edit request succeeds, changed fields are visible after re-querying list or detail.
- Delete/void/disable: operation is safe or explicitly allowed; after operation, list/detail reflects deleted, voided, disabled, or hidden state.
- Detail: navigation opens the expected record and fields match list or backend response.
- Pagination/sorting: page, size, sort fields and visible result order are consistent with interface behavior.
- Dialog/drawer: open, close, submit, cancel, validation, and state reset work as expected.
- Upload/download/export/import: trigger succeeds, user feedback appears, and related request or download behavior is observable.
- Permission state: hidden, disabled, or denied behavior matches role and data-scope expectations.
- Error/empty/loading state: page shows appropriate feedback and recovers when the condition changes.

## Retest Strategy

Use retest strategy to avoid repeating already-passed checks blindly.

- `完整测试`: Required for core flows, changed interfaces, changed permissions, changed data model, changed frontend behavior, and previous failures.
- `微测试`: Allowed when an item previously passed and this round has no direct related code/interface/config/schema change. Verify the smallest observable signal, such as page opens, query works, or key button triggers the expected request.
- `本轮跳过`: Allowed only when previous pass evidence exists and no related change is detected. Record the reason in `未覆盖范围` or `清单更新记录`.
- `阻塞未测`: Use when environment, authorization, data, or safety conditions prevent testing.
- `人工确认`: Use for irreversible delete, approval, stock, finance, external notification, or hardware/third-party operations.

Core paths such as login/session, query, add, edit, delete/void, submit/audit, and affected interfaces should not be skipped solely because a prior round passed.

## Required Coverage

For target module pages, cover all visible and enabled interactions by default:

1. Query and reset.
2. Filter controls, including date and dictionary controls.
3. Table pagination and sorting.
4. Detail navigation.
5. Add, edit, delete, save, cancel, submit, audit, return.
6. Dialog or drawer open, close, submit, cancel, validation.
7. Upload, preview, download, import, export when present.
8. Tab, tree, step, and linkage controls when present.
9. Empty, loading, error, disabled, and no-permission states when reachable.

Hidden permission states, uncommon roles, extreme data, and long cross-module chains can be marked as extended coverage. If not tested, list them in `审查问题清单.md` as uncovered scope.

## CRUD Flow Items

When a page supports CRUD, generate a linked group of items in this order:

1. Add test data.
2. Query list or detail to confirm add.
3. Edit test data.
4. Query again to confirm edit.
5. Delete, void, revoke, or disable.
6. Query again to confirm delete/void/revoke/disable result.

Use a unique test data prefix such as `AI_REVIEW_YYYYMMDD_<module>_<random>`.

If delete is irreversible or may affect approval, stock, finance, notifications, or external systems, do not execute it automatically. Mark the item as `阻塞未测` or `不适用`, and write the reason in `审查问题清单.md`.

## Checklist Discipline

Do not write detailed problems in `运行时待审查清单.md`.

Allowed:

- completion status,
- acceptance criteria and validation method,
- whether an error occurred,
- whether the item is blocked,
- linked issue id such as `P1-001`.

Not allowed:

- stack traces,
- full API responses,
- root-cause analysis,
- screenshots,
- repair suggestions,
- long reproduction text.

Write those details in `审查问题清单.md`.

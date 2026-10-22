# Acceptance And Retest Rules

## Purpose

Runtime review is not just clicking controls. Each checklist item must define what counts as acceptance and how much retesting is needed.

## Acceptance Principle

An item is `已测通过` only when its `验收标准` is met.

Examples:

- Query is accepted only when request succeeds and visible results match filters, pagination, and expected data scope.
- Add is accepted only when validation works, save succeeds, and the new record can be found again.
- Edit is accepted only when the changed value appears after re-query.
- Delete or void is accepted only when the expected hidden, deleted, voided, or disabled state appears after re-query.
- Export is accepted only when the trigger, request, feedback, and download behavior match expectations.

## Validation Method

Use one of:

- `完整测试`: Execute the full user flow and verify the final state.
- `微测试`: Verify a reduced signal because prior pass evidence exists and this item is low-risk this round.
- `静态确认`: Confirm through code, interface contract, or config when runtime action is not necessary or not possible.
- `人工确认`: Require user or external system confirmation.

## Retest Strategy

Use one of:

- `完整测试`: Use for core flows, changed code, changed interface, changed permission, changed config, changed schema, or previous failures.
- `微测试`: Use for previously passed low-risk items with no related change.
- `本轮跳过`: Use only when prior pass evidence exists and the item is outside current impact scope.
- `阻塞未测`: Use when environment, authorization, data, or safety conditions prevent testing.
- `人工确认`: Use for irreversible or external side-effect actions.

## Must Not Skip

Do not skip solely because a previous round passed when the item is:

- login/session or authorization,
- query/list load,
- add/edit/delete/void,
- submit/audit/status transition,
- affected by current frontend, backend, permission, config, SQL, or route changes,
- previously failed or blocked.

Skipped and micro-tested items must be summarized in `审查问题清单.md` under `未覆盖范围` or `测试缺口` when they leave meaningful residual risk.

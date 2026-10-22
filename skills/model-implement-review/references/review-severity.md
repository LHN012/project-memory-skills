# Review Severity

Use `P0` to `P3` for concrete findings in `审查问题清单.md`.

## P0

Blocks release or must be handled immediately.

Typical cases:

- Serious data corruption or data loss.
- Severe permission or data-scope bypass.
- Core module page cannot be opened or core flow cannot be completed.
- CRUD flow writes wrong data or cannot verify persisted result.
- Irreversible operation may affect real approval, stock, finance, notification, or external systems.

## P1

High-risk issue that should be prioritized.

Typical cases:

- Frontend calls a missing backend endpoint on a common path.
- Request/response contract mismatch breaks save, edit, detail, query, upload, export, submit, audit, or delete.
- Backend returns 500, 403, 404, or invalid payload during a core interaction.
- Important UI action has no effect because event binding, permission, route, or API call is wrong.
- State transition, transaction, idempotency, permission, or data scope is clearly wrong.

## P2

Medium-risk issue that should be fixed but may not block all release scenarios.

Typical cases:

- Boundary filter, date, enum, pagination, sorting, empty-state, or validation issue.
- Non-core interaction works inconsistently.
- Page does not refresh after write, but data is saved.
- Console or network warning indicates likely future regression.
- UI or interaction deviates from the confirmed plan but has a workaround.

## P3

Low-risk robustness, maintainability, or experience issue.

Typical cases:

- Minor prompt, empty-state, loading-state, or disabled-state issue.
- Low-risk duplicate request or non-blocking console warning.
- Interaction is usable but feedback is weak.
- Small maintainability issue discovered during interface alignment.

## Principles

- Severity follows business impact, data risk, permission risk, and release blocking risk.
- Do not raise a style preference to P1 unless it causes behavior, data, or acceptance risk.
- A checklist item marked `已测有报错` does not automatically mean P1; judge by impact.
- Missing implementation is an implementation gap, not necessarily a bug. Recommend `model-implement-executor` when appropriate.

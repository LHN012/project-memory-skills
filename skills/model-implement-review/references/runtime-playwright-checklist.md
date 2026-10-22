# Playwright Runtime Review Checklist

## Purpose

Use Playwright to test the actual target module page after interface alignment and `运行时待审查清单.md` are prepared.

## Runtime Gate

Before running Playwright actions, confirm:

- The URL is a test, dev, staging, or otherwise safe environment.
- Test data can be created with a unique prefix.
- Data cleanup or rollback strategy is known.
- Delete, approval, stock, finance, external notification, and irreversible actions are safe or explicitly skipped.
- The target page can be reached by URL or menu path.

If any gate is not satisfied, do not execute destructive actions. Mark affected checklist items as `阻塞未测`.

Account and authorization information is optional before testing starts. If the page requires login, captcha, SMS, SSO, menu authorization, or session refresh, pause and ask the user to complete authorization in the browser, then continue from the current checklist item. If authorization cannot be completed, mark affected items as `阻塞未测`.

If the user provides reusable test account notes, environment notes, or flow requirements during this process, save non-sensitive information to `reports/review-config/`. Do not save real passwords, tokens, production URLs, or sensitive business data unless explicitly requested.

## Control Operation Memory

Before interacting with controls, read available stable review memory:

- `memory/review-rules.md`
- `memory/shared-rules.md`
- `memory/shared-memory.md`

Prefer prior successful operation recipes when they match the current framework, page pattern, or component type. Examples include dropdowns that require opening the overlay before selecting text, table row buttons that should be scoped to a matched row, tree nodes that require expansion before click, and upload controls that require targeting the hidden file input.

When Playwright exploration produces reusable control-operation experience, append a compact observation to `memory/review.jsonl`. Record:

- Module and page or route.
- Component type and applicable UI framework if known.
- Failed attempts that should not be repeated.
- Successful operation sequence.
- Locator strategy and stable wait condition.
- Scope of applicability.
- Whether it is a shared-rule candidate.

Promote only repeated, cross-page, or user-confirmed operation patterns to `memory/review-rules.md`. Do not record real credentials, tokens, captcha values, production URLs, sensitive business data, or one-off random DOM ids.

## Evidence To Capture

During Playwright testing, capture:

- Browser console errors.
- Failed or suspicious network requests, including method, URL/path, status, and brief response summary.
- Page-level symptoms such as no response, loading stuck, wrong toast, data not refreshed, modal not closed, table unchanged, or navigation failure.
- Screenshots only when useful for explaining a finding.

Do not paste large logs into `运行时待审查清单.md`. Put evidence summaries into `审查问题清单.md`.

## Test Order

For normal interaction items:

1. Open the target page.
2. Wait for initial requests to finish or for the main content to become stable.
3. Test one checklist item.
4. Record console/network/page evidence.
5. Judge whether the item meets its `验收标准`; only then mark it as `已测通过`.
6. Update `运行时待审查清单.md` immediately.
7. If a concrete problem exists, add or update a finding in `审查问题清单.md` and link its issue id in the checklist.

For CRUD:

1. Add test data with a unique prefix.
2. Query the list or detail page and verify the new record appears.
3. Edit a distinctive field.
4. Query again and verify the edited value appears.
5. Delete, void, disable, or revoke only when safe.
6. Query again and verify the expected result.

## Common Interaction Checks

- Buttons trigger the expected request or UI state.
- Save and submit buttons show loading or prevent duplicate submission.
- Required-field validation appears before invalid requests.
- Cancel and close clear form state when expected.
- Search omits empty optional fields instead of sending empty strings for dates or invalid filters.
- Reset restores default conditions.
- Pagination sends correct page and size.
- Sorting sends or applies expected sort.
- Dialogs and drawers open, close, submit, cancel, and clear state correctly.
- Upload and export show progress or user feedback.
- Permission-disabled buttons are hidden or disabled consistently.
- After successful writes, list/detail data refreshes correctly.

## Result Mapping

Update `运行时待审查清单.md` as follows:

- `已测通过`: action worked and no relevant console/network/page error was found.
- `已测有报错`: action completed enough to observe a concrete error.
- `阻塞未测`: cannot safely or technically test the item.
- `不适用`: item does not apply to the current role, page, state, or environment.

Every `已测有报错` item should have a linked issue id in `审查问题清单.md`.

## Retest Behavior

When an item already passed in this round or a previous round:

- Use `完整测试` for core business paths or anything affected by current changes.
- Use `微测试` for previously passed, low-risk items with no related frontend/backend/interface/config/schema change.
- Use `本轮跳过` only when prior evidence exists and the item is outside current impact scope.
- Use `人工确认` for destructive or external side-effect actions.

Do not mark skipped or micro-tested items as fully verified unless the acceptance criteria were actually checked.

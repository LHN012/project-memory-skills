# Reuse Capture

Use this reference when replacing the old reuse skill with knowledge-library capture.

## Goal

Reusable implementation knowledge should become maintainable library entries, not isolated reuse reports.

## Capture Workflow

1. Clarify the asset name, source path, scope, and whether code modification is allowed.
2. Default to study-only. Do not refactor or extract code unless the user explicitly asks.
3. Read only relevant files: components, services, routes, APIs, SQL, styles, docs, and screenshots when visual behavior matters.
4. Decide the destination:
   - `组件库/` for reusable components or feature packages.
   - `规则库/` for stable rules or implementation constraints.
   - `样式库/` for UI/style patterns.
   - A new category only when none of the above fits.
5. Write the knowledge entry with:
   - Scope.
   - Applicability.
   - Contract.
   - Dependencies.
   - Integration steps.
   - Examples.
   - Caveats and non-reusable parts.
   - Verification checklist.
6. Register the entry in `定义规则.md` if it should be discoverable by triggers.
7. Run index and validation scripts.

## Boundaries

Do not copy large source files into knowledge docs. Link paths and summarize contracts. Do not promote one-off project quirks into global rules unless they are confirmed stable.

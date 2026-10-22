# Maintenance Rules

Use this reference when adding, deleting, archiving, or deprecating knowledge.

## Add Knowledge

1. Choose the right category.
2. Write a human-readable Markdown entry or example file.
3. Add or update the category README when needed.
4. Register important routes in `定义规则.md`.
5. Run `kb-index.ps1`.
6. Test with 3-5 realistic `kb-search.ps1` queries.

## Delete Knowledge

- Wrong content: fix or delete it.
- Replaced content: mark deprecated first when traceability matters.
- Temporarily unused content: move it under `archive/`; archive is excluded by default.

## Deprecation Block

Use a short YAML-like block at the top:

```yaml
---
status: deprecated
deprecated_at: 2026-06-22
replaced_by: path/to/new-doc.md
reason: short reason
---
```

Run the indexer after deprecation so search results can down-rank or hide the document.

## Validation

Run `kb-validate.ps1` after structural changes. Fix missing `定义规则.md`, stale indexes, missing source files, and obvious broken relative links.

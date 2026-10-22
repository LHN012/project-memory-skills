# AGENTS.md Knowledge Block

Use this reference before adding or editing project-level `AGENTS.md` content.

## Principle

`AGENTS.md` should contain a short durable pointer and mandatory routing rules. It should not duplicate the whole library.

The init script owns only this marked block:

```md
<!-- BEGIN KNOWLEDGE_LIBRARY -->
...
<!-- END KNOWLEDGE_LIBRARY -->
```

Everything outside that block belongs to the user or project.

## Recommended Content

The block should state:

- The absolute or project-relative knowledge library path.
- Read `定义规则.md` first for code, SQL, component, style, review, or maintenance tasks.
- Do not scan the entire library without a reason.
- Use local search (`kb-search.ps1`) when the relevant document is unclear.
- For SQL, confirm the active database before using dialect rules.
- For insufficient information, mark `待确认` instead of guessing.
- When `.codex/model-implement/reports/` or `memory/` has been supplemented and the user is entering the next stage, refresh `model-context-rag` first; if `reports/context-rag/index-status.json` is `blocked`, do not rely on context search results.
- Final answers should list the actual knowledge-library paths read.

## Idempotence

Running initialization repeatedly must update the marked block instead of appending duplicates.

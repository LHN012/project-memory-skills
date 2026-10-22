# Knowledge Library Structure

Use this reference when creating or reorganizing a local knowledge library.

## Recommended Tree

```text
library/
  README.md
  定义规则.md
  规则库/
  组件库/
  样式库/
  archive/
  .ai/
    manifest.json
    chunks.jsonl
    search-report.md
  .codex/
    skills/
      knowledge-library/
```

`README.md` is for human browsing. `定义规则.md` is the routing contract for Codex. `.ai/` is generated and can be deleted/rebuilt.

## Entry Documents

Every major category should have a `README.md` or an obvious entry document. Component entries should include:

- Scope and when to use it.
- Required prerequisites.
- Frontend integration.
- Backend integration.
- Database or config requirements.
- Interface contract and examples.
- Common problems.
- Maintenance notes.

Rule entries should include:

- Mandatory rules.
- Recommended patterns.
- Forbidden patterns.
- Examples.
- Pre-submit checklist.

## Indexing Policy

Index normal source files. Exclude `.ai/`, `.git/`, `node_modules/`, `dist/`, `build/`, `target/`, `.idea/`, `.vscode/`, and `archive/` by default.

Do not index secrets, production data, private credentials, copied large source dumps, or binary files.

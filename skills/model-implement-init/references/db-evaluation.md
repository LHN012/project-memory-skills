# Database Evaluation Adapter

Use the full SQL file in `.codex/model-implement/.sql/` as the primary schema source. Before writing `reports/init-read/数据库审查报告.md`, run `scripts/sql_schema_digest.py` and read `reports/init-airead/sql-schema-digest.json` or `reports/init-airead/sql-schema-digest.md` to ground table, field, key, index, and enum-comment observations. Use `.codex/规则文档/数据库表结构设计评估指南.md` when it exists. If the rules doc is unreadable or absent, apply the condensed checklist below.

Write findings in human-readable business language. Do not output bare table or field names. Every table, field, index, or relation should include its Chinese meaning, business use, and impact on pages or flows when possible.

## Required Checks

- Entity coverage: every business entity from requirements, business flows, and prototypes has a table or documented persistence strategy.
- Attribute coverage: important business attributes have corresponding fields.
- Relationship coverage: one-to-one, one-to-many, and many-to-many relationships are represented by keys, join tables, or explicit documented conventions.
- State coverage: business statuses, approval states, after-sales states, and reminders have a storable representation or a documented fallback.
- Query support: frequent filters, sorts, grouping, list screens, and statistics have supporting fields and indexes.
- Data operations: create, update, delete, batch operations, state transitions, and audit needs are supported.
- Business rules: uniqueness, required fields, statuses, calculations, and constraints are represented.
- Field quality: data types, lengths, nullability, default values, and monetary precision are appropriate.
- Relationship consistency: related key field types and lengths match.
- Index quality: primary, foreign, unique, and common query indexes are present where needed.

## Priority

- `P0`: blocks core functionality or makes required data impossible to store or query.
- `P1`: supports basic function but has obvious correctness, integrity, or maintainability risk.
- `P2`: works but should be improved for clarity, performance, or long-term quality.

## Report Shape

For each issue, include:

- Problem
- Impact
- Recommendation
- Priority
- Business flow or page affected
- Suggested table or field location
- Chinese meaning of the suggested field or table

Prefer concrete table and field names. Avoid inventing schema changes when requirements are ambiguous; record an open question instead.

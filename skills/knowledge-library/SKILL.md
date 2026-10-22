---
name: knowledge-library
description: "维护本地知识库、生成轻量索引、执行本地检索、初始化项目 AGENTS.md 知识库读取规则，并从项目实现中沉淀可复用知识条目。适用于 library/定义规则.md、规则库、组件库、样式库、知识删除/废弃/归档、kb-index、kb-search、AGENTS 初始化、替代旧复用 skill 的知识沉淀流程。"
---

# Knowledge Library

## Overview

Use this skill to keep a human-readable knowledge library usable by Codex. The source of truth stays in Markdown and example files; generated `.ai/` indexes are disposable search caches.

## Quick Choice

- Need to prepare a project to use a knowledge library: run `scripts/kb-init-project.ps1`.
- Need to refresh search data after editing docs: run `scripts/kb-index.ps1`.
- Need to find relevant knowledge before coding: run `scripts/kb-search.ps1`.
- Need to check broken paths, missing entry docs, or stale indexes: run `scripts/kb-validate.ps1`.
- Need to remove knowledge safely: use archive/deprecated rules and optionally run `scripts/kb-deprecate.ps1`.
- Need to replace reuse capture: write the reusable asset into `组件库/`, `规则库/`, or `样式库/`, then regenerate the index.

## Working Model

Keep these layers separate:

- `AGENTS.md`: durable project instruction and knowledge-library entry pointer.
- `library/定义规则.md`: human and AI routing table for mandatory and on-demand reads.
- `library/**/*.md`, code, SQL, config examples: human-maintained source material.
- `library/.ai/manifest.json` and `library/.ai/chunks.jsonl`: generated search cache; never hand edit.

## Standard Workflow

1. Resolve `LibraryRoot`. Prefer a user-provided path. Otherwise use the current project knowledge path such as `.codex/model-implement/library` or a directory containing `定义规则.md`.
2. Read `定义规则.md` before changing routing rules or answering how the library should be used.
3. Edit only human-facing source files: Markdown, examples, SQL, or README files.
4. Run `kb-index.ps1 -LibraryRoot <path>` after changes.
5. Run `kb-search.ps1 -LibraryRoot <path> -Query "<terms>"` for realistic tasks and check whether the expected documents appear.
6. Run `kb-validate.ps1 -LibraryRoot <path>` before considering the library healthy.
7. When wiring a code project, run `kb-init-project.ps1 -ProjectRoot <project> -LibraryRoot <library>` to update a marked block in `AGENTS.md`.

## Library Rules

- Keep original docs readable for people. Do not split source docs into tiny RAG chunks by hand.
- Keep generated `.ai/` files out of manual review except for debugging search quality.
- Keep `archive/` out of the index by default.
- Mark outdated material with `status: deprecated` and `replaced_by` before deleting it when traceability matters.
- Do not index secrets, connection strings, production data, private tokens, or copied proprietary source dumps.
- Final answers that rely on library knowledge should list the actual source paths read.

## Reuse Replacement

This skill replaces the old reuse-only workflow. When the user asks to learn a reusable component, common implementation, cross-project pattern, or "沉淀复用":

1. Treat the work as knowledge capture, not automatic refactoring.
2. Read only the relevant source files and existing library entry.
3. Decide where the knowledge belongs: `组件库/`, `规则库/`, `样式库/`, or a clearly named new category.
4. Write a human-readable entry with scope, contract, integration steps, caveats, and examples.
5. Register the entry in `定义规则.md` if it should be discoverable or mandatory.
6. Regenerate and test the index.
7. Modify project code only when the user explicitly asks for implementation, extraction, or refactoring.

## Scripts

- `scripts/kb-index.ps1`: build `.ai/manifest.json`, `.ai/chunks.jsonl`, and `.ai/search-report.md`.
- `scripts/kb-search.ps1`: local keyword search over generated chunks with path/title/body scoring.
- `scripts/kb-init-project.ps1`: insert or update a stable knowledge-library block in a target `AGENTS.md`.
- `scripts/kb-validate.ps1`: check required files, generated index health, broken obvious links, and stale hashes.
- `scripts/kb-deprecate.ps1`: add or replace a small deprecation frontmatter block at the top of a document.

## References

- Read `references/library-structure.md` before reorganizing the library.
- Read `references/agents-block.md` before changing AGENTS initialization behavior.
- Read `references/maintenance-rules.md` before deleting, archiving, or deprecating knowledge.
- Read `references/reuse-capture.md` when replacing reuse-skill behavior with library entries.

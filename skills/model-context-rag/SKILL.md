---
name: model-context-rag
description: "为 .codex/model-implement/memory 和 reports 初始化/模块文档建立本地上下文 RAG 索引，执行结构化切分、关键词检索、索引状态读取和切分质量门禁。适用于 memory 或 reports 变大、其他 skill 需要先检索再精读原文、需要检查索引是否 healthy/warning/blocked、需要根据模块名/界面名/严重等级/报告类型查找初始化报告、模块方案、待确认点、数据库审查和历史记忆。第一版使用本地 JSONL/关键词索引，向量能力预留。"
---

# Model Context RAG

## 概述

这个 skill 为 `.codex/model-implement/` 下的项目过程知识建立可验证的本地检索层。它不替代 `knowledge-library`；`knowledge-library` 维护稳定规则和组件沉淀，本 skill 面向 `memory/`、`reports/init-read/`、`reports/modules/` 这些会随项目推进增长的上下文。

默认只创建和读取可丢弃机器产物，不改写原始报告和记忆。

## 快速选择

- 上下文有变化或首次使用：运行 `scripts/rag-index.ps1`。
- 只检查索引是否可信：运行 `scripts/rag-status.ps1`。
- 重新检测切分和索引质量：运行 `scripts/rag-validate.ps1`。
- 需要按问题、模块、界面、严重等级或报告类型找上下文：运行 `scripts/rag-search.ps1`。

## 工作区

默认模型上下文根目录是 `.codex/model-implement/`。索引输入范围固定为：

- `memory/`
- `reports/init-read/`
- `reports/modules/`

默认输出到：

- `reports/context-rag/manifest.json`
- `reports/context-rag/chunks.jsonl`
- `reports/context-rag/keyword-index.json`
- `reports/context-rag/index-status.json`
- `reports/context-rag/chunk-quality.json`
- `reports/context-rag/chunk-quality-report.md`
- `reports/context-rag/retrieval-quality-report.md`
- `reports/context-rag/search-report.md`

这些文件都是机器索引和质量报告，可以重建，不要手工编辑。

## 标准流程

1. 解析 `ModelRoot`。优先使用用户传入的 `-ModelRoot`；否则使用 `-ProjectRoot\.codex\model-implement`；再否则从当前目录向上寻找。
2. 运行 `scripts/rag-index.ps1 -ModelRoot <path>` 建立或刷新索引。
3. 读取 `reports/context-rag/index-status.json` 或运行 `scripts/rag-status.ps1`。
4. 若状态为 `healthy`，可以直接使用 `rag-search` 的命中结果作为候选上下文。
5. 若状态为 `warning`，可以搜索，但最终回答或规划前必须打开命中的原始报告精读，并说明索引质量风险。
6. 若状态为 `blocked`，不要把检索结果当作可靠事实；先重新运行 `rag-index` 或直接回退读取原始报告。
7. 搜索结果只负责定位候选上下文；需要做业务判断、方案设计、编码或审查时，必须读取命中的原始文件章节。

## 命令

```powershell
scripts/rag-index.ps1 -ModelRoot ".codex/model-implement"
scripts/rag-status.ps1 -ModelRoot ".codex/model-implement"
scripts/rag-validate.ps1 -ModelRoot ".codex/model-implement"
scripts/rag-search.ps1 "数据库字段缺口 P1" -ModelRoot ".codex/model-implement" -Top 8
scripts/rag-search.ps1 "登录人 附件上传" -ModelRoot ".codex/model-implement" -Module "合同管理"
scripts/rag-search.ps1 "待确认" -ModelRoot ".codex/model-implement" -SourceType "confirm-points" -Json
```

## 质量门禁

索引状态只有三种：

- `healthy`：源文件覆盖、元数据、结构检测和检索冒烟测试均满足要求，可供其他流程调用。
- `warning`：可检索，但存在轻微质量风险，例如敏感值被脱敏、chunk 偏小、重复率偏高或冒烟查询未全部通过。
- `blocked`：索引不可作为可靠上下文，例如索引过期、源文件覆盖不足、元数据缺失、空 chunk 或结构被切断。

切分质量细则见 `references/quality-gates.md`。切分规则见 `references/chunking-rules.md`。

## 调用契约

其他 skill 将来接入时，应遵守这个顺序：

1. 先调用 `rag-status`。
2. `healthy` 或用户明确允许 `warning` 时，再调用 `rag-search`。
3. 按搜索结果中的 `source_path` 与 `heading` 打开原始文件精读。
4. 在最终报告或方案中引用实际读取的原始路径，不把 `chunks.jsonl` 当作人读来源。
5. 如果 `blocked`，回退到直接读取 `reports/init-read/`、`reports/modules/` 和 `memory/` 的原文。

完整接入约定见 `references/integration-contract.md`。检索排序规则见 `references/retrieval-policy.md`。

## 边界

- 不索引 `library/`，稳定知识仍由 `knowledge-library` 管理。
- 不索引 `prototypes/`、`.sql/` 或真实源码；这些属于初始化或实施阶段的原始输入。
- 不生成 embedding，不连接外部向量库；第一版只做本地 JSONL 和关键词检索，并预留 `vectors.jsonl` 扩展位置。
- 不修改其他 skill 的 SKILL.md；接入由用户明确要求后再做。
- 不把账号、密码、token、JDBC URL 或密钥写入索引；脚本会脱敏并在质量报告中记录命中次数。

## 参考资料

- 需要调整切分策略时，读取 `references/chunking-rules.md`。
- 需要解释检索排序和回退策略时，读取 `references/retrieval-policy.md`。
- 需要解释 `healthy/warning/blocked` 或质量指标时，读取 `references/quality-gates.md`。
- 需要让其他 skill 调用本 skill 时，读取 `references/integration-contract.md`。

# Retrieval Policy

## 检索模型

第一版使用本地关键词检索和结构化元数据加权，不依赖外部向量库。

排序权重优先考虑：

- 文件路径、报告类型、模块名、界面名。
- 标题和章节标题。
- 严重等级，如 `P0`、`P1`。
- 正文命中次数。

## 查询建议

优先组合业务词和结构词：

```powershell
scripts/rag-search.ps1 "合同详情页 状态字段 P1" -ModelRoot ".codex/model-implement"
scripts/rag-search.ps1 "附件上传 登录人" -ModelRoot ".codex/model-implement" -Module "合同管理"
scripts/rag-search.ps1 "阻塞" -ModelRoot ".codex/model-implement" -SourceType "confirm-points"
```

## 结果使用

搜索结果用于定位候选上下文，不作为最终事实来源。真正生成方案、实施或审查前，必须打开结果中的 `source_path`，并围绕 `heading` 精读原文。

## 回退策略

- `healthy`：正常使用检索结果定位原文。
- `warning`：可以使用检索结果，但需说明质量风险，并扩大原文读取范围。
- `blocked`：不要使用索引作为事实来源，直接读取 `reports/` 和 `memory/` 原文。

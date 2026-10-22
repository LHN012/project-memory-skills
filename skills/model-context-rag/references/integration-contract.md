# Integration Contract

## 稳定入口

其他 skill 调用时只使用 PowerShell 入口：

- `scripts/rag-index.ps1`
- `scripts/rag-status.ps1`
- `scripts/rag-search.ps1`
- `scripts/rag-validate.ps1`

不要直接依赖 Python 内部函数。

## 推荐调用顺序

1. 调用 `rag-status.ps1 -ModelRoot <path> -Json`。
2. 若状态是 `blocked`，停止使用索引，回退原文读取。
3. 若状态是 `warning`，允许搜索，但必须扩大原文读取范围。
4. 调用 `rag-search.ps1 "<query>" -ModelRoot <path> -Json`。
5. 按返回的 `source_path` 和 `heading` 打开原始文件。
6. 最终输出引用原始路径，不引用 `chunks.jsonl`。

## JSON 返回约定

`rag-status` 返回：

```json
{
  "schema": "model-context-rag-v1",
  "status": "healthy",
  "source_coverage": 1.0,
  "metadata_complete_rate": 1.0,
  "retrieval_smoke_passed": true
}
```

`rag-search` 返回：

```json
{
  "schema": "model-context-rag-v1",
  "status": "healthy",
  "query": "数据库字段缺口",
  "results": [
    {
      "source_path": "reports/init-read/数据库审查报告.md",
      "heading": "合同状态字段缺口",
      "source_type": "db-review",
      "module": "合同管理",
      "page_name": "合同详情页",
      "severity": "P1 高风险",
      "suggested_read": "reports/init-read/数据库审查报告.md :: 合同状态字段缺口"
    }
  ]
}
```

## 版本

当前 schema 是 `model-context-rag-v1`。后续增加 embedding 或向量库时，应保持 `rag-status` 和 `rag-search` 的核心字段兼容。

# Quality Gates

## 状态

- `healthy`：可以被其他流程正常调用。
- `warning`：可以辅助定位，但必须精读原文并提示质量风险。
- `blocked`：不能作为可靠上下文，需要重建索引或回退原文读取。

## 阻塞条件

出现以下情况会进入 `blocked`：

- 存在源文件但没有生成 chunk。
- 索引过期，源文件 hash 与 manifest 不一致。
- 新增、缺失或删除的源文件尚未反映到索引。
- chunk 必填元数据完整率低于 90%。
- 存在空 chunk。
- 检测到代码块、表格等结构疑似被切断。

## 警告条件

出现以下情况会进入 `warning`：

- 没有发现可索引源文件。
- 存在超长 chunk。
- 过短 chunk 比例过高。
- 重复 chunk 比例偏高。
- 发现并脱敏了疑似敏感信息。
- 检索冒烟测试未全部通过。

## 主要指标

- `source_coverage`：当前源文件被索引覆盖的比例。
- `metadata_complete_rate`：必填元数据完整率。
- `broken_structure_count`：疑似切断表格、代码块等结构的 chunk 数。
- `duplicate_rate`：重复正文比例。
- `redacted_sensitive_hit_count`：脱敏命中次数。
- `retrieval_smoke_passed`：标题/章节冒烟查询是否能召回预期来源。

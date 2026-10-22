# Chunking Rules

## 目标

切分的目标是让 Codex 先定位上下文，再读取原文。chunk 不能取代原始报告，也不能把业务流程、风险项或表格切得失去语义。

## 输入范围

默认只切分：

- `memory/`
- `reports/init-read/`
- `reports/modules/`

不要默认切分 `library/`、`prototypes/`、`.sql/` 或源码目录。

## 切分规则

- Markdown 优先按标题层级切分。
- 单个标题章节过长时，再按自然块合并切分。
- 代码块、Mermaid 图、Markdown 表格尽量保持完整。
- `P0 阻塞`、`P1 高风险`、`P2 建议处理`、`P3 记录观察` 风险项必须保留在同一 chunk 中。
- 模块方案路径中的模块名和界面名必须进入 chunk 元数据。
- `memory/*.jsonl` 以单行事件为基本切分单位。
- 默认 chunk 上限为 2400 字符；超过 3600 字符会进入质量警告。

## 元数据

每个 chunk 至少应包含：

- `source_path`
- `source_type`
- `title`
- `heading`
- `text`

能识别时还应包含：

- `module`
- `page_name`
- `severity`

## 脱敏

疑似密码、token、密钥、JDBC URL、账号字段会被替换成 `[REDACTED]`。质量报告会记录脱敏命中次数。

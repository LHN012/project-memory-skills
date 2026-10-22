# Implementation Record Format

Create or update `reports/modules/<module-name>/<screen-name>/implementation-record.md` when executor changes code.

Keep it concise and useful for later `model-implement-fix`, review, or manual confirmation.

## Template

```markdown
# 实施记录：<界面名>

## 状态

implementing / done / blocked

## 本次实施范围

- 模块：
- 界面：
- 用户触发语义：
- 本次完成的功能闭环：
- 本次未覆盖范围：

## 读取依据

### Implement 方案

- `reports/modules/<模块名>/module-readiness.md`
- `reports/modules/<模块名>/module-relations.md`
- `reports/modules/<模块名>/<界面名>/frontend-plan.md`
- `reports/modules/<模块名>/<界面名>/backend-plan.md`

### RAG 与原文

- RAG 状态：
- 检索词：
- 精读原文路径：
- 关键结论：
- RAG 不可用时的回退读取范围：

### 原型与 SQL

- 原型材料：
- SQL/数据库审查依据：
- 表、字段、索引、状态口径确认：
- 数据库缺口：

### 知识库

- `library/定义规则.md`
- 实际读取的知识库路径：
- 对本次实施产生约束的规则：

## 代码改动

- 前端文件：
- 后端文件：
- SQL/配置文件：
- 测试或辅助文件：

## 验证结果

- 执行命令：
- 通过项：
- 失败项：
- 未验证原因：

## 跳过的高风险项与待人工确认

| 严重等级 | 项目 | 跳过原因 | 影响范围 | 建议处理 |
|---|---|---|---|---|
| P1/P2/P3 | 待补充 | 待补充 | 待补充 | 待补充 |

## 残余风险

- 待补充。

## 后续建议

- 待补充给 fix/review/人工确认的建议。
```

## Rules

- Do not record secrets, tokens, connection strings, production data, or private personal data.
- Do not list `reports/context-rag/chunks.jsonl` as a source. List the original files opened from RAG hits.
- If no code changed, do not create a fake implementation record unless the user asks for an execution attempt record.
- If high-risk work was skipped, record it even when implementation otherwise succeeded.

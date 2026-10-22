# 数据库表事实：<表名>

```yaml
---
memory_id: DATA-<DOMAIN>-<TABLE>-001
type: module
coverage: partial
status: draft
updated_at: YYYY-MM-DD
---
```

机器核验字段（`verified_commit`、`impact_paths`、`evidence_sources`、`record_hash` 等）写入 `modules/.audit.json`，不放回表文档头。

## 表作用与数据权威

- 表用途：
- 数据权威系统：
- 当前核验范围：

## 主键与生命周期

- 主键：
- 创建、更新、失效或删除规则：

## 字段

| 字段 | 类型 | 可空 | 默认值 | 业务含义 | 来源/状态 |
| --- | --- | --- | --- | --- | --- |

## 表关系

| 关系 | 目标表/字段 | 用途 | 当前依据 |
| --- | --- | --- | --- |

## 状态与约束

- 状态含义：
- 唯一性、外键、数据范围或事务约束：

## 读写入口

| 场景 | API/Service/Mapper | 读写 | 权限或事务 |
| --- | --- | --- | --- |

## 未确认项

| 问题 | 影响 | 确认方 |
| --- | --- | --- |

只记录当前已核验的表事实。DDL 原文作为来源，不整段复制；结构变更原因、迁移执行、验证和回滚写入 `changes`，计划中的新增/修改/删除写入 `plans`。

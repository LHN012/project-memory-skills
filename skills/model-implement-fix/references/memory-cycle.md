# Memory Cycle

## Private and Shared Memory

model-implement 相关 skill 分别维护自己的私有记忆：

- `memory/init.jsonl`
- `memory/init-rules.md`
- `memory/model-implement.jsonl`
- `memory/model-implement-rules.md`
- `memory/executor.jsonl`
- `memory/executor-rules.md`
- `memory/fix.jsonl`
- `memory/fix-rules.md`
- `memory/review.jsonl`
- `memory/review-rules.md`
共享记忆仍由 `model-implement-init` 负责合成：

- `memory/shared-memory.md`
- `memory/shared-rules.md`

共享规则是过滤后的合成结果，不是六套私有规则的简单并集。

## What To Record

只记录紧凑、可复用、经过验证的修复经验和项目认知：

- 重复出现的根因模式。
- 本次修复确认过的核心问题和有效定位路径。
- 用户明确确认的问题修复约束。
- 会反向影响规划或实施阶段的修复教训。
- 常见回归点和验证习惯。
- 修复过程中发现的项目基础事实，例如请求封装、路由/菜单方式、权限判断、接口返回结构、分页口径、后端分层、Mapper/SQL 位置、数据库方言、常用组件或样式约定。

不要记录：

- 密钥、账号、连接串、生产数据。
- 一次性临时日志。
- 未确认的猜测。
- 大段复制的源码或 SQL。
- 每个问题的完整流水账、复现步骤全文、无复用价值的 fix-result 摘要。

## Init-Read Backfill

修复过程中发现的项目基础事实，应逐步补充到初始化报告，让项目理解在修复中自然完善：

- 框架版本、目录结构、请求封装、路由、权限、代码风格：补到 `reports/init-read/代码及框架信息.md`。
- 新识别的页面、模块入口、接口和可复用能力：补到 `reports/init-read/已有功能模块信息.md`。
- 新确认的业务流程、状态含义、页面穿透、弹窗/详情/编辑链路：补到 `reports/init-read/业务理解.md`。
- 新发现的表、字段、索引、SQL 缺口、数据库风险：补到 `reports/init-read/数据库审查报告.md`。
- 修复中仍无法确认且会影响后续实现的问题：补到 `reports/init-read/待确认点.md`。

如果对应报告不存在，可以创建简短条目，并标记：

`> 修复过程中发现，待初始化阶段复核。`

不要为了回填初始化信息而全量扫描项目；只记录本次修复已经验证过的事实。

## Rule Promotion

提升路径如下：

1. 观察写入 `fix.jsonl`。
2. 重复出现或用户确认后成为规则候选。
3. 稳定后提升到 `fix-rules.md`。
4. 跨阶段有效时再进入 `shared-rules.md`。

只有明确会影响初始化、页面规划或代码实施的修复规则，才建议标记 `shared_candidate=true`，并且要谨慎使用。

## Synthesis

共享合成时：

- 读取初始化、页面规划、实施、问题修复和代码审查的私有规则文件。
- 只有在至少两个 skill 中重复出现，或某条私有规则显式带有 `shared_candidate=true` 时，才进入共享规则。
- 问题修复侧的局部 workaround 默认保留在 `fix-rules.md`，不要轻易提升为共享规则。

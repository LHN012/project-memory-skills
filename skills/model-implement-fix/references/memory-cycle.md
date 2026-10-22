# Memory Cycle

## Private and Shared Memory

六个 skill 分别维护自己的私有记忆：

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
- `memory/reuse.jsonl`
- `memory/reuse-rules.md`

共享记忆仍由 `model-implement-init` 负责合成：

- `memory/shared-memory.md`
- `memory/shared-rules.md`

共享规则是过滤后的合成结果，不是六套私有规则的简单并集。

## What To Record

只记录紧凑、可复用、经过验证的修复经验：

- 重复出现的根因模式。
- 用户明确确认的问题修复约束。
- 会反向影响规划或实施阶段的修复教训。
- 常见回归点和验证习惯。

不要记录：

- 密钥、账号、连接串、生产数据。
- 一次性临时日志。
- 未确认的猜测。
- 大段复制的源码或 SQL。

## Rule Promotion

提升路径如下：

1. 观察写入 `fix.jsonl`。
2. 重复出现或用户确认后成为规则候选。
3. 稳定后提升到 `fix-rules.md`。
4. 跨阶段有效时再进入 `shared-rules.md`。

只有明确会影响初始化、页面规划或代码实施的修复规则，才建议标记 `shared_candidate=true`，并且要谨慎使用。

## Synthesis

共享合成时：

- 读取六套私有规则文件。
- 只有在至少两个 skill 中重复出现，或某条私有规则显式带有 `shared_candidate=true` 时，才进入共享规则。
- 问题修复侧的局部 workaround 默认保留在 `fix-rules.md`，不要轻易提升为共享规则。

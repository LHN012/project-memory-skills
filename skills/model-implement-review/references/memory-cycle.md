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

只记录紧凑、可复用、经过验证的审查经验：

- 多次重复出现的高风险模式。
- 用户明确确认的审查标准。
- 会反向影响规划、实施或修复的审查教训。
- 常见测试缺口和回归风险模式。
- Playwright 控件操作经验：组件类型、失败尝试、成功步骤、选择器策略、等待条件和适用范围。

不要记录：

- 密钥、账号、连接串、生产数据。
- 一次性临时日志。
- 未确认的猜测。
- 大段复制的源码或 SQL。
- 真实密码、token、验证码、生产地址、敏感业务数据或一次性随机 DOM id。

## Rule Promotion

提升路径如下：

1. 观察写入 `review.jsonl`。
2. 重复出现或用户确认后成为规则候选。
3. 稳定后提升到 `review-rules.md`。
4. 跨阶段有效时再进入 `shared-rules.md`。

只有明确会影响初始化、页面规划、代码实施或问题修复的审查规则，才建议标记 `shared_candidate=true`。

Playwright 控件操作经验默认只留在 review 记忆中。只有当某条操作规则对多个模块、多个页面或多个 skill 都有稳定帮助时，才建议标记为共享候选。

## Synthesis

共享合成时：

- 读取初始化、页面规划、实施、问题修复和代码审查的私有规则文件。
- 只有在至少两个 skill 中重复出现，或某条私有规则显式带有 `shared_candidate=true` 时，才进入共享规则。
- 审查侧的一次性发现默认保留在 `review-rules.md` 或报告中，不要轻易提升为共享规则。

# Memory Cycle

## 私有与共享记忆

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

只记录紧凑、可复用、经过验证的复用经验：

- 哪些公共抽象真正提升了后续复用效率。
- 哪些组件或功能看起来相似，但实际不该合并。
- 哪些依赖边界是抽离时最容易遗漏的。
- 哪些跨项目适配点必须提前暴露。
- 用户明确确认的复用边界和抽离原则。

不要记录：

- 外部项目的大段源码拷贝。
- 密钥、账号、连接串、生产数据。
- 一次性目录结构细节或局部 hack。
- 未验证的抽象猜测。

## Rule Promotion

提升路径如下：

1. 观察写入 `reuse.jsonl`。
2. 重复出现或用户确认后成为规则候选。
3. 稳定后提升到 `reuse-rules.md`。
4. 跨阶段有效时再进入 `shared-rules.md`。

只有明确会影响初始化、页面规划、代码实施、问题修复或代码审查的复用规则，才建议标记 `shared_candidate=true`。

## Synthesis

共享合成时：

- 读取六套私有规则文件。
- 只有在至少两个 skill 中重复出现，或某条私有规则显式带有 `shared_candidate=true` 时，才进入共享规则。
- 复用侧的局部目录命名、单项目依赖和一次性抽离技巧，默认保留在 `reuse-rules.md`，不要轻易提升为共享规则。

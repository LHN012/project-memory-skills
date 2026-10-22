# Review Workflow

## Goal

`model-implement-review` 用于审查代码改动、模块实现或上线前风险。它只输出发现和建议，不默认修复，也不自动调用其他 skill。

## Modes

1. `diff review`
   - 优先模式。
   - 用于审查当前改动、指定文件或 diff。
2. `module review`
   - 用于审查某个模块、页面、接口或功能范围。
3. `release review`
   - 用于上线前审查回归风险、测试缺口和阻塞项。

## Steps

1. 确认审查模式和范围。
2. 收集输入：用户说明、diff、代码路径、方案文档、初始化上下文、必要的问题修复文档。
3. 判断是否需要参考原型：
   - 默认不参考原型。
   - 只有 UI 还原、交互一致性、页面视觉偏差审查，或用户明确要求时才参考原型。
4. 按 `review-checklist.md` 做风险检查。
5. 按 `review-severity.md` 给发现定级。
6. 更新 `reports/reviews/<评审名>/review.md`。
7. 输出所有发现和“待用户选择”列表。
8. 等待用户选择要处理的发现项；没有用户明确选择，不进入任何后续 skill。

## Source Priority

1. 用户最新明确指令。
2. 本次审查范围和目标。
3. 当前代码改动或目标文件。
4. 已确认方案文档。
5. 初始化上下文文档：优先读取 `reports/init-airead/shared-context.md`、`business-flows.md`、`db-assessment.md`、`input-materials.md`。
6. 人读初始化辅助文档：`reports/init-read/功能模块清单.md`、`reports/init-read/待人工确认.md`，仅在需要确认页面归属、人工待确认项或用户侧表述时读取。
7. 必要的问题修复文档。
8. 原型图，仅在审查类型触发时使用。
9. `shared-rules.md` 与 `review-rules.md`。

## Downstream Recommendation

可以在发现项中推荐后续 skill：

- `model-implement-init`：上下文、SQL 评估、业务流程不清。
- `model-implement`：页面方案缺失、方案不细或方案冲突。
- `model-implement-executor`：已确认方案未实施或属于实施缺口。
- `model-implement-fix`：已有实现存在 bug、回归或偏差。

推荐不是执行。必须等待用户明确选择发现项和授权后，才允许进入对应 skill。

## Stop Conditions

遇到以下情况应先停下：

- 审查范围过大且用户没有指定优先级。
- 缺少关键代码或报告，导致无法形成可靠发现。
- 发现需要业务决策，而不是代码审查能判断。
- 用户要求直接修复，但尚未选择具体发现项或授权后续 skill。

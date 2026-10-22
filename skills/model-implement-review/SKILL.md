---
name: model-implement-review
description: "用于审查当前项目代码改动、模块实现或上线前风险，重点发现 bug、回归、权限/数据范围、接口契约、事务幂等、状态流转、性能索引、测试缺口，以及 UI 与方案或原型不一致。只输出 findings 和推荐后续处理，不默认修改代码或调用其他 skill。触发词：代码审查、review、上线前风险、审查 diff、审查模块、P0/P1 发现。必须等待用户选择发现项后才进入修复、实施或规划。"
---

# Model Implement Review

## 概述

这个 skill 用于代码审查和风险审查。它的核心目标是发现真实 bug、行为回归、业务风险和测试缺口，而不是做风格挑刺，也不是默认修复问题。

## 触发与交付速查

- 触发词：代码审查、review、上线前风险、审查 diff、审查模块、UI 一致性审查、P0/P1 发现。
- 必要输入：审查模式、diff/提交/文件/模块/页面/接口范围、相关方案或初始化上下文、必要时的原型。
- 必须产出：`reports/reviews/<评审名>/review.md`，按 P0/P1/P2/P3 排序的 findings、残余风险和待用户选择项。
- 交接出口：审查结束后停止；用户明确选择发现项和后续 skill 后，才进入 `model-implement-fix`、`model-implement-executor` 或 `model-implement`。

## 工作区

统一使用 `.codex/model-implement/` 作为共享工作区：

- `reports/init-airead/shared-context.md`、`reports/init-airead/business-flows.md`、`reports/init-airead/db-assessment.md`、`reports/init-airead/input-materials.md`：用于理解项目、业务、数据库约束和输入材料归类。
- `reports/init-read/功能模块清单.md`、`reports/init-read/待人工确认.md`：仅在需要确认页面归属、材料来源、人工待确认项或用户侧表述时读取。
- `reports/modules/<模块名>/module-readiness.md`、`module-relations.md`、`frontend-plan.md`、`backend-plan.md`：用于确认实现是否符合已确认方案。
- `reports/issues/<问题名>/issue.md` 与 `fix-result.md`：在审查已有修复或回归时作为参考。
- `reports/reviews/<评审名>/review.md`：本 skill 输出的代码审查报告。
- `prototypes/<模块名>/`：仅在 UI 还原、交互一致性或用户明确要求审查原型一致性时读取。
- `memory/review.jsonl`：代码审查阶段的观察、经验和规则候选。
- `memory/review-rules.md`：代码审查阶段沉淀出的私有稳定规则。
- `memory/shared-memory.md` 与 `memory/shared-rules.md`：跨 skill 共享记忆与共享规则。

## 审查模式

根据用户输入选择一种模式：

- `diff review`：优先模式，审查本次改动、指定 diff 或变更文件。
- `module review`：没有明确 diff 时，审查指定模块、页面、接口或功能范围。
- `release review`：上线前集中检查风险、回归影响和测试缺口。

## 工作流程

1. 若存在，先读取 `memory/review-rules.md`、`memory/shared-rules.md` 和 `memory/shared-memory.md`。
2. 确认审查模式和范围；如果范围过大或不明确，先收敛范围，不做泛化评审。
3. 使用 `scripts/review_doc_bootstrap.py` 为本次评审创建或刷新 `reports/reviews/<评审名>/review.md`。
4. 读取相关代码、diff、方案文档、初始化上下文和必要的问题修复文档。
5. 根据审查类型决定是否参考原型：默认不看原型；只有 UI 还原、交互一致性、页面视觉偏差审查，或用户明确要求时才读取原型。
6. 按 `references/review-checklist.md` 检查业务逻辑、权限/数据范围、接口契约、状态流转、事务与幂等、回归影响、异常处理、性能、测试缺口和必要的 UI 一致性。
7. 按 `references/review-severity.md` 给每条发现标注 `P0`、`P1`、`P2`、`P3`。
8. 在 `review.md` 中优先输出发现列表，按严重级别排序；没有明确发现时，也要写明未发现明确问题和残余风险。
9. 每条发现都可以给出建议后续处理 skill，但只能推荐，不能自动执行。
10. 最后输出“待用户选择”区，列出可处理的发现项，让用户决定后续执行哪几条。
11. 只有用户明确选择某些发现项并允许进入对应 skill 后，才可以继续使用 `model-implement-init`、`model-implement`、`model-implement-executor` 或 `model-implement-fix`。
12. 将有价值的审查观察或规则候选写入 `memory/review.jsonl`，把稳定规则提升到 `memory/review-rules.md`；共享规则合成默认仍由 `model-implement-init` 负责。

## 🔴 CHECKPOINT · 审查门禁

开始审查前必须先收敛范围和模式。遇到以下情况要停止并让用户补充或选择：

- 没有 diff、模块、页面、接口、提交范围或上线范围。
- 用户要求“顺手修复”，但尚未选择具体发现项和后续 skill。
- UI 一致性审查缺少原型、方案或目标页面路径。
- 方案、初始化上下文或问题修复文档之间互相冲突，且无法判断优先级。
- 审查会读取外部路径、敏感日志或生产数据，但用户未说明边界。

## 失败分支与兜底

| 触发条件 | 一线处理 | 仍失败兜底 |
|---|---|---|
| 范围不清 | 让用户在 diff、module、release 三种模式中收敛 | 只输出需要补充的范围，不做泛化评审 |
| 没有明确发现 | 写明“未发现明确问题”和已覆盖范围 | 列出未覆盖测试、数据、权限或 UI 风险 |
| 发现属于实施缺口 | 标注为缺口并推荐 `model-implement-executor` | 不把缺口写成 bug |
| UI 审查依据不足 | 读取方案、原型和当前实现的可用部分 | 将视觉结论标为待确认 |
| 用户要求自动修复 | 先列 findings 和推荐 skill | 等用户选择发现项后再进入后续流程 |

## 后续 skill 推荐规则

审查报告可以推荐分流，但不能默认执行：

- 初始化上下文缺失、SQL 评估不足、业务流程不清：建议 `model-implement-init`。
- 页面方案缺失、方案不细、方案与原型或业务冲突：建议 `model-implement`。
- 已确认方案还没实现，或属于新功能实施缺口：建议 `model-implement-executor`。
- 已有实现存在 bug、回归、接口偏差、权限/状态/事务问题：建议 `model-implement-fix`。
- 需要人工确认的业务问题：保留在 `review.md`，等待用户补充或确认。

强制边界：

- 不自动调用其他 skill。
- 不默认修改代码。
- 不默认修复审查发现。
- 必须先列出所有发现，再等待用户选择要处理的条目。
- 用户明确说“修复第 1、3 条”或“交给 fix 处理 P1 问题”后，才允许进入对应 skill。

## 输出约束

- findings 是主体，必须优先于总结。
- 发现项必须包含严重级别、标题、位置、问题说明、影响、建议处理、推荐 skill、是否需要用户确认。
- 不要把个人偏好的代码风格当成主要审查结论。
- 不要把“功能未实现”直接当成 bug，应标注为实施缺口并建议合适 skill。
- 如果没有发现明确问题，明确写“未发现明确问题”，并列出残余风险或未覆盖范围。

## 反模式黑名单

- 不要把代码风格偏好当成主要审查发现。
- 不要在 findings 之前先写长篇总结。
- 不要自动调用修复、实施或规划 skill。
- 不要把功能未实现直接定性为 bug。
- 不要在范围不清时做全库泛化评审。

## 记忆规则

参见 `references/memory-cycle.md`。简要规则如下：

- 审查阶段的观察、经验和规则候选写入 `memory/review.jsonl`。
- 只有重复出现、用户确认或经验证稳定的审查规则，才提升到 `memory/review-rules.md`。
- 读取共享规则用于对齐，但不要在本 skill 中重写其他 skill 的私有规则。
- 只有会反向影响初始化、规划、实施或修复的稳定审查规则，才标记 `shared_candidate=true`，并且要谨慎使用。
- 共享规则合成默认仍交给 `model-implement-init`，除非用户明确要求当前就刷新共享记忆。

## 参考资料

- 需要详细审查流程时，读取 `references/workflow.md`。
- 执行审查前，读取 `references/review-checklist.md`。
- 给发现定级时，读取 `references/review-severity.md`。
- 需要确认报告结构时，读取 `references/review-report-contract.md`。
- 需要设置或解释文档状态时，读取 `references/status-contract.md`。
- 进行规则提升或共享记忆对齐前，读取 `references/memory-cycle.md`。


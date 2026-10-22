---
name: model-implement-executor
description: "基于 model-implement-init 初始化文档、model-implement 已确认页面方案和模块关联文档，实施前后端代码修改。只在用户明确决定开始编码后使用；实施前必须读取 library/定义规则.md 及命中资料，遵守当前框架、同类页面和原型校准结果。触发词：开始实现、按方案编码、执行开发、实现页面、落代码、model-implement-executor。不要跳过 confirmed 方案或知识库门禁。"
---

# Model Implement Executor

## 概述

这个 skill 用于在用户明确同意开始实施后，依据 `model-implement` 产出的已确认方案真正修改代码。它属于流程中的执行阶段，应建立在 `model-implement-init` 的初始化上下文和 `model-implement` 的页面方案之上，并尽量避免重复做原型和 SQL 分析。

## 触发与交付速查

- 触发词：开始实现、按方案编码、执行开发、落代码、实现页面、对接接口、`model-implement-executor`。
- 必要输入：目标模块/页面、已允许继续的 `module-readiness.md`、`module-relations.md`、页面 `frontend-plan.md`/`backend-plan.md`、知识库命中资料、对应原型或同类页面。
- 必须产出：完成的最小代码改动、执行过的验证命令或未验证原因、实施观察记忆候选。
- 交接出口：实现后停止并报告验证结果；若发现 bug 或回归，交给 `model-implement-fix` 前等待用户确认。

## 输入

在实施前必须读取以下文档：

- `.codex/model-implement/reports/init-airead/shared-context.md`
- `.codex/model-implement/reports/init-airead/business-flows.md`
- `.codex/model-implement/reports/init-airead/db-assessment.md`
- `.codex/model-implement/reports/init-airead/input-materials.md`
- `.codex/model-implement/reports/modules/<模块名>/module-readiness.md`
- `.codex/model-implement/reports/modules/<模块名>/module-relations.md`
- `.codex/model-implement/reports/modules/<模块名>/<界面名>/frontend-plan.md`
- `.codex/model-implement/reports/modules/<模块名>/<界面名>/backend-plan.md`
- `.codex/model-implement/prototypes/<模块名>/` 下与目标页面对应的原型图或补充原型材料
- `.codex/model-implement/library/定义规则.md`
- `.codex/model-implement/library/` 下由 `定义规则.md` 命中的具体规则、组件、样式、SQL 或特殊资料路径
- `.codex/model-implement/memory/shared-rules.md`
- `.codex/model-implement/memory/executor-rules.md`

只有在需要理解用户侧表述或人工审查背景时，才读取 `reports/init-read/` 下的中文文档。实施约束以 `reports/init-airead/` 和页面方案报告为主，但 `reports/init-read/待人工确认.md`、`reports/init-read/功能模块清单.md` 仍可作为人工审查和页面归属提示输入。旧路径 `reports/shared-context.md`、`reports/business-flows.md`、`reports/db-assessment.md`、`reports/review-needed.zh.md` 仅作为兼容回退。原型图不替代方案文档；当页面视觉、布局、间距、层级、颜色、控件组合等细节未完全写清时，应优先沿用当前框架、设计系统、组件库和同类页面样式，并用原型校准布局结构、组件组合、相对位置和明确差异。

知识库是实施前强制门禁，不是可选参考。若 `.codex/model-implement/library/定义规则.md` 存在，必须先读取它，再按命中项读取具体资料并严格遵守。若 `library/` 存在但 `定义规则.md` 缺失、命中规则无法读取、规则与用户指令/项目约定冲突且无法判断优先级，应停止并暴露问题，不能直接修改代码。若 `library/` 完全不存在，也必须在回复和执行记录中说明“未发现知识库”，并等待用户确认是否允许在无知识库约束下继续。

## 执行流程

1. 确认目标模块的 `module-readiness.md` 已存在，并且状态为 `ready`、`done`，或已被用户明确批准继续。
2. 确认目标页面方案和 `module-relations.md` 已存在，并且状态为 `confirmed`、`implementing`，或已被用户明确批准继续。
3. 在编辑任何代码前执行知识库门禁：读取 `library/定义规则.md`，判断当前实施命中的强制规则和用到时查询路径，读取所有命中的具体资料，并记录本次实际参考路径。
4. 如果目标模块准备度仍是 `draft` 或 `blocked`，应停止并暴露初始化阶段未解决的问题，不要猜测实现。
5. 如果目标页面方案或模块关联文档仍是 `draft` 或 `blocked`，应停止并暴露未决问题，不要猜测实现。
6. 编辑代码前，除了读取相关真实代码路径，也要定位目标页面对应的原型图，并查看同类页面、组件实现和样式文件，确认当前框架的默认视觉语言。
7. 先遵循确认后的页面方案、模块关联文档、知识库规则和命中资料实施；当文档未明确写死样式、间距、颜色、尺寸、视觉主次、留白、对齐方式或控件组合时，应优先沿用当前框架/同类页面样式，并用原型校准布局结构、组件组合、相对位置和明确差异，而不是自由发挥。
8. 如果原型样式与当前框架明显冲突，且方案未明确要求引入新视觉，应停下来暴露冲突点或按方案中的待确认项处理，不要默认照搬原型，也不要私自补一套新样式。
9. 按确认后的页面方案、模块关联文档、知识库规则、当前框架约定和原型校准结果实施前后端代码。
10. 如果方案文档与原型图存在明显冲突，或方案样式依据与当前框架存在明显冲突，优先停下来暴露冲突点；除非用户明确指定以哪一方为准，否则不要自行选边。
11. 只有在用户希望报告同步维护时，才更新相关页面方案或模块关系文档，而且只写入对后续运行有价值的稳定事实。
12. 运行必要的检查或测试。
13. 将实施阶段发现的经验、框架约束或用户确认偏好写入 `.codex/model-implement/memory/executor.jsonl`。
14. 只有稳定、重复出现或用户明确确认的实施经验，才提升到 `.codex/model-implement/memory/executor-rules.md`。
15. 只有当某条实施经验也会反向约束初始化或页面规划时，才标记 `shared_candidate=true`，并且要谨慎使用，因为它可以绕过普通私有规则提升阈值。
16. 共享规则合成默认仍由 `model-implement-init` 负责，除非用户明确要求立即刷新共享记忆。

## 🔴 CHECKPOINT · 实施门禁

编辑任何代码前，必须完成以下确认；任一项不满足就停止并暴露原因：

- 目标模块 `module-readiness.md` 已存在，且状态允许继续。
- `module-relations.md`、目标页面 `frontend-plan.md`、`backend-plan.md` 已存在，且状态允许继续。
- `library/定义规则.md` 已读取；若 `library/` 存在但入口缺失、命中资料缺失或规则冲突，必须等待用户确认。
- 已定位目标页面对应原型、同类页面、组件实现和样式依据。
- 当前工作树没有会被本次实施覆盖的用户未确认改动。

## 失败分支与兜底

| 触发条件 | 一线处理 | 仍失败兜底 |
|---|---|---|
| 准备度或页面方案为 `draft`/`blocked` | 读取文档中的未决项并汇总影响 | 停止实施，要求用户确认或回到规划阶段 |
| 知识库入口或命中资料缺失 | 列出缺失路径、命中规则和风险 | 不改代码，等待补齐或明确豁免 |
| 方案与原型或当前框架冲突 | 对照方案、原型、同类页面列出冲突点 | 不自行选边，等待用户指定优先级 |
| 代码定位不明确 | 先用路由、菜单、接口、组件名收敛范围 | 范围仍不清时停止，避免全库试改 |
| 测试命令不可用 | 运行可用的静态检查或最小验证，并记录缺口 | 在结果中标注未验证范围和残余风险 |

## 边界

- 不要在初始化文档或页面方案仍不成熟时跳过前置条件直接实施。
- 不要绕过知识库门禁直接实施；必须先读 `library/定义规则.md`，读取命中的具体资料，并严格遵守。
- 如果知识库入口缺失、命中资料缺失、规则冲突或优先级不清，不能直接改代码，必须先暴露并等待用户确认。
- 除非初始化文档或页面方案已明显过期，否则不要重新全量解析原型图或 `.codex/model-implement/.sql/`；但当前目标页面对应的原型图仍应作为布局结构、组件组合和明确差异的校准输入被读取。
- 不要在未经说明的情况下引入超出既有方案范围的大规模架构改动。
- 当前端方案没有明确样式时，不要擅自设计一套新视觉语言；未明确说明时，默认沿用当前框架、设计系统、组件库和同类页面样式，并用原型校准布局结构和明确差异。
- 不要覆盖用户已有改动或不相关工作。
- 不要把密钥、账号、连接串、生产数据或原始隐私数据写入记忆。

## 反模式黑名单

- 不要用原型替代已确认的前后端方案。
- 不要绕过知识库门禁直接改代码。
- 不要把 `draft` 页面当作可以自由实现的需求。
- 不要为了实现单页而改动跨模块基础架构，除非方案和用户都明确要求。
- 不要在未说明验证缺口的情况下宣称实施完成。

## 参考资料

- 需要详细执行检查清单时，读取 `references/execution-workflow.md`。
- 需要确认初始化与模块文档契约时，读取 `references/report-contract.md`。
- 需要设置或解释文档状态时，读取 `references/status-contract.md`。

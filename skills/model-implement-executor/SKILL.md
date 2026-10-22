---
name: model-implement-executor
description: "在用户明确决定开始编码后，基于 model-implement 已确认页面方案和模块关联文档，综合 model-context-rag 定位的项目上下文、初始化报告、原型材料、SQL/数据库审查、knowledge-library 命中资料和真实代码，实施前后端代码修改。触发词：开始实现、按方案编码、执行开发、实现页面、落代码、对接接口、model-implement-executor。不要跳过 confirmed 方案、RAG 原文精读、SQL 对照或知识库门禁；风险较大的非阻塞项优先跳过，完成安全实施后集中列入待人工确认。"
---

# Model Implement Executor

## 概述

这个 skill 用于在用户明确同意开始实施后，依据 `model-implement` 产出的已确认方案真正修改代码。它属于流程中的执行阶段，应建立在 `model-implement-init` 的初始化上下文、`model-implement` 的页面方案、`model-context-rag` 定位的原始报告、原型材料、SQL/数据库审查、知识库规则和真实代码之上。

`model-implement` 的方案是施工图，RAG 是上下文定位器，原型是界面校准源，SQL/数据库审查是数据落点约束，知识库是实现规则门禁，真实代码是最终落地方式。任何一方出现实质冲突时，先判断是否阻塞当前安全闭环；高风险但可跳过的项先不实施，集中列入待人工确认。

## 触发与交付速查

- 触发词：开始实现、按方案编码、执行开发、落代码、实现页面、对接接口、`model-implement-executor`。
- 必要输入：目标模块/页面、已允许继续的 `module-readiness.md`、`module-relations.md`、页面 `frontend-plan.md`/`backend-plan.md`、RAG 状态与命中原文、知识库命中资料、对应原型、SQL/数据库审查依据和同类代码。
- 必须产出：完成的必要代码改动、执行过的验证命令或未验证原因、实施记录、实施观察记忆候选、跳过的高风险待人工确认项。
- 交接出口：实现后停止并报告验证结果；若发现 bug 或回归，交给 `model-implement-fix` 前等待用户确认。

## 输入

在实施前必须读取以下文档：

- `.codex/model-implement/reports/init-read/初始化契约.md`
- `.codex/model-implement/reports/init-read/代码及框架信息.md`
- `.codex/model-implement/reports/init-read/已有功能模块信息.md`
- `.codex/model-implement/reports/init-read/待办清单.md`
- `.codex/model-implement/reports/init-read/业务理解.md`
- `.codex/model-implement/reports/init-read/数据库审查报告.md`
- `.codex/model-implement/reports/init-read/待确认点.md`
- `.codex/model-implement/reports/modules/<模块名>/module-readiness.md`
- `.codex/model-implement/reports/modules/<模块名>/module-relations.md`
- `.codex/model-implement/reports/modules/<模块名>/<界面名>/frontend-plan.md`
- `.codex/model-implement/reports/modules/<模块名>/<界面名>/backend-plan.md`
- `model-context-rag` 的 `rag-status.ps1` 和 `rag-search.ps1` 结果，以及命中结果对应的原始报告章节
- `.codex/model-implement/prototypes/<模块名>/` 下与目标页面对应的原型图或补充原型材料
- `.codex/model-implement/.sql/` 下与目标模块、页面、接口或表相关的 SQL 文件，以及数据库审查报告中对应的字段/索引/缺口说明
- `.codex/model-implement/library/定义规则.md`
- `.codex/model-implement/library/` 下由 `定义规则.md` 命中的具体规则、组件、样式、SQL 或特殊资料路径
- `.codex/model-implement/memory/shared-rules.md`
- `.codex/model-implement/memory/executor-rules.md`

实施约束以新版 `reports/init-read/` 初始化报告和已确认页面方案报告为主；旧路径 `reports/init-airead/shared-context.md`、`business-flows.md`、`db-assessment.md` 仅作为历史辅助输入，不能替代新版主报告。RAG 只负责定位候选上下文，不能替代原文精读。原型图不替代方案文档；当页面视觉、布局、间距、层级、颜色、控件组合等细节未完全写清时，应优先沿用当前框架、设计系统、组件库和同类页面样式，并用原型校准布局结构、组件组合、相对位置和明确差异。

知识库是实施前强制门禁，不是可选参考。若 `.codex/model-implement/library/定义规则.md` 存在，必须先读取它，再按命中项读取具体资料并严格遵守。若 `library/` 存在但 `定义规则.md` 缺失、命中规则无法读取、规则与用户指令/项目约定冲突且无法判断优先级，应停止并暴露问题，不能直接修改代码。若 `library/` 完全不存在，也必须在回复和执行记录中说明“未发现知识库”，并等待用户确认是否允许在无知识库约束下继续。

## 风险处理原则

- 优先完成方案中已经确认、代码影响范围清楚、不会改变公共架构或数据口径的安全闭环。
- 遇到高风险但非当前闭环必需的项，先跳过，不阻塞其他安全实施；在实施记录和最终回复中集中列为“待人工确认”。
- 高风险项包括：新增或变更公共基础组件、重构请求/权限/路由/状态体系、修改跨模块通用 SQL、补充未确认数据库字段、改变既有业务状态口径、批量迁移历史数据、覆盖用户未确认改动。
- 如果高风险项是当前功能闭环的必需前提，不能跳过继续伪实现；应停止对应子任务，写清阻塞原因和待确认点。
- 跳过项不得静默忽略。必须写明影响范围、建议处理方式、严重等级和是否阻塞上线验收。

## 执行流程

1. 确认目标模块的 `module-readiness.md` 已存在，并且状态为 `ready`、`done`，或已被用户明确批准继续。
2. 确认目标页面方案和 `module-relations.md` 已存在，并且状态为 `confirmed`、`implementing`，或已被用户明确批准继续。
3. 按 `model-context-rag/references/integration-contract.md` 调用 RAG：先 `rag-status.ps1 -ModelRoot ".codex/model-implement" -Json`，必要时运行 `rag-index.ps1` 后复查；对模块名、界面名、接口名、表名、字段业务含义、待确认点、数据库缺口、已有同类功能执行 `rag-search.ps1`。
4. 按 RAG 命中的 `source_path`、`heading`、`suggested_read` 打开原始报告精读；`healthy` 正常使用，`warning` 扩大原文读取范围，`blocked` 回退直接读取 `reports/init-read/`、`reports/modules/` 和 `memory/`。不要把 `chunks.jsonl` 当作事实来源。
5. 在编辑任何代码前执行知识库门禁：读取 `library/定义规则.md`，按当前模块、页面类型、组件、权限、接口、SQL、样式、上传、字典、状态流转等关键词查询并读取所有命中的具体资料，记录本次实际参考路径。
6. 如果目标模块准备度仍是 `draft` 或 `blocked`，应停止并暴露初始化阶段未解决的问题，不要猜测实现。
7. 如果目标页面方案或模块关联文档仍是 `draft` 或 `blocked`，应停止并暴露未决问题，不要猜测实现。
8. 编辑代码前，定位目标页面对应原型图、说明文档和同类页面；查看组件实现、样式文件、路由、菜单、权限、请求封装、接口目录和后端分层。
9. 对照 `.codex/model-implement/.sql/`、`数据库审查报告.md`、`backend-plan.md` 和真实后端代码，确认表、字段、索引、Mapper/SQL、Entity、DTO、VO、状态枚举和权限口径；不得静默新增未确认字段或改变状态含义。
10. 先遵循确认后的页面方案、模块关联文档、知识库规则和命中资料实施；当文档未明确写死样式、间距、颜色、尺寸、视觉主次、留白、对齐方式或控件组合时，应优先沿用当前框架/同类页面样式，并用原型校准布局结构、组件组合、相对位置和明确差异，而不是自由发挥。
11. 如果原型样式与当前框架明显冲突，且方案未明确要求引入新视觉，应把冲突记入待人工确认；若不影响当前安全闭环，先沿用当前框架完成可实施部分；若影响核心交互或验收，停止对应子任务。
12. 按确认后的页面方案、模块关联文档、RAG 精读结论、SQL 对照结果、知识库规则、当前框架约定和原型校准结果实施必要的前后端代码。
13. 实施时控制影响范围：完成当前页面/接口闭环所需的前端、后端、SQL、权限、路由、菜单、校验和异常处理，不顺手重构无关模块或公共架构。
14. 如果方案文档与原型图、SQL、知识库或当前框架存在明显冲突，优先判断是否可跳过；可跳过则记录到待人工确认并继续安全部分，不可跳过则停止对应子任务。
15. 只有在用户希望报告同步维护时，才更新相关页面方案或模块关系文档，而且只写入对后续运行有价值的稳定事实。
16. 写入或更新实施记录，建议位置为 `reports/modules/<模块名>/<界面名>/implementation-record.md`。
17. 运行必要的检查或测试。
18. 将实施阶段发现的经验、框架约束或用户确认偏好写入 `.codex/model-implement/memory/executor.jsonl`。
19. 只有稳定、重复出现或用户明确确认的实施经验，才提升到 `.codex/model-implement/memory/executor-rules.md`。
20. 只有当某条实施经验也会反向约束初始化或页面规划时，才标记 `shared_candidate=true`，并且要谨慎使用，因为它可以绕过普通私有规则提升阈值。
21. 共享规则合成默认仍由 `model-implement-init` 负责，除非用户明确要求立即刷新共享记忆。

## 🔴 CHECKPOINT · 实施门禁

编辑任何代码前，必须完成以下确认；任一项不满足就停止并暴露原因：

- 目标模块 `module-readiness.md` 已存在，且状态允许继续。
- `module-relations.md`、目标页面 `frontend-plan.md`、`backend-plan.md` 已存在，且状态允许继续。
- 已调用 RAG 状态检查；若 RAG 可用，已检索并精读命中的原始报告；若不可用，已回退直接读取原文。
- `library/定义规则.md` 已读取；若 `library/` 存在但入口缺失、命中资料缺失或规则冲突，必须等待用户确认。
- 已对照 `.sql`、数据库审查报告、后端方案和真实代码确认必要表字段、索引、状态和接口落点。
- 已定位目标页面对应原型、同类页面、组件实现和样式依据。
- 当前工作树没有会被本次实施覆盖的用户未确认改动。

## 失败分支与兜底

| 触发条件 | 一线处理 | 仍失败兜底 |
|---|---|---|
| 准备度或页面方案为 `draft`/`blocked` | 读取文档中的未决项并汇总影响 | 停止实施，要求用户确认或回到规划阶段 |
| RAG 不可用或索引质量不足 | `warning` 时扩大原文读取；`blocked` 时回退直接读取原文 | 仍无法确认关键上下文时停止对应子任务 |
| 知识库入口或命中资料缺失 | 列出缺失路径、命中规则和风险 | 不改代码，等待补齐或明确豁免 |
| SQL/字段/状态口径缺失 | 对照数据库审查报告、后端方案、`.sql` 和真实代码列出缺口 | 非阻塞项跳过并列入待人工确认；阻塞核心闭环时停止 |
| 方案与原型或当前框架冲突 | 对照方案、原型、同类页面列出冲突点 | 不自行选边，等待用户指定优先级 |
| 高风险公共改动 | 判断是否是当前闭环必需；非必需则跳过 | 集中列入待人工确认并说明影响 |
| 代码定位不明确 | 先用路由、菜单、接口、组件名收敛范围 | 范围仍不清时停止，避免全库试改 |
| 测试命令不可用 | 运行可用的静态检查或最小验证，并记录缺口 | 在结果中标注未验证范围和残余风险 |

## 边界

- 不要在初始化文档或页面方案仍不成熟时跳过前置条件直接实施。
- 不要绕过知识库门禁直接实施；必须先读 `library/定义规则.md`，读取命中的具体资料，并严格遵守。
- 如果知识库入口缺失、命中资料缺失、规则冲突或优先级不清，不能直接改代码，必须先暴露并等待用户确认。
- 除非初始化文档或页面方案已明显过期，否则不要重新全量解析原型图或 `.codex/model-implement/.sql/`；但当前目标页面对应的原型图仍应作为布局结构、组件组合和明确差异的校准输入被读取。
- 不要绕过 RAG/原文定位流程直接靠记忆落代码；RAG 不可用时也必须明确回退读取了哪些原始报告。
- 不要静默新增、删除或重命名数据库字段；字段/索引/状态口径缺失时按风险策略跳过或停止。
- 不要在未经说明的情况下引入超出既有方案范围的大规模架构改动。
- 当前端方案没有明确样式时，不要擅自设计一套新视觉语言；未明确说明时，默认沿用当前框架、设计系统、组件库和同类页面样式，并用原型校准布局结构和明确差异。
- 不要覆盖用户已有改动或不相关工作。
- 不要把密钥、账号、连接串、生产数据或原始隐私数据写入记忆。

## 反模式黑名单

- 不要用原型替代已确认的前后端方案。
- 不要把 RAG chunk 当作实施事实来源。
- 不要绕过知识库门禁直接改代码。
- 不要跳过 SQL/数据库审查对照直接写 Mapper、Entity 或 DTO。
- 不要把 `draft` 页面当作可以自由实现的需求。
- 不要为了实现单页而改动跨模块基础架构，除非方案和用户都明确要求。
- 不要在未说明验证缺口的情况下宣称实施完成。
- 不要把高风险项悄悄做掉或悄悄忽略；要么跳过并列入待人工确认，要么停止对应子任务。

## 参考资料

- 需要详细执行检查清单时，读取 `references/execution-workflow.md`。
- 需要确认初始化与模块文档契约时，读取 `references/report-contract.md`。
- 需要记录本次执行范围、资料来源、改动文件、验证结果和待人工确认项时，读取 `references/implementation-record-format.md`。
- 需要设置或解释文档状态时，读取 `references/status-contract.md`。

# Runtime Review Workflow

## Goal

`model-implement-review` 用于对目标模块做验收型审查。审查顺序固定为：

1. 前后端接口契约审查。
2. 根据接口和页面交互生成待审查清单。
3. 使用 Playwright 真实页面测试，逐项更新待审查清单。
4. 输出最终审查问题清单。

本 skill 不默认修复问题。

## Required Inputs

- 目标模块名称。
- 审查轮次，默认从第 1 轮开始。
- 测试环境 URL、菜单路径或页面路由。
- 测试账号、角色、组织或数据范围说明；这是可选输入，没有时运行到登录或授权处再提示用户人工授权。
- 是否允许新增、修改、删除或作废测试数据。
- 测试数据前缀，建议使用 `AI_REVIEW_<日期>_<模块>_<随机串>`。
- 前端页面代码、API 调用文件、路由和组件范围。
- 后端 Controller/API、DTO/VO、Service、Mapper/XML、权限和分页实现范围。
- 已确认方案或初始化上下文；如果缺失，仍可审查当前实现，但要在报告中标注依据不足。

## Steps

1. 读取 `memory/review-rules.md`、`memory/shared-rules.md` 和 `memory/shared-memory.md`，复用已有 Playwright 控件操作经验、选择器策略和等待条件。
2. 读取可选配置：`reports/review-config/测试账号与环境.md`、`测试流程与要求.md`、`<目标模块>-测试要求.md`。配置不存在时继续审查。
3. 使用 `scripts/review_doc_bootstrap.py --module <目标模块> --round <轮次>` 创建三份审查文档，并创建缺失的 `reports/review-config/` 配置骨架。
4. 读取目标模块相关初始化报告、模块关系、前端方案、后端方案和当前代码。
5. 按 `interface-contract-checklist.md` 建立接口契约对齐判断：
   - 前端调用了哪些接口。
   - 每个接口的 method、path、参数、分页、排序、枚举、日期和文件字段是什么。
   - 后端实际暴露了哪些接口。
   - 请求 DTO、响应 VO、错误码、权限、数据范围是否能对上。
6. 把接口契约结论写入 `接口契约对齐判断.md`。此阶段只做静态判断，不运行页面。
7. 从接口动作和页面交互生成 `运行时待审查清单.md`：
   - 接口动作：查询、新增、详情、编辑、删除、提交、审核、上传、导出等。
   - 页面交互：按钮、表单、筛选、表格、弹窗、抽屉、Tab、树、日期控件、下拉、分页、排序、详情跳转等。
   - 每项必须写明验收标准、验收方式和复测策略，达到验收标准才算通过。
8. 执行运行时门禁：
   - 确认环境不是生产。
   - 确认数据前缀和清理策略。
   - 确认不可逆或高风险动作不会自动执行。
   - 账号、登录或授权信息缺失时不提前阻塞；打开页面后遇到登录、验证码、二次认证或权限阻塞，再提示用户在浏览器完成授权。
9. 使用 Playwright 打开页面，注册 console 和 network 监听，按 `运行时待审查清单.md` 逐项测试；操作控件前优先参考 review memory 中的稳定操作套路。
10. 每完成一项，立即更新 `运行时待审查清单.md`：
   - `已测通过`
   - `已测有报错`
   - `阻塞未测`
   - `不适用`
11. 对已通过项按复测策略处理：核心链路和受当前变更影响的项完整测试或微测试；低风险且已有通过证据的项可以本轮跳过，但要记录原因。
12. 具体问题只写入 `审查问题清单.md`。待审查清单只填写问题编号。
13. CRUD 业务按顺序测试：
   - 新增测试数据。
   - 查询列表或详情确认新增成功。
   - 修改测试数据。
   - 再查确认修改成功。
   - 删除、作废或撤销。
   - 再查确认删除、作废或撤销结果。
14. 对不可逆删除、审批、库存、账务、外部通知等动作，不自动执行；记录为阻塞或人工确认项。
15. 用户在审查过程中补充测试账号、授权方式、环境、测试流程或模块要求时，把可复用信息写入 `reports/review-config/`；不要默认保存真实密码、token、生产连接串或敏感业务数据。
16. 按 `review-severity.md` 给具体问题定级。
17. 在 `审查问题清单.md` 输出发现列表、回归风险、测试缺口、未覆盖范围和待用户选择项。
18. 记录可复用审查经验到 `memory/review.jsonl`。Playwright 控件探索经验包括失败尝试、成功步骤、选择器策略、等待条件和适用范围；重复出现或用户确认后再提升到 `memory/review-rules.md`。

## Source Priority

1. 用户最新明确指令。
2. 可选审查配置：`reports/review-config/` 下的账号环境、通用流程和模块要求。
3. 当前审查目标、环境和数据操作边界。
4. 当前前端 API 调用、页面代码和后端接口实现。
5. 已确认方案文档：`frontend-plan.md`、`backend-plan.md`、`module-relations.md`。
6. 初始化上下文：`初始化契约.md`、`代码及框架信息.md`、`已有功能模块信息.md`、`待办清单.md`、`业务理解.md`、`数据库审查报告.md`、`待确认点.md`。
7. 旧的 `shared-context.md`、`business-flows.md`、`db-assessment.md` 仅作为历史辅助输入。
8. Playwright 运行证据：console、network、页面表现、截图或录制。
9. `shared-rules.md` 与 `review-rules.md`。

## Stop Or Downgrade Conditions

- 目标模块、轮次、入口或环境不明确。
- 环境疑似生产，或无法确认数据操作安全。
- 页面无法打开，且没有可替代路由或菜单入口。
- 关键接口缺失导致无法生成可执行的测试清单。
- 需要验证码、短信、硬件、电话控件或第三方人工操作，且用户无法完成授权或外部操作。
- 用户要求审查同时修复。

遇到这些情况时，继续完成能做的静态接口审查和清单生成，把运行时项标记为 `阻塞未测`。

## Optional Review Config

`reports/review-config/` is optional. Use it when present and create skeleton files when missing:

- `测试账号与环境.md`
- `测试流程与要求.md`
- `<目标模块>-测试要求.md`

If the files are missing, do not block the review. Continue until login, authorization, captcha, menu permission, or session expiration requires user action, then pause and ask the user to complete authorization in the browser.

When the user provides reusable test accounts, role notes, environment notes, data prefixes, process rules, or module requirements during the review, update the matching config file. Do not store real passwords, tokens, production connection strings, or sensitive business data unless the user explicitly asks for local storage and accepts the risk.

## Completion Standard

完成一次审查至少应具备：

- `接口契约对齐判断.md` 写明前后端接口是否对齐。
- `运行时待审查清单.md` 覆盖目标模块可见且启用的交互项，并记录每项状态。
- `审查问题清单.md` 写明发现、证据摘要、风险、测试缺口、未覆盖范围和待用户选择项。

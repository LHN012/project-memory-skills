# Issue Report Contract

`model-implement-fix` 需要把问题修复过程沉淀成两份中文文档：

- `reports/issues/<issue-name>/issue.md`
- `reports/issues/<issue-name>/fix-result.md`

## issue.md

`issue.md` 是问题分析主文档，建议至少包含以下章节：

- `状态`
- `问题概述`
- `问题分类`
- `知识库参考与规则遵守`
- `是否需要参考原型`
- `输入与依据`
- `复现信息`
- `期望行为`
- `实际行为`
- `影响范围`
- `根因分析`
- `修复方案`
- `待确认项`

要求：

- `问题分类` 要引用 `issue-classification-checklist.md` 的分类结果。
- `知识库参考与规则遵守` 必须列出是否读取 `library/定义规则.md`、实际命中的知识库路径、必须遵守的规则、是否存在冲突和处理结论。
- `是否需要参考原型` 必须写清 `是` / `否` / `待判断` 以及理由。
- `期望行为` 要写明依据来源，不要只写主观判断。
- `影响范围` 至少覆盖页面、接口、上下游模块、权限或数据链路中的相关项。

## fix-result.md

`fix-result.md` 是实际修复结果文档，建议至少包含以下章节：

- `状态`
- `修复摘要`
- `知识库参考与规则遵守`
- `实际改动`
- `修改文件`
- `验证结果`
- `修复验证清单`
- `剩余风险`
- `后续建议`

要求：

- `验证结果` 应说明执行过哪些检查、测试或手工验证。
- `知识库参考与规则遵守` 应说明本次修复是否严格遵守命中的知识库规则；如未发现知识库或存在冲突，应写清用户确认或阻塞原因。
- `修复验证清单` 应按 `fix-validation-checklist.md` 逐项记录 `适用/不适用/待补充/失败`。
- `剩余风险` 只写仍然真实存在的问题，不要写成空洞提醒。

## 状态建议

问题修复文档状态以 `references/status-contract.md` 为准。`issue.md` 可使用 `draft`、`blocked`、`reproducing`、`diagnosed`、`fixing`、`fixed`；`fix-result.md` 可使用 `draft`、`blocked`、`fixing`、`fixed`。

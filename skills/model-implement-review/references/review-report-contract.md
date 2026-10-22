# Review Report Contract

`model-implement-review` outputs three Chinese documents for each review round:

- `reports/reviews/<目标模块>-第<轮次>轮/接口契约对齐判断.md`
- `reports/reviews/<目标模块>-第<轮次>轮/运行时待审查清单.md`
- `reports/reviews/<目标模块>-第<轮次>轮/审查问题清单.md`

The folder name is the review name. Prefer `<目标模块>-第<轮次>轮`.

## 接口契约对齐判断.md

This is the static frontend/backend contract judgment.

Required sections:

- `状态`
- `审查范围`
- `输入依据`
- `前端接口清单`
- `后端接口清单`
- `接口契约对齐表`
- `分页、排序、筛选对齐`
- `枚举、字典、日期格式对齐`
- `权限与数据范围对齐`
- `错误码、空态、异常态对齐`
- `阻塞项`
- `进入 Playwright 测试的影响`

The contract table should include:

- frontend caller,
- frontend method/path,
- frontend params,
- expected response,
- backend endpoint,
- backend request object,
- backend response object,
- alignment label,
- impact.

Use labels from `interface-contract-checklist.md`. Do not use those labels as lifecycle statuses.

## 运行时待审查清单.md

This is the testing progress checklist. It must not contain detailed issue descriptions.

Required sections:

- `状态`
- `审查范围`
- `测试环境与数据策略`
- `清单字段说明`
- `待审查清单`
- `阻塞未测项`
- `未覆盖范围`
- `清单更新记录`

Checklist columns:

```text
编号 / 页面 / 交互项 / 关联接口 / 验收标准 / 验收方式 / 测试状态 / 是否报错 / 是否阻塞 / 问题编号 / 复测策略
```

Allowed status values:

- `未测`
- `已测通过`
- `已测有报错`
- `阻塞未测`
- `不适用`

Allowed validation method values:

- `完整测试`
- `微测试`
- `静态确认`
- `人工确认`

Allowed retest strategy values:

- `完整测试`
- `微测试`
- `本轮跳过`
- `阻塞未测`
- `人工确认`

`已测通过` means the acceptance criteria were met. It must not mean only that no error appeared after clicking.

## 审查问题清单.md

This is the final issue list and review conclusion.

Required sections:

- `状态`
- `审查名称`
- `目标模块与轮次`
- `审查范围`
- `输入依据`
- `接口契约结论`
- `Playwright 测试摘要`
- `发现列表`
- `回归风险`
- `测试缺口`
- `未覆盖范围`
- `待确认项`
- `待用户选择`

Each finding should use this shape:

```text
### P1-001 标题

- 页面/交互项：页面或组件
- 关联接口：method path，或写“不涉及”
- 位置：代码路径、接口、页面路径或菜单
- 问题：具体错误或风险
- 证据摘要：console/network/页面表现/接口契约差异
- 影响：业务、数据、权限、回归或测试风险
- 建议：建议如何处理
- 推荐 skill：model-implement-fix / model-implement-executor / model-implement
- 是否需要用户确认：是/否
- 默认动作：仅记录，不自动修复
```

## No Finding Case

If no concrete issue is found, `审查问题清单.md` must still include:

- `未发现明确问题`
- 已完成的接口契约覆盖范围
- 已完成的 Playwright 测试范围
- 未覆盖范围
- 残余风险
- 已执行或未执行的验证

## User Selection

The final `待用户选择` section must list actionable items:

```text
- [ ] P1-001：标题，建议交给 model-implement-fix
- [ ] P2-002：标题，建议交给 model-implement
```

Do not execute downstream skills until the user explicitly selects findings.

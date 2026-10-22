# Interface Contract Alignment Checklist

## Purpose

Use this checklist before any Playwright page testing. The goal is to determine whether frontend calls and backend APIs can actually align.

Write the result to:

`reports/reviews/<目标模块>-第<轮次>轮/接口契约对齐判断.md`

## Frontend Inventory

Inspect the target module frontend code and list:

- API files and exported methods.
- Hardcoded request paths in page components.
- HTTP method for each request.
- Query params, path params, request body fields, file fields.
- Pagination params and expected response shape.
- Sort, filter, date, enum, and dictionary fields.
- Expected success, empty, error, and permission-denied handling.
- Components that trigger each request.

## Backend Inventory

Inspect the target module backend code and list:

- Controller/API paths and HTTP methods.
- Request DTO, command, query object, path variables, multipart fields.
- Response VO, page object, list object, error code, message format.
- Permission annotations or manual permission checks.
- Data-scope filters such as user, org, tenant, supplier, department, budget unit.
- Service method behavior and required business state.
- Mapper/XML SQL params and result mappings.

## Alignment Checks

For each frontend call, check:

- Does a backend endpoint exist with the same path and method?
- Do request field names match?
- Are required fields supplied?
- Are optional fields omitted correctly when empty?
- Are date and datetime formats aligned?
- Are enum values and dictionary values aligned?
- Is pagination structure aligned?
- Is sorting or filter behavior supported by backend?
- Does the response shape match frontend usage?
- Do list, detail, save, update, delete, upload, export, and audit actions return what frontend expects?
- Are error, empty, and no-permission states handled?
- Are permissions and data-scope assumptions aligned?
- Does backend support true pagination when frontend has a pagination component?

## Risk Labels

Use these labels in `接口契约对齐判断.md`:

- `aligned`: frontend and backend appear aligned.
- `mismatch`: concrete mismatch found.
- `missing-backend`: frontend calls an endpoint that is not implemented.
- `missing-frontend`: backend exposes an action that the target page does not use.
- `unclear`: code or document evidence is insufficient.
- `blocked`: contract cannot be judged because required code, config, or route is missing.

These are classification labels, not lifecycle statuses.

## Output Shape

Include these sections:

- `状态`
- `审查范围`
- `前端接口清单`
- `后端接口清单`
- `接口契约对齐表`
- `分页、排序、筛选对齐`
- `枚举、字典、日期格式对齐`
- `权限与数据范围对齐`
- `错误码、空态、异常态对齐`
- `阻塞项`
- `进入 Playwright 测试的影响`

Concrete issues should later be copied or referenced in `审查问题清单.md` as findings. Keep this document focused on interface alignment.

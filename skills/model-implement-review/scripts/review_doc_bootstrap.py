#!/usr/bin/env python3
"""Create review docs for model-implement-review runtime checks."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ACCOUNT_CONFIG_TEMPLATE = """# 测试账号与环境

## 说明

- 本文件是可选审查配置；不存在时不阻塞审查。
- 建议只记录测试环境、账号角色、组织/数据范围、授权方式和禁止操作。
- 不建议保存真实密码、token、生产连接串或敏感业务数据；如确需保存，应明确标注本地存储风险。

## 环境

- 测试环境 URL：待补充。
- 后端接口地址：待补充。
- 是否允许写入测试数据：待补充。
- 禁止操作：待补充。

## 账号与角色

| 角色 | 用户名/账号标识 | 密码保存方式 | 组织/数据范围 | 用途 | 备注 |
|---|---|---|---|---|---|
| 待补充 | 待补充 | 不在本文保存真实密码 | 待补充 | 待补充 | 待补充 |

## 授权方式

- 登录方式：待补充。
- 遇到验证码/短信/SSO/二次认证：由用户在浏览器中人工完成授权后继续。
"""


FLOW_CONFIG_TEMPLATE = """# 测试流程与要求

## 说明

- 本文件是可选审查配置；不存在时不阻塞审查。
- 用户在审查过程中补充的通用测试流程、数据策略和安全边界，可沉淀到这里。

## 通用流程

- CRUD 默认顺序：增 -> 查 -> 改 -> 再查 -> 删/作废 -> 再查。
- 测试数据前缀：`AI_REVIEW_<日期>_<模块名>_<随机串>`。
- 每测完一项，同步更新 `运行时待审查清单.md`。
- 每个清单项必须有验收标准，达到标准才算通过。
- 已通过项可按复测策略微测试或本轮跳过；核心链路和本轮受影响项必须完整测试或微测试。
- 具体问题只写入 `审查问题清单.md`。

## 数据安全边界

- 生产环境：禁止写入测试数据。
- 不可逆删除、审批、库存、账务、外部通知：默认不自动执行，需人工确认。
- 删除不安全时，优先验证作废、停用或软删除。
"""


MODULE_CONFIG_TEMPLATE = """# {module_name}-测试要求

## 说明

- 本文件是可选模块审查配置；不存在时不阻塞审查。
- 用户在审查过程中补充的模块特殊账号、数据、流程或禁测动作，可沉淀到这里。

## 模块范围

- 目标模块：{module_name}
- 常用入口：待补充。

## 测试数据要求

- 测试数据前缀：`AI_REVIEW_{module_slug}_`
- 必填字段默认值：待补充。
- 特殊状态数据：待补充。

## 特殊流程与禁测动作

- 特殊流程：待补充。
- 禁止自动执行动作：待补充。
- 需要人工确认动作：待补充。
"""


REVIEW_RULES_TEMPLATE = """# Review Rules

本文件记录 model-implement-review 的稳定审查规则和 Playwright 控件操作经验。

- 只有重复出现、跨页面稳定或用户确认有效的经验才写入这里。
- 原始观察先追加到 `review.jsonl`。
- 不记录真实密码、token、验证码、生产地址、敏感业务数据或一次性随机 DOM id。
"""


INTERFACE_TEMPLATE = """# 接口契约对齐判断：{review_name}

## 状态

draft

## 审查范围

- 目标模块：{module_name}
- 审查轮次：第 {round_no} 轮
- 页面/接口/功能范围：{scope}
- 测试入口：{entry}

## 输入依据

- 前端代码范围：待补充。
- 后端代码范围：待补充。
- 方案文档：待补充。
- 初始化上下文：待补充。

## 前端接口清单

| 编号 | 调用位置 | 方法 | 路径 | 入参/请求体 | 期望响应 | 触发交互 |
|---|---|---|---|---|---|---|
| F-001 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 |

## 后端接口清单

| 编号 | Controller/API | 方法 | 路径 | 请求对象 | 响应对象 | 权限/数据范围 |
|---|---|---|---|---|---|---|
| B-001 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 |

## 接口契约对齐表

| 前端接口 | 后端接口 | 对齐标签 | 差异摘要 | 对 Playwright 测试影响 |
|---|---|---|---|---|
| 待补充 | 待补充 | aligned/mismatch/missing-backend/missing-frontend/unclear/blocked | 待补充 | 待补充 |

## 分页、排序、筛选对齐

- 待补充分页参数、返回结构、排序字段、筛选条件、空参数处理是否一致。

## 枚举、字典、日期格式对齐

- 待补充枚举值、字典来源、日期/日期时间格式、空值传参是否一致。

## 权限与数据范围对齐

- 待补充按钮权限、接口权限、角色、组织、用户、部门、租户、供应商等数据范围是否一致。

## 错误码、空态、异常态对齐

- 待补充前端是否能处理后端错误码、空列表、无权限、校验失败和服务异常。

## 阻塞项

- 待补充。

## 进入 Playwright 测试的影响

- 待补充哪些接口可以进入实测，哪些项需要阻塞或降级测试。
"""


CHECKLIST_TEMPLATE = """# 运行时待审查清单：{review_name}

## 状态

draft

## 审查范围

- 目标模块：{module_name}
- 审查轮次：第 {round_no} 轮
- 页面/接口/功能范围：{scope}
- 测试入口：{entry}

## 测试环境与数据策略

- 测试环境 URL：待补充。
- 测试账号/角色：待补充。
- 测试组织/数据范围：待补充。
- 测试数据前缀：`AI_REVIEW_{module_slug}_第{round_no}轮_`
- 新增/修改/删除权限边界：待补充。
- 数据清理策略：待补充。
- 不可逆动作处理：待补充。

## 清单字段说明

- 测试状态只允许：`未测` / `已测通过` / `已测有报错` / `阻塞未测` / `不适用`。
- 验收方式只允许：`完整测试` / `微测试` / `静态确认` / `人工确认`。
- 复测策略只允许：`完整测试` / `微测试` / `本轮跳过` / `阻塞未测` / `人工确认`。
- `已测通过` 表示已达到验收标准，不表示“点击后没有报错”。
- 本清单只记录进度、是否报错、是否阻塞和问题编号，不记录具体问题细节。
- 具体问题写入 `审查问题清单.md`。

## 待审查清单

| 编号 | 页面 | 交互项 | 关联接口 | 验收标准 | 验收方式 | 测试状态 | 是否报错 | 是否阻塞 | 问题编号 | 复测策略 |
|---|---|---|---|---|---|---|---|---|---|---|
| R-001 | 待补充 | 待补充 | 待补充 | 待补充达到什么结果才算通过 | 完整测试 | 未测 | 否 | 否 |  | 完整测试 |

## 阻塞未测项

- 待补充。

## 未覆盖范围

- 待补充。

## 清单更新记录

- 待补充每轮 Playwright 操作后的清单更新时间和范围。
"""


REVIEW_TEMPLATE = """# 审查问题清单：{review_name}

## 状态

draft

## 审查名称

{review_name}

## 目标模块与轮次

- 目标模块：{module_name}
- 审查轮次：第 {round_no} 轮

## 审查范围

- 页面/接口/功能范围：{scope}
- 测试入口：{entry}
- 审查模式：{mode}

## 输入依据

- 接口契约对齐判断：`接口契约对齐判断.md`
- 运行时待审查清单：`运行时待审查清单.md`
- 前端代码：待补充。
- 后端代码：待补充。
- 方案与初始化文档：待补充。

## 接口契约结论

- 待补充前后端接口是否整体可对齐、主要阻塞项和对运行时测试的影响。

## Playwright 测试摘要

- 已测试项：待补充。
- 通过项：待补充。
- 有报错项：待补充。
- 阻塞未测项：待补充。
- 捕获证据：console / network / 页面表现，待补充摘要。

## 发现列表

### 暂无发现

- 页面/交互项：待补充。
- 关联接口：待补充。
- 位置：待补充。
- 问题：待补充。
- 证据摘要：待补充。
- 影响：待补充。
- 建议：待补充。
- 推荐 skill：待判断。
- 是否需要用户确认：是。
- 默认动作：仅记录，不自动修复。

## 回归风险

- 待补充。

## 测试缺口

- 待补充。

## 未覆盖范围

- 待补充。

## 待确认项

- 待补充。

## 待用户选择

- [ ] 待补充发现项编号和建议处理 skill。未获得用户明确选择前，不自动执行任何后续 skill。
"""


INVALID_CHARS_RE = re.compile(r'[<>:"/\\\\|?*]+')


def safe_name(value: str) -> str:
    cleaned = INVALID_CHARS_RE.sub("-", value).strip().strip(".")
    return cleaned or "review"


def module_slug(value: str) -> str:
    return re.sub(r"\s+", "-", safe_name(value)).lower()


def write_if_needed(path: Path, content: str, force: bool, created: list[Path]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if force or not path.exists():
        path.write_text(content, encoding="utf-8")
        created.append(path)


def create_review_config(workspace: Path, module_name: str, module_slug_value: str, force: bool, created: list[Path]) -> None:
    config_dir = workspace / "reports" / "review-config"
    write_if_needed(config_dir / "测试账号与环境.md", ACCOUNT_CONFIG_TEMPLATE, force, created)
    write_if_needed(config_dir / "测试流程与要求.md", FLOW_CONFIG_TEMPLATE, force, created)
    write_if_needed(
        config_dir / f"{safe_name(module_name)}-测试要求.md",
        MODULE_CONFIG_TEMPLATE.format(module_name=module_name, module_slug=module_slug_value),
        force,
        created,
    )


def create_review_memory(workspace: Path, created: list[Path]) -> None:
    memory_dir = workspace / "memory"
    write_if_needed(memory_dir / "review.jsonl", "", False, created)
    write_if_needed(memory_dir / "review-rules.md", REVIEW_RULES_TEMPLATE, False, created)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".codex/model-implement", help="Model implement workspace directory.")
    parser.add_argument("--module", required=True, help="Target module name.")
    parser.add_argument("--round", dest="round_no", type=int, default=1, help="Review round number.")
    parser.add_argument("--review", help="Review folder name. Defaults to '<module>-第<round>轮'.")
    parser.add_argument("--mode", default="runtime review", help="Review mode label.")
    parser.add_argument("--scope", default="<审查范围>", help="Related page, API, feature, or runtime scope.")
    parser.add_argument("--entry", default="<测试入口>", help="Target URL, route, or menu path.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated docs.")
    args = parser.parse_args()

    review_name = args.review or f"{args.module}-第{args.round_no}轮"
    workspace = Path(args.workspace)
    review_dir = workspace / "reports" / "reviews" / safe_name(review_name)
    created: list[Path] = []
    module_slug_value = module_slug(args.module)
    common = {
        "review_name": review_name,
        "module_name": args.module,
        "module_slug": module_slug_value,
        "round_no": args.round_no,
        "mode": args.mode,
        "scope": args.scope,
        "entry": args.entry,
    }

    create_review_config(workspace, args.module, module_slug_value, args.force, created)
    create_review_memory(workspace, created)
    write_if_needed(review_dir / "接口契约对齐判断.md", INTERFACE_TEMPLATE.format(**common), args.force, created)
    write_if_needed(review_dir / "运行时待审查清单.md", CHECKLIST_TEMPLATE.format(**common), args.force, created)
    write_if_needed(review_dir / "审查问题清单.md", REVIEW_TEMPLATE.format(**common), args.force, created)

    if created:
        print("Created or updated:")
        for path in created:
            print(path)
    else:
        print("No report files needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

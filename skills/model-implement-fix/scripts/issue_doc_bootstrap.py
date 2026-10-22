#!/usr/bin/env python3
"""Create optional issue analysis and fix-result docs for model-implement-fix."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ISSUE_TEMPLATE = """# 问题记录：{issue_name}

## 状态

draft

## 问题概述

- 待补充问题现象、出现位置、影响对象和紧急程度。

## 问题分类

- 分类结果：待判断
- 分类依据：待结合 `references/issue-classification-checklist.md` 补充。

## 按需资料查询

- 是否查询知识库：待判断；只有涉及权限、数据范围、状态流转、公共组件、SQL 兼容、样式规范或业务规则不清时才需要。
- 知识库入口：`library/定义规则.md`
- 实际命中的知识库路径：待补充；若未查询，写明理由。
- 是否查询 RAG/初始化报告/方案/SQL：待补充。
- 必须遵守的规则：待补充。
- 规则冲突或缺失：待补充；如当前问题需要这些资料且存在冲突或缺失，应保持 `blocked`，不得直接修复相关风险代码。
- 遵守结论：待补充。

## 是否需要参考原型

- 判断结果：待判断
- 判断理由：待补充。
- 原型来源：{prototype_hint}

## 输入与依据

- 模块：{module_name}
- 页面：{screen_name}
- 用户问题描述：待补充。
- 相关方案文档：
  - `reports/modules/{module_name}/module-relations.md`
  - `reports/modules/{module_name}/{screen_name}/frontend-plan.md`
  - `reports/modules/{module_name}/{screen_name}/backend-plan.md`
- 相关原型：{prototype_hint}
- 其他依据：待补充日志、报错、截图、接口文档或代码路径。

## 复现信息

- 环境与角色：待补充。
- 前置数据：待补充。
- 复现步骤：待补充。
- 复现结果：待补充。

## 期望行为

- 待写清期望表现及依据来源。

## 实际行为

- 待写清实际错误表现。

## 影响范围

- 页面影响：待补充。
- 接口/数据影响：待补充。
- 上下游流程影响：待补充。
- 是否属于回归：待补充。

## 根因分析

- 待补充。

## 修复方案

- 待补充拟修改点、范围控制、是否涉及前后端、是否涉及 SQL、是否需要回归验证。

## 可沉淀到 memory 的核心信息

- 根因模式：待补充；没有复用价值可写“无”。
- 项目基础事实：待补充本次修复确认过的请求封装、接口结构、权限、SQL、路由、组件等信息；没有可写“无”。
- 是否需要回填 init-read：待补充。

## 待确认项

- 待补充。
"""


FIX_RESULT_TEMPLATE = """# 修复结果：{issue_name}

## 状态

draft

## 修复摘要

- 待补充本次修复目标与结果。

## 按需资料查询

- 是否查询知识库：待补充。
- 知识库入口：`library/定义规则.md`
- 实际参考路径：待补充；若未查询，写明理由。
- 是否查询 RAG/初始化报告/方案/SQL/原型：待补充。
- 规则遵守情况：待补充。
- 冲突处理：待补充；如无冲突写“无”。

## 实际改动

- 待补充代码改动说明。

## 修改文件

- 待补充。

## 验证结果

- 执行的检查/测试：待补充。
- 手工验证结果：待补充。

## 修复验证清单

- 原问题已消失：待补充。
- 根因路径已覆盖：待补充。
- 相邻流程未被破坏：待补充。
- 权限与数据范围未扩大：待补充或写“不适用”。
- 接口契约未破坏：待补充或写“不适用”。
- 状态流转正确：待补充或写“不适用”。
- 事务与幂等正确：待补充或写“不适用”。
- 原型一致性已恢复：待补充或写“不适用”。
- 性能未明显恶化：待补充或写“不适用”。
- 必要测试或检查已执行：待补充。

## 剩余风险

- 待补充。

## 后续建议

- 待补充。

## memory 与 init-read 沉淀

- 已写入 `memory/fix.jsonl` 的核心信息：待补充；没有复用价值可写“无”。
- 已回填 init-read 的项目基础事实：待补充；没有可写“无”。
"""


INVALID_CHARS_RE = re.compile(r'[<>:"/\\\\|?*]+')


def safe_name(value: str) -> str:
    cleaned = INVALID_CHARS_RE.sub("-", value).strip().strip(".")
    return cleaned or "issue"


def write_if_needed(path: Path, content: str, force: bool, created: list[Path]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if force or not path.exists():
        path.write_text(content, encoding="utf-8")
        created.append(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".codex/model-implement", help="Model implement workspace directory.")
    parser.add_argument("--issue", required=True, help="Issue name for the report folder.")
    parser.add_argument("--module", default="<模块名>", help="Related module name.")
    parser.add_argument("--screen", default="<界面名>", help="Related screen name.")
    parser.add_argument("--prototype-hint", default="待根据问题类型判断是否需要引用对应原型。", help="Prototype hint text.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated docs.")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    issue_dir = workspace / "reports" / "issues" / safe_name(args.issue)
    created: list[Path] = []

    write_if_needed(
        issue_dir / "issue.md",
        ISSUE_TEMPLATE.format(
            issue_name=args.issue,
            module_name=args.module,
            screen_name=args.screen,
            prototype_hint=args.prototype_hint,
        ),
        args.force,
        created,
    )
    write_if_needed(
        issue_dir / "fix-result.md",
        FIX_RESULT_TEMPLATE.format(issue_name=args.issue),
        args.force,
        created,
    )

    if created:
        print("Created or updated:")
        for path in created:
            print(path)
    else:
        print("No report files needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

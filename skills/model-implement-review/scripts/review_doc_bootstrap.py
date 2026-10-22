#!/usr/bin/env python3
"""Create a review report doc for model-implement-review."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REVIEW_TEMPLATE = """# 代码审查报告：{review_name}

## 状态

draft

## 评审模式

{mode}

## 评审范围

- 模块：{module_name}
- 页面/接口/功能：{scope}
- 代码范围：待补充。

## 输入依据

- 用户审查要求：待补充。
- 相关方案文档：待补充。
- 相关初始化上下文：待补充。
- 是否参考原型：默认不参考；仅在 UI/交互一致性审查或用户明确要求时参考。
- 其他输入：待补充 diff、日志、测试结果或问题修复文档。

## 总体结论

- 待补充。

## 发现列表

### 暂无发现

- 位置：待补充。
- 问题：待补充。
- 影响：待补充。
- 建议：待补充。
- 推荐 skill：待判断。
- 是否需要用户确认：是。
- 默认动作：仅记录，不自动修复。

## 回归风险

- 待补充。

## 测试缺口

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


def write_if_needed(path: Path, content: str, force: bool, created: list[Path]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if force or not path.exists():
        path.write_text(content, encoding="utf-8")
        created.append(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".codex/model-implement", help="Model implement workspace directory.")
    parser.add_argument("--review", required=True, help="Review name for the report folder.")
    parser.add_argument("--mode", default="diff review", choices=["diff review", "module review", "release review"])
    parser.add_argument("--module", default="<模块名>", help="Related module name.")
    parser.add_argument("--scope", default="<评审范围>", help="Related page, API, feature, or diff scope.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated docs.")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    review_dir = workspace / "reports" / "reviews" / safe_name(args.review)
    created: list[Path] = []

    write_if_needed(
        review_dir / "review.md",
        REVIEW_TEMPLATE.format(
            review_name=args.review,
            mode=args.mode,
            module_name=args.module,
            scope=args.scope,
        ),
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

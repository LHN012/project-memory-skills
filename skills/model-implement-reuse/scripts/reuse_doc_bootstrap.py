#!/usr/bin/env python3
"""Create reuse asset docs for model-implement-reuse."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


OVERVIEW_TEMPLATE = """# 复用资产概览：{asset_name}

## 状态

draft

## 工作模式

{mode}

## 资产类型

{asset_type}

## 来源

- 来源项目路径：{source_path}
- 来源功能范围：{feature_scope}
- 来源模块/目录：{module_name}
- 是否当前工作区来源：{is_current_project}
- 原型/截图提示：{prototype_hint}

## 本次目标

- 待补充本次为什么要学习、沉淀或抽离这块能力。

## 资产摘要

- 待补充这块资产当前在做什么。

## 建议复用的部分

- 待补充。

## 明显项目耦合的部分

- 待补充。

## 依赖与风险

- 待补充依赖的框架、组件库、接口、权限、状态、样式或数据来源。

## 适用范围

- 当前项目：待补充。
- 其他项目：待补充。

## 初步结论

- 待选择：`建议沉淀，暂不抽离` / `建议沉淀，并可进入抽离准备` / `建议直接抽离` / `暂不建议复用，保留在原模块`

## 待确认项

- 待补充。
"""


CONTRACT_TEMPLATE = """# 复用资产契约：{asset_name}

## 状态

draft

## 基础信息

- 资产名称：{asset_name}
- 资产类型：{asset_type}
- 来源项目路径：{source_path}
- 来源功能范围：{feature_scope}
- 来源模块/目录：{module_name}

## 职责边界

- 负责：待补充。
- 不负责：待补充。

## 输入输出契约

- 输入参数/props/上下文：待补充。
- 输出事件/返回值/副作用：待补充。
- 错误态/空态/加载态：待补充。

## 状态与权限

- 内部状态：待补充。
- 状态流转：待补充。
- 权限/数据范围要求：待补充或写“不适用”。

## 数据与接口依赖

- 表/字段/接口/DTO/缓存依赖：待补充。
- 可替换依赖：待补充。
- 强绑定依赖：待补充。

## 视觉与交互契约

- 组件组成、数量和层级：待补充或写“不适用”。
- 相对位置、颜色、间距、字号、边框：待补充或写“不适用”。
- 原型或截图基准：{prototype_hint}

## 扩展点与限制

- 可扩展点：待补充。
- 禁止破坏的稳定契约：待补充。
- 当前不建议抽象的部分：待补充。

## 适用范围与禁用范围

- 适用范围：待补充。
- 禁用范围：待补充。
"""


ADOPTION_TEMPLATE = """# 复用接入指南：{asset_name}

## 状态

draft

## 当前项目接入方式

- 接入位置：待补充。
- 替换目标：待补充。
- 兼容策略：待补充。

## 指定项目路径学习结论

- 来源项目路径：{source_path}
- 来源功能范围：{feature_scope}
- 对当前项目可借鉴的点：待补充。
- 不建议直接照搬的点：待补充。

## 跨项目参考方式

- 需要替换的依赖：待补充。
- 需要对齐的接口/样式/权限：待补充。
- 推荐保留的扩展点：待补充。

## 抽离或重构步骤建议

1. 待补充。
2. 待补充。
3. 待补充。

## 验证清单

- 公共契约未被破坏：待补充。
- 当前项目调用点已完成替换：待补充或写“不适用”。
- 外部依赖已显式暴露：待补充。
- 权限、状态、事务与异常处理未丢失：待补充或写“不适用”。
- UI 视觉基准已对齐：待补充或写“不适用”。
- 回归范围已确认：待补充。

## 剩余风险与待确认项

- 待补充。
"""


INVALID_CHARS_RE = re.compile(r'[<>:"/\\\\|?*]+')


def safe_name(value: str) -> str:
    cleaned = INVALID_CHARS_RE.sub("-", value).strip().strip(".")
    return cleaned or "reuse-asset"


def resolve_source_path(value: str) -> str:
    return str(Path(value).expanduser().resolve())


def write_if_needed(path: Path, content: str, force: bool, created: list[Path]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if force or not path.exists():
        path.write_text(content, encoding="utf-8")
        created.append(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".codex/model-implement", help="Model implement workspace directory.")
    parser.add_argument("--asset", required=True, help="Reuse asset name for the output folder.")
    parser.add_argument(
        "--mode",
        default="study",
        choices=["study", "extract"],
        help="Reuse work mode. Defaults to study.",
    )
    parser.add_argument(
        "--asset-type",
        default="mixed",
        choices=["component", "feature", "logic", "mixed"],
        help="Reuse asset type.",
    )
    parser.add_argument("--source-path", default=".", help="Source project path or feature path to study.")
    parser.add_argument("--feature-scope", default="<功能范围>", help="Target feature block, page area, or code scope.")
    parser.add_argument("--module", default="<模块名或目录名>", help="Related module or directory name.")
    parser.add_argument(
        "--prototype-hint",
        default="按需补充；只有在 UI 组件或视觉模式分析时才建议引用。",
        help="Prototype or screenshot hint text.",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated docs.")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    asset_dir = workspace / "reuse" / safe_name(args.asset)
    source_path = resolve_source_path(args.source_path)
    created: list[Path] = []
    cwd = str(Path.cwd().resolve())
    is_current_project = "是" if source_path == cwd else "否"

    common_kwargs = {
        "asset_name": args.asset,
        "mode": args.mode,
        "asset_type": args.asset_type,
        "source_path": source_path,
        "feature_scope": args.feature_scope,
        "module_name": args.module,
        "is_current_project": is_current_project,
        "prototype_hint": args.prototype_hint,
    }

    write_if_needed(asset_dir / "overview.md", OVERVIEW_TEMPLATE.format(**common_kwargs), args.force, created)
    write_if_needed(asset_dir / "contract.md", CONTRACT_TEMPLATE.format(**common_kwargs), args.force, created)
    write_if_needed(asset_dir / "adoption-guide.md", ADOPTION_TEMPLATE.format(**common_kwargs), args.force, created)

    if created:
        print("Created or updated:")
        for path in created:
            print(path)
    else:
        print("No reuse report files needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

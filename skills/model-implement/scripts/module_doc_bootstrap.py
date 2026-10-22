#!/usr/bin/env python3
"""Create per-module and per-screen planning docs from prototype images."""

from __future__ import annotations

import argparse
from pathlib import Path


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}


MODULE_RELATIONS_TEMPLATE = """# 模块关联文档：{module_name}

## 状态

draft

## RAG 上下文检索记录

- RAG 状态：待运行 `scripts/rag-status.ps1 -ModelRoot ".codex/model-implement" -Json` 后填写 healthy/warning/blocked/fallback。
- 检索词：待记录围绕模块名、界面名、业务对象、待办类型、数据库缺口、待确认点、已有可复用功能、框架/样式关键词执行的检索词。
- 命中原文：待列出实际打开精读的原始报告路径、标题或小节；禁止把 `reports/context-rag/chunks.jsonl` 当作事实来源。
- 精读结论：待总结从原始报告、模块报告或记忆文件中确认的模块边界、风险和实施依据。
- 未命中或回退：若 RAG warning/blocked 或未命中关键问题，待写明回退读取了哪些原始文档。

## 初始化前置信息

- 初始化契约：`reports/init-read/初始化契约.md`
- 代码及框架信息：`reports/init-read/代码及框架信息.md`
- 已有功能模块信息：`reports/init-read/已有功能模块信息.md`
- 待办清单：`reports/init-read/待办清单.md`
- 业务理解：`reports/init-read/业务理解.md`
- 数据库审查报告：`reports/init-read/数据库审查报告.md`
- 待确认点：`reports/init-read/待确认点.md`
- 模块准备度：`reports/modules/{module_name}/module-readiness.md`

## 知识库参考项

- 知识库入口：`library/定义规则.md`
- 待补充本模块实际命中的规则、组件、样式、特殊资料路径；若知识库不存在或本模块未命中，需明确写明。
- 禁止无目的全量读取 `library/`，禁止默认读取 `library/README.md`。

## 模块范围

- 原型来源：`.codex/model-implement/prototypes/{module_name}/`
- 当前模块下识别到的界面：
{screen_list}

## 原型对照摘要

- 待说明原型中体现的新增页面、已有页面改造、弹窗/抽屉/详情穿透和批量处理需求。
- 待说明原型相比当前系统同类界面新增或调整了哪些业务区域、字段、按钮、状态和交互。
- 待说明哪些部分按原型布局实现，哪些部分沿用当前项目框架、组件库和同类页面样式。
- 若原型视觉或交互与当前系统规范冲突，待列入待确认点，不要自行裁决。

## 模块内流程关联

- 待分析各界面之间的前置、后置、跳转、返回、弹窗、抽屉、列表到详情、详情到编辑等关系。

## 模块内界面穿透关系

- 待分析哪些页面可以穿透到子页面、详情页、编辑页、弹窗页或其他状态页。

## 与其他模块/界面的业务关联

- 待分析该模块与其他模块在流程、业务对象、状态、权限、数据同步上的关联。

## 共享数据、表、字段和接口

- 待结合初始化输出与目标模块原型分析共用表、字段、字典、枚举和接口。

## 状态流转与业务依赖

- 待分析当前模块操作会影响哪些后续页面展示、状态变更或审批/下单/查询流程。

## 业务闭环检查清单

- 状态枚举：待补充模块级状态、状态来源、状态依赖和跨页面状态同步规则。
- 权限/数据范围：待补充角色、组织、用户、单位、供应商、预算主体等数据范围约束。
- 写操作事务与幂等：待补充模块内写操作的事务边界、重复提交风险、去重和回滚策略；纯读模块需明确写“无”。
- 关联模块影响：待补充上游输入模块、下游消费模块、统计/提醒/列表/详情/审批链路影响。
- 接口契约：待补充模块级共用接口、接口输入输出、错误码、空态和枚举口径。
- 验收用例：待补充模块内主流程、异常流程、权限流程、状态流转流程的验收场景。
- 测试数据：待补充最小测试数据集、角色组合、状态组合、空数据和异常数据准备要求。
- 性能索引：待补充高频查询、分页、排序、聚合、跨表关联和潜在索引需求。
- 待确认项：待补充仍影响实施的业务问题、默认兜底方案及是否阻塞。

## 联动风险与同步点

- 待识别如果某个界面未同步实现，会导致哪些流程断裂、数据不一致或交互缺口。

## 待确认点

- 待补充。

## 给后续 executor 的实施提示

- 待补充推荐实施顺序、应优先阅读的页面方案、同类代码位置、接口/SQL 风险点和联调顺序。
- 这里只写后续建议，不表示已经调用或移交 `model-implement-executor`；实施必须由用户另行明确触发。
"""


FRONTEND_TEMPLATE = """# 前端实施方案：{screen_name}

## 状态

draft

## RAG 上下文检索记录

- RAG 状态：待运行 `scripts/rag-status.ps1 -ModelRoot ".codex/model-implement" -Json` 后填写 healthy/warning/blocked/fallback。
- 检索词：待记录围绕模块名、界面名、页面类型、组件类型、已有同类页面、业务动作、权限、接口、样式关键词执行的检索词。
- 命中原文：待列出实际打开精读的原始报告路径、标题或小节；禁止把 `reports/context-rag/chunks.jsonl` 当作事实来源。
- 精读结论：待总结从原始报告、模块报告或记忆文件中确认的页面入口、布局依据、交互规则和复用点。
- 未命中或回退：若 RAG warning/blocked 或未命中关键问题，待写明回退读取了哪些原始文档或代码。

## 原型来源

`{source_path}`

## 初始化前置信息

- 初始化契约：`reports/init-read/初始化契约.md`
- 代码及框架信息：`reports/init-read/代码及框架信息.md`
- 已有功能模块信息：`reports/init-read/已有功能模块信息.md`
- 待办清单：`reports/init-read/待办清单.md`
- 业务理解：`reports/init-read/业务理解.md`
- 数据库审查报告：`reports/init-read/数据库审查报告.md`
- 待确认点：`reports/init-read/待确认点.md`
- 模块准备度：`reports/modules/{module_name}/module-readiness.md`

## 知识库参考项

- 知识库入口：`library/定义规则.md`
- 待补充本界面实际命中的规则、组件、样式、特殊资料路径；若知识库不存在或本界面未命中，需明确写明。
- 如果使用了组件库、权限组件、上传组件、SQL 兼容规则或特殊业务资料，必须列出具体路径和对本界面的影响。

## 原型对照

- 原型区域：待按顶部、筛选区、操作区、列表/表单区、详情区、弹窗/抽屉、底部操作等拆解原型。
- 已有同类界面：待列出当前项目中可对照的界面名、代码位置或模块说明；不要只写路由。
- 照原型实现：待说明哪些布局、字段组合、按钮位置、穿透关系或业务差异必须按原型实现。
- 沿用现有系统：待说明哪些组件、颜色、间距、表格密度、表单样式、弹窗样式和交互反馈应沿用当前项目。
- 冲突与确认：若原型与当前框架或同类页面不一致，待写明冲突、影响和是否阻塞。

## 页面定位与入口

- 待说明该界面是列表页、详情页、编辑页、弹窗页、步骤页、看板页还是其他类型。
- 待说明它在当前模块流程中的入口、出口和业务目的。

## 布局分区与相对位置规划

- 待拆解页面的顶部、左侧、主体、底部、筛选区、表格区、卡片区、操作区、弹窗/抽屉等区域。
- 待说明各区域的上下左右关系、主次层级、对齐方式和页面滚动方式。

## 组件清单与数量估算

- 按原型逐项统计按钮、输入框、下拉框、日期选择器、表格、卡片、Tab、弹窗、抽屉、分页、标签、图标、上传组件、图表等组件类型和数量。

## 分区组件细化

- 待按页面区域列出每个区域内的组件、文案、字段含义、是否必填、是否禁用、默认值、联动关系和展示状态。

## 视觉样式与颜色规划

- 默认样式依据：未额外说明时，以当前项目已有框架、设计系统、组件库和同类页面样式为主。
- 原型用途：用于校准布局结构、组件组合、相对位置、业务差异和明确标注的新视觉要求。
- 待提取当前框架已有的主色、辅助色、背景色、边框色、文字层级颜色、状态色、按钮样式、卡片圆角、阴影、间距、表格密度等视觉规则。
- 待对比原型与当前框架样式的差异；若冲突会影响实施，写入待确认项，不要默认照搬原型，也不要自行设计新视觉。

## 交互行为与页面状态

- 待说明点击、筛选、搜索、重置、分页、排序、查看、编辑、新增、删除、提交、取消、返回、二次确认等交互。
- 待覆盖加载态、空态、错误态、禁用态、提交中态、无权限态和接口失败态。

## 数据绑定与接口依赖

- 待说明页面显示数据来自哪些接口、字段如何绑定、哪些字段只读、哪些字段可编辑、哪些字段需要字典或枚举。

## 业务闭环检查清单

- 状态枚举：待补充界面展示的状态标签、步骤态、禁用态、按钮显隐态，以及与后端状态口径的映射关系。
- 权限/数据范围：待补充哪些按钮、字段、区域、操作受角色、组织、用户、数据范围控制。
- 写操作事务与幂等：待补充前端提交防重、按钮防连点、重复打开弹窗、重复回填、重复回调处理；纯展示页需明确写“无写操作”。
- 关联模块影响：待补充该界面对上下游页面、模块入口、返回路径、联动提示、穿透链路的影响。
- 接口契约：待补充前端依赖的接口路径、字段名、枚举值、分页结构、错误提示和空态约定，并与 `backend-plan.md` 保持一致。
- 验收用例：待补充页面还原、交互、状态切换、权限显隐、异常提示、界面穿透等可视化验收用例。
- 测试数据：待补充前端联调所需的角色、状态、空数据、超长文本、异常图片、异常枚举等样例数据要求。
- 性能索引：待补充大列表、大图片、图表刷新、级联筛选、并发请求、缓存和懒加载等前端性能关注点。
- 待确认项：待补充仍影响页面实现的业务问题、兜底交互方案以及是否阻塞。

## 响应式与兼容性说明

- 待说明桌面主宽度、内容溢出、表格横向滚动、弹窗尺寸、低分辨率适配和移动端是否需要支持。

## 前端实施步骤

1. 待规划页面容器、路由和文件位置。
2. 待规划静态布局和组件拆分。
3. 待规划数据模型、接口接入和状态管理。
4. 待规划表单校验、交互状态和错误处理。
5. 待规划联调、样式还原和验收检查。

## 风险与待确认点

- 待补充。

## 验收清单

- 待补充页面还原、交互、接口、状态、权限、异常和兼容性验收项。

## 给后续 executor 的实施提示

- 待补充推荐前端文件位置、路由/菜单接入点、可复用组件、同类页面代码、接口联调顺序和样式核对点。
- 这里只写后续建议，不表示已经调用或移交 `model-implement-executor`；实施必须由用户另行明确触发。
"""


BACKEND_TEMPLATE = """# 后端实施方案：{screen_name}

## 状态

draft

## RAG 上下文检索记录

- RAG 状态：待运行 `scripts/rag-status.ps1 -ModelRoot ".codex/model-implement" -Json` 后填写 healthy/warning/blocked/fallback。
- 检索词：待记录围绕模块名、界面名、业务动作、接口、数据库表、字段含义、状态流转、权限、待确认点执行的检索词。
- 命中原文：待列出实际打开精读的原始报告路径、标题或小节；禁止把 `reports/context-rag/chunks.jsonl` 当作事实来源。
- 精读结论：待总结从原始报告、模块报告或记忆文件中确认的业务动作、数据对象、接口规则和数据库缺口。
- 未命中或回退：若 RAG warning/blocked 或未命中关键问题，待写明回退读取了哪些原始文档、SQL 或代码。

## 原型来源

`{source_path}`

## 初始化前置信息

- 初始化契约：`reports/init-read/初始化契约.md`
- 代码及框架信息：`reports/init-read/代码及框架信息.md`
- 已有功能模块信息：`reports/init-read/已有功能模块信息.md`
- 待办清单：`reports/init-read/待办清单.md`
- 业务理解：`reports/init-read/业务理解.md`
- 数据库审查报告：`reports/init-read/数据库审查报告.md`
- 待确认点：`reports/init-read/待确认点.md`
- 模块准备度：`reports/modules/{module_name}/module-readiness.md`

## 知识库参考项

- 知识库入口：`library/定义规则.md`
- 待补充本界面实际命中的规则、组件、SQL、权限、接口或特殊资料路径；若知识库不存在或本界面未命中，需明确写明。
- 如果使用了组件库、权限组件、上传组件、SQL 兼容规则或特殊业务资料，必须列出具体路径和对本后端方案的影响。

## 原型到后端能力映射

- 可见控件：待把原型中的按钮、筛选项、表单项、列表列、详情字段、状态标签、弹窗动作映射为后端查询、保存、校验、状态变更或导出等能力。
- 业务动作：待说明每个动作对应的接口、服务方法、数据读写和异常处理。
- 数据含义：待用人能看懂的业务语言说明字段来源和用途，不要只罗列表名、字段名或路由。
- 冲突与确认：若原型字段、状态或动作在数据库审查报告/已有模块中找不到依据，待写明缺口和严重影响等级。

## 页面对应业务目标

- 待说明该界面要支撑的查询、新增、编辑、删除、提交、审核、状态变更或统计类业务动作。

## 涉及表与字段

- 待结合初始化输出和 `.codex/model-implement/.sql/` 列出主表、从表、关联表、字典表、日志表、视图或存储过程。
- 待细化每个页面字段对应的表字段、字段用途、是否查询条件、是否展示、是否写入、是否排序/聚合。

## 读写操作与数据流

- 待说明页面初始化、搜索、详情、保存、删除、状态变更、批量操作等动作对应的数据读写流程。
- 待说明是否需要事务、幂等、并发控制、软删除、审计日志或状态校验。

## 接口规划

- 待列出接口名称、请求方式、建议路径、入参、出参、分页结构、排序结构、错误场景和权限要求。

## 请求与响应字段说明

- 待拆分查询参数、路径参数、请求体、响应 DTO、列表字段、详情字段、字典字段和错误码。

## 业务规则与校验

- 待说明必填、唯一性、状态流转、数据范围、权限范围、删除限制、金额/数量精度、字典枚举和跨字段校验。

## 权限与数据范围

- 待说明哪些角色可以查询、编辑、提交、审核、删除、导出。
- 待说明按组织、单位、人员、供应商、预算主体、创建人等维度的数据范围过滤规则。

## 事务、视图、过程与触发器

- 待说明是否依赖已有表、视图、函数、触发器、存储过程，或是否需要新增/调整查询 SQL。

## 日志、审计与幂等说明

- 待说明操作日志、审计日志、状态日志、异常日志要求。
- 待说明重复提交、重复回调、重复审核、重复导入等幂等策略。

## 业务闭环检查清单

- 状态枚举：待补充业务状态、界面状态、审批状态、售后状态、是否评价/发货/提醒等枚举及流转条件。
- 权限/数据范围：待补充角色权限、按钮权限、接口权限、组织范围、单位范围、本人/本部门/全量等数据口径。
- 写操作事务与幂等：待补充事务边界、乐观锁/悲观锁、唯一约束、防重复提交、消息重复消费、失败回滚策略。
- 关联模块影响：待补充对首页、订单、商品、地址、预算、售后、统计、提醒等模块的影响面。
- 接口契约：待补充接口方法、路径、DTO、分页、排序、错误码、空态、枚举值口径，并与前端计划保持一致。
- 验收用例：待补充正常流、异常流、权限流、边界流、状态流转流、并发流的验收用例。
- 测试数据：待补充主数据、从数据、关联数据、空数据、脏数据、异常状态、跨组织数据的最小测试集合。
- 性能索引：待补充高频查询、模糊搜索、分页排序、聚合统计、跨表关联、批量写入和建议索引。
- 待确认项：待补充影响实现的业务问题、临时兜底规则、已知风险和是否阻塞。

## 后端实施步骤

1. 待规划 Controller/API 契约。
2. 待规划 Service 业务逻辑。
3. 待规划 Mapper/SQL 查询和写入。
4. 待规划 DTO/VO/Entity 映射。
5. 待规划权限、校验、事务和异常处理。
6. 待规划测试、联调和验收检查。

## 风险与待确认点

- 待补充。

## 验收清单

- 待补充接口、数据、权限、异常、性能和事务验收项。

## 给后续 executor 的实施提示

- 待补充推荐后端包/类/接口/SQL 位置、同类接口代码、数据库变更顺序、联调顺序和测试重点。
- 这里只写后续建议，不表示已经调用或移交 `model-implement-executor`；实施必须由用户另行明确触发。
"""


def image_files(module_dir: Path) -> list[Path]:
    return sorted(
        [path for path in module_dir.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS],
        key=lambda item: item.relative_to(module_dir).as_posix().lower(),
    )


def screen_dir_for(module_report_dir: Path, module_dir: Path, image_path: Path) -> Path:
    relative = image_path.relative_to(module_dir)
    parent = relative.parent
    if str(parent) == ".":
        return module_report_dir / image_path.stem
    return module_report_dir / parent / image_path.stem


def write_if_needed(path: Path, content: str, force: bool, created: list[Path]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if force or not path.exists():
        path.write_text(content, encoding="utf-8")
        created.append(path)


def migrate_legacy_files(modules_root: Path, module_name: str, module_report_dir: Path, force: bool, created: list[Path]) -> None:
    legacy_map = {
        modules_root / f"{module_name}.md": module_report_dir / "_legacy" / "legacy-module-plan.md",
        modules_root / f"{module_name}.zh.md": module_report_dir / "_legacy" / "legacy-module-plan.zh.md",
    }
    for source, target in legacy_map.items():
        if not source.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not force:
            continue
        source.replace(target)
        created.append(target)


def create_module_reports(workspace: Path, module_name: str, force: bool) -> list[Path]:
    module_dir = workspace / "prototypes" / module_name
    modules_root = workspace / "reports" / "modules"
    module_report_dir = modules_root / module_name
    created: list[Path] = []

    if not module_dir.exists() or not module_dir.is_dir():
        raise FileNotFoundError(f"Prototype module folder not found: {module_dir}")

    module_report_dir.mkdir(parents=True, exist_ok=True)
    migrate_legacy_files(modules_root, module_name, module_report_dir, force, created)

    images = image_files(module_dir)
    screen_items = "\n".join([f"- `{image.relative_to(module_dir).as_posix()}`" for image in images]) or "- No prototype images found yet."
    write_if_needed(
        module_report_dir / "module-relations.md",
        MODULE_RELATIONS_TEMPLATE.format(module_name=module_name, screen_list=screen_items),
        force,
        created,
    )

    for image in images:
        screen_dir = screen_dir_for(module_report_dir, module_dir, image)
        source_path = image.as_posix()
        write_if_needed(
            screen_dir / "frontend-plan.md",
            FRONTEND_TEMPLATE.format(screen_name=image.stem, source_path=source_path, module_name=module_name),
            force,
            created,
        )
        write_if_needed(
            screen_dir / "backend-plan.md",
            BACKEND_TEMPLATE.format(screen_name=image.stem, source_path=source_path, module_name=module_name),
            force,
            created,
        )

    return created


def create_reports(workspace: Path, module: str | None, force: bool) -> list[Path]:
    prototypes = workspace / "prototypes"
    prototypes.mkdir(parents=True, exist_ok=True)

    if module:
        return create_module_reports(workspace, module, force)

    created: list[Path] = []
    module_dirs = sorted([path for path in prototypes.iterdir() if path.is_dir()], key=lambda item: item.name.lower())
    for module_dir in module_dirs:
        created.extend(create_module_reports(workspace, module_dir.name, force))
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".codex/model-implement", help="Model implement workspace directory.")
    parser.add_argument("--module", help="Only create docs for this prototype module folder.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated docs and legacy targets.")
    args = parser.parse_args()

    created = create_reports(Path(args.workspace), args.module, args.force)
    if created:
        print("Created, updated, or migrated:")
        for path in created:
            print(path)
    else:
        print("No report files needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



#!/usr/bin/env python3
"""Create initialization reports and module readiness docs for model-implement-init."""

from __future__ import annotations

import argparse
from pathlib import Path


INIT_CONTRACT_TEMPLATE = """# 初始化契约

## 状态

draft

## 本次初始化范围

- 项目根目录：待补充。
- 初始化目标：先了解项目框架、已有功能模块、原型材料、SQL 结构和待办任务，不生成页面方案，不改业务代码。
- 当前轮次：待补充。

## 输入目录与材料来源

- 原型和需求材料：`.codex/model-implement/prototypes/`
- SQL 材料：`.codex/model-implement/.sql/`
- 知识库入口：`.codex/model-implement/library/定义规则.md`
- 项目约束入口：`AGENTS.md`
- 其他用户指定路径：待补充。

## 输出文档清单

- `reports/init-read/代码及框架信息.md`
- `reports/init-read/已有功能模块信息.md`
- `reports/init-read/待办清单.md`
- `reports/init-read/业务理解.md`
- `reports/init-read/数据库审查报告.md`
- `reports/init-read/待确认点.md`
- `reports/modules/<模块名>/module-readiness.md`

## 知识库与 AGENTS 约定

- 是否已创建或更新 `AGENTS.md`：待补充。
- 是否已执行 `knowledge-library/scripts/kb-init-project.ps1`：待补充。
- 本轮实际读取的知识库路径：待补充。
- 知识库缺失、入口缺失或索引缺失情况：待补充。

## 扫描边界

- 代码扫描范围：待补充。
- 原型扫描范围：待补充。
- SQL 扫描范围：待补充。
- 不扫描或暂缓扫描范围：待补充。

## 脱敏规则

- 不写入账号、密码、token、密钥、连接串、生产数据、内部地址。
- 数据库连接只记录方言判断证据，不记录敏感连接信息。
- 日志或截图中如含敏感信息，报告只保留摘要。

## 状态与严重等级

- 生命周期状态遵循 `references/status-contract.md`。
- 严重等级使用：`P0 阻塞`、`P1 高风险`、`P2 建议处理`、`P3 记录观察`。

## 人话表达规则

- 表、字段、接口、路由、文件路径都必须配合业务解释。
- 页面引用优先写界面名和用途，再补路由或文件路径。
- 数据库缺口必须写清业务动作、建议位置、中文含义和影响。

## 下游交接规则

- 新增模块或新增页面：准备度通过后交给 `model-implement`。
- 已确认方案实施：交给 `model-implement-executor`。
- 已有实现问题：交给 `model-implement-fix`。
- 上线前验收或运行时审查：交给 `model-implement-review`。

## 禁止事项

- 初始化阶段不生成 `frontend-plan.md`、`backend-plan.md`、`module-relations.md`。
- 初始化阶段不修改业务代码。
- 不把不确定但可本地查证的问题直接丢给用户。
"""


CODE_FRAMEWORK_TEMPLATE = """# 代码及框架信息

## 状态

draft

## 一句话结论

- 待用人能看懂的话总结当前项目技术底座，以及它对后续开发的影响。

## 前端框架与版本

- Vue 版本：待补充来源和影响。
- VS/VSUI 或组件框架版本：待补充来源和影响。
- 构建工具：待补充。
- 路由方式：待补充。
- 状态管理：待补充。

## 后端框架与版本

- Spring/Spring Boot 版本：待补充来源和影响。
- MyBatis/ORM：待补充。
- 分页、权限、日志、异常处理：待补充。

## VS 或组件框架信息

- 待补充项目使用的 VS 组件、权限组件、上传组件、码表、流程组件或其他公共框架能力。

## 构建与启动方式

- 前端启动：待补充。
- 后端启动：待补充。
- 配置文件和环境：待补充，注意脱敏。

## 路由、菜单与页面组织

- 待补充路由文件、菜单来源、页面目录组织方式。

## 请求封装与接口组织

- 待补充前端请求封装、API 文件组织、后端 Controller/API 组织方式。

## 权限、登录人与数据范围

- 待补充当前登录人获取、角色/菜单/按钮权限、组织/部门/用户等数据范围线索。

## 数据库连接与方言判断

- active datasource 证据：待补充，禁止记录敏感连接信息。
- 数据库方言判断：待补充。
- 不确定项：待补充。

## 代码目录与分层结构

- 前端目录：待补充。
- 后端目录：待补充。
- Mapper/XML 目录：待补充。

## 已有代码风格与约定

- 命名约定：待补充。
- 日期时间处理：待补充。
- 弹窗初始化、loading、分页、动态查询条件：待补充。

## 可复用工程能力

- 待补充公共组件、工具类、服务封装、接口模式、权限写法、上传/导入/导出等能力。

## 风险与待确认项

- 待补充会影响后续规划或实施的技术风险。
"""


EXISTING_MODULES_TEMPLATE = """# 已有功能模块信息

## 状态

draft

## 模块总览

- 待总结当前系统已有模块、主要入口和模块之间的大致关系。

## 路由与菜单来源

- 待说明本报告从哪些路由、菜单、页面目录或后端入口识别模块。

## 已有模块清单

| 模块/界面 | 界面用途 | 菜单或入口 | 主要动作 | 关联接口 | 可复用点 |
|---|---|---|---|---|---|
| 待补充 | 待补充 | 界面名 + 路由/文件路径 | 查询/新增/编辑等 | 动作 + method/path | 待补充 |

## 界面与功能动作

### 待补充界面名称

- 界面用途：待补充。
- 菜单或入口：待补充界面名，再补路由或文件路径。
- 主要动作：待补充查询、新增、编辑、删除、提交、审核、导入、导出、上传等。
- 关联接口：待补充动作、method/path、后端入口。
- 关联数据对象：待补充业务对象中文名和表/字段线索。
- 可复用点：待补充页面结构、组件、接口模式、权限写法、公共工具。

## 模块接口与后端入口

- 待补充 Controller/API、Service、Mapper/XML 与界面动作之间的关系。

## 关联数据对象

- 待补充业务对象中文名、用途、相关表和关键字段含义。

## 权限与数据范围观察

- 待补充按钮权限、菜单权限、接口权限和数据范围过滤方式。

## 已封装可复用功能

- 待补充列表页模式、查询/重置、分页、弹窗/抽屉、详情/编辑穿透、附件上传、导入导出、码表、权限、当前登录人、流程组件、公共工具。

## 可作为新需求参考的同类页面

- 待补充新需求可能复用或模仿的已有页面。

## 未识别或需确认的模块

- 待补充。
"""


TODO_TEMPLATE = """# 待办清单

## 状态

draft

## 任务总览

- 待总结 `prototypes/` 中已有材料整体分成哪些任务类型，以及当前推进状态。

## 材料来源清单

| 材料 | 类型 | 推断模块/界面 | 归类状态 | 依据 | 备注 |
|---|---|---|---|---|---|
| 待补充 | 待补充 | 待补充 | confirmed/inferred/unclassified | 待补充 | 待补充 |

## 新增功能模块或新增页面

| 编号 | 任务 | 来源材料 | 需要新建的界面/页面 | 业务目标 | 当前状态 | 下一步 |
|---|---|---|---|---|---|---|
| N-001 | 待补充 | 待补充 | 待补充 | 待补充 | 未开始 | 待补充 |

## 已有界面新增功能或调整

| 编号 | 任务 | 来源材料 | 目标已有界面 | 调整内容 | 当前状态 | 下一步 |
|---|---|---|---|---|---|---|
| E-001 | 待补充 | 待补充 | 界面名 + 入口 | 待补充 | 未开始 | 待补充 |

## 批量 bug 或问题修复

| 编号 | 问题 | 来源材料 | 目标界面/接口 | 问题类型 | 当前状态 | 建议后续 skill |
|---|---|---|---|---|---|---|
| B-001 | 待补充 | 待补充 | 待补充 | 待补充 | 未开始 | model-implement-fix |

## 待归类材料

- 待补充无法可靠归入新增、已有界面调整或 bug 修复的材料。

## 进度状态表

- `未开始`：尚未分析。
- `已归类`：已归入任务类型。
- `待确认`：缺少影响方向的信息。
- `可进入页面方案`：适合交给 `model-implement`。
- `可进入修复`：适合交给 `model-implement-fix`。
- `已交接`：已进入后续阶段。

## 建议执行顺序

- 待补充。

## 阻塞与依赖

- 待补充。
"""


BUSINESS_UNDERSTANDING_TEMPLATE = """# 业务理解

## 状态

draft

## 业务总体理解

- 待用人能看懂的话说明当前材料和已有系统涉及的业务范围。

## 角色与参与方

- 待补充用户、管理员、审批人、业务人员、供应商、部门、单位等角色。

## 业务对象说明

| 业务对象 | 中文含义 | 来源材料/已有模块 | 相关表或接口线索 | 备注 |
|---|---|---|---|---|
| 待补充 | 待补充 | 待补充 | 待补充 | 待补充 |

## 业务流程清单

- 流程 1：待补充。

## 业务流程图

```mermaid
flowchart TD
  Start["业务入口"] --> Step1["关键步骤"]
  Step1 --> End["业务结果"]
```

## 界面穿透与弹窗关系

```mermaid
flowchart LR
  List["列表界面"] --> Detail["详情界面"]
  List --> Dialog["新增/编辑弹窗"]
  Dialog -.保存后刷新.-> List
```

## 跨模块流转

- 待补充模块之间的业务交接、数据交接、页面跳转和状态影响。

## 状态与关键规则

- 待补充业务状态、触发动作、前置条件、后续影响。

## 与已有功能模块的关系

- 待补充哪些流程可复用已有界面、接口、组件或代码模式。

## 业务风险与待确认项

- 待补充。
"""


DATABASE_REVIEW_TEMPLATE = """# 数据库审查报告

## 状态

draft

## 审查结论

- 待总结当前 SQL 是否支撑后续功能实现，以及最主要的数据库风险。

## SQL 输入来源

- SQL 目录：`.codex/model-implement/.sql/`
- SQL 摘要 JSON：`reports/init-airead/sql-schema-digest.json`
- SQL 摘要 Markdown：`reports/init-airead/sql-schema-digest.md`
- 实际参考文件：待补充。

## 数据库方言与证据

- 方言判断：待补充。
- 证据：待补充 active datasource、driver、dialect 或不确定原因；禁止记录敏感连接信息。

## 业务对象覆盖情况

| 业务对象 | 需要支撑的业务动作 | 已有表/字段证据 | 覆盖判断 | 备注 |
|---|---|---|---|---|
| 待补充 | 待补充 | 表/字段 + 中文含义 | 足够/不足/待确认 | 待补充 |

## 已有表结构可支撑的功能

- 待补充哪些已有表和字段能支撑哪些页面或业务动作。

## 必须补充的表或字段

### P0-001 待补充标题

- 严重等级：P0 阻塞
- 涉及业务：待补充哪个页面/流程/动作需要它。
- 当前证据：待补充已有表、字段、SQL 摘要或材料来源。
- 缺口说明：待用业务语言解释缺什么。
- 建议位置：待补充建议在哪张表补字段，或建议新增哪张表。
- 字段/表含义：待补充中文含义 + 技术名建议。
- 影响：待补充不处理会影响什么。

## 建议补充的表或字段

- 待补充 P1/P2/P3 级建议。

## 关系、状态与字典审查

- 待补充表关系、状态字段、字典值、审批/流程状态、软删除等审查结果。

## 查询、分页、统计与索引风险

- 待补充高频查询、分页、模糊搜索、排序、统计、跨表关联和索引建议。

## 数据质量与约束风险

- 待补充唯一性、必填、长度、精度、默认值、主外键、一致性等风险。

## 严重等级汇总

| 编号 | 严重等级 | 问题 | 影响 | 建议 |
|---|---|---|---|---|
| 待补充 | P0/P1/P2/P3 | 待补充 | 待补充 | 待补充 |

## 待确认数据库问题

- 待补充。
"""


CONFIRMATION_TEMPLATE = """# 待确认点

## 状态

draft

## 确认点处理原则

- 先从代码、原型、SQL、知识库、已有功能模块中找答案。
- 只有找不到且影响实现方向、数据结构、权限口径、流程状态或验收标准的问题才列入。
- 每个确认点都必须写严重等级、已查证据、为什么必须确认和默认兜底建议。

## P0 阻塞确认点

- 待补充。

## P1 高风险确认点

### P1-001 待补充标题

- 涉及范围：待补充模块/界面/接口/表/流程。
- 已查找证据：待补充查过哪些材料和结论。
- 仍不确定的问题：待补充。
- 为什么必须确认：待补充。
- 默认兜底建议：待补充。

## P2 建议确认点

- 待补充。

## P3 记录观察

- 待补充。

## 已自行查证并关闭的问题

- 待补充曾经不确定、但已经从材料中找到答案的问题。

## 建议向用户提问的最小问题集

- 待补充真正需要用户回答的问题，数量越少越好。
"""


MODULE_READINESS_TEMPLATE = """# 模块准备度文档：{module_name}

## 状态

draft

## 模块或任务范围

- 原型来源：{prototype_source}
- 当前识别到的输入材料：
{source_list}

## 对应待办项

- 待补充本模块或任务对应 `reports/init-read/待办清单.md` 中的编号和分类。

## 输入材料清单

- 待补充材料类型、路径、页面/功能来源和是否已确认。

## 材料归类依据

- 归类状态：{classification_status}
- 归类依据：{classification_basis}

## 关联已有界面或新增判断

- 待说明这是新增模块/页面，还是已有界面新增功能/问题修复。
- 若关联已有界面，必须写界面名、入口、代码范围或接口范围。

## 知识库参考项

- 待补充本模块初始化时命中的 `library/` 规则、组件、样式或特殊资料路径；若无知识库或未命中，写明原因。

## 业务理解摘要

- 待结合 `reports/init-read/业务理解.md` 总结业务目标、主要流程、核心角色、关键状态和上下游关系。

## 可复用已有能力

- 待结合 `reports/init-read/已有功能模块信息.md` 写明可复用页面、组件、接口、服务、权限能力或数据模型。

## 数据库覆盖判断

- 待结合 `reports/init-read/数据库审查报告.md` 判断实体、字段、状态、关系和统计能力是否覆盖。

## 页面方案前置检查

- 待办归类是否清楚：待补充。
- 输入材料是否足够：待补充。
- 关联已有界面或新增判断是否明确：待补充。
- 业务流程和穿透关系是否清楚：待补充。
- 状态/角色/权限口径是否清楚：待补充。
- 现有模块复用点是否明确：待补充。
- 数据库覆盖是否足够或已有兜底：待补充。
- `待确认点.md` 是否存在 P0 阻塞项：待补充。
- 是否可进入详细页面实施方案阶段：待补充。

## 阻塞项

- 待补充。

## 建议先确认事项

- 待补充。

## 下一步建议

- 待补充应进入 `model-implement`、`model-implement-fix`、`model-implement-executor` 或继续补充材料。
"""


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"}
MATERIAL_EXTENSIONS = IMAGE_EXTENSIONS | {
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".pdf",
    ".doc",
    ".docx",
    ".md",
    ".txt",
    ".html",
    ".htm",
}
UNCLASSIFIED_MODULE = "_unclassified-inputs"


def write_if_needed(path: Path, content: str, force: bool, created: list[Path]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if force or not path.exists():
        path.write_text(content, encoding="utf-8")
        created.append(path)


def module_source_list(module_dir: Path) -> str:
    files = sorted(
        [path for path in module_dir.rglob("*") if path.is_file()],
        key=lambda item: item.relative_to(module_dir).as_posix().lower(),
    )
    if not files:
        return "- No input files found yet."
    lines = []
    for path in files:
        suffix = "image" if path.suffix.lower() in IMAGE_EXTENSIONS else "material"
        lines.append(f"- `{path.relative_to(module_dir).as_posix()}` ({suffix})")
    return "\n".join(lines)


def workspace_relative(path: Path, workspace: Path) -> str:
    try:
        return path.relative_to(workspace).as_posix()
    except ValueError:
        return path.as_posix()


def root_material_files(prototypes_dir: Path) -> list[Path]:
    if not prototypes_dir.exists():
        return []
    files = [
        path
        for path in prototypes_dir.iterdir()
        if path.is_file() and path.suffix.lower() in MATERIAL_EXTENSIONS
    ]
    return sorted(files, key=lambda item: item.name.lower())


def material_file_label(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in IMAGE_EXTENSIONS:
        return "image"
    if suffix in {".ppt", ".pptx"}:
        return "presentation"
    if suffix in {".xls", ".xlsx"}:
        return "spreadsheet"
    if suffix in {".doc", ".docx"}:
        return "document"
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".html", ".htm"}:
        return "html"
    if suffix in {".md", ".txt"}:
        return "text"
    return "material"


def unclassified_source_list(prototypes_dir: Path, workspace: Path) -> str:
    files = root_material_files(prototypes_dir)
    if not files:
        return "- No root-level prototype or requirement material found yet."
    lines = []
    for path in files:
        lines.append(f"- `{workspace_relative(path, workspace)}` ({material_file_label(path)})")
    return "\n".join(lines)


def create_shared_reports(workspace: Path, force: bool, created: list[Path]) -> None:
    reports_dir = workspace / "reports"
    human_dir = reports_dir / "init-read"
    (reports_dir / "init-airead").mkdir(parents=True, exist_ok=True)
    write_if_needed(human_dir / "初始化契约.md", INIT_CONTRACT_TEMPLATE, force, created)
    write_if_needed(human_dir / "代码及框架信息.md", CODE_FRAMEWORK_TEMPLATE, force, created)
    write_if_needed(human_dir / "已有功能模块信息.md", EXISTING_MODULES_TEMPLATE, force, created)
    write_if_needed(human_dir / "待办清单.md", TODO_TEMPLATE, force, created)
    write_if_needed(human_dir / "业务理解.md", BUSINESS_UNDERSTANDING_TEMPLATE, force, created)
    write_if_needed(human_dir / "数据库审查报告.md", DATABASE_REVIEW_TEMPLATE, force, created)
    write_if_needed(human_dir / "待确认点.md", CONFIRMATION_TEMPLATE, force, created)


def create_module_report(
    workspace: Path,
    module_name: str,
    force: bool,
    created: list[Path],
    *,
    prototype_source: str | None = None,
    source_list: str | None = None,
    classification_status: str = "confirmed",
    classification_basis: str = "standard module folder name",
) -> None:
    module_dir = workspace / "prototypes" / module_name
    if source_list is None and (not module_dir.exists() or not module_dir.is_dir()):
        raise FileNotFoundError(f"Prototype module folder not found: {module_dir}")

    module_report_dir = workspace / "reports" / "modules" / module_name
    write_if_needed(
        module_report_dir / "module-readiness.md",
        MODULE_READINESS_TEMPLATE.format(
            module_name=module_name,
            prototype_source=prototype_source or f"`.codex/model-implement/prototypes/{module_name}/`",
            source_list=source_list or module_source_list(module_dir),
            classification_status=classification_status,
            classification_basis=classification_basis,
        ),
        force,
        created,
    )


def create_reports(workspace: Path, module: str | None, force: bool) -> list[Path]:
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / "prototypes").mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    create_shared_reports(workspace, force, created)
    prototypes_dir = workspace / "prototypes"

    if module:
        create_module_report(workspace, module, force, created)
        return created

    module_dirs = sorted([path for path in prototypes_dir.iterdir() if path.is_dir()], key=lambda item: item.name.lower())
    for module_dir in module_dirs:
        create_module_report(workspace, module_dir.name, force, created)

    if root_material_files(prototypes_dir):
        create_module_report(
            workspace,
            UNCLASSIFIED_MODULE,
            force,
            created,
            prototype_source="`.codex/model-implement/prototypes/` root-level material files",
            source_list=unclassified_source_list(prototypes_dir, workspace),
            classification_status="unclassified",
            classification_basis="root-level material file names; assign to modules after reading PPT/PPTX pages, Excel rows, document headings, or user confirmation",
        )
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=".codex/model-implement", help="Model implement workspace directory.")
    parser.add_argument("--module", help="Only create initialization docs for this prototype module folder.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated docs.")
    args = parser.parse_args()

    created = create_reports(Path(args.workspace), args.module, args.force)
    if created:
        print("Created or updated:")
        for path in created:
            print(path)
    else:
        print("No report files needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

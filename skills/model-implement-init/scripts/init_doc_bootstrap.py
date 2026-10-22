#!/usr/bin/env python3
"""Create initialization reports and module readiness docs for model-implement-init."""

from __future__ import annotations

import argparse
from pathlib import Path


SHARED_CONTEXT_TEMPLATE = """# Shared Context

## Status

draft

## Source Manifest

- Primary manifest path: `reports/init-airead/source-manifest.json`
- Primary prototype input root: `.codex/model-implement/prototypes/`
- Primary SQL input root: `.codex/model-implement/.sql/`
- Primary knowledge library root: `.codex/model-implement/library/`

## Project Understanding

- TODO: Summarize the current project, main applications, and why the target prototype work matters here.

## Framework Scan

- TODO: Summarize frontend stack, backend stack, routing conventions, API conventions, auth conventions, and data-access conventions.

## Existing Module Inventory

- TODO: Summarize existing modules or pages that may be reused for the prototype implementation.

## Knowledge Library References

- Library root: `.codex/model-implement/library/`
- Entry file to check: `library/定义规则.md`
- TODO: State whether the library exists, whether `library/定义规则.md` was read, which paths matched this initialization pass, and which useful entries are missing or not indexed.

## Prototype and Requirement Inputs

- TODO: Summarize which prototype folders, root-level PPT/PPTX, Excel, PDF/Word, Markdown, HTML, scattered images, exported prototype folders, notes, and requirement sources were used in this initialization pass.
- TODO: Mark each module ownership conclusion as confirmed, inferred, or unclassified.

## Shared Assumptions

- TODO: Record stable non-blocking assumptions that later planning can inherit.

## Shared Risks

- TODO: Record cross-module, framework, database, or delivery risks discovered during initialization.

## Next Update Notes

- TODO: Record what should trigger the next initialization refresh.
"""


SHARED_CONTEXT_ZH_TEMPLATE = """# 共享上下文

## 状态

draft

## Source Manifest

- 主指纹文件：`reports/init-airead/source-manifest.json`
- 原型输入根目录：`.codex/model-implement/prototypes/`
- SQL 输入根目录：`.codex/model-implement/.sql/`
- 知识库根目录：`.codex/model-implement/library/`

## 项目理解

- 待补充当前项目组成、主要应用、以及本次原型实施工作在项目中的位置。

## 框架扫描

- 待补充前端栈、后端栈、路由约定、接口约定、权限约定、数据访问约定。

## 已有模块清单

- 待补充当前代码中可复用的模块、页面、组件、能力或接口。

## 知识库参考情况

- 知识库根目录：`.codex/model-implement/library/`
- 入口文件：`library/定义规则.md`
- 待补充知识库是否存在、本轮是否读取 `library/定义规则.md`、命中了哪些规则/组件/样式/特殊资料路径、哪些资料缺少索引。

## 原型与需求输入

- 待补充本轮初始化使用了哪些模块目录、根目录 PPT/PPTX、Excel、PDF/Word、Markdown、HTML、散落图片、导出原型目录、说明文档和需求来源。
- 待补充每个模块归属是已确认、推断还是未归类。

## 共享假设

- 待补充后续页面方案可以继承的稳定且非阻塞假设。

## 共享风险

- 待补充初始化阶段识别出的跨模块、框架、数据库或交付风险。

## 下一次更新说明

- 待补充什么变化会触发下一次初始化刷新。
"""


INIT_SUMMARY_ZH_TEMPLATE = """# 初始化总结报告

## 状态

draft

## 一句话结论

- 待补充本轮初始化最重要的结论，用非技术人员也容易理解的方式说明当前项目、原型和数据库是否具备继续规划条件。

## 本轮覆盖范围

- 原型范围：待补充。
- 代码范围：待补充。
- SQL 范围：待补充。
- 知识库范围：待补充是否存在 `library/`，以及本轮命中的知识库路径。
- 重点模块：待补充。

## 知识库参考情况

- 待补充是否存在 `.codex/model-implement/library/`。
- 若存在：待列出本轮实际读取的 `library/定义规则.md` 以及命中的规则、组件、样式或特殊资料路径。
- 若不存在：提醒用户当前初始化缺少知识库参考，后续高复用任务可能需要人工补充规则或组件资料。

## 业务逻辑层面

### 业务流程路线

- 待用宽泛语言说明从入口、关键操作、状态变化到结果页的主流程。

```mermaid
flowchart TD
  Start["业务入口"] --> Step1["关键步骤"]
  Step1 --> Step2["业务处理"]
  Step2 --> End["业务结果"]
```

### 页面关联穿透跳转情况

- 待说明页面之间的跳转、穿透、回流、跨模块入口和共享业务对象。

```mermaid
flowchart LR
  PageA["页面A"] --> PageB["页面B"]
  PageB --> PageC["页面C"]
  PageC -.回流.-> PageA
```

## 代码层面

### 已有可复用的方法与能力

- 待总结公共方法、工具函数、公共组件、服务封装、接口模式、权限处理、上传/导入/导出等可复用能力。

### 知识库可参考能力

- 待总结知识库中与本轮业务、组件、样式、SQL 或特殊规则相关的可参考资料。

### 原型需求可提取公共实现的地方

- 待总结哪些页面相似度高，适合复用同一套页面骨架、组件、后端接口、查询逻辑、状态处理或公共样式。

## 重点风险与待确认项

- 待提炼业务流程、页面关系、代码复用、数据库覆盖、权限/数据范围中最影响下一步的问题。

## 建议下一步

- 待说明哪些模块可以进入 `model-implement`，哪些模块需要先补充资料或确认规则。
"""


MODULE_DIRECTORY_ZH_TEMPLATE = """# 功能模块清单

## 状态

draft

## 说明

- 本文档给使用人阅读，用类似目录或菜单的方式记录系统功能模块、子模块和页面层级。
- 有几级就写几级；如果层级来自推断，需要标注“推断”。
- 页面来源可以是 PPT/PPTX 文件、PPT 页标题、Excel 功能项、图片路径、文档标题、HTML 导出路径或用户说明。

## 模块层级目录

```text
大模块（待补充）
  子模块（待补充）
    页面（待补充，来源：待补充）
      子页面/弹窗/详情/编辑（待补充，来源：待补充）
```

## 未归类材料

- 待补充暂时无法归入模块或页面的原型、Excel、文档、图片、HTML 导出等材料。

## 页面来源索引

| 页面/功能 | 所属层级 | 来源材料 | 归类状态 | 备注 |
|---|---|---|---|---|
| 待补充 | 待补充 | 待补充 | confirmed/inferred/unclassified | 待补充 |

## 待确认项

- 待补充模块名称、菜单层级、页面归属、页面顺序、穿透关系或页面缺失问题。
"""


INPUT_MATERIALS_TEMPLATE = """# Input Materials

## Status

draft

## Prototype Root

- Primary prototype input root: `.codex/model-implement/prototypes/`
- Inputs may be module folders, root-level PPT/PPTX, Excel function lists, PDF/Word documents, Markdown, HTML exports, scattered images, extracted prototype folders, or user-specified paths.

## Material Inventory

- TODO: List all source materials used by initialization with type, path, and purpose.

## Module and Page Classification

- TODO: Record inferred or confirmed module/page ownership and the evidence for each decision.

## Unclassified Inputs

- TODO: List materials that cannot yet be assigned to a module or page.

## Knowledge Library Matches

- TODO: Record whether `library/定义规则.md` exists and which knowledge-library paths were matched.

## Source Evidence Rules

- confirmed: explicitly provided by folder name, user instruction, existing route/menu, or clear source document.
- inferred: inferred from filename, PPT page title, Excel row, document heading, screenshot, or context.
- unclassified: insufficient evidence; requires user confirmation.

## Open Questions

- TODO: Record material classification questions that affect downstream planning.
"""


BUSINESS_FLOWS_TEMPLATE = """# Business Flows

## Status

draft

## Scope

- TODO: Define the business scope covered by the current prototype inputs.

## Input Sources

- TODO: List the prototype folders, root-level files, notes, and requirement files that informed this flow analysis.

## Prototype Material Inventory

- TODO: Inventory standard module folders, root-level PPT/PPTX, Excel function lists, PDF/Word docs, Markdown, HTML exports, scattered images, extracted folders, or user-specified paths.
- TODO: Record whether each module/page relationship is confirmed, inferred, or unclassified.

## Roles and Actors

- TODO: List users, admins, approvers, suppliers, buyers, finance roles, or other actors involved in the flows.

## Module Flow Summary

- TODO: Summarize the main end-to-end flow at module level.

## Cross-Module Flow Details

- TODO: Explain how one module hands off to another in the business process.

## State and Process Dependencies

- TODO: Summarize key statuses, transitions, gates, and process dependencies.

## Shared Data Hand-offs

- TODO: List the key entities, IDs, tables, or payloads handed between modules.

## Reusable Existing Capabilities

- TODO: Note current code capabilities that may support the new flows.

## Ambiguities and Gaps

- TODO: Record unclear parts of the process or missing requirement details.

## Next Update Notes

- TODO: Record what additional sources or confirmations would improve this report.
"""


BUSINESS_FLOWS_ZH_TEMPLATE = """# 业务流程分析

## 状态

draft

## 范围

- 待补充当前原型输入覆盖的业务范围。

## 输入来源

- 待补充本轮流程分析参考了哪些原型目录、根目录文件、说明文档和需求文件。

## 原型材料清单

- 待清点标准模块目录、根目录 PPT/PPTX、Excel 功能清单、PDF/Word、Markdown、HTML 导出、散落图片、导出原型目录或用户指定路径。
- 待记录每个模块/页面关系是已确认、推断还是未归类。

## 角色与参与方

- 待补充用户、管理员、审批人、供应商、采购人、财务人员等角色。

## 模块流程总览

- 待补充模块层面的端到端流程总结。

## 跨模块流程明细

- 待补充一个模块如何把业务流转交给另一个模块。

## 状态与流程依赖

- 待补充关键状态、状态流转、流程门槛和依赖关系。

## 共享数据交接

- 待补充模块之间传递的关键实体、ID、表或接口载荷。

## 可复用现有能力

- 待补充当前代码中可以支撑新流程的能力。

## 模糊点与缺口

- 待补充流程里不清晰或缺失的要求。

## 下一次更新说明

- 待补充补哪些资料或确认哪些问题后，这份文档会更完整。
"""


DB_ASSESSMENT_TEMPLATE = """# Database Assessment

## Status

draft

## Source SQL Inputs

- Primary SQL root: `.codex/model-implement/.sql/`
- Schema digest JSON: `reports/init-airead/sql-schema-digest.json`
- Schema digest Markdown: `reports/init-airead/sql-schema-digest.md`
- TODO: List the main SQL files or schema notes used in this assessment.

## Business Flow Coverage

- TODO: Explain whether the database can support the business flows described in `reports/init-airead/business-flows.md`.

## Entity and Attribute Coverage

- TODO: Summarize whether core business entities and fields are covered.

## Relationship and State Coverage

- TODO: Summarize whether relationships and status storage are covered.

## Write Operation Support

- TODO: Summarize whether create, update, delete, submit, audit, and state-transition writes are supported.

## Query and Reporting Support

- TODO: Summarize whether lists, search, sort, filter, aggregation, and report-style queries are supported.

## Constraints and Data Quality

- TODO: Summarize uniqueness, nullability, precision, foreign-key, and data-quality findings.

## Performance and Index Notes

- TODO: Summarize likely performance hotspots and missing indexes or summary structures.

## Risks and Recommendations

- TODO: Record key risks and recommendations, prioritized if possible.

## Open Questions

- TODO: Record schema questions that still affect planning.
"""


DB_ASSESSMENT_ZH_TEMPLATE = """# 数据库评估

## 状态

draft

## SQL 输入来源

- 主 SQL 目录：`.codex/model-implement/.sql/`
- SQL 摘要 JSON：`reports/init-airead/sql-schema-digest.json`
- SQL 摘要 Markdown：`reports/init-airead/sql-schema-digest.md`
- 待补充本轮评估实际参考了哪些 SQL 文件或结构说明。

## 业务流程覆盖情况

- 待补充数据库是否能支撑 `reports/init-read/业务流程.md` 中描述的业务流程。

## 实体与属性覆盖

- 待补充核心业务实体和字段是否覆盖。

## 关系与状态覆盖

- 待补充表关系、业务状态、审批状态、售后状态等是否可落库。

## 写操作支撑情况

- 待补充新增、编辑、删除、提交、审核、状态变更等写操作是否可支撑。

## 查询与统计支撑情况

- 待补充列表、搜索、筛选、排序、聚合、统计类查询是否可支撑。

## 约束与数据质量

- 待补充唯一性、可空性、精度、主外键、一致性和数据质量发现。

## 性能与索引说明

- 待补充潜在性能热点、缺失索引和可能需要的汇总结构。

## 风险与建议

- 待补充关键风险和建议，尽量给出优先级。

## 待确认问题

- 待补充仍会影响后续规划的数据库问题。
"""


REVIEW_NEEDED_TEMPLATE = """# 待人工审查与补充报告

## 状态

draft

## 本轮结论摘要

- 待补充本轮初始化的主要结论。

## 需人工确认的阻塞项

- 待补充会阻塞页面方案生成或代码实施的问题。

## 建议补充的业务信息

- 待补充哪些业务规则、状态口径、权限口径、流程口径需要补充。

## 原型或文档不清晰点

- 待补充原型、说明文档、页面命名、交互说明不清晰的地方。

## 原型材料归类待确认

- 待补充根目录 PPT/PPTX、Excel、散落图片、导出目录等材料的模块归属、页面归属、页面顺序或业务流程归属是否需要人工确认。

## 知识库待确认点

- 待补充 `.codex/model-implement/library/` 是否不存在、入口文件是否缺失、索引是否未登记、或命中的知识库资料是否与当前项目冲突。

## 数据库待确认点

- 待补充表结构、字段口径、状态存储、关系模型、索引等仍待确认的问题。

## 默认兜底假设

- 待补充当前为了继续推进而采用的非阻塞默认假设。

## 建议下一步

- 待补充建议先确认什么，再运行哪个 skill。
"""


MODULE_READINESS_TEMPLATE = """# 模块准备度文档：{module_name}

## 状态

draft

## 模块范围

- 原型来源：{prototype_source}
- 当前识别到的输入材料：
{source_list}

## 输入材料归类依据

- 归类状态：{classification_status}
- 归类依据：{classification_basis}

## 知识库参考项

- 待补充本模块初始化时命中的 `library/` 规则、组件、样式或特殊资料路径；若无知识库或未命中，写明原因。

## 业务理解摘要

- 待补充该模块的业务目标、主要流程、核心角色、关键状态和上下游关系。

## 现有模块复用点

- 待补充当前代码中可复用的页面、组件、接口、服务、权限能力或数据模型。

## 数据库覆盖判断

- 待结合 `reports/init-airead/db-assessment.md` 判断该模块所需的实体、字段、状态、关系和统计能力是否已覆盖。

## 页面方案前置检查

- 输入材料完整性：待补充。
- 输入材料归类清晰度：待补充。
- 知识库参考充分性：待补充。
- 业务流程清晰度：待补充。
- 状态/角色/权限口径：待补充。
- 现有模块复用清晰度：待补充。
- 数据库覆盖充分性：待补充。
- 是否可进入详细页面实施方案阶段：待补充。

## 阻塞项

- 待补充。

## 建议先确认事项

- 待补充。

## 下一步建议

- 待补充。
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
    files = sorted([path for path in module_dir.rglob("*") if path.is_file()], key=lambda item: item.relative_to(module_dir).as_posix().lower())
    if not files:
        return "- No input files found yet."
    lines = []
    for path in files:
        suffix = "image" if path.suffix.lower() in IMAGE_EXTENSIONS else "doc"
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
    ai_dir = reports_dir / "init-airead"
    human_dir = reports_dir / "init-read"
    write_if_needed(human_dir / "初始化总结.md", INIT_SUMMARY_ZH_TEMPLATE, force, created)
    write_if_needed(human_dir / "功能模块清单.md", MODULE_DIRECTORY_ZH_TEMPLATE, force, created)
    write_if_needed(human_dir / "共享上下文.md", SHARED_CONTEXT_ZH_TEMPLATE, force, created)
    write_if_needed(human_dir / "业务流程.md", BUSINESS_FLOWS_ZH_TEMPLATE, force, created)
    write_if_needed(human_dir / "数据库评估.md", DB_ASSESSMENT_ZH_TEMPLATE, force, created)
    write_if_needed(human_dir / "待人工确认.md", REVIEW_NEEDED_TEMPLATE, force, created)
    write_if_needed(ai_dir / "shared-context.md", SHARED_CONTEXT_TEMPLATE, force, created)
    write_if_needed(ai_dir / "business-flows.md", BUSINESS_FLOWS_TEMPLATE, force, created)
    write_if_needed(ai_dir / "db-assessment.md", DB_ASSESSMENT_TEMPLATE, force, created)
    write_if_needed(ai_dir / "input-materials.md", INPUT_MATERIALS_TEMPLATE, force, created)


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

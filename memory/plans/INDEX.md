---
memory_id: MEM-PLANS-INDEX
type: index
record_level: index
coverage: partial
status: verified
metadata_state: native
scope: plan-navigation
aliases: [大需求, 阶段需求, 复杂问题, 计划, 验收]
record_path: plans/INDEX.md
record_anchor: Plans 大需求计划
parent_id: MEM-ROOT-INDEX
impact_paths: ["skills/project-memory-maintenance/references/plans-format.md"]
evidence_sources:
  - kind: config
    path: skills/project-memory-maintenance/references/plans-format.md
    anchor: 创建条件
    evidence_hash: "sha256:f9ed3b3b11eaed48ca8c40786a8a112351f57a08edc1615b214d04b78ebd2a8b"
    verified_at: "2026-10-09"
updated_at: "2026-10-09"
record_hash: "sha256:56787acc24ce2cece470e4e3bc6dce1a5ed4318dccee915904cf7ab556263d6b"
---
# Plans 大需求计划

## 职责与创建条件

仅记录材料中的大需求，或需要分阶段处理且有依赖、待确认项或独立验收安排的复杂问题。材料存在本身不代表需要生成计划；普通问答、按钮/文案/样式小修改及简单修复不创建计划，不建立日计划。

## 文件命名与版本

计划文件直接保存在本目录，命名为 `YYYY-MM-DD-vN.md`，例如 `2026-10-09-v1.md`。日期是该版本形成的日期；普通进度更新继续使用当前文件，范围、方案或关键约束发生实质变化时才建立更高版本并保留旧版。重名时选择未占用的更高编号，不覆盖其他需求；同一需求通过稳定 `plan_id` 关联，版本节点标识由索引根据 `plan_id` 和文件名自动生成，不额外维护 `memory_id`。

## 需求文件头

只保留 `plan_id`、`plan_state`、`updated_at`；替代旧版本时才加 `supersedes`，不填 null 占位。日期/版本从文件名读取，来源/范围/进度保留在正文，其他索引字段和哈希由脚本推导。代码新鲜度对需求计划为 `not_applicable`，不要求 Git 核验字段；正文来源、依赖和待补充仍需核对。本导航文件继续使用索引元数据。

## 读取条件

执行大需求、恢复复杂问题或核对需求进度时，先按下面的文件级需求简介和 `plan_id` 定位当前有效版本，再读取需求清单、待补充和实施计划；比较历史决策时才读取旧版本，不根据日期独自判断需求归属。

## 详细内容与实施门槛

格式见 [plans-format.md](../../skills/project-memory-maintenance/references/plans-format.md)，正文使用 [详细需求模板](../../skills/project-memory-maintenance/assets/requirement-plan-template.md)，包含：来源文档、目标与范围、需求清单、现状与影响范围、表结构计划、分级待补充、依赖与前置条件、实施计划、验收与验证、风险/回滚/决策、计划变更记录。

清单分别记录需求明确性、可立即实施及原因、完成进度；P0 未解决时禁止实施受影响需求及其依赖，影响整个核心方案则整体暂停。P1 在确认后实施相关部分，P2/P3 按影响处理。计划不授予额外实施权限，沿用当前会话授权。

## 维护与文件导航

计划记录预期和真实进度，不替代当前实现。每个实际计划文件仅登记一句需求简介和编号/版本/状态；不为文件内部的需求清单逐条建索引。历史版本标记被替代关系。没有实际计划文件时保持下表为空，不根据旧失效索引重建需求。

| 文件 | 需求简介 | 计划编号 | 版本 | 状态 | 更新时间 |
| --- | --- | --- | --- | --- | --- |

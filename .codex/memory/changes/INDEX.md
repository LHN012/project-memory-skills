# Changes

本层记录重要变更、影响范围和回滚线索，采用按日期追加的 JSONL 时间线。

- 文件名固定为 `YYYY-MM-DD.jsonl`，直接放在本目录。
- 同一天的记录写入同一个文件，每行一条 JSON 记录。
- 当前记录字段为 `change_id`、`timestamp`、`issue`、`observation`。
- 本索引只说明格式和读取规则，不为单条记录建立索引。
- 读取条件：需要历史追踪、回归或回滚时。
- 写入权限：重要变更后维护。

维护和校验规则见 [changes-format.md](../../skills/project-memory-maintenance/references/changes-format.md)。

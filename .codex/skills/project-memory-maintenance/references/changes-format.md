# Changes 记录格式

`changes` 是按日期追加的变更时间线，权威来源是 `.codex/memory/changes/` 下直接保存的 JSONL 文件。

## 文件约定

- 文件名固定为 `YYYY-MM-DD.jsonl`，直接放在 `changes/` 根目录。
- 同一天的记录追加到同一个文件，不按主题、月份或记录条目继续拆目录。
- 一行对应一条 JSON 对象；不要使用多行 JSON、Markdown frontmatter 或单条记录文件。
- `changes/INDEX.md` 只说明本层用途和读取规则，不为每一条记录建立索引。
- 记录按 `timestamp` 顺序追加；历史记录不覆盖、不重排。

## 记录字段

```json
{
  "change_id": "CHG-20260915-003",
  "timestamp": "2026-09-15T10:12:56+08:00",
  "issue": "all_order_log_callers_migrated",
  "observation": "……"
}
```

四个字段都是必填字段，当前不扩展其他字段：

- `change_id`：唯一记录编号，格式为 `CHG-YYYYMMDD-NNN`；`NNN` 是当天的顺序号。
- `timestamp`：变更发生或确认的时间，必须包含时区；文件日期应与时间的日期部分一致。
- `issue`：问题或变更主题，使用稳定的英文 `snake_case` 标识；同一个主题可以有多条记录。
- `observation`：本次变更的完整描述，可包含现象、原因、处理方式、影响、验证结果和未确认事项。

`change_id` 是记录引用和去重依据，`issue` 只用于搜索和归类。记录已经确认的内容，不把未验证推测写成确定结论。

## 写入和校验

优先使用维护 Skill 的 `scripts/append_change.py` 追加记录；不要用通用 Markdown 写入器替换 JSONL 文件。写入前后可使用 `scripts/validate_changes.py` 检查：

- 文件名和目录位置；
- JSONL 每行是否为合法对象；
- 四个字段、字段类型和标识格式；
- 文件日期、`timestamp` 和 `change_id` 日期是否一致；
- `change_id` 是否在所有日期文件中重复。

`changes` 不参与 Markdown 导航索引或 SQLite/FTS5 Markdown 同步；需要检索时按日期文件名、`change_id`、`issue` 和文本内容读取。

#!/usr/bin/env python3
"""Create a lightweight schema digest from SQL files for model-implement-init."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path


SQL_EXTENSIONS = {".sql"}
CREATE_TABLE_RE = re.compile(
    r"create\s+(?:global\s+temporary\s+|temporary\s+)?table\s+(?:if\s+not\s+exists\s+)?(?P<name>[`\"\[\]\w.$]+)\s*\(",
    re.IGNORECASE,
)
TABLE_COMMENT_RE = re.compile(
    r"comment\s+on\s+table\s+(?P<table>[`\"\[\]\w.$]+)\s+is\s+'(?P<comment>(?:''|[^'])*)'",
    re.IGNORECASE,
)
COLUMN_COMMENT_RE = re.compile(
    r"comment\s+on\s+column\s+(?P<table>[`\"\[\]\w.$]+)\.(?P<column>[`\"\[\]\w$]+)\s+is\s+'(?P<comment>(?:''|[^'])*)'",
    re.IGNORECASE,
)
MYSQL_TABLE_COMMENT_RE = re.compile(r"\bcomment\s*=\s*'(?P<comment>(?:''|[^'])*)'", re.IGNORECASE)
MYSQL_COLUMN_COMMENT_RE = re.compile(r"\bcomment\s+'(?P<comment>(?:''|[^'])*)'", re.IGNORECASE)
PK_ALTER_RE = re.compile(
    r"alter\s+table\s+(?P<table>[`\"\[\]\w.$]+)\s+add\s+(?:constraint\s+(?P<constraint>[`\"\[\]\w.$]+)\s+)?primary\s+key\s*\((?P<columns>[^)]+)\)",
    re.IGNORECASE,
)
FK_ALTER_RE = re.compile(
    r"alter\s+table\s+(?P<table>[`\"\[\]\w.$]+)\s+add\s+(?:constraint\s+(?P<constraint>[`\"\[\]\w.$]+)\s+)?foreign\s+key\s*\((?P<columns>[^)]+)\)\s+references\s+(?P<ref_table>[`\"\[\]\w.$]+)\s*\((?P<ref_columns>[^)]+)\)",
    re.IGNORECASE,
)
INDEX_RE = re.compile(
    r"create\s+(?P<unique>unique\s+)?index\s+(?P<name>[`\"\[\]\w.$]+)\s+on\s+(?P<table>[`\"\[\]\w.$]+)\s*\((?P<columns>[^)]+)\)",
    re.IGNORECASE,
)


@dataclass
class Column:
    name: str
    data_type: str = ""
    nullable: str = "unknown"
    default: str = ""
    comment: str = ""
    enum_hint: str = ""


@dataclass
class Index:
    name: str
    columns: list[str]
    unique: bool = False


@dataclass
class ForeignKey:
    name: str
    columns: list[str]
    ref_table: str
    ref_columns: list[str]


@dataclass
class Table:
    name: str
    source: str
    comment: str = ""
    columns: dict[str, Column] = field(default_factory=dict)
    primary_key: list[str] = field(default_factory=list)
    foreign_keys: list[ForeignKey] = field(default_factory=list)
    indexes: list[Index] = field(default_factory=list)


def normalize_identifier(value: str) -> str:
    value = value.strip().rstrip(";")
    while value and value[0] in "`\"[" and value[-1:] in "`\"]":
        value = value[1:-1]
    return value.strip()


def unescape_sql_string(value: str) -> str:
    return value.replace("''", "'").strip()


def split_csv(value: str) -> list[str]:
    items: list[str] = []
    current: list[str] = []
    depth = 0
    quote: str | None = None
    index = 0
    while index < len(value):
        char = value[index]
        if quote:
            current.append(char)
            if char == quote:
                if index + 1 < len(value) and value[index + 1] == quote:
                    current.append(value[index + 1])
                    index += 1
                else:
                    quote = None
        else:
            if char in {"'", '"', "`"}:
                quote = char
                current.append(char)
            elif char == "(":
                depth += 1
                current.append(char)
            elif char == ")":
                depth = max(0, depth - 1)
                current.append(char)
            elif char == "," and depth == 0:
                item = "".join(current).strip()
                if item:
                    items.append(item)
                current = []
            else:
                current.append(char)
        index += 1
    item = "".join(current).strip()
    if item:
        items.append(item)
    return items


def find_matching_paren(sql: str, open_index: int) -> int:
    depth = 0
    quote: str | None = None
    index = open_index
    while index < len(sql):
        char = sql[index]
        if quote:
            if char == quote:
                if index + 1 < len(sql) and sql[index + 1] == quote:
                    index += 1
                else:
                    quote = None
        else:
            if char in {"'", '"', "`"}:
                quote = char
            elif char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0:
                    return index
        index += 1
    return -1


def strip_comments(sql: str) -> str:
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    return re.sub(r"--[^\n\r]*", " ", sql)


def enum_hint_from_comment(comment: str) -> str:
    if not comment:
        return ""
    markers = ["0:", "1:", "0-", "1-", "0=", "1=", "枚举", "状态", "类型", "：", ":"]
    if any(marker in comment for marker in markers):
        return comment
    return ""


def parse_column(definition: str) -> Column | None:
    match = re.match(r"\s*([`\"\[\]\w$]+)\s+(.+)", definition, flags=re.DOTALL)
    if not match:
        return None
    name = normalize_identifier(match.group(1))
    if not name:
        return None
    rest = match.group(2).strip()
    upper = rest.upper()
    stop_words = [" NOT NULL", " NULL", " DEFAULT ", " PRIMARY KEY", " UNIQUE", " CHECK ", " COMMENT ", " REFERENCES "]
    stop_positions = [upper.find(word) for word in stop_words if upper.find(word) >= 0]
    type_end = min(stop_positions) if stop_positions else len(rest)
    data_type = rest[:type_end].strip()
    nullable = "not null" if re.search(r"\bnot\s+null\b", rest, re.IGNORECASE) else "nullable" if re.search(r"\bnull\b", rest, re.IGNORECASE) else "unknown"
    default_match = re.search(r"\bdefault\s+(.+?)(?:\s+not\s+null|\s+null|\s+primary\s+key|\s+unique|\s+check|\s+comment|\s+references|$)", rest, re.IGNORECASE)
    comment_match = MYSQL_COLUMN_COMMENT_RE.search(rest)
    comment = unescape_sql_string(comment_match.group("comment")) if comment_match else ""
    default = default_match.group(1).strip() if default_match else ""
    return Column(name=name, data_type=data_type, nullable=nullable, default=default, comment=comment, enum_hint=enum_hint_from_comment(comment))


def columns_from_group(value: str) -> list[str]:
    return [normalize_identifier(item.split()[0]) for item in split_csv(value)]


def get_or_create_table(tables: dict[str, Table], name: str, source: str) -> Table:
    norm = normalize_identifier(name)
    if norm not in tables:
        tables[norm] = Table(name=norm, source=source)
    return tables[norm]


def parse_create_table(sql: str, source: str, tables: dict[str, Table]) -> None:
    for match in CREATE_TABLE_RE.finditer(sql):
        table_name = normalize_identifier(match.group("name"))
        open_index = match.end() - 1
        close_index = find_matching_paren(sql, open_index)
        if close_index < 0:
            continue
        body = sql[open_index + 1 : close_index]
        tail = sql[close_index + 1 : close_index + 500]
        table = get_or_create_table(tables, table_name, source)
        table_comment_match = MYSQL_TABLE_COMMENT_RE.search(tail)
        if table_comment_match and not table.comment:
            table.comment = unescape_sql_string(table_comment_match.group("comment"))
        for item in split_csv(body):
            leading = item.strip().split(None, 1)[0].lower() if item.strip() else ""
            if leading in {"primary", "constraint"} and re.search(r"\bprimary\s+key\b", item, re.IGNORECASE):
                pk_match = re.search(r"primary\s+key\s*\((?P<columns>[^)]+)\)", item, re.IGNORECASE)
                if pk_match:
                    table.primary_key = columns_from_group(pk_match.group("columns"))
                continue
            if leading in {"foreign", "constraint"} and re.search(r"\bforeign\s+key\b", item, re.IGNORECASE):
                fk_match = re.search(
                    r"(?:constraint\s+(?P<constraint>[`\"\[\]\w.$]+)\s+)?foreign\s+key\s*\((?P<columns>[^)]+)\)\s+references\s+(?P<ref_table>[`\"\[\]\w.$]+)\s*\((?P<ref_columns>[^)]+)\)",
                    item,
                    re.IGNORECASE,
                )
                if fk_match:
                    table.foreign_keys.append(
                        ForeignKey(
                            name=normalize_identifier(fk_match.group("constraint") or ""),
                            columns=columns_from_group(fk_match.group("columns")),
                            ref_table=normalize_identifier(fk_match.group("ref_table")),
                            ref_columns=columns_from_group(fk_match.group("ref_columns")),
                        )
                    )
                continue
            if leading in {"unique", "key", "index", "constraint", "check"}:
                continue
            column = parse_column(item)
            if column:
                table.columns[column.name] = column
                if re.search(r"\bprimary\s+key\b", item, re.IGNORECASE) and column.name not in table.primary_key:
                    table.primary_key.append(column.name)


def apply_comments(sql: str, tables: dict[str, Table]) -> None:
    for match in TABLE_COMMENT_RE.finditer(sql):
        table = get_or_create_table(tables, match.group("table"), "")
        table.comment = unescape_sql_string(match.group("comment"))
    for match in COLUMN_COMMENT_RE.finditer(sql):
        table = get_or_create_table(tables, match.group("table"), "")
        column_name = normalize_identifier(match.group("column"))
        if column_name not in table.columns:
            table.columns[column_name] = Column(name=column_name)
        comment = unescape_sql_string(match.group("comment"))
        table.columns[column_name].comment = comment
        table.columns[column_name].enum_hint = enum_hint_from_comment(comment)


def apply_constraints(sql: str, tables: dict[str, Table]) -> None:
    for match in PK_ALTER_RE.finditer(sql):
        table = get_or_create_table(tables, match.group("table"), "")
        table.primary_key = columns_from_group(match.group("columns"))
    for match in FK_ALTER_RE.finditer(sql):
        table = get_or_create_table(tables, match.group("table"), "")
        table.foreign_keys.append(
            ForeignKey(
                name=normalize_identifier(match.group("constraint") or ""),
                columns=columns_from_group(match.group("columns")),
                ref_table=normalize_identifier(match.group("ref_table")),
                ref_columns=columns_from_group(match.group("ref_columns")),
            )
        )
    for match in INDEX_RE.finditer(sql):
        table = get_or_create_table(tables, match.group("table"), "")
        table.indexes.append(
            Index(
                name=normalize_identifier(match.group("name")),
                columns=columns_from_group(match.group("columns")),
                unique=bool(match.group("unique")),
            )
        )


def table_to_dict(table: Table) -> dict:
    return {
        "name": table.name,
        "comment": table.comment,
        "source": table.source,
        "columns": [
            {
                "name": column.name,
                "data_type": column.data_type,
                "nullable": column.nullable,
                "default": column.default,
                "comment": column.comment,
                "enum_hint": column.enum_hint,
            }
            for column in table.columns.values()
        ],
        "primary_key": table.primary_key,
        "foreign_keys": [
            {
                "name": item.name,
                "columns": item.columns,
                "ref_table": item.ref_table,
                "ref_columns": item.ref_columns,
            }
            for item in table.foreign_keys
        ],
        "indexes": [
            {
                "name": item.name,
                "columns": item.columns,
                "unique": item.unique,
            }
            for item in table.indexes
        ],
    }


def iter_sql_files(sql_root: Path) -> list[Path]:
    if not sql_root.exists():
        return []
    if sql_root.is_file() and sql_root.suffix.lower() in SQL_EXTENSIONS:
        return [sql_root]
    return sorted(
        [path for path in sql_root.rglob("*") if path.is_file() and path.suffix.lower() in SQL_EXTENSIONS],
        key=lambda item: item.as_posix().lower(),
    )


def build_digest(sql_root: Path, base: Path) -> dict:
    tables: dict[str, Table] = {}
    files = iter_sql_files(sql_root)
    for path in files:
        raw_sql = path.read_text(encoding="utf-8", errors="ignore")
        clean_sql = strip_comments(raw_sql)
        try:
            source = path.relative_to(base).as_posix()
        except ValueError:
            source = path.as_posix()
        parse_create_table(clean_sql, source, tables)
        apply_comments(clean_sql, tables)
        apply_constraints(clean_sql, tables)
    sorted_tables = sorted(tables.values(), key=lambda item: item.name.lower())
    return {
        "schema_version": 1,
        "sql_root": sql_root.as_posix(),
        "files": [path.relative_to(base).as_posix() if path.is_relative_to(base) else path.as_posix() for path in files],
        "table_count": len(sorted_tables),
        "tables": [table_to_dict(table) for table in sorted_tables],
    }


def write_markdown(digest: dict, path: Path) -> None:
    lines: list[str] = []
    lines.append("# SQL Schema Digest")
    lines.append("")
    lines.append(f"- SQL root: `{digest['sql_root']}`")
    lines.append(f"- SQL files: {len(digest['files'])}")
    lines.append(f"- Table count: {digest['table_count']}")
    lines.append("")
    if digest["files"]:
        lines.append("## Source Files")
        lines.append("")
        for file_name in digest["files"]:
            lines.append(f"- `{file_name}`")
        lines.append("")
    lines.append("## Tables")
    lines.append("")
    for table in digest["tables"]:
        title = table["name"]
        if table.get("comment"):
            title += f" - {table['comment']}"
        lines.append(f"### {title}")
        lines.append("")
        if table.get("primary_key"):
            lines.append(f"- Primary key: `{', '.join(table['primary_key'])}`")
        if table.get("indexes"):
            index_text = "; ".join(
                f"{'unique ' if index['unique'] else ''}{index['name']}({', '.join(index['columns'])})"
                for index in table["indexes"]
            )
            lines.append(f"- Indexes: {index_text}")
        if table.get("foreign_keys"):
            fk_text = "; ".join(
                f"{fk['name'] or '<unnamed>'}({', '.join(fk['columns'])}) -> {fk['ref_table']}({', '.join(fk['ref_columns'])})"
                for fk in table["foreign_keys"]
            )
            lines.append(f"- Foreign keys: {fk_text}")
        lines.append("")
        lines.append("| Column | Type | Nullable | Default | Comment | Enum hint |")
        lines.append("|---|---|---|---|---|---|")
        for column in table["columns"]:
            lines.append(
                "| {name} | {data_type} | {nullable} | {default} | {comment} | {enum_hint} |".format(
                    name=column["name"],
                    data_type=column["data_type"],
                    nullable=column["nullable"],
                    default=column["default"],
                    comment=column["comment"],
                    enum_hint=column["enum_hint"],
                )
            )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=".", help="Project root used for relative output paths.")
    parser.add_argument("--sql-root", default=".codex/model-implement/.sql", help="SQL file or directory to parse.")
    parser.add_argument("--json-output", default=".codex/model-implement/reports/init-airead/sql-schema-digest.json")
    parser.add_argument("--md-output", default=".codex/model-implement/reports/init-airead/sql-schema-digest.md")
    args = parser.parse_args()

    base = Path(args.base).resolve()
    sql_root = (base / args.sql_root).resolve() if not Path(args.sql_root).is_absolute() else Path(args.sql_root)
    digest = build_digest(sql_root, base)
    json_output = (base / args.json_output).resolve() if not Path(args.json_output).is_absolute() else Path(args.json_output)
    md_output = (base / args.md_output).resolve() if not Path(args.md_output).is_absolute() else Path(args.md_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(digest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(digest, md_output)
    print(f"Wrote {json_output}")
    print(f"Wrote {md_output}")
    print(f"SQL files: {len(digest['files'])}")
    print(f"Tables: {digest['table_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

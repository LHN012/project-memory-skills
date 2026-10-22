"""Shared, dependency-free helpers for the project memory SQLite index."""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sqlite3
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
SCRIPT_VERSION = "1.0.0"
SOURCE_ROOT = ".codex/memory"
DATABASE_FILE = ".codex/.knowledge/index.sqlite"
MODULE_AUDIT_FILE = ".audit.json"


def manifest_compatibility_error(manifest: dict[str, str]) -> str | None:
    expected = {
        "schema_version": str(SCHEMA_VERSION),
        "script_version": SCRIPT_VERSION,
        "source_root": SOURCE_ROOT,
        "database": DATABASE_FILE,
    }
    if not manifest:
        return "manifest_missing"
    for key, value in expected.items():
        if manifest.get(key) != value:
            return f"unsupported_manifest_{key}={manifest.get(key, 'missing')}"
    return None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_project_root(value: str | None = None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    # scripts/ -> .knowledge/ -> .codex/ -> project root
    return Path(__file__).resolve().parents[3]


def memory_root(project_root: Path) -> Path:
    return project_root / ".codex" / "memory"


def knowledge_root(project_root: Path) -> Path:
    return project_root / ".codex" / ".knowledge"


def database_path(project_root: Path) -> Path:
    return knowledge_root(project_root) / "index.sqlite"


def manifest_path(project_root: Path) -> Path:
    return knowledge_root(project_root) / "manifest.yaml"


def normalize_text(value: str) -> str:
    return value.replace("\r\n", "\n").replace("\r", "\n")


def sha256_text(value: str) -> str:
    return "sha256:" + hashlib.sha256(normalize_text(value).encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value or value in {"null", "~"}:
        return None
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except (SyntaxError, ValueError):
            pass
        return [part.strip().strip("'\"") for part in inner.split(",") if part.strip()]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any], str, bool]:
    lines = normalize_text(text).splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, normalize_text(text), False
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        return {}, normalize_text(text), False

    metadata: dict[str, Any] = {}
    active_list: str | None = None
    active_item: dict[str, Any] | None = None
    active_map: str | None = None
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        stripped = raw.strip()
        if indent == 0 and ":" in raw:
            key, value = raw.split(":", 1)
            key = key.strip()
            value = value.strip()
            active_list = None
            active_item = None
            active_map = None
            if value:
                metadata[key] = parse_scalar(value)
            elif key in {"evidence_sources", "impact_paths"}:
                metadata[key] = []
                active_list = key
            elif key == "relations":
                metadata[key] = {}
                active_map = key
            else:
                metadata[key] = None
            continue
        if active_list in {"evidence_sources", "impact_paths"} and stripped.startswith("-"):
            if active_list == "impact_paths":
                remainder = stripped[1:].strip()
                if remainder:
                    metadata[active_list].append(parse_scalar(remainder))
                continue
            active_item = {}
            metadata[active_list].append(active_item)
            remainder = stripped[1:].strip()
            if ":" in remainder:
                key, value = remainder.split(":", 1)
                active_item[key.strip()] = parse_scalar(value)
            continue
        if active_list == "evidence_sources" and active_item is not None and indent >= 4 and ":" in stripped:
            key, value = stripped.split(":", 1)
            active_item[key.strip()] = parse_scalar(value)
            continue
        if active_map == "relations" and indent >= 2 and ":" in stripped:
            key, value = stripped.split(":", 1)
            metadata[active_map][key.strip()] = parse_scalar(value)

    body = "\n".join(lines[end + 1:]).lstrip("\n")
    return metadata, body, True


def first_heading(body: str) -> str:
    for line in normalize_text(body).splitlines():
        match = re.match(r"^\s*#\s+(.+?)\s*$", line)
        if match:
            return match.group(1).strip()
    return ""


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def relative_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def module_audit_path(source_root: Path) -> Path:
    return source_root / "modules" / MODULE_AUDIT_FILE


def read_module_audit(source_root: Path) -> dict[str, Any]:
    path = module_audit_path(source_root)
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {}
    records = payload.get("records") if isinstance(payload, dict) else None
    return records if isinstance(records, dict) else {}


def load_record_metadata(path: Path, source_root: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    """Merge machine audit metadata without putting it in Markdown frontmatter."""
    merged = dict(metadata)
    try:
        record_path = relative_path(path, source_root)
    except ValueError:
        return merged
    if record_path.startswith("modules/") and path.name != "INDEX.md":
        audit = read_module_audit(source_root).get(record_path)
        if isinstance(audit, dict):
            for key, value in audit.items():
                if key not in {"memory_id", "type", "status", "coverage", "updated_at"}:
                    merged[key] = value
    return merged


def evidence_records(metadata: dict[str, Any], project_root: Path) -> list[dict[str, Any]]:
    records = metadata.get("evidence_sources") or []
    if not isinstance(records, list):
        return []
    result: list[dict[str, Any]] = []
    for item in records:
        if not isinstance(item, dict):
            continue
        record = dict(item)
        source_path = record.get("path")
        if source_path:
            candidate = Path(str(source_path))
            if not candidate.is_absolute():
                candidate = project_root / candidate
            if candidate.is_file():
                record["computed_hash"] = sha256_file(candidate)
        result.append(record)
    return result


PLAN_STATES = {"draft", "active", "blocked", "completed", "cancelled", "superseded"}
PLAN_FILENAME = re.compile(r"(\d{4}-\d{2}-\d{2})-v([1-9]\d*)\.md")


def plan_metadata(path: Path, source_root: Path, metadata: dict[str, Any]) -> dict[str, str] | None:
    """Derive index fields for requirement plans without expanding their headers."""
    if path.parent.resolve() != (source_root / "plans").resolve() or path.name == "INDEX.md":
        return None
    match = PLAN_FILENAME.fullmatch(path.name)
    if not match:
        # Preserve existing full-metadata documents outside the date-vN convention.
        if metadata.get("memory_id") and not metadata.get("plan_id"):
            return None
        raise ValueError(f"invalid_plan_filename:{path.name}")
    plan_id = str(metadata.get("plan_id") or "")
    if not re.fullmatch(r"PLAN-\d{8}-\d{3,}", plan_id):
        raise ValueError(f"invalid_plan_id:{path.name}")
    state = str(metadata.get("plan_state") or "")
    if state not in PLAN_STATES:
        raise ValueError(f"invalid_plan_state:{path.name}:{state}")
    updated = str(metadata.get("updated_at") or "")
    try:
        date.fromisoformat(match.group(1))
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated):
            raise ValueError(updated)
        date.fromisoformat(updated)
    except ValueError as exc:
        raise ValueError(f"invalid_plan_date:{path.name}") from exc
    supersedes = metadata.get("supersedes")
    if supersedes is not None and (
        not PLAN_FILENAME.fullmatch(str(supersedes)) or str(supersedes) == path.name
    ):
        raise ValueError(f"invalid_plan_supersedes:{path.name}")
    return {
        "memory_id": str(metadata.get("memory_id") or f"{plan_id}@{path.stem}"),
        "type": "plan",
        "scope": plan_id,
        "status": state,
        "metadata_state": "native",
        "updated_at": updated,
    }


def node_from_file(path: Path, project_root: Path, source_root: Path) -> dict[str, Any]:
    raw = normalize_text(path.read_text(encoding="utf-8"))
    metadata, body, has_frontmatter = parse_frontmatter(raw)
    metadata = load_record_metadata(path, source_root, metadata)
    plan = plan_metadata(path, source_root, metadata)
    if plan is not None:
        metadata.update(plan)
    source_file = relative_path(path, project_root)
    record_path = str(metadata.get("record_path") or relative_path(path, source_root))
    memory_id = str(metadata.get("memory_id") or "LEGACY-" + hashlib.sha256(source_file.encode("utf-8")).hexdigest()[:16])
    status = str(metadata.get("status") or "draft")
    metadata_state = str(metadata.get("metadata_state") or ("native" if has_frontmatter else "legacy"))
    title = str(metadata.get("title") or first_heading(body) or path.stem)
    aliases = as_list(metadata.get("aliases"))
    relations = metadata.get("relations") if isinstance(metadata.get("relations"), dict) else {}
    evidence = evidence_records(metadata, project_root)
    normalized_body = normalize_text(body).strip() + "\n"
    return {
        "memory_id": memory_id,
        "type": str(metadata.get("type") or "unknown"),
        "title": title,
        "status": status,
        "metadata_state": metadata_state,
        "scope": str(metadata.get("scope") or ""),
        "aliases": aliases,
        "record_path": record_path,
        "record_anchor": str(metadata.get("record_anchor") or ""),
        "parent_id": str(metadata.get("parent_id") or ""),
        "record_hash": sha256_text(normalized_body),
        "declared_record_hash": str(metadata.get("record_hash") or ""),
        "evidence": evidence,
        "relations": relations,
        "source_file": source_file,
        "source_hash": sha256_text(raw),
        "updated_at": str(metadata.get("updated_at") or utc_now()),
        "content": normalized_body,
    }


def read_manifest(project_root: Path) -> dict[str, str]:
    path = manifest_path(project_root)
    if not path.is_file():
        return {}
    result: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip("'\"")
    return result


def write_manifest(project_root: Path, values: dict[str, Any]) -> None:
    target = manifest_path(project_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = read_manifest(project_root)
    existing.update({key: str(value) if value is not None else "null" for key, value in values.items()})
    ordered = ["schema_version", "script_version", "corpus_version", "index_status", "source_root", "database", "last_build_at", "last_error"]
    lines = []
    for key in ordered:
        if key in existing:
            lines.append(f"{key}: {existing[key]}")
    for key, value in existing.items():
        if key not in ordered:
            lines.append(f"{key}: {value}")
    fd, temp_name = tempfile.mkstemp(prefix="manifest-", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write("\n".join(lines) + "\n")
        os.replace(temp_name, target)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def connect_database(project_root: Path, *, read_only: bool = False) -> tuple[sqlite3.Connection, bool]:
    path = database_path(project_root)
    existed = path.is_file()
    if read_only:
        if not path.is_file():
            raise FileNotFoundError(f"database_missing:{path}")
        conn = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    version = int(conn.execute("PRAGMA user_version").fetchone()[0])
    if read_only and version != SCHEMA_VERSION:
        conn.close()
        raise RuntimeError(f"unsupported_schema_version:{version}")
    if not read_only and existed and version != SCHEMA_VERSION:
        conn.close()
        raise RuntimeError(f"unsupported_existing_schema_version:{version}")
    if not read_only and not existed and version != 0:
        conn.close()
        raise RuntimeError(f"unsupported schema_version={version}; expected {SCHEMA_VERSION}")
    if read_only:
        required_tables = {
            "nodes": {"row_id", "memory_id", "type", "title", "status", "metadata_state", "scope", "aliases_json", "record_path", "record_anchor", "parent_id", "record_hash", "declared_record_hash", "evidence_json", "relations_json", "source_file", "source_hash", "updated_at", "content"},
            "relations": {"source_id", "relation", "target_id"},
        }
        for table, expected_columns in required_tables.items():
            row = conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)).fetchone()
            columns = {str(item[1]) for item in conn.execute(f"PRAGMA table_info([{table}])")}
            if row is None or columns != expected_columns:
                conn.close()
                raise RuntimeError(f"unsupported_table_schema:{table}")
        fts_row = conn.execute("SELECT type, sql FROM sqlite_master WHERE name = 'nodes_fts'").fetchone()
        if fts_row is None:
            return conn, False
        if fts_row[0] != "table" or "fts5" not in str(fts_row[1] or "").lower():
            conn.close()
            raise RuntimeError("unsupported_table_schema:nodes_fts")
        return conn, True
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS nodes (
            row_id INTEGER PRIMARY KEY,
            memory_id TEXT NOT NULL UNIQUE,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            metadata_state TEXT NOT NULL,
            scope TEXT NOT NULL,
            aliases_json TEXT NOT NULL,
            record_path TEXT NOT NULL,
            record_anchor TEXT NOT NULL,
            parent_id TEXT NOT NULL,
            record_hash TEXT NOT NULL,
            declared_record_hash TEXT NOT NULL,
            evidence_json TEXT NOT NULL,
            relations_json TEXT NOT NULL,
            source_file TEXT NOT NULL UNIQUE,
            source_hash TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            content TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS relations (
            source_id TEXT NOT NULL,
            relation TEXT NOT NULL,
            target_id TEXT NOT NULL,
            PRIMARY KEY (source_id, relation, target_id)
        );
        CREATE INDEX IF NOT EXISTS idx_nodes_status ON nodes(status);
        CREATE INDEX IF NOT EXISTS idx_nodes_scope ON nodes(scope);
        CREATE INDEX IF NOT EXISTS idx_nodes_parent ON nodes(parent_id);
        """
    )
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    fts = True
    try:
        conn.execute(
            """CREATE VIRTUAL TABLE IF NOT EXISTS nodes_fts USING fts5(
                memory_id UNINDEXED, title, aliases, scope, content
            )"""
        )
    except sqlite3.OperationalError:
        fts = False
    return conn, fts


def fts_delete(conn: sqlite3.Connection, memory_id: str, enabled: bool) -> None:
    if enabled:
        conn.execute("DELETE FROM nodes_fts WHERE memory_id = ?", (memory_id,))


def fts_insert(conn: sqlite3.Connection, node: dict[str, Any], enabled: bool) -> None:
    if enabled:
        conn.execute(
            "INSERT INTO nodes_fts(memory_id, title, aliases, scope, content) VALUES (?, ?, ?, ?, ?)",
            (node["memory_id"], node["title"], " ".join(node["aliases"]), node["scope"], node["content"]),
        )


def delete_source(
    conn: sqlite3.Connection,
    source_file: str,
    fts_enabled: bool,
    *,
    preserve_incoming: bool = False,
) -> int:
    ids = [row[0] for row in conn.execute("SELECT memory_id FROM nodes WHERE source_file = ?", (source_file,))]
    for memory_id in ids:
        fts_delete(conn, memory_id, fts_enabled)
        if preserve_incoming:
            # Replacing a node must keep relations owned by other source files.
            conn.execute("DELETE FROM relations WHERE source_id = ?", (memory_id,))
        else:
            conn.execute("DELETE FROM relations WHERE source_id = ? OR target_id = ?", (memory_id, memory_id))
    conn.execute("DELETE FROM nodes WHERE source_file = ?", (source_file,))
    return len(ids)


def upsert_node(conn: sqlite3.Connection, node: dict[str, Any], fts_enabled: bool) -> None:
    existing = conn.execute("SELECT source_file FROM nodes WHERE memory_id = ?", (node["memory_id"],)).fetchone()
    if existing and existing[0] != node["source_file"]:
        raise RuntimeError(f"duplicate memory_id={node['memory_id']} in {existing[0]} and {node['source_file']}")
    existing_source_ids = [
        row[0] for row in conn.execute(
            "SELECT memory_id FROM nodes WHERE source_file = ?", (node["source_file"],)
        )
    ]
    preserve_incoming = existing_source_ids == [node["memory_id"]]
    delete_source(
        conn,
        node["source_file"],
        fts_enabled,
        preserve_incoming=preserve_incoming,
    )
    fts_delete(conn, node["memory_id"], fts_enabled)
    conn.execute(
        """INSERT INTO nodes(
            memory_id, type, title, status, metadata_state, scope, aliases_json,
            record_path, record_anchor, parent_id, record_hash, declared_record_hash,
            evidence_json, relations_json, source_file, source_hash, updated_at, content
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(memory_id) DO UPDATE SET
            type=excluded.type, title=excluded.title, status=excluded.status,
            metadata_state=excluded.metadata_state, scope=excluded.scope,
            aliases_json=excluded.aliases_json, record_path=excluded.record_path,
            record_anchor=excluded.record_anchor, parent_id=excluded.parent_id,
            record_hash=excluded.record_hash, declared_record_hash=excluded.declared_record_hash,
            evidence_json=excluded.evidence_json, relations_json=excluded.relations_json,
            source_file=excluded.source_file, source_hash=excluded.source_hash,
            updated_at=excluded.updated_at, content=excluded.content""",
        (
            node["memory_id"], node["type"], node["title"], node["status"], node["metadata_state"],
            node["scope"], json.dumps(node["aliases"], ensure_ascii=False), node["record_path"],
            node["record_anchor"], node["parent_id"], node["record_hash"], node["declared_record_hash"],
            json.dumps(node["evidence"], ensure_ascii=False), json.dumps(node["relations"], ensure_ascii=False),
            node["source_file"], node["source_hash"], node["updated_at"], node["content"],
        ),
    )
    for relation, targets in node["relations"].items():
        if not isinstance(targets, list):
            targets = [targets]
        for target in targets:
            conn.execute(
                "INSERT OR IGNORE INTO relations(source_id, relation, target_id) VALUES (?, ?, ?)",
                (node["memory_id"], str(relation), str(target)),
            )
    fts_insert(conn, node, fts_enabled)


def json_node(row: sqlite3.Row) -> dict[str, Any]:
    result = dict(row)
    for key in ("aliases_json", "evidence_json", "relations_json"):
        source_key = key
        output_key = key.removesuffix("_json")
        try:
            result[output_key] = json.loads(result.pop(source_key))
        except (TypeError, json.JSONDecodeError):
            result[output_key] = [] if key != "relations_json" else {}
    if result["type"] == "plan" and re.fullmatch(r"PLAN-\d{8}-\d{3,}", result["scope"]):
        result["plan_id"] = result["scope"]
        result["plan_state"] = result["status"]
        match = PLAN_FILENAME.fullmatch(Path(result["record_path"]).name)
        if match:
            result["version_date"] = match.group(1)
            result["version"] = int(match.group(2))
    return result

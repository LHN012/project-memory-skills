"""Check the project memory SQLite/FTS5 index without changing Markdown."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from index_lib import (
    connect_database,
    database_path,
    manifest_compatibility_error,
    memory_root,
    node_from_file,
    read_manifest,
    resolve_project_root,
)


def main() -> int:
    project_root = resolve_project_root(sys.argv[sys.argv.index("--project-root") + 1] if "--project-root" in sys.argv else None)
    manifest = read_manifest(project_root)
    issues: list[str] = []
    warnings: list[str] = []
    compatibility_error = manifest_compatibility_error(manifest)
    if compatibility_error:
        issues.append(compatibility_error)
    if manifest.get("index_status") not in {"fresh", "sqlite-only"}:
        warnings.append(f"manifest_status:{manifest.get('index_status', 'missing')}")
    if not memory_root(project_root).is_dir():
        issues.append("source_root_missing")
    if not database_path(project_root).is_file():
        print(json.dumps({"status": "missing", "issues": ["database_missing"], "warnings": warnings}, ensure_ascii=False, indent=2))
        return 2
    try:
        conn, fts_enabled = connect_database(project_root, read_only=True)
    except Exception as exc:
        print(json.dumps({"status": "stale", "issues": [str(exc)], "warnings": warnings}, ensure_ascii=False, indent=2))
        return 1

    rows = conn.execute("SELECT * FROM nodes").fetchall()
    known_ids = {row["memory_id"] for row in rows}
    for row in rows:
        source = project_root / row["source_file"]
        if not source.is_file():
            issues.append(f"missing_source:{row['source_file']}")
            continue
        node = node_from_file(source, project_root, memory_root(project_root))
        if node["source_hash"] != row["source_hash"]:
            issues.append(f"source_hash_mismatch:{row['memory_id']}")
        if node["record_hash"] != row["record_hash"]:
            issues.append(f"record_hash_mismatch:{row['memory_id']}")
        if json.dumps(node["evidence"], ensure_ascii=False, sort_keys=True) != json.dumps(json.loads(row["evidence_json"]), ensure_ascii=False, sort_keys=True):
            issues.append(f"evidence_mismatch:{row['memory_id']}")
        if json.dumps(node["relations"], ensure_ascii=False, sort_keys=True) != json.dumps(json.loads(row["relations_json"]), ensure_ascii=False, sort_keys=True):
            issues.append(f"relations_mismatch:{row['memory_id']}")
        if row["parent_id"] and row["parent_id"] not in known_ids:
            issues.append(f"missing_parent:{row['memory_id']}->{row['parent_id']}")
    relation_rows = conn.execute("SELECT source_id, relation, target_id FROM relations").fetchall()
    for relation in relation_rows:
        if relation["source_id"] not in known_ids or relation["target_id"] not in known_ids:
            issues.append(f"missing_relation_target:{relation['source_id']}->{relation['target_id']}")
    if not fts_enabled:
        warnings.append("fts5_unavailable")
    indexed_count = len(rows)
    fts_count = conn.execute("SELECT COUNT(*) FROM nodes_fts").fetchone()[0] if fts_enabled else 0
    if fts_enabled and indexed_count != fts_count:
        issues.append(f"fts_count_mismatch:{indexed_count}!={fts_count}")
    conn.close()
    status = "fresh" if not issues else "stale"
    print(json.dumps({"status": status, "nodes": indexed_count, "fts5": fts_enabled, "issues": issues, "warnings": warnings}, ensure_ascii=False, indent=2))
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())

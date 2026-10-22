"""Query the project memory SQLite/FTS5 index and emit an evidence packet."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from index_lib import (
    connect_database,
    database_path,
    json_node,
    manifest_compatibility_error,
    read_manifest,
    resolve_project_root,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Query project memory with exact-first retrieval.")
    parser.add_argument("--project-root")
    parser.add_argument("--query", default="")
    parser.add_argument("--id", dest="memory_id", help="Exact memory_id or requirement plan_id.")
    parser.add_argument("--path", dest="source_path")
    parser.add_argument("--scope")
    parser.add_argument("--status", action="append", default=[])
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--include-deprecated", action="store_true")
    parser.add_argument("--include-audit", action="store_true", help="Include machine audit metadata in each result.")
    return parser.parse_args()


def output(payload: dict) -> int:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def compact_node(node: dict) -> dict:
    """Return readable retrieval metadata; audit fields stay opt-in."""
    keep = {
        "memory_id", "type", "title", "status", "scope", "aliases",
        "record_path", "parent_id", "updated_at", "content", "plan_id",
        "plan_state", "version_date", "version",
    }
    return {key: value for key, value in node.items() if key in keep}


def main() -> int:
    args = parse_args()
    if not args.query and not args.memory_id and not args.source_path:
        return output({"status": "missing", "reason": "query_or_id_or_path_required"})
    project_root = resolve_project_root(args.project_root)
    manifest = read_manifest(project_root)
    compatibility_error = manifest_compatibility_error(manifest)
    if compatibility_error:
        return output({"status": "fallback_required", "reason": compatibility_error})
    if not database_path(project_root).is_file():
        return output({"status": "fallback_required", "reason": "database_missing"})
    if manifest.get("index_status") not in {"fresh", "sqlite-only"}:
        return output({"status": "fallback_required", "reason": manifest.get("index_status", "manifest_missing")})

    try:
        conn, fts_enabled = connect_database(project_root, read_only=True)
    except Exception as exc:
        return output({"status": "fallback_required", "reason": str(exc)})

    conditions = []
    params: list[str] = []
    mode = "exact"
    if args.memory_id:
        conditions.append("(n.memory_id = ? OR (n.type = 'plan' AND n.scope = ?))")
        params.extend([args.memory_id, args.memory_id])
    elif args.source_path:
        conditions.append("(n.source_file = ? OR n.record_path = ?)")
        params.extend([args.source_path.replace("\\", "/"), args.source_path.replace("\\", "/")])
    elif args.query:
        mode = "fts" if fts_enabled else "text"
    if args.scope:
        conditions.append("n.scope = ?")
        params.append(args.scope)
    statuses = args.status or ["draft", "derived", "verified", "legacy", "active", "blocked", "completed"]
    if args.include_deprecated and not args.status:
        statuses += ["deprecated", "cancelled", "superseded"]
    placeholders = ",".join("?" for _ in statuses)
    conditions.append(f"n.status IN ({placeholders})")
    params.extend(statuses)
    where = " AND ".join(conditions)
    limit = max(1, min(args.limit, 50))

    rows = []
    if args.query and fts_enabled:
        tokens = re.findall(r"[\w\-]+", args.query, flags=re.UNICODE)
        if tokens:
            match = " AND ".join('"' + token.replace('"', '""') + '"' for token in tokens[:12])
            sql = f"SELECT n.* FROM nodes_fts JOIN nodes n ON n.memory_id = nodes_fts.memory_id WHERE nodes_fts MATCH ? AND {where} ORDER BY bm25(nodes_fts) LIMIT ?"
            rows = conn.execute(sql, [match, *params, limit]).fetchall()
    if args.query and not rows and args.query:
        mode = "text"
        like = f"%{args.query}%"
        sql = f"SELECT n.* FROM nodes n WHERE (n.title LIKE ? OR n.aliases_json LIKE ? OR n.scope LIKE ? OR n.content LIKE ?) AND {where} ORDER BY n.updated_at DESC LIMIT ?"
        rows = conn.execute(sql, [like, like, like, like, *params, limit]).fetchall()
    elif not args.query:
        sql = f"SELECT n.* FROM nodes n WHERE {where} ORDER BY n.updated_at DESC LIMIT ?"
        rows = conn.execute(sql, [*params, limit]).fetchall()

    results = [json_node(row) for row in rows]
    parent_ids = [item["parent_id"] for item in results if item.get("parent_id")]
    parents = []
    if parent_ids:
        placeholders = ",".join("?" for _ in parent_ids[:3])
        parent_rows = conn.execute(f"SELECT * FROM nodes WHERE memory_id IN ({placeholders})", parent_ids[:3]).fetchall()
        parents = [json_node(row) for row in parent_rows]
    relations = []
    related_nodes = []
    if results:
        ids = [item["memory_id"] for item in results[:limit]]
        placeholders = ",".join("?" for _ in ids)
        relation_rows = conn.execute(
            f"SELECT source_id, relation, target_id FROM relations "
            f"WHERE source_id IN ({placeholders}) OR target_id IN ({placeholders}) LIMIT 3",
            [*ids, *ids],
        ).fetchall()
        relations = [dict(row) for row in relation_rows]
        related_ids = {
            target
            for row in relation_rows
            for target in (row["source_id"], row["target_id"])
            if target not in ids
        }
        if related_ids:
            selected_related_ids = sorted(related_ids)[:3]
            related_placeholders = ",".join("?" for _ in selected_related_ids)
            related_rows = conn.execute(
                f"SELECT * FROM nodes WHERE memory_id IN ({related_placeholders}) LIMIT 3",
                selected_related_ids,
            ).fetchall()
            related_nodes = [json_node(row) for row in related_rows]
    if not args.include_audit:
        results = [compact_node(item) for item in results]
        parents = [compact_node(item) for item in parents]
        related_nodes = [compact_node(item) for item in related_nodes]
    conn.close()
    return output({
        "status": "ok" if results else "missing",
        "mode": mode,
        "index_status": manifest.get("index_status"),
        "corpus_version": manifest.get("corpus_version"),
        "results": results,
        "parents": parents,
        "relations": relations,
        "related": related_nodes,
        "conflicts": [],
        "missing": [] if results else [args.query or args.memory_id or args.source_path],
    })


if __name__ == "__main__":
    sys.exit(main())

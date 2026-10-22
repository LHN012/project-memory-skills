"""Build or incrementally update the project memory SQLite/FTS5 index."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from index_lib import (
    SCRIPT_VERSION,
    connect_database,
    delete_source,
    memory_root,
    manifest_compatibility_error,
    node_from_file,
    read_manifest,
    relative_path,
    resolve_project_root,
    utc_now,
    upsert_node,
    write_manifest,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Markdown project memory into SQLite/FTS5.")
    parser.add_argument("--project-root", help="Project directory; defaults to the template-derived root.")
    parser.add_argument("--changed", nargs="*", default=[], help="Changed paths, relative to the project or memory root.")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild all derived nodes from Markdown.")
    return parser.parse_args()


def resolve_changed(value: str, project_root: Path, source_root: Path) -> Path:
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.resolve()
    project_candidate = (project_root / candidate).resolve()
    if project_candidate.exists() or str(candidate).startswith(".codex"):
        return project_candidate
    return (source_root / candidate).resolve()


def main() -> int:
    args = parse_args()
    project_root = resolve_project_root(args.project_root)
    source_root = memory_root(project_root)
    if not source_root.is_dir():
        write_manifest(project_root, {"script_version": SCRIPT_VERSION, "index_status": "missing", "last_error": "source_root_missing"})
        print('{"status":"missing","reason":"source_root_missing"}')
        return 2

    manifest = read_manifest(project_root)
    compatibility_error = manifest_compatibility_error(manifest)
    if compatibility_error:
        print(json.dumps({"status": "stale", "reason": compatibility_error}, ensure_ascii=False))
        return 3

    try:
        conn, fts_enabled = connect_database(project_root)
        conn.execute("BEGIN IMMEDIATE")
        all_files = {relative_path(path, project_root): path for path in source_root.rglob("*.md") if path.name != "INDEX.md"}
        if args.rebuild or not args.changed:
            changed_files = list(all_files.values())
        else:
            changed_files = [resolve_changed(item, project_root, source_root) for item in args.changed]

        updated = 0
        removed = 0
        for path in changed_files:
            source_file = relative_path(path, project_root)
            if not path.is_file() or path.name == "INDEX.md":
                removed += delete_source(conn, source_file, fts_enabled)
                continue
            node = node_from_file(path, project_root, source_root)
            upsert_node(conn, node, fts_enabled)
            updated += 1

        if args.rebuild or not args.changed:
            indexed = {row[0] for row in conn.execute("SELECT source_file FROM nodes")}
            for source_file in indexed - set(all_files):
                removed += delete_source(conn, source_file, fts_enabled)

        conn.commit()
        conn.close()
        old_version = int(manifest.get("corpus_version", "0") or 0)
        write_manifest(
            project_root,
            {
                "script_version": SCRIPT_VERSION,
                "corpus_version": old_version + 1,
                "index_status": "fresh" if fts_enabled else "sqlite-only",
                "last_build_at": utc_now(),
                "last_error": "null",
            },
        )
        print(f'{{"status":"fresh","fts5":{str(fts_enabled).lower()},"updated":{updated},"removed":{removed}}}')
        return 0
    except Exception as exc:
        try:
            conn.rollback()
            conn.close()
        except Exception:
            pass
        write_manifest(project_root, {"script_version": SCRIPT_VERSION, "index_status": "stale", "last_error": str(exc)})
        print(json.dumps({"status": "stale", "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""Check project memory file placement and stable identifiers without changing files."""

from __future__ import annotations

import json
import sys
from collections import defaultdict

from index_lib import load_record_metadata, memory_root, node_from_file, parse_frontmatter, relative_path, resolve_project_root


def main() -> int:
    project_root = resolve_project_root(
        sys.argv[sys.argv.index("--project-root") + 1] if "--project-root" in sys.argv else None
    )
    root = memory_root(project_root)
    issues: list[str] = []
    warnings: list[str] = []
    if not root.is_dir():
        print(
            json.dumps(
                {"status": "missing", "issues": ["memory_root_missing"], "warnings": []},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    root_files = [path for path in root.iterdir() if path.is_file() and path.name != "INDEX.md"]
    issues.extend(f"memory_root_file:{relative_path(path, project_root)}" for path in root_files)

    library = root / "library"
    if library.is_dir():
        library_root_files = [path for path in library.iterdir() if path.is_file() and path.name != "INDEX.md"]
        issues.extend(f"library_root_file:{relative_path(path, project_root)}" for path in library_root_files)

    modules = root / "modules"
    if modules.is_dir():
        for path in modules.iterdir():
            if not path.is_file() or path.name == "INDEX.md" or path.suffix.lower() != ".md":
                continue
            try:
                metadata, _, _ = parse_frontmatter(path.read_text(encoding="utf-8"))
            except (OSError, UnicodeError) as exc:
                issues.append(f"unreadable_module_record:{relative_path(path, project_root)}:{exc}")
                continue
            metadata = load_record_metadata(path, root, metadata)
            record_level = str(metadata.get("record_level") or "").lower()
            record_type = str(metadata.get("type") or "").lower()
            if record_level == "page" or record_type == "page":
                issues.append(f"page_record_must_be_nested:{relative_path(path, project_root)}")

    ids: dict[str, list[str]] = defaultdict(list)
    records = 0
    for path in root.rglob("*.md"):
        if path.name == "INDEX.md":
            continue
        records += 1
        try:
            node = node_from_file(path, project_root, root)
        except (OSError, UnicodeError, ValueError) as exc:
            issues.append(f"unreadable_record:{relative_path(path, project_root)}:{exc}")
            continue
        ids[node["memory_id"]].append(relative_path(path, project_root))
        declared_path = node.get("record_path")
        actual_path = relative_path(path, root)
        if declared_path and declared_path != actual_path:
            issues.append(f"record_path_mismatch:{relative_path(path, project_root)}->{declared_path}")

    for memory_id, paths in ids.items():
        if len(paths) > 1:
            issues.append(f"duplicate_memory_id:{memory_id}:{','.join(paths)}")

    status = "fresh" if not issues else "stale"
    print(
        json.dumps(
            {"status": status, "records": records, "issues": issues, "warnings": warnings},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if not issues else 1


if __name__ == "__main__":
    sys.exit(main())

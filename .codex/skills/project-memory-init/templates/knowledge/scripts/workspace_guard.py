"""Audit project-memory work for writes outside the declared allowlist.

The guard is intentionally read-only during audit. It never removes files or
directories; an unauthorized change is reported for human review.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ALLOWED_ROOTS = (
    ".codex/memory",
    ".codex/.knowledge",
    ".codex/.runtime",
)
READ_ONLY_ROOTS = (".codex/source-materials",)
EXCLUDED_ROOTS = (".git",)
INIT_ALLOWED_FILES = ("AGENTS.md",)


def resolve_project_root(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    # scripts/ -> .knowledge/ -> .codex/ -> project root
    return Path(__file__).resolve().parents[3]


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def relative_path(path: Path, project_root: Path) -> str:
    # Keep symlink paths lexical so scanning a link cannot escape the project root.
    return Path(os.path.relpath(os.path.abspath(path), os.path.abspath(project_root))).as_posix()


def path_in_roots(path: Path, project_root: Path, roots: tuple[str, ...]) -> bool:
    return any(is_within(path, project_root / root) for root in roots)


def is_init_allowed_file(path: Path, project_root: Path, allow_project_instructions: bool) -> bool:
    if not allow_project_instructions:
        return False
    try:
        return relative_path(path, project_root) in INIT_ALLOWED_FILES
    except ValueError:
        return False


def is_excluded(relative: str) -> bool:
    return any(relative == root or relative.startswith(root + "/") for root in EXCLUDED_ROOTS)


def scan(project_root: Path) -> dict[str, dict[str, int | str]]:
    entries: dict[str, dict[str, int | str]] = {}
    if not project_root.is_dir():
        return entries
    for current, dirs, files in os.walk(project_root, topdown=True, followlinks=False):
        current_path = Path(current)
        dirs[:] = [name for name in dirs if not is_excluded(relative_path(current_path / name, project_root))]
        for name in [*dirs, *files]:
            path = current_path / name
            relative = relative_path(path, project_root)
            if is_excluded(relative):
                continue
            try:
                stat = path.lstat()
            except OSError:
                continue
            kind = "symlink" if path.is_symlink() else ("dir" if path.is_dir() else "file")
            entries[relative] = {
                "kind": kind,
                "size": int(stat.st_size),
                "mtime_ns": int(stat.st_mtime_ns),
            }
    return entries


def write_snapshot(path: Path, project_root: Path) -> None:
    payload = {
        "schema": 1,
        "project_root": str(project_root),
        "created_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "entries": scan(project_root),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def read_snapshot(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != 1 or not isinstance(payload.get("entries"), dict):
        raise ValueError("unsupported_snapshot_schema")
    return payload


def audit(snapshot_path: Path, project_root: Path, allow_project_instructions: bool = False) -> dict:
    before = read_snapshot(snapshot_path)
    before_entries = before["entries"]
    after_entries = scan(project_root)
    changed = []
    for relative in sorted(set(before_entries) | set(after_entries)):
        old = before_entries.get(relative)
        new = after_entries.get(relative)
        if old == new:
            continue
        change = "added" if old is None else "deleted" if new is None else "modified"
        target = project_root / Path(relative)
        allowed = path_in_roots(target, project_root, ALLOWED_ROOTS) or is_init_allowed_file(
            target, project_root, allow_project_instructions
        )
        read_only = path_in_roots(target, project_root, READ_ONLY_ROOTS)
        changed.append({
            "path": relative,
            "change": change,
            "allowed": allowed and not read_only,
            "read_only": read_only,
        })
    unauthorized = [item for item in changed if not item["allowed"]]
    return {
        "status": "fresh" if not unauthorized else "blocked",
        "snapshot": str(snapshot_path),
        "changed": changed,
        "unauthorized": unauthorized,
        "allowed_roots": list(ALLOWED_ROOTS),
        "init_allowed_files": list(INIT_ALLOWED_FILES) if allow_project_instructions else [],
        "read_only_roots": list(READ_ONLY_ROOTS),
    }


def check_write(target_value: str, project_root: Path, allow_project_instructions: bool = False) -> dict:
    target = Path(target_value).expanduser()
    if not target.is_absolute():
        target = project_root / target
    target = target.resolve(strict=False)
    relative = None
    try:
        relative = relative_path(target, project_root)
    except ValueError:
        pass
    allowed = path_in_roots(target, project_root, ALLOWED_ROOTS) or is_init_allowed_file(
        target, project_root, allow_project_instructions
    )
    read_only = path_in_roots(target, project_root, READ_ONLY_ROOTS)
    result = {
        "status": "allowed" if allowed and not read_only else "blocked",
        "path": str(target),
        "relative_path": relative,
        "allowed_roots": list(ALLOWED_ROOTS),
        "init_allowed_files": list(INIT_ALLOWED_FILES) if allow_project_instructions else [],
        "read_only": read_only,
    }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit project-memory workspace side effects.")
    parser.add_argument("--project-root")
    parser.add_argument(
        "--allow-project-instructions",
        action="store_true",
        help="Allow the initialization-only project AGENTS.md file.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    snapshot = subparsers.add_parser("snapshot", help="Write a read-only workspace snapshot.")
    snapshot.add_argument("--output", required=True)
    audit_parser = subparsers.add_parser("audit", help="Compare the workspace with a snapshot.")
    audit_parser.add_argument("--before", required=True)
    write_parser = subparsers.add_parser("check-write", help="Validate one write target.")
    write_parser.add_argument("--path", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = resolve_project_root(args.project_root)
    if args.command == "snapshot":
        output = Path(args.output).expanduser().resolve()
        temp_root = Path(tempfile.gettempdir()).resolve()
        if is_within(output, project_root) and not path_in_roots(output, project_root, ALLOWED_ROOTS):
            print(json.dumps({"status": "blocked", "reason": "snapshot_output_outside_allowlist"}, ensure_ascii=False))
            return 2
        if not is_within(output, project_root) and not is_within(output, temp_root):
            print(json.dumps({"status": "blocked", "reason": "snapshot_output_must_be_project_allowlist_or_temp"}, ensure_ascii=False))
            return 2
        write_snapshot(output, project_root)
        print(json.dumps({"status": "ok", "snapshot": str(output)}, ensure_ascii=False))
        return 0
    if args.command == "audit":
        try:
            result = audit(
                Path(args.before).expanduser().resolve(),
                project_root,
                allow_project_instructions=args.allow_project_instructions,
            )
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(json.dumps({"status": "blocked", "reason": str(exc)}, ensure_ascii=False))
            return 2
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] == "fresh" else 1
    result = check_write(args.path, project_root, allow_project_instructions=args.allow_project_instructions)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "allowed" else 1


if __name__ == "__main__":
    sys.exit(main())

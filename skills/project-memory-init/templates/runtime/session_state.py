"""Save and restore a small project-local session checkpoint.

This file stores operational state only. It is not part of project memory and
must never be indexed as an authoritative fact.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1


def project_root(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name == "skills":
            return parent.parent
    raise RuntimeError("project_root_required")


def state_path(root: Path) -> Path:
    return root / ".runtime" / "session-state.json"


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_state(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return value if isinstance(value, dict) else None


def values(items: list[str] | None) -> list[str]:
    return [item for item in (items or []) if item.strip()]


def save(args: argparse.Namespace) -> int:
    root = project_root(args.project_root)
    path = state_path(root)
    previous = read_state(path) or {}
    state = {
        "schema_version": SCHEMA_VERSION,
        "session_id": args.session_id or previous.get("session_id") or str(uuid.uuid4()),
        "goal": args.goal if args.goal is not None else previous.get("goal", ""),
        "last_completed_step": args.step if args.step is not None else previous.get("last_completed_step", ""),
        "changed_files": values(args.changed) or previous.get("changed_files", []),
        "tests_run": values(args.test) or previous.get("tests_run", []),
        "pending_decisions": values(args.pending_decision) or previous.get("pending_decisions", []),
        "pending_memory_updates": values(args.pending_memory) or previous.get("pending_memory_updates", []),
        "updated_at": now(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="session-state-", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(json.dumps({"status": "saved", "path": str(path), "state": state}, ensure_ascii=False, indent=2))
    return 0


def show(args: argparse.Namespace) -> int:
    path = state_path(project_root(args.project_root))
    state = read_state(path)
    print(json.dumps({"status": "ok" if state else "missing", "path": str(path), "state": state}, ensure_ascii=False, indent=2))
    return 0 if state else 2


def clear(args: argparse.Namespace) -> int:
    path = state_path(project_root(args.project_root))
    if path.is_file():
        path.unlink()
    print(json.dumps({"status": "cleared", "path": str(path)}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage a project-local session checkpoint.")
    parser.add_argument("--project-root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    save_parser = subparsers.add_parser("save")
    save_parser.add_argument("--session-id")
    save_parser.add_argument("--goal")
    save_parser.add_argument("--step")
    save_parser.add_argument("--changed", action="append")
    save_parser.add_argument("--test", action="append")
    save_parser.add_argument("--pending-decision", action="append")
    save_parser.add_argument("--pending-memory", action="append")
    save_parser.set_defaults(handler=save)

    show_parser = subparsers.add_parser("show")
    show_parser.set_defaults(handler=show)

    clear_parser = subparsers.add_parser("clear")
    clear_parser.set_defaults(handler=clear)

    args = parser.parse_args()
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())

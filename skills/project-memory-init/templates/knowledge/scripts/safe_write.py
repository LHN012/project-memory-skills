"""Atomically write a Markdown memory file under memory only."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from workspace_guard import is_within, resolve_project_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safely write one project-memory Markdown file.")
    parser.add_argument("--project-root")
    parser.add_argument("--path", required=True, help="Path relative to the project root or an absolute path.")
    parser.add_argument("--content-file", help="Read UTF-8 content from a file; otherwise read stdin.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = resolve_project_root(args.project_root)
    target = Path(args.path).expanduser()
    if not target.is_absolute():
        target = project_root / target
    target = target.resolve(strict=False)
    memory_root = (project_root / "memory").resolve()
    if not is_within(target, memory_root) or target.suffix.lower() != ".md":
        print("blocked: target must be a Markdown file under memory", file=sys.stderr)
        return 2
    if target.exists() and target.is_dir():
        print("blocked: target is a directory", file=sys.stderr)
        return 2
    if args.content_file:
        content = Path(args.content_file).read_text(encoding="utf-8")
    else:
        content = sys.stdin.read()
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="memory-", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content.replace("\r\n", "\n").replace("\r", "\n"))
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print(f"written: {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

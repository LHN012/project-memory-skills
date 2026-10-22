"""Create or update the project-level AGENTS.md managed block."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path


BEGIN = "<!-- BEGIN CODEX PROJECT MEMORY MANAGED BLOCK -->"
END = "<!-- END CODEX PROJECT MEMORY MANAGED BLOCK -->"


def resolve_project_root(value: str | None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    return Path.cwd().resolve()


def template_path() -> Path:
    return Path(__file__).resolve().parents[1] / "templates" / "AGENTS.md"


def read_template() -> tuple[str, str]:
    content = template_path().read_text(encoding="utf-8")
    if BEGIN not in content or END not in content:
        raise ValueError("agents_template_markers_missing")
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    begin = normalized.index(BEGIN)
    end = normalized.index(END, begin) + len(END)
    heading = normalized[:begin].strip()
    managed_block = normalized[begin:end].strip()
    return heading, managed_block


def merge_content(existing: str, heading: str, managed_block: str) -> tuple[str, str]:
    normalized = existing.replace("\r\n", "\n").replace("\r", "\n")
    begin_count = normalized.count(BEGIN)
    end_count = normalized.count(END)
    if begin_count != end_count or begin_count > 1:
        raise ValueError("existing_agents_managed_block_invalid")
    if begin_count == 1:
        pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.DOTALL)
        merged = pattern.sub(managed_block, normalized, count=1)
        return merged.rstrip() + "\n", "updated"
    if not normalized.strip():
        return heading.rstrip() + "\n\n" + managed_block + "\n", "created"
    document = heading.rstrip() + "\n\n" + managed_block
    return normalized.rstrip() + "\n\n" + document + "\n", "appended"


def atomic_write(target: Path, content: str) -> None:
    fd, temporary = tempfile.mkstemp(prefix="agents-", suffix=".tmp", dir=str(target.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the project-memory AGENTS.md managed block.")
    parser.add_argument("--project-root", help="Project directory; defaults to the current directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = resolve_project_root(args.project_root)
    if not project_root.is_dir():
        print(json.dumps({"status": "blocked", "reason": "project_root_missing"}, ensure_ascii=False))
        return 2
    target = project_root / "AGENTS.md"
    try:
        heading, managed_block = read_template()
        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        merged, action = merge_content(existing, heading, managed_block)
        if not target.exists() or target.read_text(encoding="utf-8") != merged:
            atomic_write(target, merged)
            changed = True
        else:
            changed = False
    except (OSError, UnicodeError, ValueError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc), "path": str(target)}, ensure_ascii=False))
        return 2
    print(json.dumps({"status": "fresh", "action": action, "changed": changed, "path": str(target)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

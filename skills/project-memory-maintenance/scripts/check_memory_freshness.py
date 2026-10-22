"""Run the project-memory freshness checker without requiring SQLite/FTS5."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


def resolve_checker() -> Path:
    project_root = Path.cwd().resolve()
    if "--project-root" in sys.argv:
        index = sys.argv.index("--project-root")
        if index + 1 < len(sys.argv):
            project_root = Path(sys.argv[index + 1]).expanduser().resolve()
    candidates = [
        project_root / ".knowledge" / "scripts" / "check_memory_freshness.py",
        project_root
        / "skills"
        / "project-memory-init"
        / "templates"
        / "knowledge"
        / "scripts"
        / "check_memory_freshness.py",
    ]
    for candidate in candidates:
        if candidate.is_file() and candidate.resolve() != Path(__file__).resolve():
            return candidate.resolve()
    raise FileNotFoundError("check_memory_freshness.py is not installed in the project")


def main() -> None:
    checker = resolve_checker()
    checker_dir = str(checker.parent)
    sys.path.insert(0, checker_dir)
    runpy.run_path(str(checker), run_name="__main__")


if __name__ == "__main__":
    main()

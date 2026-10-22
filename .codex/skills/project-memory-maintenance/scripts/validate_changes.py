"""Validate the date-partitioned project-memory changes JSONL log."""

from __future__ import annotations

import argparse
import json
import sys

from changes_lib import changes_root, validate_all, resolve_project_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate project-memory changes JSONL files.")
    parser.add_argument("--project-root", help="Project directory; defaults to the current skill's project root.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = resolve_project_root(args.project_root)
    errors, ids = validate_all(project_root)
    payload = {
        "status": "fresh" if not errors else "stale",
        "root": changes_root(project_root).as_posix(),
        "records": len(ids),
        "errors": errors,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())

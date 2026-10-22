"""Append one validated record to the date-partitioned changes JSONL log."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from changes_lib import changes_root, parse_iso_timestamp, validate_all, validate_record, resolve_project_root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append one project-memory changes JSONL record.")
    parser.add_argument("--project-root", help="Project directory; defaults to the current skill's project root.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--record-file", help="UTF-8 JSON file containing one record.")
    source.add_argument("--record-json", help="One JSON object supplied as a command-line value.")
    return parser.parse_args()


def load_record(args: argparse.Namespace) -> dict:
    if args.record_file:
        raw = Path(args.record_file).expanduser().read_text(encoding="utf-8")
    else:
        raw = args.record_json
    record = json.loads(raw)
    if not isinstance(record, dict):
        raise ValueError("record must be a JSON object")
    return record


def main() -> int:
    args = parse_args()
    try:
        project_root = resolve_project_root(args.project_root)
        record = load_record(args)
        timestamp = record.get("timestamp")
        if not isinstance(timestamp, str):
            raise ValueError("timestamp must be a non-empty string")
        event_date = parse_iso_timestamp(timestamp).date()
        errors = validate_record(record, event_date)
        if errors:
            raise ValueError("; ".join(errors))

        existing_errors, existing_ids = validate_all(project_root)
        if existing_errors:
            raise ValueError("existing changes log is invalid: " + " | ".join(existing_errors))
        change_id = record["change_id"]
        if change_id in existing_ids:
            raise ValueError(f"duplicate change_id: {change_id}")

        root = changes_root(project_root)
        root.mkdir(parents=True, exist_ok=True)
        target = root / f"{event_date.isoformat()}.jsonl"
        needs_separator = target.exists() and target.stat().st_size > 0 and not target.read_bytes().endswith(b"\n")
        serialized = json.dumps(record, ensure_ascii=False, separators=(",", ":"))
        with target.open("a", encoding="utf-8", newline="\n") as handle:
            if needs_separator:
                handle.write("\n")
            handle.write(serialized)
            handle.write("\n")

        written_errors, _ = validate_all(project_root)
        if written_errors:
            print(json.dumps({"status": "invalid_after_write", "errors": written_errors}, ensure_ascii=False))
            return 1
        print(json.dumps({"status": "written", "path": target.as_posix(), "change_id": change_id}, ensure_ascii=False))
        return 0
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

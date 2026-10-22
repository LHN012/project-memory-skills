"""Shared validation helpers for the date-partitioned changes JSONL log."""

from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable


REQUIRED_FIELDS = ("change_id", "timestamp", "issue", "observation")
CHANGE_ID_RE = re.compile(r"^CHG-(\d{8})-(\d{3})$")
ISSUE_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
DATE_FILE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\.jsonl$")


def resolve_project_root(value: str | None = None) -> Path:
    if value:
        return Path(value).expanduser().resolve()
    current = Path(__file__).resolve()
    for parent in current.parents:
        if parent.name in {"skills", ".knowledge"}:
            return parent.parent
    raise RuntimeError("project_root_required")


def changes_root(project_root: Path) -> Path:
    return (project_root / "memory" / "changes").resolve()


def parse_iso_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    if "T" not in value:
        raise ValueError("timestamp must use ISO-8601 date-time form with T")
    return parsed


def file_date(path: Path) -> date:
    if not DATE_FILE_RE.fullmatch(path.name):
        raise ValueError("file name must match YYYY-MM-DD.jsonl")
    return date.fromisoformat(path.stem)


def validate_record(record: Any, expected_date: date | None = None) -> list[str]:
    errors: list[str] = []
    if not isinstance(record, dict):
        return ["record must be a JSON object"]

    actual_fields = set(record)
    required_fields = set(REQUIRED_FIELDS)
    missing = sorted(required_fields - actual_fields)
    extra = sorted(actual_fields - required_fields)
    if missing:
        errors.append(f"missing fields: {', '.join(missing)}")
    if extra:
        errors.append(f"unsupported fields: {', '.join(extra)}")

    change_id = record.get("change_id")
    if not isinstance(change_id, str) or not CHANGE_ID_RE.fullmatch(change_id):
        errors.append("change_id must match CHG-YYYYMMDD-NNN")

    timestamp = record.get("timestamp")
    parsed_timestamp: datetime | None = None
    if not isinstance(timestamp, str) or not timestamp:
        errors.append("timestamp must be a non-empty string")
    else:
        try:
            parsed_timestamp = parse_iso_timestamp(timestamp)
        except ValueError as exc:
            errors.append(str(exc))

    issue = record.get("issue")
    if not isinstance(issue, str) or not ISSUE_RE.fullmatch(issue):
        errors.append("issue must use lowercase snake_case")

    observation = record.get("observation")
    if not isinstance(observation, str) or not observation.strip():
        errors.append("observation must be a non-empty string")

    if expected_date is not None and parsed_timestamp is not None:
        if parsed_timestamp.date() != expected_date:
            errors.append(
                f"timestamp date {parsed_timestamp.date().isoformat()} does not match "
                f"file date {expected_date.isoformat()}"
            )

    if isinstance(change_id, str):
        match = CHANGE_ID_RE.fullmatch(change_id)
        if match and expected_date is not None:
            try:
                id_date = date(
                    int(match.group(1)[:4]), int(match.group(1)[4:6]), int(match.group(1)[6:8])
                )
            except ValueError:
                errors.append("change_id contains an invalid calendar date")
            else:
                if id_date != expected_date:
                    errors.append(
                        f"change_id date {id_date.isoformat()} does not match file date "
                        f"{expected_date.isoformat()}"
                    )

    return errors


def validate_file(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    records: list[dict[str, Any]] = []
    try:
        expected_date = file_date(path)
    except ValueError as exc:
        return records, [f"{path}: {exc}"]

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        return records, [f"{path}: cannot read file: {exc}"]

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            errors.append(f"{path}:{line_number}: blank lines are not allowed")
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"{path}:{line_number}: invalid JSON: {exc.msg}")
            continue
        record_errors = validate_record(record, expected_date)
        errors.extend(f"{path}:{line_number}: {error}" for error in record_errors)
        if isinstance(record, dict):
            records.append(record)
    return records, errors


def iter_change_files(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        return ()
    return sorted(path for path in root.iterdir() if path.is_file() and path.suffix.lower() == ".jsonl")


def validate_all(project_root: Path) -> tuple[list[str], set[str]]:
    root = changes_root(project_root)
    errors: list[str] = []
    seen_ids: dict[str, Path] = {}
    if not root.is_dir():
        return [f"{root}: changes directory is missing"], set()

    for path in iter_change_files(root):
        records, file_errors = validate_file(path)
        errors.extend(file_errors)
        for record in records:
            change_id = record.get("change_id")
            if not isinstance(change_id, str):
                continue
            previous = seen_ids.get(change_id)
            if previous is not None:
                errors.append(f"{path}: duplicate change_id {change_id}; first seen in {previous}")
            else:
                seen_ids[change_id] = path

    nested_jsonl = sorted(path for path in root.rglob("*.jsonl") if path.parent != root)
    errors.extend(f"{path}: JSONL files must be directly under changes/" for path in nested_jsonl)
    return errors, set(seen_ids)

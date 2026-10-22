"""Report project-memory records that are stale relative to the current Git state.

The checker is intentionally read-only. It does not edit memory, indexes, or the
working tree. A maintenance agent can use the emitted refresh plan to update
module/page records and then run the normal index and workspace checks.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from index_lib import (
    load_record_metadata,
    memory_root,
    parse_frontmatter,
    plan_metadata,
    relative_path,
    resolve_project_root,
    sha256_file,
)


MODULE_TYPES = {"module", "page"}
HIGH_RISK_PARTS = {
    "auth",
    "permission",
    "permissions",
    "security",
    "migration",
    "migrations",
    "schema",
    "database",
}


def run_git(project_root: Path, *args: str) -> tuple[int, str, str]:
    try:
        process = subprocess.run(
            ["git", *args],
            cwd=project_root,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        return 127, "", str(exc)
    return process.returncode, process.stdout.strip(), process.stderr.strip()


def git_value(project_root: Path, *args: str) -> str | None:
    code, stdout, _ = run_git(project_root, *args)
    return stdout if code == 0 and stdout else None


def project_git_root(project_root: Path) -> Path | None:
    value = git_value(project_root, "rev-parse", "--show-toplevel")
    return Path(value).resolve() if value else None


def normalize_git_path(value: str, git_root: Path, project_root: Path) -> str | None:
    candidate = (git_root / value).resolve()
    try:
        return candidate.relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return None


def changed_paths(project_root: Path, git_root: Path, revision: str, head: str) -> tuple[list[str], list[str]]:
    """Return changed project-relative paths and Git diagnostics."""
    diagnostics: list[str] = []
    paths: set[str] = set()
    code, stdout, stderr = run_git(
        project_root,
        "diff",
        "--name-status",
        "--find-renames",
        f"{revision}..{head}",
        "--",
    )
    if code != 0:
        diagnostics.append(f"git_diff_failed:{stderr or code}")
    else:
        for line in stdout.splitlines():
            fields = line.split("\t")
            for value in fields[1:]:
                normalized = normalize_git_path(value, git_root, project_root)
                if normalized:
                    paths.add(normalized)

    for args, label in ((["diff", "--name-only", "HEAD", "--"], "unstaged"), (["diff", "--cached", "--name-only", "--"], "staged")):
        code, stdout, stderr = run_git(project_root, *args)
        if code != 0:
            diagnostics.append(f"git_{label}_diff_failed:{stderr or code}")
            continue
        for value in stdout.splitlines():
            normalized = normalize_git_path(value, git_root, project_root)
            if normalized:
                paths.add(normalized)
    return sorted(paths), diagnostics


def path_matches(path: str, pattern: str) -> bool:
    normalized_path = path.strip("/").replace("\\", "/")
    normalized_pattern = pattern.strip().replace("\\", "/")
    if not normalized_pattern:
        return False
    if normalized_pattern.endswith("/**"):
        prefix = normalized_pattern[:-3].rstrip("/")
        return normalized_path == prefix or normalized_path.startswith(prefix + "/")
    return normalized_path == normalized_pattern or fnmatch.fnmatchcase(normalized_path, normalized_pattern)


def high_risk(path: str) -> bool:
    parts = {part.lower() for part in Path(path).parts}
    return bool(parts & HIGH_RISK_PARTS)


def record_id(metadata: dict[str, Any], path: Path, project_root: Path) -> str:
    value = metadata.get("memory_id")
    if value:
        return str(value)
    return "LEGACY-" + relative_path(path, project_root).replace("/", "_")


def resolve_revision(metadata: dict[str, Any]) -> str | None:
    value = metadata.get("verified_commit")
    if value:
        return str(value)
    for item in metadata.get("evidence_sources") or []:
        if not isinstance(item, dict):
            continue
        revision = item.get("revision") if isinstance(item, dict) else None
        if revision and len(str(revision)) >= 7 and str(revision).lower() not in {"commit-or-version", "unknown"}:
            return str(revision)
    return None


def evidence_status(metadata: dict[str, Any], project_root: Path) -> tuple[list[str], list[str]]:
    reasons: list[str] = []
    evidence_paths: list[str] = []
    records = metadata.get("evidence_sources") or []
    if not isinstance(records, list) or not records:
        return ["missing_evidence_sources"], evidence_paths
    for item in records:
        if not isinstance(item, dict):
            reasons.append("invalid_evidence_source")
            continue
        raw_path = item.get("path")
        if not raw_path:
            reasons.append("evidence_path_missing")
            continue
        candidate = Path(str(raw_path))
        if not candidate.is_absolute():
            candidate = project_root / candidate
        candidate = candidate.resolve()
        try:
            evidence_paths.append(candidate.relative_to(project_root.resolve()).as_posix())
        except ValueError:
            reasons.append(f"evidence_path_outside_project:{raw_path}")
            continue
        if not candidate.is_file():
            reasons.append(f"evidence_path_missing:{raw_path}")
            continue
        expected = str(item.get("evidence_hash") or "")
        if not expected or expected.startswith("sha256:generated"):
            reasons.append(f"evidence_hash_missing:{raw_path}")
        elif expected != sha256_file(candidate):
            reasons.append(f"evidence_hash_mismatch:{raw_path}")
    return reasons, evidence_paths


def inspect_record(path: Path, project_root: Path, git_root: Path, head: str) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    metadata, _, has_frontmatter = parse_frontmatter(raw)
    metadata = load_record_metadata(path, memory_root(project_root), metadata)
    try:
        plan = plan_metadata(path, memory_root(project_root), metadata)
    except ValueError as exc:
        return {
            "memory_id": record_id(metadata, path, project_root),
            "record_path": relative_path(path, memory_root(project_root)),
            "type": "plan", "status": "unknown", "coverage": "unknown",
            "reasons": [str(exc)], "changed_paths": [],
            "refreshable": False, "needs_review": True,
        }
    if plan is not None:
        return {
            "memory_id": plan["memory_id"],
            "record_path": relative_path(path, memory_root(project_root)),
            "type": "plan", "plan_id": plan["scope"], "plan_state": plan["status"],
            "status": "not_applicable", "coverage": "not_applicable",
            "reasons": ["plan_is_not_code_fact"], "changed_paths": [],
            "refreshable": False, "needs_review": False,
        }
    memory_id = record_id(metadata, path, project_root)
    record_path = str(metadata.get("record_path") or relative_path(path, memory_root(project_root)))
    result: dict[str, Any] = {
        "memory_id": memory_id,
        "record_path": record_path,
        "type": str(metadata.get("type") or "unknown"),
        "record_level": str(metadata.get("record_level") or ""),
        "coverage": str(metadata.get("coverage") or "unknown"),
        "status": "unknown",
        "reasons": [],
        "changed_paths": [],
        "refreshable": False,
        "needs_review": True,
    }
    reasons: list[str] = result["reasons"]
    if not has_frontmatter:
        reasons.append("legacy_metadata")

    evidence_reasons, evidence_paths = evidence_status(metadata, project_root)
    reasons.extend(evidence_reasons)
    impact_paths = metadata.get("impact_paths") or evidence_paths
    if not isinstance(impact_paths, list):
        impact_paths = [impact_paths]
    impact_paths = [str(item) for item in impact_paths if str(item).strip()]
    result["impact_paths"] = impact_paths
    result["path_basis"] = "impact_paths" if metadata.get("impact_paths") else "evidence_sources"

    revision = resolve_revision(metadata)
    result["verified_commit"] = revision
    if not revision:
        reasons.append("verified_commit_missing")
    else:
        code, _, stderr = run_git(project_root, "rev-parse", "--verify", f"{revision}^{{commit}}")
        if code != 0:
            reasons.append(f"verified_commit_invalid:{revision}")
        else:
            ancestor_code, _, _ = run_git(project_root, "merge-base", "--is-ancestor", revision, head)
            if ancestor_code != 0:
                reasons.append(f"history_not_ancestor:{revision}")
            changed, diagnostics = changed_paths(project_root, git_root, revision, head)
            reasons.extend(diagnostics)
            matched = [item for item in changed if any(path_matches(item, pattern) for pattern in impact_paths)]
            result["changed_paths"] = matched
            if matched:
                reasons.append("source_changed_after_verification")
                if any(high_risk(item) for item in matched):
                    reasons.append("high_risk_source_change")

    if any(reason.startswith("evidence_hash_mismatch") or reason.startswith("evidence_path_missing") for reason in reasons):
        result["status"] = "stale"
    elif "source_changed_after_verification" in reasons:
        result["status"] = "stale"
    elif not reasons:
        result["status"] = "fresh"
    else:
        result["status"] = "unknown"

    refreshable_reasons = {
        "source_changed_after_verification",
    }
    result["refreshable"] = (
        result["status"] == "stale"
        and (result["type"] in MODULE_TYPES or result["record_level"] == "page")
        and bool(result["changed_paths"])
        and "high_risk_source_change" not in reasons
        and not any(reason.startswith("history_not_ancestor:") for reason in reasons)
        and not any(reason.startswith("evidence_path_missing") for reason in reasons)
        and any(reason in refreshable_reasons for reason in reasons)
    )
    result["needs_review"] = (
        (result["status"] != "fresh" and not result["refreshable"])
        or result["coverage"] == "partial"
    )
    if result["refreshable"]:
        result["refresh_plan"] = {
            "action": "refresh_module_memory",
            "instruction": "Re-read the changed sources, update only this module/page record, set verified_commit to the current HEAD, then rebuild recursive and derived indexes.",
        }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check project-memory freshness against Git and evidence files.")
    parser.add_argument("--project-root")
    parser.add_argument("--head", help="Git commit to inspect; defaults to current HEAD.")
    parser.add_argument("--fail-on-stale", action="store_true")
    parser.add_argument("--fail-on-unknown", action="store_true")
    parser.add_argument("--fail-on-review", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = resolve_project_root(args.project_root)
    git_root = project_git_root(project_root)
    if git_root is None:
        print(json.dumps({"status": "missing", "reason": "git_repository_missing", "records": []}, ensure_ascii=False, indent=2))
        return 2
    head = args.head or git_value(project_root, "rev-parse", "HEAD")
    if not head:
        print(json.dumps({"status": "missing", "reason": "git_head_missing", "records": []}, ensure_ascii=False, indent=2))
        return 2

    records = []
    root = memory_root(project_root)
    if root.is_dir():
        for path in sorted(root.rglob("*.md")):
            if path.name == "INDEX.md":
                continue
            records.append(inspect_record(path, project_root, git_root, head))

    stale = [item for item in records if item["status"] == "stale"]
    unknown = [item for item in records if item["status"] == "unknown"]
    refreshable = [item for item in records if item["refreshable"]]
    needs_review = [item for item in records if item["needs_review"]]
    applicable = [item for item in records if item["status"] != "not_applicable"]
    status = "stale" if stale else "unknown" if unknown else "needs_review" if needs_review else "fresh" if applicable else "not_applicable" if records else "fresh"
    payload = {
        "status": status,
        "project_root": str(project_root),
        "git_root": str(git_root),
        "head": head,
        "counts": {
            "records": len(records),
            "fresh": sum(item["status"] == "fresh" for item in records),
            "not_applicable": sum(item["status"] == "not_applicable" for item in records),
            "stale": len(stale),
            "unknown": len(unknown),
            "refreshable": len(refreshable),
            "needs_review": len(needs_review),
        },
        "records": records,
        "refresh_queue": refreshable,
        "review_queue": [item for item in records if item["needs_review"]],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.fail_on_stale and stale:
        return 1
    if args.fail_on_unknown and unknown:
        return 1
    if args.fail_on_review and needs_review:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

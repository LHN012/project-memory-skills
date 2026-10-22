#!/usr/bin/env python3
"""Create a deterministic manifest for source files used by model-implement-init."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def iter_files(base: Path, source: Path) -> list[Path]:
    target = (base / source).resolve() if not source.is_absolute() else source.resolve()
    if not target.exists():
        return []
    if target.is_file():
        return [target]
    files: list[Path] = []
    for path in target.rglob("*"):
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda item: item.as_posix().lower())


def build_manifest(base: Path, sources: list[Path]) -> dict:
    entries = []
    combined = hashlib.sha256()
    for source in sources:
        for path in iter_files(base, source):
            digest = file_hash(path)
            try:
                rel_path = path.relative_to(base).as_posix()
            except ValueError:
                rel_path = path.as_posix()
            stat = path.stat()
            entry = {
                "path": rel_path,
                "bytes": stat.st_size,
                "modified_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                "sha256": digest,
            }
            entries.append(entry)
            combined.update(rel_path.encode("utf-8"))
            combined.update(digest.encode("ascii"))
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "combined_sha256": combined.hexdigest(),
        "files": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "sources",
        nargs="*",
        default=[
            ".codex/model-implement/prototypes",
            ".codex/model-implement/.sql",
            ".codex/model-implement/library/定义规则.md",
        ],
        help="Files or directories to fingerprint.",
    )
    parser.add_argument("--base", default=".", help="Base directory for relative paths.")
    parser.add_argument(
        "--output",
        default=".codex/model-implement/reports/init-airead/source-manifest.json",
        help="Manifest output path.",
    )
    args = parser.parse_args()

    base = Path(args.base).resolve()
    sources = [Path(item) for item in args.sources]
    manifest = build_manifest(base, sources)

    output = (base / args.output).resolve() if not Path(args.output).is_absolute() else Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Files: {len(manifest['files'])}")
    print(f"Combined SHA256: {manifest['combined_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

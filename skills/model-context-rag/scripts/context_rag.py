#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


SCHEMA = "model-context-rag-v1"
DEFAULT_MAX_CHUNK_CHARS = 2400
DEFAULT_MIN_CHUNK_CHARS = 120
HARD_MAX_CHUNK_CHARS = 3600
SOURCE_ROOTS = ("memory", "reports/init-read", "reports/modules")
TEXT_EXTENSIONS = {".md", ".markdown", ".jsonl", ".txt"}
EXCLUDED_PARTS = {
    ".git",
    ".ai",
    ".codex-cache",
    "context-rag",
    "node_modules",
    "dist",
    "build",
    "target",
    "__pycache__",
}


SEVERITY_RE = re.compile(r"(P[0-3]\s*(?:阻塞|高风险|建议处理|记录观察)?)")
HEADING_RE = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*$")
TOKEN_RE = re.compile(r"[A-Za-z0-9_.\-]+|[\u4e00-\u9fff]{2,}")
SENSITIVE_PATTERNS = [
    re.compile(r"(?i)\b(password|passwd|pwd|token|secret|access[_-]?key|private[_-]?key)\b\s*[:=]\s*[^\s'\";]+"),
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s]+"),
    re.compile(r"(?i)jdbc:[^\s'\"<>]+"),
    re.compile(r"(?i)\b(username|user)\b\s*[:=]\s*[^\s'\";]+"),
]


@dataclass
class SourceFile:
    path: Path
    rel: str
    source_type: str
    size: int
    modified_time: str
    hash: str
    encoding: str
    text: str
    title: str
    headings: list[str]


def now_stamp() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def stable_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_text(path: Path) -> tuple[str, str]:
    data = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace"), "utf-8-replace"


def resolve_model_root(project_root: str | None, model_root: str | None) -> Path:
    if model_root:
        root = Path(model_root).expanduser().resolve()
        if not root.exists():
            raise SystemExit(f"Model root does not exist: {root}")
        return root

    candidates: list[Path] = []
    if project_root:
        project = Path(project_root).expanduser().resolve()
        candidates.extend([project / ".codex" / "model-implement", project])
    else:
        cwd = Path.cwd().resolve()
        for current in (cwd, *cwd.parents):
            candidates.append(current / ".codex" / "model-implement")
            candidates.append(current)

    for candidate in candidates:
        if (candidate / "memory").exists() or (candidate / "reports").exists():
            if candidate.name == "model-implement" or (candidate / "memory").exists():
                return candidate.resolve()

    raise SystemExit("Could not resolve .codex/model-implement. Pass --project-root or --model-root.")


def default_out_dir(model_root: Path, out_dir: str | None) -> Path:
    if out_dir:
        return Path(out_dir).expanduser().resolve()
    return model_root / "reports" / "context-rag"


def rel_to_model(model_root: Path, path: Path) -> str:
    return path.resolve().relative_to(model_root.resolve()).as_posix()


def is_excluded(rel_path: str) -> bool:
    parts = set(rel_path.replace("\\", "/").split("/"))
    return bool(parts & EXCLUDED_PARTS)


def classify_source(rel_path: str) -> str:
    rel = rel_path.replace("\\", "/")
    name = Path(rel).name
    if rel.startswith("memory/"):
        if name.endswith("-rules.md"):
            return "memory-rules"
        if name.endswith(".jsonl"):
            return "memory-log"
        return "memory-doc"

    if rel.startswith("reports/init-read/"):
        mapping = {
            "初始化契约.md": "init-contract",
            "代码及框架信息.md": "framework-info",
            "已有功能模块信息.md": "existing-modules",
            "待办清单.md": "todo-list",
            "业务理解.md": "business-flow",
            "数据库审查报告.md": "db-review",
            "待确认点.md": "confirm-points",
        }
        return mapping.get(name, "init-report")

    if rel.startswith("reports/modules/"):
        mapping = {
            "module-readiness.md": "module-readiness",
            "module-relations.md": "module-relations",
            "frontend-plan.md": "frontend-plan",
            "backend-plan.md": "backend-plan",
        }
        return mapping.get(name, "module-report")

    return "context-doc"


def discover_source_paths(model_root: Path) -> list[Path]:
    paths: list[Path] = []
    for root_rel in SOURCE_ROOTS:
        root = model_root / root_rel
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() not in TEXT_EXTENSIONS:
                continue
            rel = rel_to_model(model_root, path)
            if is_excluded(rel):
                continue
            paths.append(path)
    return sorted(paths, key=lambda item: rel_to_model(model_root, item).lower())


def get_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            return match.group(2).strip()
    return Path(fallback).stem


def get_headings(text: str) -> list[str]:
    headings: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
        if in_fence:
            continue
        match = HEADING_RE.match(line)
        if match:
            headings.append(match.group(2).strip())
    return headings


def load_sources(model_root: Path) -> list[SourceFile]:
    sources: list[SourceFile] = []
    for path in discover_source_paths(model_root):
        data = path.read_bytes()
        text, encoding = read_text(path)
        rel = rel_to_model(model_root, path)
        sources.append(
            SourceFile(
                path=path,
                rel=rel,
                source_type=classify_source(rel),
                size=path.stat().st_size,
                modified_time=datetime.fromtimestamp(path.stat().st_mtime).astimezone().replace(microsecond=0).isoformat(),
                hash=sha256_bytes(data),
                encoding=encoding,
                text=text,
                title=get_title(text, rel),
                headings=get_headings(text),
            )
        )
    return sources


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    seen: set[str] = set()
    for match in TOKEN_RE.finditer(text):
        value = match.group(0).lower()
        candidates = [value]
        if re.fullmatch(r"[\u4e00-\u9fff]+", value) and len(value) > 4:
            candidates.extend(value[i : i + n] for n in (2, 3, 4) for i in range(0, len(value) - n + 1))
        for token in candidates:
            if len(token) < 2 or token in seen:
                continue
            seen.add(token)
            tokens.append(token)
    return tokens


def redact_sensitive(text: str) -> tuple[str, int]:
    total = 0
    redacted = text
    for pattern in SENSITIVE_PATTERNS:
        matches = list(pattern.finditer(redacted))
        total += len(matches)
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted, total


def compact_ws_length(text: str) -> int:
    return len(re.sub(r"\s+", "", text))


def split_markdown_sections(text: str, title: str) -> list[dict[str, Any]]:
    lines = text.splitlines()
    sections: list[dict[str, Any]] = []
    current: list[str] = []
    heading = title
    level = 1
    in_fence = False

    def flush() -> None:
        nonlocal current
        body = "\n".join(current).strip()
        if body:
            sections.append({"heading": heading, "level": level, "text": body})
        current = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
        match = None if in_fence else HEADING_RE.match(line)
        if match:
            flush()
            level = len(match.group(1))
            heading = match.group(2).strip()
        current.append(line)
    flush()
    return sections or [{"heading": title, "level": 1, "text": text.strip()}]


def split_into_blocks(text: str) -> list[str]:
    lines = text.splitlines()
    blocks: list[str] = []
    buffer: list[str] = []
    in_fence = False
    table_buffer: list[str] = []

    def flush_buffer() -> None:
        nonlocal buffer
        body = "\n".join(buffer).strip()
        if body:
            blocks.append(body)
        buffer = []

    def flush_table() -> None:
        nonlocal table_buffer
        body = "\n".join(table_buffer).strip()
        if body:
            blocks.append(body)
        table_buffer = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_table()
            if in_fence:
                buffer.append(line)
                flush_buffer()
                in_fence = False
            else:
                flush_buffer()
                buffer.append(line)
                in_fence = True
            continue

        if in_fence:
            buffer.append(line)
            continue

        if "|" in line and stripped.startswith("|"):
            flush_buffer()
            table_buffer.append(line)
            continue
        flush_table()

        if stripped == "":
            flush_buffer()
            continue

        buffer.append(line)

    flush_table()
    flush_buffer()
    return blocks


def split_large_text(text: str, max_chars: int, min_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text.strip()] if text.strip() else []

    blocks = split_into_blocks(text)
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    def flush() -> None:
        nonlocal current, current_len
        body = "\n\n".join(current).strip()
        if body:
            chunks.append(body)
        current = []
        current_len = 0

    for block in blocks:
        block_len = len(block)
        if block_len > max_chars:
            flush()
            start = 0
            while start < block_len:
                piece = block[start : start + max_chars].strip()
                if piece:
                    chunks.append(piece)
                start += max_chars
            continue

        if current and current_len + block_len + 2 > max_chars and current_len >= min_chars:
            flush()

        current.append(block)
        current_len += block_len + 2

    flush()
    return chunks


def merge_tiny_raw_chunks(raw_chunks: list[dict[str, Any]], min_chars: int, max_chars: int) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    pending: dict[str, Any] | None = None

    for raw in raw_chunks:
        text = raw["text"].strip()
        if not text:
            continue

        if pending is None:
            pending = dict(raw)
            pending["text"] = text
            continue

        pending_text = str(pending["text"]).strip()
        can_merge = len(pending_text) < min_chars or len(text) < min_chars
        merged_len = len(pending_text) + len(text) + 2
        if can_merge and merged_len <= max_chars:
            pending["text"] = pending_text + "\n\n" + text
            if len(pending_text) < min_chars and raw.get("heading"):
                pending["heading"] = raw["heading"]
                pending["level"] = raw.get("level", pending.get("level", 1))
        else:
            merged.append(pending)
            pending = dict(raw)
            pending["text"] = text

    if pending is not None:
        merged.append(pending)

    if len(merged) >= 2 and len(str(merged[-1]["text"])) < min_chars:
        last = merged.pop()
        if len(str(merged[-1]["text"])) + len(str(last["text"])) + 2 <= max_chars:
            merged[-1]["text"] = str(merged[-1]["text"]).strip() + "\n\n" + str(last["text"]).strip()
        else:
            merged.append(last)

    return merged


def extract_field(text: str, names: Iterable[str]) -> str | None:
    joined_names = "|".join(re.escape(name) for name in names)
    pattern = re.compile(rf"(?:{joined_names})\s*[:：]\s*([^\n|,，；;]+)")
    match = pattern.search(text)
    if match:
        value = match.group(1).strip()
        return value[:80] if value else None
    return None


def extract_metadata(rel_path: str, source_type: str, text: str, heading: str) -> dict[str, Any]:
    parts = rel_path.replace("\\", "/").split("/")
    module = None
    page_name = None
    if len(parts) >= 3 and parts[0] == "reports" and parts[1] == "modules":
        module = parts[2]
        if len(parts) >= 5:
            page_name = parts[3]

    module = module or extract_field(text, ("模块", "功能模块", "所属模块"))
    page_name = page_name or extract_field(text, ("界面", "页面", "界面名", "页面名"))
    severity_match = SEVERITY_RE.search(text)

    return {
        "module": module,
        "page_name": page_name,
        "severity": severity_match.group(1).strip() if severity_match else None,
        "source_type": source_type,
        "heading": heading,
    }


def build_chunks(source: SourceFile, max_chars: int, min_chars: int) -> list[dict[str, Any]]:
    suffix = source.path.suffix.lower()
    raw_chunks: list[dict[str, Any]] = []

    if suffix in {".md", ".markdown"}:
        for section in split_markdown_sections(source.text, source.title):
            for piece in split_large_text(section["text"], max_chars, min_chars):
                raw_chunks.append({"heading": section["heading"], "level": section["level"], "text": piece})
    elif suffix == ".jsonl":
        for index, line in enumerate(source.text.splitlines(), start=1):
            if not line.strip():
                continue
            heading = f"{source.title} line {index}"
            try:
                obj = json.loads(line)
                pretty = json.dumps(obj, ensure_ascii=False, indent=2)
                if isinstance(obj, dict):
                    heading = str(obj.get("title") or obj.get("type") or obj.get("event") or heading)
                line_text = pretty
            except json.JSONDecodeError:
                line_text = line
            for piece in split_large_text(line_text, max_chars, min_chars):
                raw_chunks.append({"heading": heading, "level": 1, "text": piece})
    else:
        for piece in split_large_text(source.text, max_chars, min_chars):
            raw_chunks.append({"heading": source.title, "level": 1, "text": piece})

    raw_chunks = merge_tiny_raw_chunks(raw_chunks, min_chars, max_chars)

    chunks: list[dict[str, Any]] = []
    for ordinal, raw in enumerate(raw_chunks, start=1):
        original_text = raw["text"].strip()
        if not original_text:
            continue
        redacted_text, sensitive_hits = redact_sensitive(original_text)
        metadata = extract_metadata(source.rel, source.source_type, redacted_text, raw["heading"])
        full_keyword_text = " ".join(
            str(value)
            for value in [
                source.rel,
                source.title,
                raw["heading"],
                metadata.get("module"),
                metadata.get("page_name"),
                metadata.get("severity"),
                redacted_text,
            ]
            if value
        )
        keywords = tokenize(full_keyword_text)[:80]
        chunk_id = f"{source.rel}#chunk-{ordinal:04d}"
        chunks.append(
            {
                "id": chunk_id,
                "schema": SCHEMA,
                "source_path": source.rel,
                "source_hash": source.hash,
                "source_type": metadata["source_type"],
                "title": source.title,
                "heading": raw["heading"],
                "level": raw["level"],
                "module": metadata["module"],
                "page_name": metadata["page_name"],
                "severity": metadata["severity"],
                "ordinal": ordinal,
                "text": redacted_text,
                "keywords": keywords,
                "char_count": len(redacted_text),
                "original_compact_char_count": compact_ws_length(original_text),
                "redacted_sensitive_hit_count": sensitive_hits,
                "text_hash": sha256_text(redacted_text),
            }
        )
    return chunks


def build_manifest(model_root: Path, sources: list[SourceFile], chunks: list[dict[str, Any]], generated_at: str) -> dict[str, Any]:
    chunk_counts = Counter(chunk["source_path"] for chunk in chunks)
    return {
        "schema": SCHEMA,
        "generated_at": generated_at,
        "model_root": str(model_root),
        "source_roots": list(SOURCE_ROOTS),
        "eligible_source_count": len(sources),
        "indexed_source_count": len(sources),
        "chunk_count": len(chunks),
        "files": [
            {
                "path": source.rel,
                "source_type": source.source_type,
                "title": source.title,
                "extension": source.path.suffix.lower(),
                "size": source.size,
                "modified_time": source.modified_time,
                "hash": source.hash,
                "encoding": source.encoding,
                "headings": source.headings,
                "text_compact_char_count": compact_ws_length(source.text),
                "chunk_count": chunk_counts.get(source.rel, 0),
            }
            for source in sources
        ],
    }


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_chunks(out_dir: Path) -> list[dict[str, Any]]:
    path = out_dir / "chunks.jsonl"
    if not path.exists():
        return []
    chunks: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                chunks.append(json.loads(line))
    return chunks


def build_keyword_index(chunks: list[dict[str, Any]]) -> dict[str, Any]:
    postings: dict[str, list[str]] = defaultdict(list)
    for chunk in chunks:
        for token in chunk.get("keywords", []):
            if len(postings[token]) < 200:
                postings[token].append(chunk["id"])
    return {
        "schema": SCHEMA,
        "token_count": len(postings),
        "chunk_count": len(chunks),
        "tokens": dict(sorted(postings.items(), key=lambda item: item[0])),
    }


def score_chunk(chunk: dict[str, Any], query: str, tokens: list[str]) -> tuple[int, list[str]]:
    fields = {
        "source_path": str(chunk.get("source_path") or "").lower(),
        "title": str(chunk.get("title") or "").lower(),
        "heading": str(chunk.get("heading") or "").lower(),
        "source_type": str(chunk.get("source_type") or "").lower(),
        "module": str(chunk.get("module") or "").lower(),
        "page_name": str(chunk.get("page_name") or "").lower(),
        "severity": str(chunk.get("severity") or "").lower(),
        "text": str(chunk.get("text") or "").lower(),
    }
    score = 0
    hits: list[str] = []
    query_l = query.lower().strip()
    if query_l:
        if query_l in fields["heading"]:
            score += 20
        if query_l in fields["text"]:
            score += 14
    for token in tokens:
        token_score = 0
        if token in fields["source_path"]:
            token_score += 10
        if token in fields["title"]:
            token_score += 8
        if token in fields["heading"]:
            token_score += 8
        if token in fields["source_type"]:
            token_score += 6
        if token in fields["module"]:
            token_score += 8
        if token in fields["page_name"]:
            token_score += 8
        if token in fields["severity"]:
            token_score += 6
        body_count = fields["text"].count(token)
        if body_count:
            token_score += min(18, body_count * 2)
        if token_score:
            score += token_score
            hits.append(token)
    return score, sorted(set(hits))


def chunk_matches_filters(chunk: dict[str, Any], args: argparse.Namespace) -> bool:
    filters = {
        "module": getattr(args, "module", None),
        "page_name": getattr(args, "page", None),
        "source_type": getattr(args, "source_type", None),
        "severity": getattr(args, "severity", None),
    }
    for field, expected in filters.items():
        if not expected:
            continue
        value = str(chunk.get(field) or "")
        if expected.lower() not in value.lower():
            return False
    return True


def snippet_for(text: str, tokens: list[str], size: int = 260) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if len(compact) <= size:
        return compact
    lower = compact.lower()
    positions = [lower.find(token) for token in tokens if token and lower.find(token) >= 0]
    start = max(0, min(positions) - 60) if positions else 0
    end = min(len(compact), start + size)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(compact) else ""
    return prefix + compact[start:end] + suffix


def search_chunks(chunks: list[dict[str, Any]], args: argparse.Namespace) -> list[dict[str, Any]]:
    query = getattr(args, "query", "") or ""
    tokens = tokenize(query)
    results: list[dict[str, Any]] = []
    for chunk in chunks:
        if not chunk_matches_filters(chunk, args):
            continue
        score, hits = score_chunk(chunk, query, tokens)
        if not tokens and chunk_matches_filters(chunk, args):
            score = 1
        if score <= 0:
            continue
        item = {
            "score": score,
            "id": chunk.get("id"),
            "source_path": chunk.get("source_path"),
            "source_type": chunk.get("source_type"),
            "title": chunk.get("title"),
            "heading": chunk.get("heading"),
            "module": chunk.get("module"),
            "page_name": chunk.get("page_name"),
            "severity": chunk.get("severity"),
            "hits": hits,
            "snippet": snippet_for(str(chunk.get("text") or ""), hits or tokens),
            "suggested_read": f"{chunk.get('source_path')} :: {chunk.get('heading')}",
        }
        if getattr(args, "show_text", False):
            item["text"] = chunk.get("text")
        results.append(item)
    return sorted(results, key=lambda item: item["score"], reverse=True)[: getattr(args, "top", 8)]


def compute_retrieval_smoke(chunks: list[dict[str, Any]], manifest: dict[str, Any]) -> dict[str, Any]:
    tests: list[dict[str, Any]] = []
    files = manifest.get("files", [])
    smoke_candidates = [item for item in files if int(item.get("chunk_count") or 0) > 0]
    for file_item in smoke_candidates[:8]:
        candidates = [file_item.get("title"), Path(str(file_item.get("path"))).stem]
        headings = file_item.get("headings") or []
        if headings:
            candidates.insert(0, headings[0])
        query = next((str(item) for item in candidates if item and len(str(item).strip()) >= 2), None)
        if not query:
            continue
        ns = argparse.Namespace(query=query, top=5, module=None, page=None, source_type=None, severity=None, show_text=False)
        results = search_chunks(chunks, ns)
        expected_path = file_item.get("path")
        passed = any(result["source_path"] == expected_path for result in results)
        tests.append(
            {
                "query": query,
                "expected_path": expected_path,
                "passed": passed,
                "top_paths": [result["source_path"] for result in results[:3]],
            }
        )
    passed_count = sum(1 for item in tests if item["passed"])
    return {
        "test_count": len(tests),
        "passed_count": passed_count,
        "passed": passed_count == len(tests) if tests else True,
        "tests": tests,
    }


def check_broken_structure(chunk: dict[str, Any]) -> list[str]:
    text = str(chunk.get("text") or "")
    issues: list[str] = []
    if text.count("```") % 2 != 0:
        issues.append("code_fence_split")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines and re.match(r"^\|?\s*:?-{3,}:?\s*\|", lines[0]):
        issues.append("table_header_missing")
    return issues


def compute_quality(model_root: Path, out_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    manifest_path = out_dir / "manifest.json"
    manifest = load_json(manifest_path) if manifest_path.exists() else {}
    chunks = load_chunks(out_dir)
    discovered_paths = {rel_to_model(model_root, path): path for path in discover_source_paths(model_root)}
    indexed_files = {item["path"]: item for item in manifest.get("files", [])}

    matched_sources = 0
    stale_sources: list[str] = []
    missing_sources: list[str] = []
    new_sources: list[str] = []
    for rel, file_item in indexed_files.items():
        path = discovered_paths.get(rel)
        if path is None:
            missing_sources.append(rel)
            continue
        current_hash = sha256_bytes(path.read_bytes())
        if current_hash != file_item.get("hash"):
            stale_sources.append(rel)
        else:
            matched_sources += 1
    for rel in discovered_paths:
        if rel not in indexed_files:
            new_sources.append(rel)

    source_count = len(discovered_paths)
    source_coverage = (matched_sources / source_count) if source_count else 1.0

    required_fields = ("id", "source_path", "source_type", "title", "heading", "text")
    complete_count = 0
    empty_chunks = 0
    oversized_chunks = 0
    tiny_chunks = 0
    broken_chunks: list[dict[str, Any]] = []
    sensitive_hit_count = 0
    text_hashes: list[str] = []
    for chunk in chunks:
        if all(chunk.get(field) not in (None, "") for field in required_fields):
            complete_count += 1
        text = str(chunk.get("text") or "")
        if not text.strip():
            empty_chunks += 1
        if len(text) > HARD_MAX_CHUNK_CHARS:
            oversized_chunks += 1
        if 0 < len(text) < DEFAULT_MIN_CHUNK_CHARS:
            tiny_chunks += 1
        issues = check_broken_structure(chunk)
        if issues:
            broken_chunks.append({"id": chunk.get("id"), "issues": issues})
        sensitive_hit_count += int(chunk.get("redacted_sensitive_hit_count") or 0)
        if chunk.get("text_hash"):
            text_hashes.append(chunk["text_hash"])

    duplicate_count = sum(count - 1 for count in Counter(text_hashes).values() if count > 1)
    chunk_count = len(chunks)
    metadata_complete_rate = (complete_count / chunk_count) if chunk_count else 1.0
    duplicate_rate = (duplicate_count / chunk_count) if chunk_count else 0.0
    retrieval_smoke = compute_retrieval_smoke(chunks, manifest) if manifest else {"test_count": 0, "passed_count": 0, "passed": False, "tests": []}

    blockers: list[str] = []
    warnings: list[str] = []
    if source_count == 0:
        warnings.append("No source files were found under memory, reports/init-read, or reports/modules.")
    if source_count > 0 and chunk_count == 0:
        blockers.append("Source files exist but no chunks were generated.")
    if source_coverage < 0.9 or stale_sources or missing_sources or new_sources:
        blockers.append("The index is stale or does not cover current source files.")
    if metadata_complete_rate < 0.9:
        blockers.append("Chunk metadata completeness is below 90%.")
    if empty_chunks:
        blockers.append("Empty chunks exist.")
    if broken_chunks:
        blockers.append("Some chunks appear to split structured Markdown blocks.")
    if oversized_chunks:
        warnings.append("Some chunks are larger than the hard quality threshold.")
    if chunk_count >= 8 and tiny_chunks / chunk_count > 0.35:
        warnings.append("More than 35% of chunks are very small.")
    if duplicate_rate > 0.2:
        warnings.append("Duplicate chunk rate is high.")
    if sensitive_hit_count:
        warnings.append("Sensitive-looking values were detected and redacted before indexing.")
    if not retrieval_smoke.get("passed"):
        warnings.append("Retrieval smoke tests did not all pass.")

    status = "blocked" if blockers else "warning" if warnings else "healthy"
    quality = {
        "schema": SCHEMA,
        "generated_at": now_stamp(),
        "source_count": source_count,
        "indexed_source_count": len(indexed_files),
        "matched_source_count": matched_sources,
        "chunk_count": chunk_count,
        "source_coverage": round(source_coverage, 4),
        "metadata_complete_rate": round(metadata_complete_rate, 4),
        "empty_chunk_count": empty_chunks,
        "oversized_chunk_count": oversized_chunks,
        "tiny_chunk_count": tiny_chunks,
        "broken_structure_count": len(broken_chunks),
        "duplicate_chunk_count": duplicate_count,
        "duplicate_rate": round(duplicate_rate, 4),
        "redacted_sensitive_hit_count": sensitive_hit_count,
        "stale_source_count": len(stale_sources),
        "missing_source_count": len(missing_sources),
        "new_source_count": len(new_sources),
        "stale_sources": stale_sources,
        "missing_sources": missing_sources,
        "new_sources": new_sources,
        "broken_chunks": broken_chunks[:50],
        "retrieval_smoke": retrieval_smoke,
    }
    status_obj = {
        "schema": SCHEMA,
        "status": status,
        "generated_at": now_stamp(),
        "model_root": str(model_root),
        "out_dir": str(out_dir),
        "source_coverage": quality["source_coverage"],
        "metadata_complete_rate": quality["metadata_complete_rate"],
        "retrieval_smoke_passed": bool(retrieval_smoke.get("passed")),
        "stale_source_count": len(stale_sources),
        "new_source_count": len(new_sources),
        "missing_source_count": len(missing_sources),
        "chunk_count": chunk_count,
        "blockers": blockers,
        "warnings": warnings,
    }
    return quality, status_obj, manifest


def write_quality_reports(out_dir: Path, quality: dict[str, Any], status_obj: dict[str, Any]) -> None:
    write_json(out_dir / "chunk-quality.json", quality)
    write_json(out_dir / "index-status.json", status_obj)

    lines = [
        "# Context RAG Chunk Quality Report",
        "",
        f"- status: {status_obj['status']}",
        f"- generated_at: {status_obj['generated_at']}",
        f"- source_coverage: {quality['source_coverage']}",
        f"- metadata_complete_rate: {quality['metadata_complete_rate']}",
        f"- chunk_count: {quality['chunk_count']}",
        f"- stale_source_count: {quality['stale_source_count']}",
        f"- new_source_count: {quality['new_source_count']}",
        f"- broken_structure_count: {quality['broken_structure_count']}",
        f"- oversized_chunk_count: {quality['oversized_chunk_count']}",
        f"- tiny_chunk_count: {quality['tiny_chunk_count']}",
        f"- duplicate_rate: {quality['duplicate_rate']}",
        f"- redacted_sensitive_hit_count: {quality['redacted_sensitive_hit_count']}",
        "",
        "## Blockers",
        "",
    ]
    lines.extend([f"- {item}" for item in status_obj.get("blockers", [])] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {item}" for item in status_obj.get("warnings", [])] or ["- None"])
    lines.extend(["", "## Stale Or Missing Sources", ""])
    source_items = quality.get("stale_sources", []) + quality.get("missing_sources", []) + quality.get("new_sources", [])
    lines.extend([f"- {item}" for item in source_items] or ["- None"])
    (out_dir / "chunk-quality-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    smoke = quality.get("retrieval_smoke", {})
    retrieval_lines = [
        "# Context RAG Retrieval Quality Report",
        "",
        f"- passed: {smoke.get('passed')}",
        f"- test_count: {smoke.get('test_count')}",
        f"- passed_count: {smoke.get('passed_count')}",
        "",
        "## Smoke Tests",
        "",
    ]
    for test in smoke.get("tests", []):
        retrieval_lines.append(f"- query: {test['query']}")
        retrieval_lines.append(f"  expected_path: {test['expected_path']}")
        retrieval_lines.append(f"  passed: {test['passed']}")
        retrieval_lines.append(f"  top_paths: {', '.join(test['top_paths'])}")
    if not smoke.get("tests"):
        retrieval_lines.append("- None")
    (out_dir / "retrieval-quality-report.md").write_text("\n".join(retrieval_lines) + "\n", encoding="utf-8")


def command_index(args: argparse.Namespace) -> int:
    model_root = resolve_model_root(args.project_root, args.model_root)
    out_dir = default_out_dir(model_root, args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    generated_at = now_stamp()
    max_chars = max(args.min_chunk_chars, args.max_chunk_chars)

    sources = load_sources(model_root)
    chunks: list[dict[str, Any]] = []
    for source in sources:
        chunks.extend(build_chunks(source, max_chars, args.min_chunk_chars))

    manifest = build_manifest(model_root, sources, chunks, generated_at)
    write_json(out_dir / "manifest.json", manifest)
    write_jsonl(out_dir / "chunks.jsonl", chunks)
    write_json(out_dir / "keyword-index.json", build_keyword_index(chunks))

    quality, status_obj, _ = compute_quality(model_root, out_dir)
    write_quality_reports(out_dir, quality, status_obj)
    search_report = [
        "# Context RAG Search Report",
        "",
        f"- generated_at: {generated_at}",
        f"- model_root: {model_root}",
        f"- source_count: {len(sources)}",
        f"- chunk_count: {len(chunks)}",
        f"- status: {status_obj['status']}",
        "",
        "Generated files are disposable context indexes. Do not hand edit this directory.",
    ]
    (out_dir / "search-report.md").write_text("\n".join(search_report) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(status_obj, ensure_ascii=False, indent=2))
    else:
        print(f"Indexed {len(sources)} files into {len(chunks)} chunks.")
        print(f"Status: {status_obj['status']}")
        print(f"OutDir: {out_dir}")
    return 0 if status_obj["status"] != "blocked" else 2


def command_validate(args: argparse.Namespace) -> int:
    model_root = resolve_model_root(args.project_root, args.model_root)
    out_dir = default_out_dir(model_root, args.out_dir)
    if not (out_dir / "manifest.json").exists():
        status_obj = {
            "schema": SCHEMA,
            "status": "blocked",
            "generated_at": now_stamp(),
            "model_root": str(model_root),
            "out_dir": str(out_dir),
            "blockers": ["Index not found. Run rag-index.ps1 first."],
            "warnings": [],
        }
        out_dir.mkdir(parents=True, exist_ok=True)
        write_json(out_dir / "index-status.json", status_obj)
        print(json.dumps(status_obj, ensure_ascii=False, indent=2) if args.json else "Status: blocked\nIndex not found. Run rag-index.ps1 first.")
        return 2
    quality, status_obj, _ = compute_quality(model_root, out_dir)
    write_quality_reports(out_dir, quality, status_obj)
    if args.json:
        print(json.dumps(status_obj, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {status_obj['status']}")
        for item in status_obj.get("blockers", []):
            print(f"BLOCKER: {item}")
        for item in status_obj.get("warnings", []):
            print(f"WARNING: {item}")
    return 0 if status_obj["status"] != "blocked" else 2


def command_status(args: argparse.Namespace) -> int:
    model_root = resolve_model_root(args.project_root, args.model_root)
    out_dir = default_out_dir(model_root, args.out_dir)
    path = out_dir / "index-status.json"
    if not path.exists():
        status_obj = {
            "schema": SCHEMA,
            "status": "blocked",
            "generated_at": now_stamp(),
            "model_root": str(model_root),
            "out_dir": str(out_dir),
            "blockers": ["index-status.json not found. Run rag-index.ps1 first."],
            "warnings": [],
        }
    else:
        status_obj = load_json(path)
    if args.json:
        print(json.dumps(status_obj, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {status_obj.get('status')}")
        print(f"OutDir: {status_obj.get('out_dir')}")
        for item in status_obj.get("blockers", []):
            print(f"BLOCKER: {item}")
        for item in status_obj.get("warnings", []):
            print(f"WARNING: {item}")
    return 0 if status_obj.get("status") != "blocked" else 2


def command_search(args: argparse.Namespace) -> int:
    model_root = resolve_model_root(args.project_root, args.model_root)
    out_dir = default_out_dir(model_root, args.out_dir)
    chunks = load_chunks(out_dir)
    status_path = out_dir / "index-status.json"
    status_obj = load_json(status_path) if status_path.exists() else {"status": "blocked", "warnings": [], "blockers": ["index-status.json not found."]}
    if not chunks:
        print("No index chunks found. Run rag-index.ps1 first.")
        return 2
    results = search_chunks(chunks, args)
    response = {
        "schema": SCHEMA,
        "status": status_obj.get("status"),
        "query": args.query,
        "top": args.top,
        "result_count": len(results),
        "results": results,
        "status_warnings": status_obj.get("warnings", []),
        "status_blockers": status_obj.get("blockers", []),
    }
    if args.json:
        print(json.dumps(response, ensure_ascii=False, indent=2))
    else:
        print(f"Index status: {response['status']}")
        if response["status"] != "healthy":
            for item in response.get("status_blockers", []):
                print(f"BLOCKER: {item}")
            for item in response.get("status_warnings", []):
                print(f"WARNING: {item}")
        if not results:
            print("No matches.")
            return 0
        for index, item in enumerate(results, start=1):
            print(f"[{index}] score={item['score']} source_type={item['source_type']}")
            print(f"    path: {item['source_path']}")
            print(f"    heading: {item['heading']}")
            if item.get("module"):
                print(f"    module: {item['module']}")
            if item.get("page_name"):
                print(f"    page: {item['page_name']}")
            if item.get("severity"):
                print(f"    severity: {item['severity']}")
            print(f"    hits: {', '.join(item['hits'])}")
            print(f"    suggested_read: {item['suggested_read']}")
            if args.show_text and item.get("text"):
                print("    text:")
                print(item["text"])
            else:
                print(f"    snippet: {item['snippet']}")
            print("")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build and query a local context RAG index for model-implement memory and reports.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common(sub: argparse.ArgumentParser) -> None:
        sub.add_argument("--project-root", help="Project root containing .codex/model-implement.")
        sub.add_argument("--model-root", help="Direct path to .codex/model-implement.")
        sub.add_argument("--out-dir", help="Index output directory. Defaults to reports/context-rag.")
        sub.add_argument("--json", action="store_true", help="Print machine-readable JSON.")

    index = subparsers.add_parser("index", help="Build chunks and indexes.")
    add_common(index)
    index.add_argument("--max-chunk-chars", type=int, default=DEFAULT_MAX_CHUNK_CHARS)
    index.add_argument("--min-chunk-chars", type=int, default=DEFAULT_MIN_CHUNK_CHARS)
    index.set_defaults(func=command_index)

    validate = subparsers.add_parser("validate", help="Validate index freshness and chunk quality.")
    add_common(validate)
    validate.set_defaults(func=command_validate)

    status = subparsers.add_parser("status", help="Read index-status.json.")
    add_common(status)
    status.set_defaults(func=command_status)

    search = subparsers.add_parser("search", help="Search indexed chunks.")
    add_common(search)
    search.add_argument("query", nargs="?", default="", help="Search query.")
    search.add_argument("--top", type=int, default=8)
    search.add_argument("--module")
    search.add_argument("--page")
    search.add_argument("--source-type")
    search.add_argument("--severity")
    search.add_argument("--show-text", action="store_true")
    search.set_defaults(func=command_search)
    return parser


def main(argv: list[str] | None = None) -> int:
    if os.name == "nt":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

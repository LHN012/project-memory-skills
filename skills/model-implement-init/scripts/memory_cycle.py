#!/usr/bin/env python3
"""Append memory entries, promote private rules, and synthesize shared rules."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROMOTABLE_KINDS = {"rule_candidate", "preference", "constraint", "lesson"}
RULE_META_RE = re.compile(r"^\[([^\]]+)\]\s*(.*)$")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            entries.append(value)
    return entries


def normalize_rule(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip()).lower()


def append_log(args: argparse.Namespace) -> int:
    path = Path(args.stream)
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "schema_version": 1,
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "role": args.role,
        "kind": args.kind,
        "text": args.text,
        "module": args.module,
        "weight": args.weight,
        "promote": args.promote,
        "shared_candidate": args.shared_candidate,
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Appended memory entry to {path}")
    return 0


def promote_rules(args: argparse.Namespace) -> int:
    stream = Path(args.stream)
    buckets: dict[str, dict[str, Any]] = {}
    for entry in read_jsonl(stream):
        kind = str(entry.get("kind", ""))
        text = str(entry.get("rule") or entry.get("text") or "").strip()
        if not text:
            continue
        is_shared_candidate = bool(entry.get("shared_candidate"))
        if kind not in PROMOTABLE_KINDS and not entry.get("promote") and not is_shared_candidate:
            continue
        key = normalize_rule(text)
        bucket = buckets.setdefault(
            key,
            {
                "text": text,
                "score": 0.0,
                "mentions": 0,
                "last_seen": "",
                "shared_candidate": False,
            },
        )
        bucket["score"] += float(entry.get("weight") or 1.0)
        bucket["mentions"] += 1
        bucket["last_seen"] = str(entry.get("time_utc") or bucket["last_seen"])
        bucket["shared_candidate"] = bool(bucket["shared_candidate"] or is_shared_candidate)

    qualified = sorted(
        [bucket for bucket in buckets.values() if bucket["score"] >= args.threshold or bucket["shared_candidate"]],
        key=lambda item: (-item["score"], item["text"].lower()),
    )

    output = Path(args.rules_out)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {args.title}",
        "",
        "Rules promoted from the private memory stream. Keep this file concise and remove rules that become stale.",
        "",
    ]
    if qualified:
        for item in qualified:
            shared_meta = " shared_candidate=true" if item["shared_candidate"] else ""
            lines.append(f"- [score={item['score']:.2f} mentions={item['mentions']}{shared_meta}] {item['text']}")
    else:
        lines.append("- No promoted rules yet.")
    lines.append("")
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output}")
    print(f"Promoted rules: {len(qualified)}")
    return 0


def parse_rule_metadata(text: str) -> tuple[dict[str, str], str]:
    match = RULE_META_RE.match(text)
    if not match:
        return {}, text.strip()

    metadata: dict[str, str] = {}
    for token in match.group(1).split():
        if "=" not in token:
            continue
        key, value = token.split("=", 1)
        metadata[key.strip().lower()] = value.strip().lower()
    return metadata, match.group(2).strip()


def read_rule_items(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    result: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        text = stripped[2:].strip()
        if text.lower() == "no promoted rules yet.":
            continue
        metadata, text = parse_rule_metadata(text)
        if text:
            result.append({"text": text, "shared_candidate": metadata.get("shared_candidate") == "true"})
    return result


def synthesize_shared(args: argparse.Namespace) -> int:
    sources = [
        ("init", Path(args.init_rules)),
        ("model-implement", Path(args.plan_rules)),
        ("executor", Path(args.executor_rules)),
    ]
    if args.fix_rules:
        sources.append(("fix", Path(args.fix_rules)))
    if args.review_rules:
        sources.append(("review", Path(args.review_rules)))
    if args.reuse_rules:
        sources.append(("reuse", Path(args.reuse_rules)))
    seen: dict[str, set[str]] = defaultdict(set)
    shared_candidate_seen: dict[str, set[str]] = defaultdict(set)
    display: dict[str, str] = {}
    counts: dict[str, int] = {}

    for origin, path in sources:
        rules = read_rule_items(path)
        counts[origin] = len(rules)
        for item in rules:
            rule = str(item["text"])
            key = normalize_rule(rule)
            seen[key].add(origin)
            display.setdefault(key, rule)
            if item.get("shared_candidate"):
                shared_candidate_seen[key].add(origin)

    shared_items = sorted(
        [
            (key, origins)
            for key, origins in seen.items()
            if len(origins) >= 2 or key in shared_candidate_seen
        ],
        key=lambda item: (-len(item[1]), display[item[0]].lower()),
    )
    skipped_count = len(seen) - len(shared_items)

    rules_out = Path(args.rules_out)
    rules_out.parent.mkdir(parents=True, exist_ok=True)
    rule_lines = [
        "# Shared Rules",
        "",
        "Synthesized from private rules. A rule is included only when it appears in at least two skill contexts or is marked shared_candidate=true in a private rule.",
        "",
    ]
    if shared_items:
        for key, origins in shared_items:
            origin = "+".join(sorted(origins))
            shared_origins = shared_candidate_seen.get(key)
            if shared_origins:
                shared_origin = "+".join(sorted(shared_origins))
                origin = f"shared_candidate:{shared_origin}; origins:{origin}"
            rule_lines.append(f"- [{origin}] {display[key]}")
    else:
        rule_lines.append("- No shared rules yet.")
    rule_lines.append("")
    rules_out.write_text("\n".join(rule_lines), encoding="utf-8")

    memory_out = Path(args.memory_out)
    memory_out.parent.mkdir(parents=True, exist_ok=True)
    memory_out.write_text(
        "\n".join(
            [
                "# Shared Memory",
                "",
                f"Last synthesized: {datetime.now(timezone.utc).isoformat()}",
                f"Init rules read: {counts.get('init', 0)}",
                f"Planning rules read: {counts.get('model-implement', 0)}",
                f"Executor rules read: {counts.get('executor', 0)}",
                f"Fix rules read: {counts.get('fix', 0)}",
                f"Review rules read: {counts.get('review', 0)}",
                f"Reuse rules read: {counts.get('reuse', 0)}",
                f"Shared rule entries written: {len(shared_items)}",
                f"Private-only rule entries skipped: {skipped_count}",
                "",
                "Selection rule: include repeated cross-skill rules or private rules explicitly marked shared_candidate=true; do not treat shared rules as a raw union.",
                "",
                "Use this file as a compact pointer to stable cross-skill learning, not as a raw log.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"Wrote {rules_out}")
    print(f"Wrote {memory_out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    log_parser = subparsers.add_parser("log", help="Append a JSONL memory entry.")
    log_parser.add_argument("--stream", required=True)
    log_parser.add_argument("--role", required=True)
    log_parser.add_argument("--kind", default="observation")
    log_parser.add_argument("--text", required=True)
    log_parser.add_argument("--module", default=None)
    log_parser.add_argument("--weight", type=float, default=1.0)
    log_parser.add_argument("--promote", action="store_true")
    log_parser.add_argument("--shared-candidate", action="store_true")
    log_parser.set_defaults(func=append_log)

    promote_parser = subparsers.add_parser("promote", help="Promote candidate entries into a rules markdown file.")
    promote_parser.add_argument("--stream", required=True)
    promote_parser.add_argument("--rules-out", required=True)
    promote_parser.add_argument("--title", default="Private Rules")
    promote_parser.add_argument("--threshold", type=float, default=3.0)
    promote_parser.set_defaults(func=promote_rules)

    synth_parser = subparsers.add_parser("synthesize-shared", help="Create shared rules and memory from private rules.")
    synth_parser.add_argument("--init-rules", required=True)
    synth_parser.add_argument("--plan-rules", required=True)
    synth_parser.add_argument("--executor-rules", required=True)
    synth_parser.add_argument("--fix-rules", help="Optional fix skill private rules file.")
    synth_parser.add_argument("--review-rules", help="Optional review skill private rules file.")
    synth_parser.add_argument("--reuse-rules", help="Optional reuse skill private rules file.")
    synth_parser.add_argument("--rules-out", required=True)
    synth_parser.add_argument("--memory-out", required=True)
    synth_parser.set_defaults(func=synthesize_shared)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

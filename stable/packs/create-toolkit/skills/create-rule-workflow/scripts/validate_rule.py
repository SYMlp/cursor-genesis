#!/usr/bin/env python3
"""Deterministic validator for a tool-neutral AGENTS.md Rule Contract block."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ACTIVATIONS = {"always", "paths", "intent", "manual"}
SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
START_PATTERN = re.compile(r"^<!-- cg-rule-contract:([a-z0-9-]+):start -->$", re.MULTILINE)
PLACEHOLDER_PATTERNS = (
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\[待填写\]"),
    re.compile(r"<(?:name|description|behavior|verification)>", re.IGNORECASE),
)
HOST_PATTERNS = (
    re.compile(r"\.cursor(?:/|\\)", re.IGNORECASE),
    re.compile(r"\.claude(?:/|\\)", re.IGNORECASE),
    re.compile(r"\.codex(?:/|\\)", re.IGNORECASE),
    re.compile(r"\.mdc\b", re.IGNORECASE),
    re.compile(r"\balwaysApply\b"),
    re.compile(r"\bglobs\s*:"),
    re.compile(r"\bsubagent_type\b"),
    re.compile(r"\bmodel\s*:"),
)
REQUIRED_SECTIONS = ("### Behavior", "### Exclusions", "### Verification")
DIRECTIVE_PATTERN = re.compile(r"^- (MUST NOT|MUST|SHOULD|MAY)\s+(.+)$")


def _issue(code: str, message: str, path: Path) -> dict[str, str]:
    return {"code": code, "message": message, "path": str(path)}


def extract_rule_block(content: str, rule_id: str) -> str:
    start = f"<!-- cg-rule-contract:{rule_id}:start -->"
    end = f"<!-- cg-rule-contract:{rule_id}:end -->"
    start_index = content.find(start)
    if start_index < 0:
        raise ValueError(f"Rule start marker not found: {rule_id}")
    end_index = content.find(end, start_index + len(start))
    if end_index < 0:
        raise ValueError(f"Rule end marker not found: {rule_id}")
    second_start = content.find(start, start_index + len(start))
    if second_start >= 0 and second_start < end_index:
        raise ValueError(f"Duplicate nested Rule marker: {rule_id}")
    return content[start_index : end_index + len(end)]


def _field(block: str, field: str) -> str | None:
    match = re.search(rf"(?m)^- {re.escape(field)}:\s*(.+)$", block)
    return match.group(1).strip() if match else None


def _section(block: str, heading: str) -> str:
    marker = re.search(rf"(?m)^{re.escape(heading)}\s*$", block)
    if not marker:
        return ""
    remainder = block[marker.end() :]
    next_heading = re.search(r"(?m)^###\s+", remainder)
    end_marker = re.search(r"(?m)^<!-- cg-rule-contract:", remainder)
    stops = [
        match.start()
        for match in (next_heading, end_marker)
        if match is not None
    ]
    return remainder[: min(stops)] if stops else remainder


def _parse_paths(raw: str | None) -> list[str]:
    parsed = json.loads(raw or "null")
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError("Paths must be a JSON string array")
    return parsed


def _valid_glob(value: str) -> bool:
    if not value or value.startswith(("/", "\\")) or "\\" in value or ":" in value:
        return False
    return ".." not in Path(value).parts


def parse_rule_block(block: str) -> dict[str, Any]:
    start_match = START_PATTERN.search(block)
    if not start_match:
        raise ValueError("Rule block start marker is missing")
    rule_id = start_match.group(1)
    id_field = _field(block, "ID")
    if id_field and id_field.startswith("`") and id_field.endswith("`"):
        id_field = id_field[1:-1]
    paths = _parse_paths(_field(block, "Paths"))
    behavior = [
        line.strip()
        for line in _section(block, "### Behavior").splitlines()
        if line.strip()
    ]
    exclusions = [
        line.strip()
        for line in _section(block, "### Exclusions").splitlines()
        if line.strip()
    ]
    verification = [
        line.strip()
        for line in _section(block, "### Verification").splitlines()
        if line.strip()
    ]
    title_match = re.search(r"(?m)^## Rule:\s*(.+)$", block)
    return {
        "id": rule_id,
        "id_field": id_field,
        "title": title_match.group(1).strip() if title_match else None,
        "activation": _field(block, "Activation"),
        "description": _field(block, "Description"),
        "paths": paths,
        "trigger": _field(block, "Trigger"),
        "rationale": _field(block, "Rationale"),
        "behavior": behavior,
        "exclusions": exclusions,
        "verification": verification,
    }


def validate_rule_block(
    block: str,
    source_path: Path,
    expected_id: str | None = None,
) -> dict[str, Any]:
    source_path = source_path.resolve()
    issues: list[dict[str, str]] = []
    try:
        parsed = parse_rule_block(block)
    except (json.JSONDecodeError, ValueError) as error:
        issues.append(_issue("RULE_PARSE_FAILED", str(error), source_path))
        return {"ok": False, "source": str(source_path), "issues": issues}

    rule_id = parsed["id"]
    end_marker = f"<!-- cg-rule-contract:{rule_id}:end -->"
    if not SLUG_PATTERN.fullmatch(rule_id):
        issues.append(_issue("RULE_ID_INVALID", "Rule ID must be kebab-case", source_path))
    if expected_id and rule_id != expected_id:
        issues.append(_issue("RULE_ID_MISMATCH", f"Expected Rule ID '{expected_id}'", source_path))
    if parsed["id_field"] != rule_id:
        issues.append(_issue("RULE_ID_FIELD_MISMATCH", "ID field must match marker ID", source_path))
    if block.count(end_marker) != 1 or not block.rstrip().endswith(end_marker):
        issues.append(_issue("RULE_END_MARKER_INVALID", "Rule end marker is missing or duplicated", source_path))
    if not parsed["title"]:
        issues.append(_issue("RULE_TITLE_MISSING", "Rule title is required", source_path))

    for field in ("description", "trigger", "rationale"):
        value = parsed[field]
        if not value:
            issues.append(_issue("RULE_FIELD_MISSING", f"Missing Rule field: {field}", source_path))
        elif "\n" in value or len(value) > 300:
            issues.append(_issue("RULE_FIELD_INVALID", f"Rule field must be a concise single line: {field}", source_path))

    activation = parsed["activation"]
    if activation not in ACTIVATIONS:
        issues.append(_issue("ACTIVATION_INVALID", f"Unsupported activation: {activation}", source_path))
    paths = parsed["paths"]
    if activation == "paths" and not paths:
        issues.append(_issue("PATHS_REQUIRED", "paths activation requires at least one path glob", source_path))
    if activation != "paths" and paths:
        issues.append(_issue("PATHS_NOT_ALLOWED", "Only paths activation may declare path globs", source_path))
    if len(paths) > 7:
        issues.append(_issue("TOO_MANY_PATHS", "A Rule may declare at most seven path globs", source_path))
    for path_glob in paths:
        if not _valid_glob(path_glob):
            issues.append(_issue("PATH_GLOB_INVALID", f"Invalid project-relative glob: {path_glob}", source_path))

    for heading in REQUIRED_SECTIONS:
        if heading not in block:
            issues.append(_issue("RULE_SECTION_MISSING", f"Missing section: {heading}", source_path))

    behavior = parsed["behavior"]
    if not 1 <= len(behavior) <= 7:
        issues.append(_issue("BEHAVIOR_COUNT_INVALID", "Behavior must contain 1-7 directives", source_path))
    for directive in behavior:
        if not DIRECTIVE_PATTERN.fullmatch(directive):
            issues.append(_issue("BEHAVIOR_DIRECTIVE_INVALID", f"Invalid directive: {directive}", source_path))

    for section_name in ("exclusions", "verification"):
        lines = parsed[section_name]
        if not lines or any(not line.startswith("- ") for line in lines):
            issues.append(_issue("RULE_SECTION_INVALID", f"{section_name} must contain bullet items", source_path))
        if any(re.fullmatch(r"-\s*(?:none|无|不需要)[。.]?", line, re.IGNORECASE) for line in lines):
            issues.append(_issue("RULE_SECTION_EMPTY", f"{section_name} must state a real boundary", source_path))

    if len(block.splitlines()) > 80:
        issues.append(_issue("RULE_TOO_LONG", "Rule block exceeds the 80-line thin-contract limit", source_path))
    for pattern in PLACEHOLDER_PATTERNS:
        if pattern.search(block):
            issues.append(_issue("PLACEHOLDER_REMAINS", f"Unresolved placeholder: {pattern.pattern}", source_path))
    for pattern in HOST_PATTERNS:
        if pattern.search(block):
            issues.append(_issue("HOST_SPECIFIC_RULE_CORE", f"Host syntax belongs in an adapter: {pattern.pattern}", source_path))

    return {
        "ok": not issues,
        "source": str(source_path),
        "issues": issues,
        "rule": parsed,
    }


def validate_rule_file(rule_file: Path, expected_id: str | None = None) -> dict[str, Any]:
    rule_file = rule_file.resolve()
    if not rule_file.is_file():
        return {
            "ok": False,
            "source": str(rule_file),
            "issues": [_issue("RULE_FILE_MISSING", "Rule draft does not exist", rule_file)],
        }
    try:
        content = rule_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return {
            "ok": False,
            "source": str(rule_file),
            "issues": [_issue("RULE_FILE_READ_FAILED", str(error), rule_file)],
        }
    start_matches = list(START_PATTERN.finditer(content))
    if len(start_matches) != 1:
        return {
            "ok": False,
            "source": str(rule_file),
            "issues": [_issue("RULE_BLOCK_COUNT_INVALID", "Draft must contain exactly one Rule block", rule_file)],
        }
    rule_id = start_matches[0].group(1)
    try:
        block = extract_rule_block(content, rule_id)
    except ValueError as error:
        return {
            "ok": False,
            "source": str(rule_file),
            "issues": [_issue("RULE_BLOCK_INVALID", str(error), rule_file)],
        }
    if content.strip() != block.strip():
        return {
            "ok": False,
            "source": str(rule_file),
            "issues": [_issue("RULE_DRAFT_EXTRA_CONTENT", "Draft may contain only the Rule block", rule_file)],
        }
    return validate_rule_block(block, rule_file, expected_id=expected_id)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an AGENTS.md Rule Contract draft")
    parser.add_argument("--rule-file", required=True)
    parser.add_argument("--expected-id")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = validate_rule_file(Path(args.rule_file), expected_id=args.expected_id)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["ok"]:
        print(f"[OK] Rule Contract is valid: {report['source']}")
    else:
        print(f"[ERROR] Rule Contract validation failed: {report['source']}")
        for issue in report["issues"]:
            print(f"  - [{issue['code']}] {issue['message']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

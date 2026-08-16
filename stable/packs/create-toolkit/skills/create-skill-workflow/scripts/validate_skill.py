#!/usr/bin/env python3
"""Deterministic validator for a generated project Skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


REQUIRED_DIRECTORIES = ("scripts", "references", "assets", "tests")
REQUIRED_FILES = ("SKILL.md", "README.md")
REQUIRED_TOP_LEVEL_FIELDS = ("name", "description", "category")
REQUIRED_HEADINGS = (
    "## Workflow",
    "## Verification",
    "## Context & Side Effects",
)
PLACEHOLDER_PATTERNS = (
    re.compile(r"\bTODO\b", re.IGNORECASE),
    re.compile(r"\[待填写\]"),
    re.compile(r"\[Add [^\]]+\]", re.IGNORECASE),
)


def _issue(code: str, message: str, path: Path) -> dict[str, str]:
    return {"code": code, "message": message, "path": str(path)}


def _split_frontmatter(content: str) -> tuple[str | None, str]:
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, content
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :])
    return None, content


def _parse_frontmatter(frontmatter: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    parent: str | None = None
    for raw_line in frontmatter.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip())
        match = re.match(r"^\s*([A-Za-z0-9_-]+):\s*(.*)$", raw_line)
        if not match:
            continue
        key, value = match.groups()
        value = value.strip().strip("\"'")
        if indent == 0:
            if value:
                result[key] = value
                parent = None
            else:
                result[key] = {}
                parent = key
        elif parent and isinstance(result.get(parent), dict):
            result[parent][key] = value
    return result


def validate_skill_dir(skill_dir: Path) -> dict[str, Any]:
    skill_dir = skill_dir.resolve()
    issues: list[dict[str, str]] = []

    if not skill_dir.is_dir():
        issues.append(_issue("SKILL_DIR_MISSING", "Skill directory does not exist", skill_dir))
        return {"ok": False, "skill_dir": str(skill_dir), "issues": issues}

    for directory in REQUIRED_DIRECTORIES:
        path = skill_dir / directory
        if not path.is_dir():
            issues.append(_issue("REQUIRED_DIRECTORY_MISSING", f"Missing directory: {directory}", path))

    for filename in REQUIRED_FILES:
        path = skill_dir / filename
        if not path.is_file():
            issues.append(_issue("REQUIRED_FILE_MISSING", f"Missing file: {filename}", path))

    skill_md = skill_dir / "SKILL.md"
    if skill_md.is_file():
        content = skill_md.read_text(encoding="utf-8")
        frontmatter_text, body = _split_frontmatter(content)
        if frontmatter_text is None:
            issues.append(_issue("FRONTMATTER_MISSING", "SKILL.md must start with closed YAML frontmatter", skill_md))
        else:
            frontmatter = _parse_frontmatter(frontmatter_text)
            for field in REQUIRED_TOP_LEVEL_FIELDS:
                if not frontmatter.get(field):
                    issues.append(_issue("FRONTMATTER_FIELD_MISSING", f"Missing frontmatter field: {field}", skill_md))
            metadata = frontmatter.get("metadata")
            if not isinstance(metadata, dict) or not metadata.get("version"):
                issues.append(_issue("FRONTMATTER_FIELD_MISSING", "Missing frontmatter field: metadata.version", skill_md))
            if frontmatter.get("name") and frontmatter["name"] != skill_dir.name:
                issues.append(
                    _issue(
                        "NAME_DIRECTORY_MISMATCH",
                        f"Frontmatter name '{frontmatter['name']}' does not match directory '{skill_dir.name}'",
                        skill_md,
                    )
                )

        for heading in REQUIRED_HEADINGS:
            if heading not in body:
                issues.append(_issue("REQUIRED_SECTION_MISSING", f"Missing section: {heading}", skill_md))

        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(content):
                issues.append(_issue("PLACEHOLDER_REMAINS", f"Unresolved placeholder matched: {pattern.pattern}", skill_md))

    return {"ok": not issues, "skill_dir": str(skill_dir), "issues": issues}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a generated project Skill")
    parser.add_argument("--skill-dir", required=True, help="Path to the Skill directory")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    args = parser.parse_args()

    report = validate_skill_dir(Path(args.skill_dir))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif report["ok"]:
        print(f"[OK] Skill is valid: {report['skill_dir']}")
    else:
        print(f"[ERROR] Skill validation failed: {report['skill_dir']}")
        for issue in report["issues"]:
            print(f"  - [{issue['code']}] {issue['message']} ({issue['path']})")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())

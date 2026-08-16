#!/usr/bin/env python3
"""Render a validated AGENTS.md Rule Contract as a Cursor Project Rule."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _load_validator(project_root: Path) -> Any:
    validator_path = (
        project_root
        / ".agents"
        / "skills"
        / "create-rule-workflow"
        / "scripts"
        / "validate_rule.py"
    )
    if not validator_path.is_file():
        raise FileNotFoundError(f"Shared Rule validator not found: {validator_path}")
    spec = importlib.util.spec_from_file_location("create_rule_validate_rule", validator_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load shared Rule validator: {validator_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(content)
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def _frontmatter(rule: dict[str, Any]) -> str:
    activation = rule["activation"]
    description = json.dumps(rule["description"], ensure_ascii=False)
    if activation == "always":
        return f"description: {description}\nglobs:\nalwaysApply: true"
    if activation == "paths":
        if len(rule["paths"]) != 1:
            raise ValueError(
                "Cursor renderer requires exactly one path glob; split the Rule instead of guessing syntax"
            )
        path_glob = json.dumps(rule["paths"][0], ensure_ascii=False)
        return f"description: {description}\nglobs: {path_glob}\nalwaysApply: false"
    if activation == "intent":
        return f"description: {description}\nglobs:\nalwaysApply: false"
    if activation == "manual":
        return "description:\nglobs:\nalwaysApply: false"
    raise ValueError(f"Unsupported activation: {activation}")


def render_cursor_rule(
    project_root: Path,
    agents_file: Path,
    rule_id: str,
    output_path: Path | None = None,
) -> Path:
    project_root = project_root.resolve()
    agents_file = agents_file.resolve() if agents_file.is_absolute() else (project_root / agents_file).resolve()
    if not _inside(agents_file, project_root) or agents_file.name != "AGENTS.md":
        raise ValueError("Rule source must be an AGENTS.md inside the project root")
    if not agents_file.is_file():
        raise FileNotFoundError(f"AGENTS.md does not exist: {agents_file}")

    validator = _load_validator(project_root)
    content = agents_file.read_text(encoding="utf-8")
    block = validator.extract_rule_block(content, rule_id)
    report = validator.validate_rule_block(block, agents_file, expected_id=rule_id)
    if not report["ok"]:
        codes = ", ".join(issue["code"] for issue in report["issues"])
        raise ValueError(f"Rule Contract validation failed: {codes}")
    rule = report["rule"]

    cursor_root = (project_root / ".cursor" / "rules").resolve()
    if output_path is None:
        output_path = cursor_root / f"{rule_id}.mdc"
    else:
        output_path = output_path.resolve() if output_path.is_absolute() else (project_root / output_path).resolve()
    if not _inside(output_path, cursor_root):
        raise ValueError("Cursor Rule output must stay under .cursor/rules")
    if output_path.exists():
        raise FileExistsError(f"Refusing to overwrite Cursor Rule: {output_path}")

    source = agents_file.relative_to(project_root).as_posix()
    behavior = "\n".join(rule["behavior"])
    exclusions = "\n".join(rule["exclusions"])
    verification = "\n".join(rule["verification"])
    rendered = f"""---
{_frontmatter(rule)}
---

<!-- Generated from {source} rule-contract:{rule_id}; edit AGENTS.md, then render a new adapter. -->

# {rule['title']}

{rule['description']}

## Trigger

{rule['trigger']}

## Behavior

{behavior}

## Exclusions

{exclusions}

## Verification

{verification}
"""
    _atomic_write(output_path, rendered)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render a Cursor Rule from AGENTS.md")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--agents-file", default="AGENTS.md")
    parser.add_argument("--rule-id", required=True)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        output = render_cursor_rule(
            Path(args.project_root),
            Path(args.agents_file),
            args.rule_id,
            Path(args.output) if args.output else None,
        )
    except (FileExistsError, FileNotFoundError, OSError, RuntimeError, UnicodeDecodeError, ValueError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 4
    print(f"[OK] Cursor Rule rendered: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Register a validated Rule Contract block into an AGENTS.md author source."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path

from validate_rule import extract_rule_block, validate_rule_file


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _atomic_write(path: Path, content: str) -> None:
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


def register_rule(
    project_root: Path,
    rule_file: Path,
    agents_file: Path,
    confirm_id: str,
) -> Path:
    project_root = project_root.resolve()
    if not project_root.is_dir():
        raise ValueError(f"Project root does not exist: {project_root}")
    rule_file = rule_file.resolve() if rule_file.is_absolute() else (project_root / rule_file).resolve()
    agents_file = agents_file.resolve() if agents_file.is_absolute() else (project_root / agents_file).resolve()
    if not _inside(rule_file, project_root) or not _inside(agents_file, project_root):
        raise ValueError("Rule draft and AGENTS.md must stay inside the project root")
    if agents_file.name != "AGENTS.md":
        raise ValueError("Public Rule Contracts may only be registered in an AGENTS.md file")
    if not agents_file.is_file():
        raise FileNotFoundError(f"AGENTS.md does not exist: {agents_file}")

    report = validate_rule_file(rule_file, expected_id=confirm_id)
    if not report["ok"]:
        codes = ", ".join(issue["code"] for issue in report["issues"])
        raise ValueError(f"Rule Contract validation failed: {codes}")
    rule_id = report["rule"]["id"]
    if confirm_id != rule_id:
        raise ValueError(f"Confirmation ID '{confirm_id}' does not match Rule ID '{rule_id}'")
    block = extract_rule_block(rule_file.read_text(encoding="utf-8"), rule_id)

    agents_content = agents_file.read_text(encoding="utf-8")
    if f"<!-- cg-rule-contract:{rule_id}:start -->" in agents_content:
        raise FileExistsError(f"Rule Contract already exists in AGENTS.md: {rule_id}")
    updated = agents_content.rstrip() + "\n\n" + block.strip() + "\n"
    _atomic_write(agents_file, updated)
    return agents_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Register a Rule Contract in AGENTS.md")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--rule-file", required=True)
    parser.add_argument("--agents-file", default="AGENTS.md")
    parser.add_argument("--confirm-id", required=True)
    args = parser.parse_args()
    try:
        output = register_rule(
            Path(args.project_root),
            Path(args.rule_file),
            Path(args.agents_file),
            args.confirm_id,
        )
    except (FileExistsError, FileNotFoundError, OSError, UnicodeDecodeError, ValueError) as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 4
    print(f"[OK] Rule Contract registered: {output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

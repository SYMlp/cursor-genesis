#!/usr/bin/env python3
"""Prepare a deterministic audit packet for an Agent/Skill/Command asset."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ASSET_TYPES = ("skill", "agent", "command", "workflow", "adapter", "prompt")
SEVERITIES = {"critical", "high", "medium", "low"}
DEFAULT_MAX_BYTES = 256 * 1024


class AuditPreparationError(ValueError):
    """Raised when an audit packet cannot be prepared safely."""


def detect_asset_type(target: Path) -> str:
    parts = [part.lower() for part in target.parts]
    name = target.name.lower()
    if name == "skill.md":
        return "skill"
    if name in {"workflow.yaml", "workflow.yml"}:
        return "workflow"
    if "adapters" in parts:
        return "adapter"
    if "agents" in parts:
        return "agent"
    if "commands" in parts:
        return "command"
    return "prompt"


def load_rubric(rubric_path: Path) -> dict[str, Any]:
    try:
        rubric = json.loads(rubric_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise AuditPreparationError(f"Rubric file not found: {rubric_path}") from error
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AuditPreparationError(f"Cannot read rubric: {error}") from error

    if not isinstance(rubric, dict) or not isinstance(rubric.get("criteria"), list):
        raise AuditPreparationError("Rubric must be an object with a criteria array")
    supported_types = rubric.get("asset_types")
    if (
        not isinstance(supported_types, list)
        or not supported_types
        or any(item not in ASSET_TYPES for item in supported_types)
    ):
        raise AuditPreparationError("Rubric asset_types must be a non-empty supported-type array")

    seen_ids: set[str] = set()
    for index, criterion in enumerate(rubric["criteria"], start=1):
        if not isinstance(criterion, dict):
            raise AuditPreparationError(f"Criterion {index} must be an object")
        criterion_id = criterion.get("id")
        if not isinstance(criterion_id, str) or not re.fullmatch(
            r"[a-z0-9]+(?:-[a-z0-9]+)*", criterion_id
        ):
            raise AuditPreparationError(f"Criterion {index} has an invalid id")
        if criterion_id in seen_ids:
            raise AuditPreparationError(f"Duplicate criterion id: {criterion_id}")
        seen_ids.add(criterion_id)
        if criterion.get("severity") not in SEVERITIES:
            raise AuditPreparationError(f"Criterion {criterion_id} has an invalid severity")
        applies_to = criterion.get("applies_to")
        if (
            not isinstance(applies_to, list)
            or not applies_to
            or any(item != "all" and item not in ASSET_TYPES for item in applies_to)
        ):
            raise AuditPreparationError(f"Criterion {criterion_id} has invalid applies_to")
        for field in ("check", "evidence"):
            if not isinstance(criterion.get(field), str) or not criterion[field].strip():
                raise AuditPreparationError(f"Criterion {criterion_id} has an empty {field}")
    return rubric


def prepare_audit_packet(
    target_path: Path,
    rubric_path: Path,
    asset_type: str = "auto",
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> dict[str, Any]:
    if max_bytes < 1:
        raise AuditPreparationError("max_bytes must be positive")
    target_path = target_path.resolve()
    if not target_path.is_file():
        raise AuditPreparationError(f"Target file not found: {target_path}")
    size = target_path.stat().st_size
    if size > max_bytes:
        raise AuditPreparationError(
            f"Target is {size} bytes, exceeding the {max_bytes}-byte limit"
        )
    try:
        content = target_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        raise AuditPreparationError(f"Cannot read target as UTF-8: {error}") from error

    if asset_type == "auto":
        asset_type = detect_asset_type(target_path)
    if asset_type not in ASSET_TYPES:
        raise AuditPreparationError(f"Unsupported asset type: {asset_type}")

    rubric = load_rubric(rubric_path.resolve())
    if asset_type not in rubric["asset_types"]:
        raise AuditPreparationError(
            f"Rubric does not support asset type '{asset_type}'"
        )
    criteria = [
        criterion
        for criterion in rubric["criteria"]
        if "all" in criterion["applies_to"] or asset_type in criterion["applies_to"]
    ]
    return {
        "schema_version": 1,
        "target": {
            "path": str(target_path),
            "asset_type": asset_type,
            "bytes": size,
            "lines": len(content.splitlines()),
            "content": content,
        },
        "rubric": {
            "version": rubric.get("version"),
            "criteria": criteria,
        },
        "auditor_contract": {
            "read_only": True,
            "verdicts": ["PASS", "WARN", "FAIL"],
            "finding_fields": ["criterion", "severity", "evidence", "impact", "recommendation"],
            "rule": "critical finding => FAIL; other findings => WARN; no findings => PASS",
        },
    }


def _fence(content: str) -> str:
    runs = [len(match.group(0)) for match in re.finditer(r"`+", content)]
    return "`" * max(3, (max(runs) + 1) if runs else 3)


def render_markdown(packet: dict[str, Any]) -> str:
    target = packet["target"]
    criteria_json = json.dumps(
        packet["rubric"]["criteria"],
        ensure_ascii=False,
        indent=2,
    )
    target_fence = _fence(target["content"])
    criteria_fence = _fence(criteria_json)
    return f"""# Asset Audit Packet

- Target: `{target['path']}`
- Asset type: `{target['asset_type']}`
- Size: {target['bytes']} bytes / {target['lines']} lines
- Rubric version: `{packet['rubric']['version']}`

## Target Content

{target_fence}text
{target['content']}
{target_fence}

## Applicable Criteria

{criteria_fence}json
{criteria_json}
{criteria_fence}

## Auditor Contract

- Remain read-only unless the user separately requests a fix.
- Evaluate every applicable criterion using evidence from the target.
- Return PASS, WARN, or FAIL and include criterion, severity, evidence, impact, and recommendation for each finding.
- A critical finding means FAIL; non-critical findings mean WARN; no findings means PASS.
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare an agent-asset audit packet")
    parser.add_argument("target", help="UTF-8 text asset to audit")
    parser.add_argument(
        "--rubric",
        default=str(Path(__file__).resolve().parents[1] / "references" / "rubric.json"),
    )
    parser.add_argument(
        "--asset-type",
        default="auto",
        choices=("auto",) + ASSET_TYPES,
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        packet = prepare_audit_packet(
            Path(args.target),
            Path(args.rubric),
            asset_type=args.asset_type,
            max_bytes=args.max_bytes,
        )
    except AuditPreparationError as error:
        print(f"[ERROR] {error}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(packet, ensure_ascii=False, indent=2))
    else:
        print(render_markdown(packet))
    return 0


if __name__ == "__main__":
    sys.exit(main())

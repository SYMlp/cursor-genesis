import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_ROOT / "scripts" / "prepare_audit.py"
RUBRIC_PATH = SKILL_ROOT / "references" / "rubric.json"
SPEC = importlib.util.spec_from_file_location("prepare_audit", SCRIPT_PATH)
prepare_audit = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(prepare_audit)


class PrepareAuditTests(unittest.TestCase):
    def test_default_rubric_and_auto_detection(self):
        packet = prepare_audit.prepare_audit_packet(
            SKILL_ROOT / "SKILL.md",
            RUBRIC_PATH,
        )
        self.assertEqual("skill", packet["target"]["asset_type"])
        self.assertTrue(packet["auditor_contract"]["read_only"])
        criterion_ids = {
            criterion["id"] for criterion in packet["rubric"]["criteria"]
        }
        self.assertIn("host-neutral-core", criterion_ids)
        self.assertNotIn("adapter-source-binding", criterion_ids)

    def test_adapter_criteria_are_filtered(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "adapters" / "cursor" / "entry.md"
            target.parent.mkdir(parents=True)
            target.write_text("# Adapter", encoding="utf-8")
            packet = prepare_audit.prepare_audit_packet(
                target,
                RUBRIC_PATH,
            )
        criterion_ids = {
            criterion["id"] for criterion in packet["rubric"]["criteria"]
        }
        self.assertEqual("adapter", packet["target"]["asset_type"])
        self.assertIn("adapter-source-binding", criterion_ids)
        self.assertNotIn("host-neutral-core", criterion_ids)

    def test_markdown_uses_a_safe_fence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "prompt.md"
            target.write_text("Before\n```text\ninside\n```\nAfter", encoding="utf-8")
            packet = prepare_audit.prepare_audit_packet(target, RUBRIC_PATH)
            output = prepare_audit.render_markdown(packet)
        self.assertIn("````text", output)
        self.assertIn("```text", output)

    def test_missing_and_oversized_targets_are_rejected(self):
        with self.assertRaises(prepare_audit.AuditPreparationError):
            prepare_audit.prepare_audit_packet(
                Path("missing.md"),
                RUBRIC_PATH,
            )
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "large.md"
            target.write_text("12345", encoding="utf-8")
            with self.assertRaises(prepare_audit.AuditPreparationError):
                prepare_audit.prepare_audit_packet(
                    target,
                    RUBRIC_PATH,
                    max_bytes=4,
                )

    def test_invalid_rubric_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "prompt.md"
            target.write_text("# Prompt", encoding="utf-8")
            rubric = Path(temp_dir) / "rubric.json"
            rubric.write_text(
                json.dumps(
                    {
                        "asset_types": ["prompt"],
                        "criteria": [
                            {
                                "id": "duplicate",
                                "severity": "high",
                                "applies_to": ["all"],
                                "check": "Check",
                                "evidence": "Evidence",
                            },
                            {
                                "id": "duplicate",
                                "severity": "high",
                                "applies_to": ["all"],
                                "check": "Check",
                                "evidence": "Evidence",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(
                prepare_audit.AuditPreparationError,
                "Duplicate criterion",
            ):
                prepare_audit.prepare_audit_packet(target, rubric)


if __name__ == "__main__":
    unittest.main()

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_skill import validate_skill_dir


class ValidateSkillTests(unittest.TestCase):
    def _valid_skill(self, root: Path) -> Path:
        skill_dir = root / "base-example"
        for directory in ("scripts", "references", "assets", "tests"):
            (skill_dir / directory).mkdir(parents=True, exist_ok=True)
        (skill_dir / "README.md").write_text("# base-example\n", encoding="utf-8")
        (skill_dir / "SKILL.md").write_text(
            """---
name: base-example
description: Deterministic example.
metadata:
  version: "0.1.0"
category: executor
---

# Skill

## Workflow
Run one deterministic step.

## Verification
Run the unit test.

## Context & Side Effects
Reads and writes only the declared target.
""",
            encoding="utf-8",
        )
        return skill_dir

    def test_valid_skill_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report = validate_skill_dir(self._valid_skill(Path(temp_dir)))
        self.assertTrue(report["ok"], report["issues"])

    def test_placeholder_and_name_mismatch_fail(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = self._valid_skill(Path(temp_dir))
            content = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            content = content.replace("name: base-example", "name: wrong-name")
            content = content.replace("Run one deterministic step.", "TODO: fill this")
            (skill_dir / "SKILL.md").write_text(content, encoding="utf-8")
            report = validate_skill_dir(skill_dir)
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("NAME_DIRECTORY_MISMATCH", codes)
        self.assertIn("PLACEHOLDER_REMAINS", codes)

    def test_missing_directory_fails(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_dir = self._valid_skill(Path(temp_dir))
            (skill_dir / "assets").rmdir()
            report = validate_skill_dir(skill_dir)
        self.assertIn("REQUIRED_DIRECTORY_MISSING", {issue["code"] for issue in report["issues"]})


if __name__ == "__main__":
    unittest.main()

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_command import validate_command_contract


class ValidateCommandContractTests(unittest.TestCase):
    def _project_with_contract(self, root: Path, risk_level: str = "low") -> Path:
        skill_file = root / ".agents" / "skills" / "base-diff-loader" / "SKILL.md"
        skill_file.parent.mkdir(parents=True)
        skill_file.write_text("# diff loader\n", encoding="utf-8")
        agent_file = root / ".agents" / "agents" / "base-reviewer.md"
        agent_file.parent.mkdir(parents=True)
        agent_file.write_text("# reviewer contract\n", encoding="utf-8")
        command_file = root / ".agents" / "commands" / "review.md"
        command_file.parent.mkdir(parents=True)
        command_file.write_text(
            f"""---
name: review
description: "Run a repeatable review SOP"
kind: command-contract
execution_mode: ordered-workflow
risk_level: {risk_level}
skills: ["base-diff-loader"]
agents: ["base-reviewer"]
---

# Command Contract: review

## User Outcome
Return verified findings.

## Inputs & Preconditions
The caller supplies a change scope.

## Dependency Bindings
- Skill `base-diff-loader`: `.agents/skills/base-diff-loader/SKILL.md`
- Agent `base-reviewer`: `.agents/agents/base-reviewer.md`

## Workflow
1. Load the declared diff with `base-diff-loader`.
2. Delegate evidence review to `base-reviewer`.
3. Verify the returned findings against the contract.

## Human Gates
{"Approval is required before external publication." if risk_level == "high" else "No approval is required for this read-only SOP."}

## Verification Contract
Return file paths and unresolved risks.

## Failure & Resume
Stop on missing evidence and resume from the persisted state.

## Adapter Notes
The host adapter exposes its current operation entry.
""",
            encoding="utf-8",
        )
        return command_file

    def test_valid_contract_passes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            report = validate_command_contract(self._project_with_contract(root), root)
        self.assertTrue(report["ok"], report["issues"])
        self.assertEqual(3, report["contract"]["step_count"])

    def test_host_specific_content_and_missing_dependency_fail(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            command_file = self._project_with_contract(root)
            (root / ".agents" / "agents" / "base-reviewer.md").unlink()
            content = command_file.read_text(encoding="utf-8")
            content += '\nTask(subagent_type="generalPurpose")\n'
            command_file.write_text(content, encoding="utf-8")
            report = validate_command_contract(command_file, root)
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("HOST_SPECIFIC_CORE_CONTENT", codes)
        self.assertIn("AGENT_DEPENDENCY_MISSING", codes)

    def test_workflow_must_be_short_consecutive_and_end_with_verification(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            command_file = self._project_with_contract(root)
            content = command_file.read_text(encoding="utf-8")
            content = content.replace(
                """1. Load the declared diff with `base-diff-loader`.
2. Delegate evidence review to `base-reviewer`.
3. Verify the returned findings against the contract.""",
                """1. Load with `base-diff-loader`.
3. Delegate to `base-reviewer`.
4. Format.
5. Format.
6. Format.
7. Format.
8. Format.
9. Return the result.""",
            )
            command_file.write_text(content, encoding="utf-8")
            report = validate_command_contract(command_file, root)
        codes = {issue["code"] for issue in report["issues"]}
        self.assertIn("WORKFLOW_NUMBERING_INVALID", codes)
        self.assertIn("WORKFLOW_TOO_LONG", codes)
        self.assertIn("FINAL_STEP_NOT_VERIFICATION", codes)

    def test_high_risk_contract_requires_human_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            command_file = self._project_with_contract(root, risk_level="high")
            content = command_file.read_text(encoding="utf-8")
            content = content.replace(
                "Approval is required before external publication.",
                "None",
            )
            command_file.write_text(content, encoding="utf-8")
            report = validate_command_contract(command_file, root)
        self.assertIn(
            "HIGH_RISK_GATE_MISSING",
            {issue["code"] for issue in report["issues"]},
        )

    def test_required_section_must_have_content(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            command_file = self._project_with_contract(root)
            content = command_file.read_text(encoding="utf-8")
            content = content.replace(
                "## User Outcome\nReturn verified findings.",
                "## User Outcome\n",
            )
            command_file.write_text(content, encoding="utf-8")
            report = validate_command_contract(command_file, root)
        self.assertIn(
            "REQUIRED_SECTION_EMPTY",
            {issue["code"] for issue in report["issues"]},
        )


if __name__ == "__main__":
    unittest.main()

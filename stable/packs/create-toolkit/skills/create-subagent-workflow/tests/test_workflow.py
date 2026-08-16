import sys
import tempfile
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from workflow import (
    EXIT_BLOCKED,
    EXIT_RETRYABLE,
    EXIT_SUCCESS,
    EXIT_WAITING,
    initialize_state,
    load_state,
    resume_gate,
    retry_failed_stage,
    run_current_stage,
)


class CreateSubagentWorkflowTests(unittest.TestCase):
    def _initialize(
        self,
        root: Path,
        max_dependency_attempts: int = 3,
        max_validation_attempts: int = 3,
    ) -> Path:
        state_path = root / "docs" / "state" / "create-subagent" / "reviewer.json"
        initialize_state(
            state_path=state_path,
            project_root=root,
            name="reviewer",
            scope="base",
            description="Review changes and return evidence.",
            goal="Find correctness risks.",
            max_dependency_attempts=max_dependency_attempts,
            max_validation_attempts=max_validation_attempts,
        )
        return state_path

    def _create_skill(self, root: Path, name: str = "base-code-search") -> None:
        skill_file = root / ".agents" / "skills" / name / "SKILL.md"
        skill_file.parent.mkdir(parents=True, exist_ok=True)
        skill_file.write_text("# skill\n", encoding="utf-8")

    def _analyze(self, state_path: Path, skills=None):
        return resume_gate(
            state_path,
            "analyzed",
            "Capability decomposition complete",
            model_profile="synthesis",
            skills=skills or [],
            isolation_note="Search traces are noise to the caller.",
        )

    def _refine(self, state_path: Path) -> None:
        state = load_state(state_path)
        agent_file = Path(state["artifacts"]["agent_contract"])
        content = agent_file.read_text(encoding="utf-8")
        content = content.replace(
            "TODO: Define the role, decision boundary, and expected return contract.",
            "Review only the declared change and return evidence-backed findings.",
        )
        content = content.replace(
            "TODO: Define no more than seven high-level reasoning and execution stages.",
            "1. Inspect scope.\n2. Gather evidence.\n3. Return findings.",
        )
        content = content.replace(
            "TODO: Define authority limits, prohibited actions, and Human Gates.",
            "Do not modify files; ask before expanding scope.",
        )
        content = content.replace(
            "TODO: Define the evidence and summary the caller must receive.",
            "Return file paths, findings, and verification gaps.",
        )
        agent_file.write_text(content, encoding="utf-8")

    def test_happy_path_persists_analysis_and_adapter_gate(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._create_skill(root)
            state_path = self._initialize(root)

            state = load_state(state_path)
            self.assertEqual(("analyze", "waiting"), (state["current_stage"], state["status"]))

            code, _, _ = self._analyze(state_path, ["base-code-search"])
            self.assertEqual(EXIT_SUCCESS, code)
            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_WAITING, code)
            self.assertEqual(("refine", "waiting"), (state["current_stage"], state["status"]))

            self._refine(state_path)
            code, _, _ = resume_gate(state_path, "refined", "Contract completed")
            self.assertEqual(EXIT_SUCCESS, code)
            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_WAITING, code)
            self.assertEqual(("adapt", "waiting"), (state["current_stage"], state["status"]))
            self.assertTrue(state["artifacts"]["validation_report"]["ok"])

            adapter_file = root / ".cursor" / "agents" / "base-reviewer.md"
            adapter_file.parent.mkdir(parents=True)
            adapter_file.write_text("# rendered\n", encoding="utf-8")
            code, state, _ = resume_gate(
                state_path,
                "adapted",
                "Cursor adapter rendered",
                adapter="cursor",
                artifact=".cursor/agents/base-reviewer.md",
            )
            self.assertEqual(EXIT_SUCCESS, code)
            self.assertEqual(("complete", "completed"), (state["current_stage"], state["status"]))
            self.assertIn("cursor", state["artifacts"]["adapters"])

    def test_missing_dependency_can_be_created_then_retried(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = self._initialize(root)
            self._analyze(state_path, ["base-code-search"])

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_RETRYABLE, code)
            self.assertEqual("dependencies", state["current_stage"])
            self.assertFalse(state["artifacts"]["dependency_report"]["ok"])

            self._create_skill(root)
            code, _, _ = retry_failed_stage(state_path, "Dependency created")
            self.assertEqual(EXIT_SUCCESS, code)
            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_WAITING, code)
            self.assertEqual("refine", state["current_stage"])

    def test_validation_failure_is_retryable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = self._initialize(root)
            self._analyze(state_path)
            run_current_stage(state_path)
            resume_gate(state_path, "refined", "Intentionally incomplete")

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_RETRYABLE, code)
            self.assertEqual("validate", state["current_stage"])

            self._refine(state_path)
            code, _, _ = retry_failed_stage(state_path, "Contract fixed")
            self.assertEqual(EXIT_SUCCESS, code)
            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_WAITING, code)
            self.assertEqual("adapt", state["current_stage"])

    def test_retry_limit_blocks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = self._initialize(root, max_dependency_attempts=1)
            self._analyze(state_path, ["missing-skill"])
            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_BLOCKED, code)
            self.assertEqual("blocked", state["status"])

    def test_existing_contract_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / ".agents" / "agents" / "base-reviewer.md"
            target.parent.mkdir(parents=True)
            target.write_text("keep", encoding="utf-8")
            state_path = self._initialize(root)
            self._analyze(state_path)

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_BLOCKED, code)
            self.assertEqual("keep", target.read_text(encoding="utf-8"))
            self.assertEqual("TARGET_EXISTS", state["errors"][-1]["code"])

    def test_adapter_artifact_must_exist_inside_project(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = self._initialize(root)
            self._analyze(state_path)
            run_current_stage(state_path)
            self._refine(state_path)
            resume_gate(state_path, "refined", "Contract complete")
            run_current_stage(state_path)

            code, _, _ = resume_gate(
                state_path,
                "adapted",
                "Not actually rendered",
                adapter="cursor",
                artifact="../outside.md",
            )
            self.assertEqual(EXIT_BLOCKED, code)


if __name__ == "__main__":
    unittest.main()

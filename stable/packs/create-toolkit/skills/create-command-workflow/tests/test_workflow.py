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


class CreateCommandWorkflowTests(unittest.TestCase):
    def _initialize(
        self,
        root: Path,
        max_dependency_attempts: int = 3,
    ) -> Path:
        state_path = root / "docs" / "state" / "create-command" / "review.json"
        initialize_state(
            state_path=state_path,
            project_root=root,
            name="review",
            scope="",
            description="Run a repeatable review SOP.",
            outcome="Return verified findings.",
            max_dependency_attempts=max_dependency_attempts,
        )
        return state_path

    def _create_dependencies(self, root: Path) -> None:
        skill_file = root / ".agents" / "skills" / "base-diff-loader" / "SKILL.md"
        skill_file.parent.mkdir(parents=True, exist_ok=True)
        skill_file.write_text("# skill\n", encoding="utf-8")
        agent_file = root / ".agents" / "agents" / "base-reviewer.md"
        agent_file.parent.mkdir(parents=True, exist_ok=True)
        agent_file.write_text("# agent\n", encoding="utf-8")

    def _analyze(self, state_path: Path, with_dependencies: bool = True):
        return resume_gate(
            state_path,
            "analyzed",
            "SOP decomposition complete",
            risk_level="low",
            skills=["base-diff-loader"] if with_dependencies else [],
            agents=["base-reviewer"] if with_dependencies else [],
            composition_note="Load deterministically, isolate review, then verify.",
        )

    def _refine(self, state_path: Path) -> None:
        state = load_state(state_path)
        command_file = Path(state["artifacts"]["command_contract"])
        content = command_file.read_text(encoding="utf-8")
        content = content.replace(
            "TODO: Define required inputs, defaults, and preconditions.",
            "The caller supplies a change scope.",
        )
        content = content.replace(
            """1. TODO: Define the first deterministic or delegated step.
2. TODO: Verify the final result against the Verification Contract.""",
            """1. Load the declared diff with `base-diff-loader`.
2. Delegate review to `base-reviewer`.
3. Verify the returned findings against the Verification Contract.""",
        )
        content = content.replace(
            "TODO: Declare approval points, or explicitly state why none are required.",
            "No approval is required for this read-only SOP.",
        )
        content = content.replace(
            "TODO: Define machine checks, evidence, and the user-visible completion signal.",
            "Return file paths, findings, and unresolved risks.",
        )
        content = content.replace(
            "TODO: Define stop conditions, retry boundary, and persisted state needed to resume.",
            "Stop on missing evidence and resume from the persisted state.",
        )
        command_file.write_text(content, encoding="utf-8")

    def test_happy_path_reaches_adapter_gate_and_completes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._create_dependencies(root)
            state_path = self._initialize(root)
            code, _, _ = self._analyze(state_path)
            self.assertEqual(EXIT_SUCCESS, code)

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_WAITING, code)
            self.assertEqual(("refine", "waiting"), (state["current_stage"], state["status"]))
            self._refine(state_path)
            resume_gate(state_path, "refined", "Contract completed")

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_WAITING, code)
            self.assertEqual(("adapt", "waiting"), (state["current_stage"], state["status"]))
            self.assertTrue(state["artifacts"]["validation_report"]["ok"])

            adapter_file = root / ".cursor" / "commands" / "review.md"
            adapter_file.parent.mkdir(parents=True)
            adapter_file.write_text("# rendered\n", encoding="utf-8")
            code, state, _ = resume_gate(
                state_path,
                "adapted",
                "Cursor command rendered",
                adapter="cursor",
                artifact=".cursor/commands/review.md",
            )
            self.assertEqual(EXIT_SUCCESS, code)
            self.assertEqual(("complete", "completed"), (state["current_stage"], state["status"]))

    def test_missing_dependencies_can_be_retried(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = self._initialize(root)
            self._analyze(state_path)

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_RETRYABLE, code)
            self.assertEqual(2, len(state["artifacts"]["dependency_report"]["missing"]))

            self._create_dependencies(root)
            self.assertEqual(EXIT_SUCCESS, retry_failed_stage(state_path, "Created dependencies")[0])
            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_WAITING, code)
            self.assertEqual("refine", state["current_stage"])

    def test_validation_failure_is_retryable(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._create_dependencies(root)
            state_path = self._initialize(root)
            self._analyze(state_path)
            run_current_stage(state_path)
            resume_gate(state_path, "refined", "Intentionally incomplete")

            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_RETRYABLE, code)
            self.assertEqual("validate", state["current_stage"])
            self._refine(state_path)
            self.assertEqual(EXIT_SUCCESS, retry_failed_stage(state_path, "Fixed contract")[0])
            self.assertEqual(EXIT_WAITING, run_current_stage(state_path)[0])

    def test_dependency_retry_limit_blocks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = self._initialize(root, max_dependency_attempts=1)
            self._analyze(state_path)
            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_BLOCKED, code)
            self.assertEqual("blocked", state["status"])

    def test_existing_contract_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            target = root / ".agents" / "commands" / "review.md"
            target.parent.mkdir(parents=True)
            target.write_text("keep", encoding="utf-8")
            state_path = self._initialize(root)
            self._analyze(state_path, with_dependencies=False)
            code, state, _ = run_current_stage(state_path)
            self.assertEqual(EXIT_BLOCKED, code)
            self.assertEqual("keep", target.read_text(encoding="utf-8"))
            self.assertEqual("TARGET_EXISTS", state["errors"][-1]["code"])


if __name__ == "__main__":
    unittest.main()

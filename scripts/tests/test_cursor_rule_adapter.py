import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER_PATH = REPO_ROOT / "scripts" / "install-pack.py"
RENDERER_PATH = (
    REPO_ROOT
    / "stable"
    / "packs"
    / "create-toolkit"
    / "adapters"
    / "cursor"
    / "render_rule.py"
)


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


installer = _load("install_pack_for_cursor_rule_adapter", INSTALLER_PATH)
renderer = _load("render_cursor_rule", RENDERER_PATH)


def rule_block(activation: str = "always", paths: str = "[]") -> str:
    return f"""<!-- cg-rule-contract:safe-edit:start -->
## Rule: Safe Edit
- ID: `safe-edit`
- Activation: {activation}
- Description: Bound risky changes before editing
- Paths: {paths}
- Trigger: When a change may affect protected behavior
- Rationale: Missing the boundary can cause irreversible regressions

### Behavior
- MUST identify the exact modification scope before writing.
- MUST NOT modify protected files without explicit authorization.

### Exclusions
- Routine read-only inspection is outside this Rule.

### Verification
- Review the final diff and test evidence before reporting completion.
<!-- cg-rule-contract:safe-edit:end -->
"""


class CursorRuleAdapterTests(unittest.TestCase):
    def _root(self, block: str) -> Path:
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)
        installer.install_pack("create-toolkit", root, REPO_ROOT)
        (root / "AGENTS.md").write_text("# Project\n\n" + block, encoding="utf-8")
        return root

    def tearDown(self):
        if hasattr(self, "temp_dir"):
            self.temp_dir.cleanup()

    def test_always_rule_renders_and_refuses_overwrite(self):
        root = self._root(rule_block())
        output = renderer.render_cursor_rule(root, Path("AGENTS.md"), "safe-edit")
        content = output.read_text(encoding="utf-8")
        self.assertIn("alwaysApply: true", content)
        self.assertIn("Generated from AGENTS.md rule-contract:safe-edit", content)
        with self.assertRaises(FileExistsError):
            renderer.render_cursor_rule(root, Path("AGENTS.md"), "safe-edit")

    def test_single_path_rule_renders_auto_attached_glob(self):
        root = self._root(rule_block("paths", '["src/critical/**"]'))
        output = renderer.render_cursor_rule(root, Path("AGENTS.md"), "safe-edit")
        content = output.read_text(encoding="utf-8")
        self.assertIn('globs: "src/critical/**"', content)
        self.assertIn("alwaysApply: false", content)

    def test_multiple_paths_are_not_guessed(self):
        root = self._root(
            rule_block("paths", '["src/critical/**", "config/*.yaml"]')
        )
        with self.assertRaisesRegex(ValueError, "exactly one path glob"):
            renderer.render_cursor_rule(root, Path("AGENTS.md"), "safe-edit")


if __name__ == "__main__":
    unittest.main()

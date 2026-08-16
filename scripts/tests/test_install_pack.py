import importlib.util
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
INSTALLER_PATH = REPO_ROOT / "scripts" / "install-pack.py"
SPEC = importlib.util.spec_from_file_location("install_pack", INSTALLER_PATH)
install_pack_module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(install_pack_module)


class InstallPackTests(unittest.TestCase):
    def test_create_toolkit_splits_author_layer_and_cursor_adapter(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            install_pack_module.install_pack("create-toolkit", target, REPO_ROOT)

            self.assertTrue(
                (target / ".agents" / "skills" / "create-skill-workflow" / "SKILL.md").is_file()
            )
            self.assertTrue(
                (target / ".agents" / "skills" / "create-subagent-workflow" / "SKILL.md").is_file()
            )
            self.assertTrue(
                (target / ".agents" / "skills" / "create-command-workflow" / "SKILL.md").is_file()
            )
            self.assertTrue(
                (target / ".agents" / "skills" / "audit-agent-assets" / "SKILL.md").is_file()
            )
            self.assertTrue(
                (target / ".agents" / "skills" / "create-rule-workflow" / "SKILL.md").is_file()
            )
            cursor_adapter = target / ".cursor" / "commands" / "create-skill.md"
            self.assertTrue(cursor_adapter.is_file())
            self.assertIn(
                "@.agents/skills/create-skill-workflow/SKILL.md",
                cursor_adapter.read_text(encoding="utf-8"),
            )
            subagent_adapter = target / ".cursor" / "commands" / "create-subagent.md"
            self.assertIn(
                "@.agents/skills/create-subagent-workflow/SKILL.md",
                subagent_adapter.read_text(encoding="utf-8"),
            )
            command_adapter = target / ".cursor" / "commands" / "create-command.md"
            command_content = command_adapter.read_text(encoding="utf-8")
            self.assertIn(
                "@.agents/skills/create-command-workflow/SKILL.md",
                command_content,
            )
            rule_adapter = target / ".cursor" / "commands" / "create-rule.md"
            self.assertIn(
                "@.agents/skills/create-rule-workflow/SKILL.md",
                rule_adapter.read_text(encoding="utf-8"),
            )
            self.assertTrue(
                (
                    target
                    / ".cursor"
                    / "adapters"
                    / "create-subagent"
                    / "render_subagent.py"
                ).is_file()
            )
            self.assertTrue(
                (
                    target
                    / ".cursor"
                    / "adapters"
                    / "create-command"
                    / "render_command.py"
                ).is_file()
            )
            self.assertTrue(
                (
                    target
                    / ".cursor"
                    / "adapters"
                    / "create-rule"
                    / "render_rule.py"
                ).is_file()
            )
            for retired_path in (
                target / ".cursor" / "commands" / "session-summary.md",
                target / ".cursor" / "commands" / "create-project.md",
                target / ".cursor" / "agents" / "base-skill-engineer.md",
                target / ".cursor" / "skills" / "base-skill-generator",
                target / ".cursor" / "skills" / "base-rule-generator",
                target / ".cursor" / "skills" / "base-closure-validator",
                target / ".cursor" / "skills" / "base-prompt-auditor",
                target / ".cursor" / "skills" / "base-inventory-updater",
                target / ".cursor" / "standards" / "skill-meta-standard.md",
            ):
                with self.subTest(retired_path=retired_path):
                    self.assertFalse(retired_path.exists())
            record = target / ".agents" / "installed-packs.yaml"
            self.assertTrue(record.is_file())
            self.assertFalse((target / ".cursor" / "installed-packs.yaml").exists())
            installed = install_pack_module.load_yaml_simple(record)
            self.assertEqual(
                12,
                len(installed["installed"]["create-toolkit"]["files"]),
            )

            install_pack_module.uninstall_pack("create-toolkit", target)
            self.assertFalse((target / ".agents" / "skills" / "create-skill-workflow").exists())
            self.assertFalse(cursor_adapter.exists())

    def test_mapping_rejects_parent_traversal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            with self.assertRaises(ValueError):
                install_pack_module._mapping_destination(
                    target,
                    {
                        "target_root": ".agents",
                        "target": "../outside.txt",
                    },
                )
            for unsafe_target in ("", ".", "\\outside.txt", "C:outside.txt"):
                with self.subTest(unsafe_target=unsafe_target):
                    with self.assertRaises(ValueError):
                        install_pack_module._mapping_destination(
                            target,
                            {
                                "target_root": ".agents",
                                "target": unsafe_target,
                            },
                        )

    def test_fallback_manifest_parser_keeps_target_roots(self):
        original = install_pack_module.HAS_YAML
        install_pack_module.HAS_YAML = False
        try:
            manifest = install_pack_module.load_yaml_simple(
                REPO_ROOT / "stable" / "packs" / "create-toolkit" / "install-manifest.yaml"
            )
        finally:
            install_pack_module.HAS_YAML = original
        self.assertEqual(".agents", manifest["record_root"])
        self.assertEqual(".agents", manifest["mappings"][0]["target_root"])

    def test_upgrade_migrates_only_matching_legacy_record(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            legacy_record = target / ".cursor" / "installed-packs.yaml"
            legacy_record.parent.mkdir(parents=True)
            retired_file = target / ".cursor" / "commands" / "session-summary.md"
            retired_file.parent.mkdir(parents=True)
            retired_file.write_text("legacy", encoding="utf-8")
            install_pack_module.dump_yaml_simple(
                {
                    "installed": {
                        "create-toolkit": {
                            "version": "1.0.0",
                            "files": ["commands/session-summary.md"],
                        },
                        "other-pack": {
                            "version": "9.9.9",
                            "files": ["commands/other.md"],
                        },
                    }
                },
                legacy_record,
            )

            install_pack_module.install_pack("create-toolkit", target, REPO_ROOT)

            current = install_pack_module.load_yaml_simple(
                target / ".agents" / "installed-packs.yaml"
            )
            legacy = install_pack_module.load_yaml_simple(legacy_record)
            self.assertEqual("1.6.0", str(current["installed"]["create-toolkit"]["version"]))
            self.assertIn(
                "commands/session-summary.md",
                current["installed"]["create-toolkit"]["retained_unmanaged"],
            )
            self.assertTrue(retired_file.is_file())
            self.assertNotIn("create-toolkit", legacy["installed"])
            self.assertIn("other-pack", legacy["installed"])

    def test_upgrade_retains_dropped_legacy_assets_as_unmanaged(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            retired_file = target / ".cursor" / "commands" / "session-summary.md"
            retired_file.parent.mkdir(parents=True)
            retired_file.write_text("legacy", encoding="utf-8")
            record_file = target / ".agents" / "installed-packs.yaml"
            record_file.parent.mkdir(parents=True)
            install_pack_module.dump_yaml_simple(
                {
                    "installed": {
                        "create-toolkit": {
                            "version": "1.3.0",
                            "files": [".cursor/commands/session-summary.md"],
                        }
                    }
                },
                record_file,
            )

            install_pack_module.install_pack("create-toolkit", target, REPO_ROOT)

            current = install_pack_module.load_yaml_simple(record_file)
            entry = current["installed"]["create-toolkit"]
            self.assertTrue(retired_file.is_file())
            self.assertIn(
                ".cursor/commands/session-summary.md",
                entry["retained_unmanaged"],
            )

            install_pack_module.uninstall_pack("create-toolkit", target)
            self.assertTrue(retired_file.is_file())

    def test_legacy_record_entry_stays_under_cursor(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir)
            resolved = install_pack_module._installed_entry_path(target, "commands/example.md")
            self.assertEqual(target / ".cursor" / "commands" / "example.md", resolved)


if __name__ == "__main__":
    unittest.main()

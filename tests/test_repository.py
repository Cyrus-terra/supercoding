"""Deterministic repository checks; these are not model behavior evaluations."""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("validate_supercoding", ROOT / "scripts/validate_skill.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class RepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="supercoding tests ")
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name) / "仓库 with spaces"
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns("__pycache__", ".git"))
        self.skill = self.repo / "skills/supercoding"

    def update_entry(self, old, new):
        path = self.skill / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def assert_invalid(self, fragment):
        errors, _ = VALIDATOR.validate(self.repo)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_valid_repository(self):
        errors, stats = VALIDATOR.validate(self.repo)
        self.assertEqual(errors, [])
        self.assertEqual(stats["eval_cases"], 22)
        self.assertEqual(stats["reference_files"], 8)

    def test_standalone_skill_needs_no_repository_resources(self):
        standalone = Path(self.temporary.name) / "standalone/supercoding"
        shutil.copytree(self.skill, standalone)
        errors, stats = VALIDATOR.validate(standalone)
        self.assertEqual(errors, [])
        self.assertNotIn("eval_cases", stats)

    def test_invalid_skill_name(self):
        self.update_entry("name: supercoding", "name: SuperCoding")
        self.assert_invalid("name must be valid")

    def test_missing_frontmatter(self):
        path = self.skill / "SKILL.md"
        path.write_text("# missing metadata\n", encoding="utf-8")
        self.assert_invalid("Missing opening")

    def test_missing_reference(self):
        self.update_entry("references/styles-and-ui.md", "references/missing.md")
        self.assert_invalid("missing linked file")

    def test_path_escape(self):
        self.update_entry("references/styles-and-ui.md", "../../README.md")
        self.assert_invalid("link escapes package")

    def test_development_material_not_in_runtime(self):
        (self.skill / "evals").mkdir()
        self.assert_invalid("Development directory inside runtime")

    def test_version_drift(self):
        path = self.repo / ".codebuddy-plugin/plugin.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["version"] = "9.0.0"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assert_invalid("versions must match")

    def test_malformed_evals(self):
        (self.repo / "tests/evals/evals.json").write_text("{", encoding="utf-8")
        self.assert_invalid("Cannot validate evals")

    def test_duplicate_eval_id(self):
        path = self.repo / "tests/evals/evals.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["evals"][1]["id"] = data["evals"][0]["id"]
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assert_invalid("id must be unique")

    def test_judgment_scenario_categories_are_required(self):
        path = self.repo / "tests/evals/evals.json"
        original = json.loads(path.read_text(encoding="utf-8"))
        for category in ("debugging-hypothesis", "review-feedback-validation"):
            with self.subTest(category=category):
                data = {**original, "evals": [case for case in original["evals"] if case["category"] != category]}
                path.write_text(json.dumps(data), encoding="utf-8")
                self.assert_invalid("Missing scenario categories: " + category)
        path.write_text(json.dumps(original), encoding="utf-8")

    def test_broken_documentation_link(self):
        path = self.repo / "README.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text + "\n[bad](docs/missing.md)\n", encoding="utf-8")
        self.assert_invalid("missing or external link")

    def test_reference_modules_have_scenarios(self):
        cases = json.loads((self.repo / "tests/evals/evals.json").read_text(encoding="utf-8"))["evals"]
        covered = {name for case in cases for name in case["reference_files"]}
        expected = {f"references/{name}" for name in VALIDATOR.REFERENCES}
        self.assertEqual(covered, expected)
        self.assertEqual({case["should_trigger"] for case in cases}, {True, False})

    def test_hook_output_for_both_client_environments(self):
        for key in ("CLAUDE_PLUGIN_ROOT", "CODEBUDDY_PLUGIN_ROOT"):
            with self.subTest(client=key):
                environment = os.environ.copy()
                environment[key] = str(self.repo)
                result = subprocess.run(
                    [sys.executable, "-B", str(self.repo / "hooks/session-start.py")],
                    cwd=self.temporary.name,
                    env=environment,
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=True,
                )
                output = json.loads(result.stdout)
                specific = output["hookSpecificOutput"]
                self.assertEqual(specific["hookEventName"], "SessionStart")
                context = specific["additionalContext"]
                self.assertIn(str(self.skill / "SKILL.md"), context)
                self.assertIn("project standards take priority", context)
                self.assertIn("no automatic full-repository audit or remediation", context)
                self.assertIn("shared English rules", context)
                self.assertIn("user's preferred language", context)
                self.assertNotIn("SKILL.zh-CN.md", context)
                self.assertIn("Skip pure README/document/report writing", context)
                self.assertIn("tiny tasks may use the entry alone", context)
                self.assertLess(len(context), 1000)
                self.assertNotIn("## Lightweight workflow", context)
                self.assertEqual(result.stderr, "")

    def test_hook_shell_expansion_for_claude_codebuddy_and_gemini(self):
        command = json.loads((self.repo / "hooks/hooks.json").read_text())["hooks"]["SessionStart"][0]["hooks"][0]["command"]
        for client in ("claude", "codebuddy", "gemini"):
            with self.subTest(client=client):
                environment = os.environ.copy()
                environment.pop("CLAUDE_PLUGIN_ROOT", None)
                environment.pop("extensionPath", None)
                rendered = command
                if client == "gemini":
                    rendered = rendered.replace("${extensionPath}", str(self.repo))
                else:
                    environment["CLAUDE_PLUGIN_ROOT"] = str(self.repo)
                result = subprocess.run(["/bin/sh", "-c", rendered], env=environment, cwd=self.temporary.name, capture_output=True, text=True, timeout=10, check=True)
                self.assertIn(str(self.skill / "SKILL.md"), json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"])

    def test_hermes_registration_and_first_turn_reminder(self):
        spec = importlib.util.spec_from_file_location("hermes_supercoding_test", self.repo / ".hermes-plugin/__init__.py")
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        class Context:
            def register_skill(self, name, path, description):
                self.skill = (name, path, description)
            def register_hook(self, event, callback):
                self.hook = (event, callback)
        context = Context()
        adapter.register(context)
        self.assertEqual(context.skill[0], "supercoding")
        self.assertEqual(context.skill[1], (self.skill / "SKILL.md").resolve())
        self.assertIn("coding", context.skill[2])
        callback = context.hook[1]
        self.assertIsNone(callback(is_first_turn=False))
        self.assertIsNone(callback(is_first_turn=True, platform="subagent"))
        self.assertIn("supercoding:supercoding", callback(is_first_turn=True)["context"])

    def test_documented_shell_blocks_parse(self):
        import re
        documents = [self.repo / "README.md", self.repo / "README.zh-CN.md", *self.repo.glob("docs/installation*.md"), *self.repo.glob("docs/clients/*.md")]
        for document in documents:
            for block in re.findall(r"```sh\n(.*?)```", document.read_text(), re.DOTALL):
                for shell in ("sh", "bash", "zsh"):
                    executable = shutil.which(shell)
                    if executable:
                        result = subprocess.run([executable, "-n"], input=block, text=True, capture_output=True, timeout=10)
                        self.assertEqual(result.returncode, 0, (document, shell, result.stderr))

    def test_openclaw_runtime_entry_is_dependency_free(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node unavailable")
        result = subprocess.run([node, "--input-type=module", "-e", "const {default: plugin} = await import(process.argv[1]); if (plugin.id !== 'supercoding' || typeof plugin.register !== 'function') process.exit(1); plugin.register({});", (self.repo / "index.js").as_uri()], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_new_client_version_drift_is_rejected(self):
        for manifest in ("gemini-extension.json", ".codex-plugin/plugin.json", "package.json", "openclaw.plugin.json"):
            with self.subTest(manifest=manifest):
                path = self.repo / manifest
                text = path.read_text()
                path.write_text(text.replace('"1.3.0"', '"9.0.0"'))
                self.assert_invalid("versions must match")
                path.write_text(text)

    def test_hook_missing_entry_fails(self):
        (self.skill / "SKILL.md").rename(self.skill / "entry.disabled")
        result = subprocess.run(
            [sys.executable, "-B", str(self.repo / "hooks/session-start.py")],
            capture_output=True, text=True, timeout=10,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("supercoding entry not found", result.stderr)

    def test_runtime_has_one_shared_rule_set(self):
        expected = {"SKILL.md", *(f"references/{name}" for name in VALIDATOR.REFERENCES)}
        actual = {str(path.relative_to(self.skill)) for path in self.skill.rglob("*.md")}
        self.assertEqual(actual, expected)

    def test_translated_runtime_entry_is_rejected(self):
        shutil.copy2(self.skill / "SKILL.md", self.skill / "SKILL.zh-CN.md")
        self.assert_invalid("eight shared English references")

    def test_translated_reference_is_rejected(self):
        path = self.skill / "references/performance.md"
        shutil.copy2(path, path.with_name("performance.zh-CN.md"))
        self.assert_invalid("eight shared English references")

    def test_missing_runtime_reference_is_rejected(self):
        (self.skill / "references/performance.md").unlink()
        self.assert_invalid("Missing or external resource")

    def test_document_language_switch_is_required(self):
        path = self.repo / "docs/installation.zh-CN.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("[English](installation.md)", "English"), encoding="utf-8")
        self.assert_invalid("missing language switch")

    def test_reference_links_are_document_relative(self):
        path = self.skill / "references/performance.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text + "\n[Entry](../SKILL.md)\n", encoding="utf-8")
        errors, _ = VALIDATOR.validate(self.repo)
        self.assertEqual(errors, [])

    def test_nested_discoverable_entry_is_rejected(self):
        directory = self.skill / "chinese"
        directory.mkdir()
        shutil.copy2(self.skill / "SKILL.md", directory / "SKILL.md")
        self.assert_invalid("exactly one discoverable")

    def test_missing_translated_document(self):
        (self.repo / "docs/installation.zh-CN.md").unlink()
        self.assert_invalid("Cannot read installation.zh-CN.md")

    def test_chinese_readme_links_are_checked(self):
        path = self.repo / "README.zh-CN.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text + "\n[bad](docs/missing.md)\n", encoding="utf-8")
        self.assert_invalid("missing or external link")

    def test_invalid_eval_reference(self):
        path = self.repo / "tests/evals/evals.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["evals"][0]["reference_files"] = ["references/missing.md"]
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assert_invalid("invalid reference")

    def test_empty_eval_assertions(self):
        path = self.repo / "tests/evals/evals.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["evals"][0]["assertions"] = []
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assert_invalid("assertions cannot be empty")

    def test_scenario_assertion_count(self):
        cases = json.loads((self.repo / "tests/evals/evals.json").read_text(encoding="utf-8"))["evals"]
        self.assertEqual(len(cases), 22)
        self.assertEqual(sum(len(case["assertions"]) for case in cases), 83)

    def test_only_public_guides_have_translations(self):
        actual = {str(path.relative_to(self.repo)) for path in self.repo.rglob("*.zh-CN.*")}
        expected = {"README.zh-CN.md", "docs/installation.zh-CN.md"}
        expected.update(f"docs/clients/{client}.zh-CN.md" for client in VALIDATOR.CLIENTS)
        self.assertEqual(actual, expected)

    def test_cli_default_root_independent_of_cwd(self):
        result = subprocess.run(
            [sys.executable, "-B", str(self.repo / "scripts/validate_skill.py")],
            cwd=self.temporary.name,
            capture_output=True, text=True, timeout=10, check=True,
        )
        self.assertIn("22 scenarios", result.stdout)
        self.assertIn("NOT evaluated", result.stdout)


if __name__ == "__main__":
    unittest.main()

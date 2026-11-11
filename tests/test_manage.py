"""Filesystem and release-boundary tests; no live downloads or user installations."""

from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import manage as manager


class ManageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="supercoding 管理 tests ")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.source = self.base / "source/supercoding"
        shutil.copytree(ROOT / "skills/supercoding", self.source)
        self.target = self.base / "client/skills/supercoding"
        self.args = SimpleNamespace(command="install", target=str(self.target), client=None, source=str(self.source), version=None, dry_run=False, replace=False)

    def run_command(self, command, **kwargs):
        self.args.command = command
        for key, value in kwargs.items():
            setattr(self.args, key, value)
        output = io.StringIO()
        with redirect_stdout(output):
            manager.restore(self.args) if command == "rollback" else manager.apply(self.args)
        return output.getvalue()

    def newer_source(self):
        entry = self.source / "SKILL.md"
        entry.write_text(entry.read_text(encoding="utf-8").replace('version: "1.3.0"', 'version: "1.10.0"'), encoding="utf-8")

    def snapshot(self):
        return {p.relative_to(self.base).as_posix(): p.read_bytes() for p in self.base.rglob("*") if p.is_file()}

    def test_cli_install_check_update_rollback_end_to_end(self):
        command = [sys.executable, "-B", str(ROOT / "scripts/manage.py")]
        def run(action, *options):
            result = subprocess.run([*command, action, "--target", str(self.target), *options], cwd=self.base, capture_output=True, text=True, encoding="utf-8", timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            return result.stdout
        run("install", "--source", str(self.source))
        self.newer_source()
        self.assertIn("1.10.0", run("check", "--source", str(self.source)))
        run("update", "--source", str(self.source), "--dry-run")
        self.assertEqual(manager.installed_version(self.target), "1.3.0")
        run("update", "--source", str(self.source))
        self.assertEqual(manager.installed_version(self.target), "1.10.0")
        run("rollback")
        self.assertEqual(manager.installed_version(self.target), "1.3.0")

    def test_install_update_rollback_preserves_both_versions(self):
        self.run_command("install")
        self.newer_source()
        self.run_command("update")
        self.assertEqual(manager.installed_version(self.target), "1.10.0")
        self.assertEqual(len(list((manager.state_root(self.target) / "backups").glob("*/SKILL.md"))), 1)
        self.run_command("rollback")
        self.assertEqual(manager.installed_version(self.target), "1.3.0")
        self.assertTrue(manager.inspection(self.target)[2])
        self.run_command("rollback")
        self.assertEqual(manager.installed_version(self.target), "1.10.0")

    def test_check_and_preview_have_no_writes(self):
        self.run_command("install")
        self.newer_source()
        before = self.snapshot()
        with patch.object(Path, "open", autospec=True, side_effect=Path.open) as opened:
            self.assertIn("1.10.0", self.run_command("check"))
            self.assertIn("changed files", self.run_command("update", dry_run=True))
            for call in opened.call_args_list:
                mode = call.args[1] if len(call.args) > 1 else call.kwargs.get("mode", "r")
                self.assertFalse(any(flag in mode for flag in "wax+"), call)
        self.assertEqual(before, self.snapshot())

    def test_check_absent_does_not_create_parent(self):
        self.run_command("check")
        self.assertFalse(self.target.parent.exists())

    def test_install_refuses_existing_copy_even_replace(self):
        self.run_command("install")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.run_command("install", replace=True)

    def test_custom_files_require_replace_and_survive_backup(self):
        self.run_command("install")
        custom = self.target / "custom.txt"
        custom.write_text("my notes", encoding="utf-8")
        self.newer_source()
        with self.assertRaisesRegex(ValueError, "modified target"):
            self.run_command("update")
        self.run_command("update", replace=True)
        backups = manager.state_root(self.target) / "backups"
        self.assertEqual(next(backups.glob("*/custom.txt")).read_text(encoding="utf-8"), "my notes")
        self.run_command("rollback")
        self.assertEqual(custom.read_text(encoding="utf-8"), "my notes")
        self.assertFalse(manager.inspection(self.target)[2])

    def test_unmanaged_snapshot_requires_explicit_adoption(self):
        shutil.copytree(self.source, self.target)
        with self.assertRaisesRegex(ValueError, "unmanaged"):
            self.run_command("update")
        self.run_command("update", replace=True)
        self.assertTrue(manager.inspection(self.target)[2])

    def test_numeric_version_order_and_downgrade_refusal(self):
        self.assertGreater(manager.version_key("1.10.0"), manager.version_key("1.9.0"))
        self.newer_source()
        self.run_command("install")
        entry = self.source / "SKILL.md"
        entry.write_text(entry.read_text(encoding="utf-8").replace("1.10.0", "1.3.0"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "downgrades"):
            self.run_command("update")

    def test_symlink_target_parent_and_state_refused(self):
        self.target.parent.mkdir(parents=True)
        try:
            self.target.symlink_to(self.source, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink creation unavailable on this host")
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.run_command("install")
        self.target.unlink()
        state = manager.state_root(self.target)
        state.symlink_to(self.source, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.run_command("install")

    def test_overlap_and_non_skill_target_refused(self):
        with self.assertRaisesRegex(ValueError, "overlap"):
            self.run_command("install", target=str(self.source))
        unrelated = self.base / "other/supercoding"
        unrelated.mkdir(parents=True)
        (unrelated / "important.txt").write_text("preserve", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "identifiable"):
            self.run_command("update", target=str(unrelated), replace=True)
        self.assertEqual((unrelated / "important.txt").read_text(encoding="utf-8"), "preserve")

    def test_switch_failure_restores_original_and_receipt(self):
        self.run_command("install")
        original = manager.inventory(self.target)
        old_receipt = manager.read_json(manager.state_root(self.target) / "receipt.json")
        self.newer_source()
        rename = Path.rename

        def fail_stage(path, dest):
            if path.name.startswith("stage-"):
                raise OSError("simulated switch failure")
            return rename(path, dest)

        with patch.object(Path, "rename", fail_stage):
            with self.assertRaisesRegex(OSError, "simulated"):
                self.run_command("update")
        self.assertEqual(manager.inventory(self.target), original)
        self.assertEqual(manager.read_json(manager.state_root(self.target) / "receipt.json"), old_receipt)

    def test_receipt_failure_restores_old_install(self):
        self.run_command("install")
        self.newer_source()
        write = manager.write_json
        failed = False

        def fail_receipt(path, value):
            nonlocal failed
            if path.name == "receipt.json" and not failed:
                failed = True
                raise OSError("disk error")
            return write(path, value)

        with patch.object(manager, "write_json", fail_receipt):
            with self.assertRaisesRegex(OSError, "disk error"):
                self.run_command("update")
        self.assertEqual(manager.installed_version(self.target), "1.3.0")
        self.assertTrue(manager.inspection(self.target)[2])

    def test_concurrent_operation_refused(self):
        with manager.locked(self.target):
            with self.assertRaisesRegex(ValueError, "lock"):
                self.run_command("install")

    def test_interrupted_update_recovery(self):
        self.run_command("install")
        state = manager.state_root(self.target)
        old_receipt = manager.read_json(state / "receipt.json")
        old_files = manager.inventory(self.target)
        backup = manager.backup_path(state)
        backup.parent.mkdir()
        self.target.rename(backup)
        manager.write_json(state / "transaction.json", {"target": str(self.target), "backup": backup.name, "old_files": old_files, "old_receipt": old_receipt})
        self.run_command("rollback")
        self.assertEqual(manager.installed_version(self.target), "1.3.0")
        self.assertFalse((state / "transaction.json").exists())

    def test_interrupted_rollback_after_move_completes_receipt(self):
        self.run_command("install")
        self.newer_source()
        self.run_command("update")
        state = manager.state_root(self.target)
        backup = next(p for p in (state / "backups").iterdir() if p.is_dir())
        metadata = manager.read_json(backup.with_suffix(".json"))
        displaced = manager.backup_path(state)
        self.target.rename(displaced)
        backup.rename(self.target)
        manager.write_json(state / "transaction.json", {"target": str(self.target), "backup": backup.name, "old_files": metadata["files"], "old_receipt": metadata["receipt"]})
        self.run_command("rollback")
        self.assertEqual(manager.installed_version(self.target), "1.3.0")
        self.assertTrue(manager.inspection(self.target)[2])

    def test_tampered_backup_refused(self):
        self.run_command("install")
        self.newer_source()
        self.run_command("update")
        backup = next((manager.state_root(self.target) / "backups").glob("*/SKILL.md"))
        backup.write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "contents differ"):
            self.run_command("rollback")
        self.assertEqual(manager.installed_version(self.target), "1.10.0")

    def test_unchanged_update_creates_no_backup(self):
        self.run_command("install")
        self.assertIn("nothing changed", self.run_command("update"))
        self.assertFalse((manager.state_root(self.target) / "backups").exists())

    def archive(self, additions=None, root=None):
        commit = "a" * 40
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            for name in manager.FILES:
                archive.writestr(f"{root or ('supercoding-' + commit)}/skills/supercoding/{name}", (self.source / name).read_bytes())
            for path, content in additions or []:
                archive.writestr(path, content)
        return buffer.getvalue(), commit

    def test_release_download_is_bound_to_immutable_commit(self):
        data, commit = self.archive()
        with patch.object(manager, "api", side_effect=[{"tag_name": "v1.3.0", "draft": False, "prerelease": False}, {"sha": commit}]), patch.object(manager, "download", return_value=data) as download:
            bundle = manager.remote_bundle()
        self.assertEqual(bundle["commit"], commit)
        self.assertEqual(bundle["version"], "1.3.0")
        self.assertTrue(download.call_args.args[0].endswith(commit))

    def test_mocked_release_full_lifecycle_preserves_hashes_and_neighbors(self):
        self.args.source = None
        self.args.version = "1.3.0"
        old_data, old_commit = self.archive()
        self.newer_source()
        new_data, _ = self.archive(root="supercoding-" + "b" * 40)
        versions = {"1.3.0": (old_data, old_commit), "1.10.0": (new_data, "b" * 40)}
        def api(path):
            tag = path.rsplit("/", 1)[-1]
            version = tag.removeprefix("v")
            if path.startswith("releases/"):
                return {"tag_name": tag, "draft": False, "prerelease": False}
            return {"sha": versions[version][1]}
        def download(url, limit):
            return next(data for data, commit in versions.values() if url.endswith(commit))
        self.target.parent.mkdir(parents=True)
        neighbor = self.target.parent / "other-skill.txt"
        neighbor.write_bytes(b"unrelated")
        with patch.object(manager, "api", side_effect=api), patch.object(manager, "download", side_effect=download):
            self.run_command("install")
            old_files = manager.inventory(self.target)
            old_receipt = manager.read_json(manager.state_root(self.target) / "receipt.json")
            self.assertEqual(old_receipt["commit"], old_commit)
            self.assertEqual(set(old_files), manager.FILES)
            self.assertEqual(len(old_files), 9)
            before = self.snapshot()
            self.run_command("check", version="1.10.0")
            self.run_command("update", dry_run=True)
            self.assertEqual(before, self.snapshot())
            self.run_command("update", dry_run=False)
            receipt = manager.read_json(manager.state_root(self.target) / "receipt.json")
            self.assertEqual(receipt["commit"], "b" * 40)
            self.assertEqual(receipt["files"], manager.inventory(self.target))
            self.run_command("rollback")
            self.assertEqual(manager.inventory(self.target), old_files)
            self.assertEqual(manager.read_json(manager.state_root(self.target) / "receipt.json"), old_receipt)
        self.assertEqual(neighbor.read_bytes(), b"unrelated")

    def test_missing_release_never_falls_back_to_branch(self):
        error = HTTPError("url", 404, "not found", {}, io.BytesIO())
        self.addCleanup(error.close)
        with patch.object(manager, "api", side_effect=error) as api:
            with self.assertRaisesRegex(ValueError, "no matching stable"):
                manager.remote_bundle()
        self.assertEqual(api.call_count, 1)

    def test_prerelease_wrong_tag_and_bad_commit_refused(self):
        for release in ({"tag_name": "v1.3.0", "prerelease": True}, {"tag_name": "main"}):
            with patch.object(manager, "api", return_value=release):
                with self.assertRaises(ValueError):
                    manager.remote_bundle()
        with patch.object(manager, "api", side_effect=[{"tag_name": "v1.3.0"}, {"sha": "main"}]):
            with self.assertRaisesRegex(ValueError, "immutable"):
                manager.remote_bundle()

    def test_release_version_must_match_skill(self):
        data, commit = self.archive()
        with patch.object(manager, "api", side_effect=[{"tag_name": "v2.0.0"}, {"sha": commit}]), patch.object(manager, "download", return_value=data):
            with self.assertRaisesRegex(ValueError, "tag and Skill"):
                manager.remote_bundle()

    def test_unsafe_duplicate_link_and_extra_members_refused(self):
        commit = "a" * 40
        for extra in ([("../escape", b"x")], [(f"supercoding-{commit}/skills/supercoding/unexpected.py", b"x")], [(f"supercoding-{commit}/skills/supercoding/SKILL.md", b"x")]):
            with self.subTest(extra=extra):
                import warnings
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", UserWarning)
                    data, _ = self.archive(extra)
                with self.assertRaises(ValueError):
                    manager.archive_payload(data, commit)
        data, _ = self.archive()
        buffer = io.BytesIO(data)
        with zipfile.ZipFile(buffer, "a") as archive:
            link = zipfile.ZipInfo(f"supercoding-{commit}/link")
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(link, "target")
        with self.assertRaisesRegex(ValueError, "unsafe"):
            manager.archive_payload(buffer.getvalue(), commit)

    def test_large_archive_and_invalid_metadata_refused(self):
        data, commit = self.archive()
        with patch.object(manager, "MAX_EXPANDED", 1):
            with self.assertRaisesRegex(ValueError, "size limit"):
                manager.archive_payload(data, commit)
        for value in ("1.2", "1.2.0-beta", "01.2.0", None):
            with self.assertRaises(ValueError):
                manager.version_key(value)
        with self.assertRaises(ValueError):
            manager.validate_payload({"SKILL.md": b"wrong"})

    def test_network_has_timeout_and_response_bound(self):
        from unittest.mock import MagicMock
        response = MagicMock()
        response.__enter__.return_value.read.return_value = b"xx"
        opener = MagicMock()
        opener.open.return_value = response
        with patch.object(manager, "build_opener", return_value=opener):
            with self.assertRaisesRegex(ValueError, "size limit"):
                manager.download("https://api.github.com/repos/example", 1)
        self.assertEqual(opener.open.call_args.kwargs["timeout"], 15)
        for url in ("http://github.com/a", "https://evil.invalid/a", "https://user@github.com/a"):
            with self.assertRaises(ValueError):
                manager.check_url(url)
        with patch.object(manager, "download", side_effect=URLError("timeout")):
            with self.assertRaises(URLError):
                manager.remote_bundle()


if __name__ == "__main__":
    unittest.main()

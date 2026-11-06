"""Release smoke orchestration with fixed local payloads, never network."""
from contextlib import redirect_stderr, redirect_stdout
import io
from pathlib import Path
import shutil
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import manage
import smoke_release as smoke


class SmokeTests(unittest.TestCase):
    def test_lifecycle_uses_only_temporary_target_and_checks_receipts(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            source = base / 'source'
            shutil.copytree(ROOT / 'skills/supercoding', source)
            old = manage.local_bundle(source)
            old.update(commit='a' * 40, source=manage.REPOSITORY + '@v1.3.0')
            new = {**old, 'version': '1.4.0', 'commit': 'b' * 40, 'source': manage.REPOSITORY + '@v1.4.0',
                   'files': {**old['files'], 'SKILL.md': old['files']['SKILL.md'].replace(b'1.3.0', b'1.4.0')}}
            calls = []
            def run(command, **kwargs):
                calls.append(command)
                action = command[3]
                target = command[command.index('--target') + 1]
                self.assertTrue(Path(target).is_relative_to(base))
                version = command[command.index('--version') + 1] if '--version' in command else None
                args = SimpleNamespace(command=action, target=target, client=None, source=None, version=version,
                                       dry_run='--dry-run' in command, replace=False)
                with patch.object(manage, 'remote_bundle', return_value=old if version == '1.3.0' else new):
                    manage.restore(args) if action == 'rollback' else manage.apply(args)
                return SimpleNamespace(returncode=0, stdout='mocked manager CLI', stderr='')
            with patch.object(smoke.subprocess, 'run', side_effect=run), redirect_stdout(io.StringIO()):
                report = smoke.lifecycle('1.3.0', '1.4.0', base)
            self.assertEqual(report['status'], 'passed')
            self.assertEqual([call[3] for call in calls], ['install', 'check', 'update', 'update', 'rollback'])
            self.assertTrue((base / 'report.json').is_file())

    def test_no_default_network_or_invalid_version_run(self):
        for args in ([], ['--old', '1.3.0', '--new', '1.3.0'], ['--old', 'main', '--new', '2.0.0']):
            with patch.object(smoke, 'lifecycle') as lifecycle:
                with self.assertRaises(SystemExit), redirect_stderr(io.StringIO()):
                    smoke.main(args)
                lifecycle.assert_not_called()

    def test_failed_process_retains_failed_evidence(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            with patch.object(smoke.subprocess, 'run', return_value=SimpleNamespace(returncode=1, stdout='', stderr='no release')):
                with self.assertRaisesRegex(RuntimeError, 'no release'):
                    smoke.lifecycle('1.3.0', '1.4.0', base)
            self.assertIn('"status": "failed"', (base / 'report.json').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()

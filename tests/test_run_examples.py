"""Offline evaluator regression tests; never invoke a model."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('run_examples', ROOT / 'scripts/run_examples.py')
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()

    def test_all_baselines_and_correct_controls(self):
        for name, case in runner.CASES.items():
            if name == 'search-race' and not shutil.which('node'):
                continue
            with self.subTest(case=name):
                baseline = (runner.EXAMPLES / name / case['implementation']).read_bytes()
                control = (runner.CONTROLS / name / case['implementation']).read_bytes()
                self.assertTrue(runner.outcome(runner.trusted_check(name, case, baseline, self.base, 'baseline'), case, case['failures']))
                self.assertTrue(runner.outcome(runner.trusted_check(name, case, control, self.base, 'control'), case, []))

    def test_unexpected_error_is_not_expected_defect(self):
        case = runner.CASES['debugging']
        for content in (b'invalid syntax !', b'raise RuntimeError("broken import")'):
            result = runner.trusted_check('debugging', case, content, self.base, str(len(list(self.base.iterdir()))))
            self.assertFalse(runner.outcome(result, case, case['failures']))
        self.assertFalse(runner.outcome({'exit_code': 1, 'stdout': '', 'stderr': 'AssertionError'}, case, case['failures']))

    def test_timeout_and_missing_executable_are_failures(self):
        with patch.object(runner.subprocess, 'run', side_effect=subprocess.TimeoutExpired(['test'], 1, output=b'partial')):
            result = runner.execute(['test'], self.base, 1)
        self.assertEqual(result['error'], 'timeout')
        self.assertEqual(result['stdout'], 'partial')
        self.assertFalse(runner.outcome(result, runner.CASES['debugging'], ['test_partial_batch_is_saved']))
        with patch.object(runner.subprocess, 'run', side_effect=FileNotFoundError('missing')):
            self.assertIsNone(runner.execute(['missing'], self.base, 1)['exit_code'])

    def candidate(self):
        directory = self.base / 'candidate'
        shutil.copytree(runner.EXAMPLES / 'debugging', directory)
        return directory, runner.snapshot(directory)

    def test_integrity_rejects_check_edits_nested_files_and_deletion(self):
        directory, original = self.candidate()
        (directory / 'check.py').write_text('tampered', encoding='utf-8')
        with self.assertRaises(ValueError):
            runner.candidate_bytes(directory, original, 'import_rows.py')
        (directory / 'check.py').write_bytes(original['check.py'])
        (directory / 'nested').mkdir()
        with self.assertRaises(ValueError):
            runner.candidate_bytes(directory, original, 'import_rows.py')
        (directory / 'nested').rmdir()
        (directory / 'import_rows.py').unlink()
        with self.assertRaises(ValueError):
            runner.candidate_bytes(directory, original, 'import_rows.py')

    def test_symlinks_are_rejected(self):
        directory, original = self.candidate()
        try:
            (directory / 'link').symlink_to(directory / 'check.py')
        except (OSError, NotImplementedError):
            self.skipTest('symlink creation unavailable')
        with self.assertRaisesRegex(ValueError, 'links'):
            runner.candidate_bytes(directory, original, 'import_rows.py')

    def test_only_implementation_may_change(self):
        directory, original = self.candidate()
        (directory / 'import_rows.py').write_bytes(b'candidate')
        self.assertEqual(runner.candidate_bytes(directory, original, 'import_rows.py'), b'candidate')

    def test_trusted_checks_use_evaluator_held_bytes(self):
        case = runner.CASES['debugging']
        fixture = runner.snapshot(runner.EXAMPLES / 'debugging')
        control = (runner.CONTROLS / 'debugging/import_rows.py').read_bytes()
        with patch.object(runner, 'snapshot', side_effect=AssertionError('must not reread mutable source')):
            result = runner.trusted_check('debugging', case, control, self.base, 'held', fixture)
        self.assertTrue(runner.outcome(result, case, []))

    def test_client_completion_requires_explicit_success_event(self):
        for output in ('', '{}', '{"type":"result"}', '{"type":"result","is_error":true}'):
            self.assertFalse(runner.client_completed({'stdout': output, 'exit_code': 0}))
        self.assertTrue(runner.client_completed({'stdout': '{"type":"result","is_error":false}', 'exit_code': 0}))
        self.assertFalse(runner.client_completed({'stdout': '{"type":"result","is_error":false}', 'exit_code': 1}))

    def test_comparison_preparation_is_neutral_and_not_isolation_proof(self):
        runner.prepare_comparison(self.base, ['debugging'])
        left = self.base / 'without-skill/debugging'
        right = self.base / 'with-skill/debugging'
        self.assertEqual(runner.snapshot(left), runner.snapshot(right))
        self.assertNotIn('Use supercoding', (left / 'TASK.txt').read_text(encoding='utf-8'))
        self.assertFalse((left / 'SKILL.md').exists())
        self.assertIn('UNVERIFIED', json.loads((self.base / 'comparison.json').read_text(encoding='utf-8'))['isolation'])

    def test_case_selection_runs_no_client(self):
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/run_examples.py'), '--case', 'debugging'],
                                capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('debugging: passed', result.stdout)
        self.assertNotIn('streaming:', result.stdout)

    def test_mocked_success_is_checked_without_invoking_model(self):
        actual_execute = runner.execute
        def execute(command, directory, timeout):
            if command[0] == 'claude':
                (directory / 'import_rows.py').write_bytes((runner.CONTROLS / 'debugging/import_rows.py').read_bytes())
                return {'exit_code': 0, 'stdout': '{"type":"result","is_error":false}', 'stderr': ''}
            return actual_execute(command, directory, timeout)
        with patch.object(runner, 'execute', side_effect=execute), patch.object(runner.shutil, 'which', return_value='fake'), \
                patch.object(runner.tempfile, 'mkdtemp', return_value=str(self.base)), redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(['--client', 'claude', '--case', 'debugging', '--model', 'fixed-test-model']), 0)
        report = json.loads((self.base / 'report.json').read_text(encoding='utf-8'))
        self.assertEqual(report['mode'], 'forced_skill')
        self.assertEqual(report['automatic_trigger'], 'not_evaluated')
        self.assertEqual(report['cases']['debugging']['after']['exit_code'], 0)
        self.assertTrue((self.base / 'debugging.patch').read_text(encoding='utf-8'))

    def test_integrity_precedes_post_check_and_stops_client_runs(self):
        actual_execute = runner.execute
        calls = []
        def execute(command, directory, timeout):
            if command[0] == 'claude':
                calls.append(command)
                (directory / 'check.py').write_text('raise RuntimeError("tampered")', encoding='utf-8')
                return {'exit_code': 0, 'stdout': '{"type":"result","is_error":false}', 'stderr': ''}
            return actual_execute(command, directory, timeout)
        with patch.object(runner, 'execute', side_effect=execute), patch.object(runner.shutil, 'which', return_value='fake'), \
                patch.object(runner.tempfile, 'mkdtemp', return_value=str(self.base)), redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(['--client', 'claude', '--case', 'debugging', '--case', 'review-feedback']), 1)
        report = json.loads((self.base / 'report.json').read_text(encoding='utf-8'))
        self.assertEqual(len(calls), 1)
        self.assertNotIn('after', report['cases']['debugging'])
        self.assertFalse(report['cases']['debugging']['scope_preserved'])


if __name__ == '__main__':
    unittest.main()

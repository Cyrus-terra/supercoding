#!/usr/bin/env python3
"""Run trusted fixture checks offline, or explicitly opt into a forced-Skill client run."""

import argparse
import difflib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'tests/evals/examples'
CONTROLS = ROOT / 'tests/evals/controls'
CASES = {
    'search-race': {
        'implementation': 'search.mjs',
        'check': ['node', '--test', '--test-reporter=tap', 'check.mjs'],
        'failures': ['older success cannot replace newer results', 'older finally cannot clear current loading', 'older failure cannot replace current error state'],
        'tests': 4,
        'prompt': 'Fix stale search responses and loading/error races in search.mjs. Preserve the public API and existing fetchResults callback, which has no cancellation contract.',
    },
    'streaming': {
        'implementation': 'process_csv.py',
        'failures': ['test_streaming_order_bounds_and_timeout'],
        'tests': 2,
        'prompt': 'Make process_csv.py stream large CSV input/output with at most workers submitted but not yet emitted rows. Preserve output order, signature and timeout contract. Propagate failures and close resources. The transform enforces its supplied I/O timeout.',
    },
    'debugging': {
        'implementation': 'import_rows.py',
        'failures': ['test_partial_batch_is_saved'],
        'tests': 3,
        'prompt': 'The importer reports seven imported rows but storage has six. Cache, timeouts and batch boundaries are competing explanations. Identify a discriminating experiment and fix the supported cause in import_rows.py, preserving full batches, empty input and error propagation.',
    },
    'refactoring': {
        'implementation': 'orders.py',
        'failures': [],
        'tests': 3,
        'prompt': 'Simplify duplicated paid/refunded handling in orders.py without changing serialization, zero/null values, errors or audit side-effect count/order. This Python fixture is an analogue of the Kotlin refactoring scenario, not a Kotlin test.',
    },
    'review-feedback': {
        'implementation': 'listing.py',
        'failures': ['test_filters_do_not_collide'],
        'tests': 3,
        'prompt': 'Evaluate review suggestions: (1) the tenant-only cache key collides across filters; (2) cache indefinitely for speed; (3) merge list/export permission checks. Freshness contract is five seconds and read/export permissions are distinct. Apply only supported corrections in listing.py and explain rejected suggestions.',
    },
}


def execute(command, directory, timeout):
    environment = os.environ.copy()
    environment.update(PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
    try:
        result = subprocess.run(command, cwd=directory, env=environment, capture_output=True,
                                text=True, encoding='utf-8', errors='replace', timeout=timeout)
        return {'command': command, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    except (subprocess.TimeoutExpired, OSError) as error:
        def text(value):
            return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else (value or '')
        return {'command': command, 'exit_code': None, 'stdout': text(getattr(error, 'stdout', '')),
                'stderr': text(getattr(error, 'stderr', '')), 'error': 'timeout' if isinstance(error, subprocess.TimeoutExpired) else str(error)}


def check_command(case):
    return case.get('check', [sys.executable, '-B', 'check.py'])


def outcome(result, case, expected_failures):
    """Require known test identities/counts; infrastructure failures never reproduce a defect."""
    if result.get('error') or result['exit_code'] != (1 if expected_failures else 0):
        return False
    output = result['stdout'] + '\n' + result['stderr']
    if 'check' in case:
        failures = re.findall(r'^not ok \d+ - (.+)$', output, re.MULTILINE)
        return (sorted(failures) == sorted(expected_failures)
                and re.search(r'^# tests ' + str(case['tests']) + r'\s*$', output, re.MULTILINE) is not None
                and re.search(r'^# fail ' + str(len(expected_failures)) + r'\s*$', output, re.MULTILINE) is not None
                and output.count("code: 'ERR_ASSERTION'") == len(expected_failures))
    failures = re.findall(r'^FAIL: (\w+) ', output, re.MULTILINE)
    return (sorted(failures) == sorted(expected_failures)
            and not re.search(r'^ERROR:', output, re.MULTILINE)
            and re.search(r'Ran ' + str(case['tests']) + r' tests? in ', output) is not None
            and (not expected_failures or 'AssertionError' in output))


def snapshot(directory):
    """Inspect recursively without following links, including empty directories and types."""
    result = {}
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError('expected a real workspace directory')
    for current, directories, files in os.walk(directory, followlinks=False):
        for name in directories + files:
            path = Path(current) / name
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode) or not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                raise ValueError('links/special files refused: ' + str(path))
            result[path.relative_to(directory).as_posix()] = path.read_bytes() if stat.S_ISREG(mode) else None
    return result


def candidate_bytes(directory, original, implementation):
    current = snapshot(directory)
    if set(current) != set(original) or not isinstance(current.get(implementation), bytes):
        raise ValueError('workspace file inventory changed')
    if any(current[name] != content for name, content in original.items() if name != implementation):
        raise ValueError('checks or non-implementation content changed')
    return current[implementation]


def trusted_check(name, case, content, workspace, label, fixture=None):
    # Use evaluator-held bytes, never a candidate workspace's checks or import paths.
    directory = workspace / (name + '-' + label)
    directory.mkdir()
    for relative, data in (fixture if fixture is not None else snapshot(EXAMPLES / name)).items():
        path = directory / relative
        if data is None:
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
    (directory / case['implementation']).write_bytes(content)
    return execute(check_command(case), directory, 30)


def client_completed(result):
    events = []
    for line in result['stdout'].splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict) and event.get('type') == 'result':
            events.append(event)
    return bool(result['exit_code'] == 0 and not result.get('error') and events
                and events[-1].get('is_error') is False)


def prompt_for(case, with_skill=False):
    return (case['prompt'] + (' Use supercoding from the session plugin.' if with_skill else '')
            + ' Read the implementation and checks. Edit only ' + case['implementation']
            + '. Do not edit checks, add dependencies/files, use agents, access the network with tools, or write documentation. '
              'The external evaluator runs checks; do not claim experiments you did not execute. Explain decisions and unrun checks.')


def prepare_comparison(workspace, names):
    for arm in ('without-skill', 'with-skill'):
        for name in names:
            directory = workspace / arm / name
            shutil.copytree(EXAMPLES / name, directory)
            (directory / 'TASK.txt').write_text(prompt_for(CASES[name]) + '\n', encoding='utf-8')
    (workspace / 'comparison.json').write_text(json.dumps({
        'status': 'prepared_not_evaluated', 'cases': names,
        'isolation': 'UNVERIFIED: prove separate client profiles; audit global skills, hooks, parent instructions and MCP. HOME alone is not isolation.',
        'instructions': 'Use identical TASK.txt prompts and model/settings. Enable the Skill only in the with-skill profile. Never score a contaminated control.',
    }, indent=2), encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', choices=('none', 'claude', 'codebuddy'), default='none')
    parser.add_argument('--case', choices=CASES, action='append', dest='cases')
    parser.add_argument('--model', help='explicit model ID for opt-in client runs')
    parser.add_argument('--client-timeout', type=int, default=180)
    parser.add_argument('--max-budget-usd', type=float, default=1.0, help='Claude per-case requested cap')
    parser.add_argument('--max-turns', type=int, default=16, help='CodeBuddy per-case cap')
    parser.add_argument('--prepare-comparison', action='store_true', help='prepare only; never invoke a client')
    args = parser.parse_args(argv)
    if args.client_timeout <= 0 or args.max_budget_usd <= 0 or args.max_turns <= 0:
        parser.error('run limits must be positive')
    if args.prepare_comparison and args.client != 'none':
        parser.error('comparison preparation cannot invoke a client')
    names = list(dict.fromkeys(args.cases or CASES))
    if not args.prepare_comparison:
        required = (['node'] if 'search-race' in names else []) + ([args.client] if args.client != 'none' else [])
        if any(not shutil.which(name) for name in required):
            parser.error('Missing executable in: ' + ', '.join(required))
    workspace = Path(tempfile.mkdtemp(prefix='supercoding-examples-')).resolve()
    if args.prepare_comparison:
        prepare_comparison(workspace, names)
        print('Prepared only; isolation and behavior NOT evaluated: ' + str(workspace))
        return 0
    report = {'client': args.client, 'mode': 'offline' if args.client == 'none' else 'forced_skill',
              'automatic_trigger': 'not_evaluated', 'debugging_experiments': 'not_evaluated',
              'model': args.model, 'plugin_root': str(ROOT), 'cases': {}}
    success = True
    for name in names:
        case = CASES[name]
        directory = workspace / name
        shutil.copytree(EXAMPLES / name, directory)
        original = snapshot(directory)
        before = original[case['implementation']]
        result = {'baseline': trusted_check(name, case, before, workspace, 'baseline', original),
                  'control': trusted_check(name, case, (CONTROLS / name / case['implementation']).read_bytes(), workspace, 'control', original)}
        result['baseline_expected'] = outcome(result['baseline'], case, case['failures'])
        result['control_passed'] = outcome(result['control'], case, [])
        passed = result['baseline_expected'] and result['control_passed']
        if passed and args.client != 'none':
            command = [args.client, '-p', prompt_for(case, True), '--plugin-dir', str(ROOT),
                       '--setting-sources', 'project', '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
                       '--tools', 'Read,Edit,Skill,Glob,Grep', '--allowedTools', 'Read,Edit,Skill,Glob,Grep',
                       '--permission-mode', 'dontAsk', '--no-session-persistence', '--output-format', 'stream-json', '--verbose']
            if args.model:
                command.extend(['--model', args.model])
            command.extend(['--max-budget-usd', str(args.max_budget_usd)] if args.client == 'claude' else ['--max-turns', str(args.max_turns)])
            result['client_run'] = execute(command, directory, args.client_timeout)
            result['client_completed'] = client_completed(result['client_run'])
            try:
                after = candidate_bytes(directory, original, case['implementation'])
                result['scope_preserved'] = True
                result['implementation_changed'] = after != before
                if result['client_completed']:
                    result['after'] = trusted_check(name, case, after, workspace, 'after', original)
                passed = bool(result['client_completed'] and result['implementation_changed']
                              and 'after' in result and outcome(result['after'], case, []))
                patch = ''.join(difflib.unified_diff(before.decode('utf-8').splitlines(True), after.decode('utf-8').splitlines(True),
                                                    fromfile='before/' + case['implementation'], tofile='after/' + case['implementation']))
                (workspace / (name + '.patch')).write_text(patch, encoding='utf-8')
            except (ValueError, OSError) as error:
                result.update(scope_preserved=False, integrity_error=str(error))
                passed = False
        result['status'] = 'passed' if passed else 'failed'
        report['cases'][name] = result
        (workspace / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(name + ': ' + result['status'] + '; expected baseline=' + str(result['baseline_expected']) + '; correct control=' + str(result['control_passed']), flush=True)
        if not passed:
            success = False
            print('Stopping after failure; no further client requests.', flush=True)
            break
    print('Evidence: ' + str(workspace / 'report.json'))
    return int(not success)


if __name__ == '__main__':
    raise SystemExit(main())

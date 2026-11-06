#!/usr/bin/env python3
"""Run isolated defective fixtures; optionally use a client to produce verifiable fixes."""

import argparse
import difflib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / 'tests/evals/examples'
CASES = {
    'search-race': {
        'implementation': 'search.mjs',
        'check': ['node', '--test', 'check.mjs'],
        'prompt': 'Fix stale search responses and loading/error races in search.mjs. Preserve the public API and use the existing fetchResults callback. The callback has no cancellation contract.',
    },
    'streaming': {
        'implementation': 'process_csv.py',
        'check': ['python3', '-B', 'check.py'],
        'prompt': 'Make process_csv.py stream large CSV input and output with at most workers submitted but not yet emitted rows. Preserve output order, the function signature and the transform timeout contract. Propagate failures and close resources. The transform owns enforcing its supplied I/O timeout.',
    },
}


def execute(command, directory, timeout):
    try:
        result = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=timeout)
        return {'command': command, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
    except subprocess.TimeoutExpired as error:
        def text(value):
            return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else (value or '')
        return {'command': command, 'exit_code': None, 'stdout': text(error.stdout), 'stderr': text(error.stderr), 'error': 'timeout'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--client', choices=('none', 'claude', 'codebuddy'), default='none')
    args = parser.parse_args()
    required = ['node', 'python3'] + ([args.client] if args.client != 'none' else [])
    missing = [name for name in required if not shutil.which(name)]
    if missing:
        parser.error('Missing executables: ' + ', '.join(missing))
    workspace = Path(tempfile.mkdtemp(prefix='supercoding-examples-')).resolve()
    report = {'client': args.client, 'plugin_root': str(ROOT), 'cases': {}}
    for name, case in CASES.items():
        directory = workspace / name
        shutil.copytree(EXAMPLES / name, directory)
        implementation = directory / case['implementation']
        before = implementation.read_text(encoding='utf-8')
        checks_before = {path.name: path.read_bytes() for path in directory.iterdir() if path.is_file() and path != implementation}
        result = {'baseline': execute(case['check'], directory, 30)}
        if args.client != 'none':
            prompt = (
                case['prompt'] + ' Use supercoding from the session plugin. Read the implementation and checks first. '
                'Edit only ' + case['implementation'] + '. Do not edit checks, add dependencies, use agents, '
                'access the network with tools, or write documentation. The external evaluator will run the checks. '
                'Report which rules you used and any checks you could not run.'
            )
            command = [
                args.client, '-p', prompt, '--plugin-dir', str(ROOT),
                '--setting-sources', 'project', '--strict-mcp-config',
                '--mcp-config', '{"mcpServers":{}}',
                '--tools', 'Read,Edit,Skill,Glob,Grep',
                '--allowedTools', 'Read,Edit,Skill,Glob,Grep',
                '--permission-mode', 'dontAsk', '--no-session-persistence',
                '--output-format', 'stream-json', '--verbose',
            ]
            if args.client == 'claude':
                command.extend(['--max-budget-usd', '1.00'])
            else:
                command.extend(['--max-turns', '16'])
            result['client_run'] = execute(command, directory, 180)
            events = []
            for line in result['client_run']['stdout'].splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if isinstance(event, dict) and event.get('type') == 'result':
                    events.append(event)
            result['client_completed'] = bool(events and not events[-1].get('is_error') and result['client_run']['exit_code'] == 0)
            result['after'] = execute(case['check'], directory, 30)
        result['checks_unchanged'] = all((directory / name).is_file() and (directory / name).read_bytes() == content for name, content in checks_before.items())
        result['files'] = sorted(path.name for path in directory.iterdir())
        result['scope_preserved'] = set(result['files']) == set(checks_before) | {case['implementation']}
        result['implementation_changed'] = implementation.is_file() and implementation.read_text(encoding='utf-8') != before
        after = implementation.read_text(encoding='utf-8') if implementation.is_file() else ''
        patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='before/' + case['implementation'], tofile='after/' + case['implementation']))
        (workspace / (name + '.patch')).write_text(patch, encoding='utf-8')
        report['cases'][name] = result
        (workspace / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(name + ': baseline=' + str(result['baseline']['exit_code']) + ', after=' + str(result.get('after', {}).get('exit_code')) + ', checks_unchanged=' + str(result['checks_unchanged']), flush=True)
        if 'client_run' in result and not result['client_completed']:
            print('Client did not complete; stopping further model requests.', flush=True)
            break
    print('Evidence: ' + str(workspace / 'report.json'))
    if any(case['baseline']['exit_code'] in (0, None) for case in report['cases'].values()):
        return 1
    if args.client != 'none':
        return int(len(report['cases']) != len(CASES) or any(not case['client_completed'] or case['after']['exit_code'] != 0 or not case['checks_unchanged'] or not case['scope_preserved'] or not case['implementation_changed'] for case in report['cases'].values()))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Opt-in published-release lifecycle smoke test; only a fresh temporary target is used."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import manage

ROOT = Path(__file__).resolve().parents[1]


def verify(target, version):
    actual_version, files, managed = manage.inspection(target)
    receipt = manage.read_json(manage.state_root(target) / 'receipt.json')
    if (not managed or actual_version != version or set(files) != manage.FILES
            or not re.fullmatch('[0-9a-f]{40}', receipt.get('commit') or '')
            or receipt.get('source') != manage.REPOSITORY + '@v' + version):
        raise ValueError('release receipt/version/hash verification failed')
    return receipt


def lifecycle(old, new, base):
    """Invoke the existing manager CLI; no alternate downloader or user destination."""
    target = base / 'skills/supercoding'
    neighbor = base / 'skills/unrelated.txt'
    neighbor.parent.mkdir()
    neighbor.write_bytes(b'preserve neighboring installation')
    results = []

    def run(action, version=None, preview=False):
        command = [sys.executable, '-B', str(ROOT / 'scripts/manage.py'), action, '--target', str(target)]
        if version:
            command.extend(['--version', version])
        if preview:
            command.append('--dry-run')
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
        results.append({'command': command, 'exit_code': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
        if result.returncode:
            raise RuntimeError('manager failed: ' + result.stderr)

    report = {'old': old, 'new': new, 'target': str(target), 'commands': results, 'status': 'failed'}
    try:
        run('install', old)
        previous = verify(target, old)
        report['old_receipt'] = previous
        files = manage.inventory(target)
        run('check', new)
        run('update', new, True)
        if manage.inventory(target) != files or verify(target, old) != previous:
            raise ValueError('read-only check/preview changed installation')
        run('update', new)
        report['new_receipt'] = verify(target, new)
        backups = manage.state_root(target) / 'backups'
        if not any(manage.inventory(path) == files for path in backups.iterdir() if path.is_dir()):
            raise ValueError('complete old release backup missing')
        run('rollback')
        if verify(target, old) != previous or manage.inventory(target) != files:
            raise ValueError('rollback did not restore the old release')
        if neighbor.read_bytes() != b'preserve neighboring installation':
            raise ValueError('neighboring file changed')
        report['status'] = 'passed'
    finally:
        (base / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old', required=True, help='existing stable x.y.z release')
    parser.add_argument('--new', required=True, help='newer existing stable x.y.z release')
    args = parser.parse_args(argv)
    try:
        if manage.version_key(args.old) >= manage.version_key(args.new):
            raise ValueError('--new must be newer than --old')
    except ValueError as error:
        parser.error(str(error))
    base = Path(tempfile.mkdtemp(prefix='supercoding-release-smoke-')).resolve()
    print('Published-release network smoke; temporary target only: ' + str(base), flush=True)
    try:
        lifecycle(args.old, args.new, base)
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        print('Evidence: ' + str(base / 'report.json'))
        return 1
    print('PASS: install/check/preview/update/rollback; evidence: ' + str(base / 'report.json'))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build and run the original scheduler scenarios on the QEMU Cortex-M3 target."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def evaluate_run(output, return_code):
    success = re.search(r'\bPASSED\b', output) is not None
    failure = re.search(r'\bFAIL(?:ED|URE)?\b|qemu: fatal|HardFault|Lockup', output, re.IGNORECASE)
    return success and not failure and return_code in (0, None)


def run_case(case, timeout, log_dir):
    folder = ROOT / ('DemoPriority' if case == 'priority' else 'DemoTest')
    command = ['make', '-C', str(folder), 'all']
    if case != 'priority':
        command.append(f'EXTRA_CFLAGS=-DTEST_NUMBER={case}')
    build_log = log_dir / f'{case}-build.log'
    with build_log.open('w') as output:
        for step in [['make', '-C', str(folder), 'clean'], command]:
            result = subprocess.run(step, stdout=output, stderr=subprocess.STDOUT)
            if result.returncode:
                return {'case': case, 'passed': False, 'reason': 'build failed', 'build_log': str(build_log)}
    command = ['qemu-system-arm', '-machine', 'mps2-an385', '-cpu', 'cortex-m3',
               '-kernel', str(folder / 'Output/demo.elf'), '-monitor', 'none', '-nographic', '-serial', 'stdio']
    try:
        run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout)
        output, return_code = run.stdout.decode(errors='replace'), run.returncode
    except subprocess.TimeoutExpired as error:
        # Firmware intentionally loops forever. A timeout is expected, but a result is still required.
        output = (error.stdout or b'').decode(errors='replace')
        return_code = None
    path = log_dir / f'{case}-qemu.log'
    path.write_text(output)
    return {'case': case, 'passed': bool(evaluate_run(output, return_code)),
            'qemu_return_code': return_code, 'expected_timeout': return_code is None, 'log': str(path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', default='priority,1,2,3,4,5,6,7,8', help='Comma-separated scenario IDs')
    parser.add_argument('--timeout', type=float, default=5, help='Seconds per QEMU scenario')
    parser.add_argument('--log-dir', type=Path, default=ROOT / 'artifacts')
    args = parser.parse_args()
    cases = args.cases.split(',')
    if args.timeout <= 0 or any(case not in {'priority', *map(str, range(1, 9))} for case in cases):
        parser.error('Use a positive timeout and cases priority or 1 through 8.')
    missing = [name for name in ['make', 'arm-none-eabi-gcc', 'arm-none-eabi-size', 'qemu-system-arm'] if not shutil.which(name)]
    if missing:
        parser.error('Missing tools: ' + ', '.join(missing))
    args.log_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for case in cases:
        result = run_case(case, args.timeout, args.log_dir)
        results.append(result)
        print(f"{case}: {'PASSED' if result['passed'] else 'FAILED'}", flush=True)
    (args.log_dir / 'summary.json').write_text(json.dumps(results, indent=2) + '\n')
    print(f'Logs: {args.log_dir}')
    return 0 if all(result['passed'] for result in results) else 1


if __name__ == '__main__':
    sys.exit(main())

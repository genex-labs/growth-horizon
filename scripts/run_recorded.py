# SPDX-License-Identifier: Apache-2.0
"""Record a module's natural exit and check its owned process group."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True)
    parser.add_argument('--module', required=True)
    args = parser.parse_args()
    root = Path.cwd()
    scratch = root/'work-tmp.noindex'
    scratch.mkdir(exist_ok=True)
    log = scratch/f'{args.name}.log'
    with log.open('w') as stream:
        child = subprocess.Popen([sys.executable, '-m', args.module], stdout=stream,
            stderr=subprocess.STDOUT, start_new_session=True,
            env={**os.environ, 'TMPDIR': str(scratch)})
        code = child.wait()
    table = subprocess.check_output(['ps', '-axo', 'pid=,pgid='], text=True)
    survivors = [int(line.split()[0]) for line in table.splitlines()
                 if len(line.split()) == 2 and int(line.split()[1]) == child.pid]
    receipt = {'module': args.module, 'exit_code': code, 'log': str(log.relative_to(root)),
               'natural_exit': True, 'surviving_descendants': survivors}
    folder = root/'data/checks'
    folder.mkdir(exist_ok=True)
    (folder/f'{args.name}.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))
    raise SystemExit(code or int(bool(survivors)))


if __name__ == '__main__':
    main()

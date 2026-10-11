# SPDX-License-Identifier: Apache-2.0
"""One-command reconstruction of the full research release candidate."""
from __future__ import annotations

import os
from pathlib import Path
import tempfile


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    scratch = root/'work-tmp.noindex'
    scratch.mkdir(exist_ok=True)
    os.environ['TMPDIR'] = str(scratch)
    tempfile.tempdir = str(scratch)
    exclude = root/'.git/info/exclude'
    if exclude.is_file() and '/work-tmp.noindex/' not in exclude.read_text():
        exclude.write_text(exclude.read_text()+'\n/work-tmp.noindex/\n')
    from scripts.rebuild import main as reconstruct
    from growth_horizon.scoring import main as score
    from growth_horizon.measure_next import main as measure
    from scripts.package_release import main as package
    reconstruct()
    score()
    measure()
    package()


if __name__ == '__main__':
    main()

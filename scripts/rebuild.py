# SPDX-License-Identifier: Apache-2.0
"""One-command source replay and complete phase-1 rebuild, never outer scoring."""
from scripts.acquire import ROOT, replay
from scripts.acquire_gtdb import main as acquire_gtdb
from scripts.audit_labels import main as audit_labels
from scripts.preflight_sample import check_space
from scripts.verify_features import main as verify_features
from growth_horizon.phase1 import main as develop
from scripts.finalise_manifest import main as finalise
from scripts.preregister import main as preregister


def main() -> None:
    check_space()
    (ROOT / 'work-tmp').mkdir(exist_ok=True)
    (ROOT / 'data/gtdb-derived/local/analysis').mkdir(exist_ok=True)
    (ROOT / 'data/gtdb-derived').mkdir(exist_ok=True)
    replay()
    audit_labels()
    acquire_gtdb()
    verify_features()
    develop()
    finalise()
    preregister()


if __name__ == '__main__':
    main()

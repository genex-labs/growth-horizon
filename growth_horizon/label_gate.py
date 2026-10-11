# SPDX-License-Identifier: Apache-2.0
"""Require verified experimental-label provenance before development or freezing."""
import json
from pathlib import Path
from typing import Any

from scripts.acquire import ROOT, digest

TRAITS = ('temperature_optimum', 'oxygen', 'salinity_optimum', 'ph_optimum')


def validate_experimental_audit(audit: dict[str, Any], label_sha256: str) -> None:
    if audit.get('label_sha256') != label_sha256:
        raise ValueError('Stop: experimental-label audit does not match the label asset')
    if not audit.get('verified_snapshot_date'):
        raise ValueError('Stop: experimental label snapshot date is unverified')
    for trait in TRAITS:
        record = audit.get('traits', {}).get(trait, {})
        if (record.get('status') != 'experimental_only_verified'
                or record.get('unresolved_labels') != 0
                or not record.get('evidence')):
            raise ValueError(f'Stop: experimental and predicted labels cannot be distinguished: {trait}')


def require_experimental_labels(root: Path = ROOT) -> None:
    path = root / 'data/experimental-label-audit.json'
    if not path.exists():
        raise ValueError('Stop: experimental-label provenance audit is missing')
    audit = json.loads(path.read_text())
    validate_experimental_audit(audit, digest(root / 'data/raw/labels/training_data.tsv'))

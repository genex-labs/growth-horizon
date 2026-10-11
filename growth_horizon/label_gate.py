# SPDX-License-Identifier: Apache-2.0
"""Require verified experimental-label provenance before development or freezing."""
import json
from pathlib import Path
from typing import Any

from scripts.acquire import ROOT, digest

TRAITS = ('temperature_optimum', 'oxygen', 'salinity_optimum', 'ph_optimum')
LABEL_SHA256 = '19a9f888f06655e17e95c7110ab4ff5ace38ece121e6cb1ac3bcb7d3c087abcc'
TABLE_SOURCE = 'GenomeSPOT/v1.0.0/training_data.tsv'
NOTEBOOK_COMMIT = 'f994ef50450f3362a4d6f93ccd3260c80e8ca45c'
LABEL_COUNTS = dict(zip(TRAITS, (4783, 7300, 2376, 3549), strict=True))
PROVENANCE_TEXT = """GenomeSPOT's preparation notebook (last changed 2024-03-21, commit f994ef50450f3362a4d6f93ccd3260c80e8ca45c) names its output training_data_20231203.tsv, and its 15,596 rows and trait summaries match the release asset; the model-predicted BacDive values come from Koblitz et al. 2025 (doi 10.1038/s42003-025-08313-3) and are served only with the API parameter predictions=1, which GenomeSPOT's parser does not request. Decision: treat the table's labels as experimental records.

Residual risk: the release asset could in principle differ from the 2023 table in ways the matching checks did not cover."""


def validate_table_provenance(audit: dict[str, Any], label_sha256: str) -> None:
    """Accept the documented decision only for its exact authorised release asset."""
    required = {
        'label_source': TABLE_SOURCE, 'label_bytes': 64412996,
        'notebook_last_commit': NOTEBOOK_COMMIT,
        'notebook_last_commit_at': '2024-03-21T03:17:27Z',
        'notebook_historical_filename_hint': 'training_data_20231203.tsv',
        'matching_row_count': 15596,
        'matching_trait_summaries': True,
        'prediction_api_parameter': 'predictions=1',
        'release_parser_requests_predictions': False,
        'provenance_basis': PROVENANCE_TEXT,
        'decision': 'Resume 5, 2026-10-11 04:17 PDT',
    }
    if label_sha256 != LABEL_SHA256 or any(audit.get(k) != v for k, v in required.items()):
        raise ValueError('Stop: table-level provenance does not match the authorised source decision')
    if not audit.get('evidence'):
        raise ValueError('Stop: table-level provenance evidence is missing')
    for trait, count in LABEL_COUNTS.items():
        record = audit.get('traits', {}).get(trait, {})
        if (record.get('status') != 'experimental_by_table_provenance'
                or record.get('nonmissing_labels') != count
                or record.get('accepted_experimental_labels') != count
                or record.get('excluded_identified_predicted_labels') != 0
                or record.get('unresolved_labels') != 0
                or not record.get('evidence')):
            raise ValueError(f'Stop: table-level experimental provenance is incomplete: {trait}')


def validate_experimental_audit(audit: dict[str, Any], label_sha256: str) -> None:
    if audit.get('label_sha256') != label_sha256:
        raise ValueError('Stop: experimental-label audit does not match the label asset')
    if audit.get('status') == 'accepted_experimental_table_provenance':
        validate_table_provenance(audit, label_sha256)
        return
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
    for record in audit.get('evidence', []):
        if not isinstance(record, dict):
            continue
        source = root / record['path']
        if source.exists() and (source.stat().st_size != record['bytes']
                                or digest(source) != record['sha256']):
            raise ValueError('Stop: experimental-label source evidence checksum mismatch')

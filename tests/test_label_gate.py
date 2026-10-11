# SPDX-License-Identifier: Apache-2.0
"""Only the authorised table decision or verified experimental labels may pass."""
from copy import deepcopy
from unittest.mock import patch
from typing import Any

import pytest

from growth_horizon.label_gate import (
    LABEL_COUNTS, LABEL_SHA256, NOTEBOOK_COMMIT, PROVENANCE_TEXT, TABLE_SOURCE,
    TRAITS, validate_experimental_audit,
)


def table_audit() -> dict[str, Any]:
    return {
        'status': 'accepted_experimental_table_provenance',
        'label_sha256': LABEL_SHA256, 'label_source': TABLE_SOURCE,
        'label_bytes': 64412996, 'notebook_last_commit': NOTEBOOK_COMMIT,
        'notebook_last_commit_at': '2024-03-21T03:17:27Z',
        'notebook_historical_filename_hint': 'training_data_20231203.tsv',
        'matching_row_count': 15596, 'matching_trait_summaries': True,
        'prediction_api_parameter': 'predictions=1',
        'release_parser_requests_predictions': False,
        'provenance_basis': PROVENANCE_TEXT, 'decision': 'Resume 5, 2026-10-11 04:17 PDT',
        'verified_snapshot_date': None, 'evidence': ['synthetic receipt'],
        'traits': {trait: {'status': 'experimental_by_table_provenance',
                          'nonmissing_labels': count, 'accepted_experimental_labels': count,
                          'excluded_identified_predicted_labels': 0, 'unresolved_labels': 0,
                          'evidence': ['synthetic receipt']}
                   for trait, count in LABEL_COUNTS.items()},
    }


def test_table_decision_is_bound_to_exact_source_chain_and_trait_dispositions() -> None:
    audit = table_audit()
    validate_experimental_audit(audit, LABEL_SHA256)
    for key, replacement in [('label_source', 'other/source'), ('label_bytes', 1),
                             ('notebook_last_commit', 'other'), ('matching_row_count', 1),
                             ('matching_trait_summaries', False),
                             ('release_parser_requests_predictions', True),
                             ('provenance_basis', ''), ('decision', 'other')]:
        changed = deepcopy(audit)
        changed[key] = replacement
        with pytest.raises(ValueError, match='authorised source decision'):
            validate_experimental_audit(changed, LABEL_SHA256)
    with pytest.raises(ValueError, match='does not match'):
        validate_experimental_audit(audit, 'other')
    changed = deepcopy(audit)
    changed['label_sha256'] = 'other'
    with pytest.raises(ValueError, match='authorised source decision'):
        validate_experimental_audit(changed, 'other')
    for trait in TRAITS:
        changed = deepcopy(audit)
        changed['traits'][trait]['unresolved_labels'] = 1
        with pytest.raises(ValueError, match=f'incomplete: {trait}'):
            validate_experimental_audit(changed, LABEL_SHA256)
    audit['status'] = 'other'
    with pytest.raises(ValueError, match='snapshot date'):
        validate_experimental_audit(audit, LABEL_SHA256)


def test_unresolved_labels_never_pass_as_zero_predicted_labels() -> None:
    audit: dict[str, Any] = {'label_sha256': 'fixture', 'verified_snapshot_date': '2023-12-03',
             'traits': {trait: {'status': 'experimental_only_verified',
                               'unresolved_labels': 0, 'evidence': ['synthetic source']}
                        for trait in TRAITS}}
    validate_experimental_audit(audit, 'fixture')
    with pytest.raises(ValueError, match='does not match'):
        validate_experimental_audit(audit, 'other')
    audit['verified_snapshot_date'] = None
    with pytest.raises(ValueError, match='snapshot date'):
        validate_experimental_audit(audit, 'fixture')
    audit['verified_snapshot_date'] = '2023-12-03'
    audit['traits']['oxygen']['unresolved_labels'] = 1
    with pytest.raises(ValueError, match='cannot be distinguished: oxygen'):
        validate_experimental_audit(audit, 'fixture')


def test_population_and_preregistration_stop_before_loading_or_writing() -> None:
    from growth_horizon.population import load_population
    from scripts.preregister import main

    with patch('growth_horizon.population.require_experimental_labels',
               side_effect=ValueError('experimental-only gate')) as gate:
        with pytest.raises(ValueError, match='experimental-only gate'):
            load_population([])
        gate.assert_called_once()
    with patch('scripts.preregister.require_experimental_labels',
               side_effect=ValueError('experimental-only gate')) as gate:
        with pytest.raises(ValueError, match='experimental-only gate'):
            main()
        gate.assert_called_once()

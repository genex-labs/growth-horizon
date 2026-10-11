# SPDX-License-Identifier: Apache-2.0
"""Experimental-label uncertainty must block development and pre-registration."""
from unittest.mock import patch
from typing import Any

import pytest

from growth_horizon.label_gate import TRAITS, validate_experimental_audit


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

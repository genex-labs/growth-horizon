# SPDX-License-Identifier: Apache-2.0
"""Independent small examples for the authorised scoring rules."""
import numpy as np

from growth_horizon.evaluation import comparison, estimate, summary
from growth_horizon.scoring import calibrated, cv_bounds


def test_cv_order_statistics_use_each_scoring_fit() -> None:
    predictions = np.array([[10, 20], [30, 40], [0, 0], [0, 0], [0, 0]])
    scores = np.arange(1, 11, dtype=float)
    assignments = np.array([0]*5+[1]*5)
    bounds, size = cv_bounds(predictions, scores, assignments, np.ones(10, bool),
                            'temperature_optimum', np.zeros(2), np.zeros(2))
    lower = np.array([9, 8, 7, 6, 5, 24, 23, 22, 21, 20])
    upper = np.array([11, 12, 13, 14, 15, 36, 37, 38, 39, 40])
    assert np.array_equal(bounds, [[min(lower), max(upper)], [min(lower)+10, max(upper)+10]])
    assert np.array_equal(size, [35, 35])


def test_cv_small_sample_has_infinite_ends() -> None:
    bounds, size = cv_bounds(np.zeros((5, 1)), np.array([1.]), np.array([0]),
                            np.array([True]), 'ph_optimum', np.array([.5]), np.array([0]))
    assert bounds[0, 0] == -np.inf and bounds[0, 1] == np.inf
    assert size[0] == np.inf


def test_oxygen_strict_comparison_retains_equal_score() -> None:
    p = np.tile([.5, .5], (5, 1, 1))
    included, sizes = cv_bounds(p, np.zeros(10), np.zeros(10, int), np.ones(10, bool),
                               'oxygen', np.ones(1), np.zeros(1, int))
    assert included.tolist() == [[True, False]]
    assert sizes.tolist() == [1]


def test_supported_width_abstention_can_cover() -> None:
    record = {'distance_edges': [], 'methods': {'method': {'bins': [
        {'original_bins': [0], 'supported': True}]}}}
    r = calibrated(np.zeros((5, 1)), np.full(10, 15.), np.zeros(10, int), np.zeros(10),
                   np.zeros(1), record, 'temperature_optimum', np.zeros(1), np.zeros(1, int), np.zeros(1))
    assert r['covered'][0] and r['abstain'][0] and r['supported'][0]


def test_unsupported_excluded_and_taxon_weighting_separate() -> None:
    r = {'y': np.zeros(4), 'point': np.zeros(4), 'taxa': np.array(['a', 'a', 'b', 'c']),
         'supported': np.array([True, True, True, False]), 'covered': np.array([True, True, False, True]),
         'size': np.ones(4), 'abstain': np.array([True, True, False, True])}
    s = summary(r, np.ones(4, bool), 'ph_optimum')
    assert s['coverage']['value'] == 2/3
    assert s['coverage']['excluded_unsupported'] == 1
    assert s['taxon_weighted_coverage']['value'] == .5
    assert s['coverage']['abstention_rate'] == 2/3


def test_paired_taxon_draws_cancel_identical_methods() -> None:
    r = comparison(np.array([0., 1., 2.]), np.ones(3), np.ones(3), ['a', 'a', 'b'], False)
    assert r['value'] == 0 and r['interval'] == [0, 0]
    assert estimate(np.array([[1., 1.]]), ['a'])['interval'] is None


def test_whole_order_budget_and_label_free_selection() -> None:
    from growth_horizon.measure_next import choose_order
    groups = np.array(['large', 'large', 'large', 'small', 'other'])
    candidates = np.arange(5)
    scores = np.array([100., 100., 100., 2., 1.])
    assert choose_order(candidates, groups, scores, 2) == 'small'
    assert choose_order(candidates, groups, scores, 0) is None
    assert choose_order(candidates, groups, scores, 2, ['other', 'large', 'small']) == 'other'

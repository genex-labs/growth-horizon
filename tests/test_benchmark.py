# SPDX-License-Identifier: Apache-2.0
"""Offline invariants for the locked benchmark's essential algorithms."""
import math

import numpy as np
import pytest

from growth_horizon.calibration import (
    assign_bins, conformal_quantile, distance_edges, merge_bins, mondrian,
    numeric_abstain, oxygen_abstain, oxygen_set,
)
from growth_horizon.folds import grouped_folds, nested_membership
from growth_horizon.phase1 import InnerBoundary
from growth_horizon.statistics import horizon, taxon_bootstrap
from growth_horizon.tree import TreeIndex


def fixture_tree() -> TreeIndex:
    # root -> internal (1), c (7); internal -> a (2), b (3).
    return TreeIndex([[1, 4], [2, 3], [], [], []], [0, 1, 2, 3, 7],
                     {'a': 2, 'b': 3, 'c': 4})


def test_grouped_nested_membership_never_splits_a_taxon() -> None:
    groups = [f'g{i}' for i in range(40) for _ in range(i % 5 + 1)]
    outer = grouped_folds(groups)
    assert np.array_equal(outer, grouped_folds(groups))
    assert set(outer) == set(range(5))
    for taxon in set(groups):
        assert len({int(outer[i]) for i, g in enumerate(groups) if g == taxon}) == 1
    for fold in range(5):
        rows, inner = nested_membership(groups, outer, fold, 12)
        assert not set(np.flatnonzero(outer == fold)) & set(rows)
        for taxon in {groups[i] for i in rows}:
            assert len({int(inner[j]) for j, i in enumerate(rows) if groups[i] == taxon}) == 1
    with pytest.raises(ValueError):
        grouped_folds(['one'] * 20)


def test_distance_paths_ties_disconnected_and_pruning() -> None:
    tree = fixture_tree()
    assert tree.nearest({'a'})['b'] == (5, 'a')
    assert tree.nearest({'a'})['c'] == (10, 'a')
    assert tree.nearest({'a', 'b'})['c'] == (10, 'a')
    assert tree.nearest(set())['c'][0] == math.inf
    pruned = tree.prune({'a', 'c'})
    assert pruned.nearest({'a'})['c'] == tree.nearest({'a'})['c']


def test_tree_pass_matches_independent_all_pairs_paths() -> None:
    rng = np.random.default_rng(14)
    children: list[list[int]] = [[] for _ in range(80)]
    lengths = [0.0] + list(rng.uniform(0, 2, 79))
    parent = [-1]
    for node in range(1, 80):
        p = int(rng.integers(node))
        parent.append(p)
        children[p].append(node)
    leaves = {f'l{i}': i for i, c in enumerate(children) if not c}
    tree = TreeIndex(children, lengths, leaves)
    def path(node: int) -> dict[int, float]:
        result = {node: 0.0}
        distance = 0.0
        while parent[node] >= 0:
            distance += lengths[node]
            node = parent[node]
            result[node] = distance
        return result
    paths = {name: path(node) for name, node in leaves.items()}
    for sources in (set(sorted(leaves)[:7]), set(sorted(leaves)[-5:])):
        actual = tree.nearest(sources)
        pruned = tree.prune(set(sorted(leaves)[::2]))
        for leaf in leaves:
            expected = min((min(paths[leaf][n] + paths[s][n]
                                for n in paths[leaf].keys() & paths[s].keys()), s)
                           for s in sources)
            assert actual[leaf][0] == pytest.approx(expected[0])
            assert actual[leaf][1] == expected[1]
        selected_sources = sources & set(pruned.names)
        for name in pruned.names:
            assert pruned.nearest(selected_sources)[name][0] == pytest.approx(
                tree.nearest(selected_sources)[name][0])


def test_bins_use_training_data_and_preserve_ties() -> None:
    train = np.arange(100, dtype=float)
    edges = distance_edges(train)
    expected = edges.copy()
    assert assign_bins(np.array([-1.0, 100000.0]), edges).tolist() == [0, 4]
    assert np.array_equal(edges, expected)
    tied = distance_edges(np.zeros(100))
    assert len(tied) == 1
    assert len(set(assign_bins(np.zeros(100), tied))) == 1


def test_finite_sample_conformal_order_statistic_and_invalid_input() -> None:
    assert conformal_quantile(np.arange(1, 10, dtype=float)) == 9
    assert conformal_quantile(np.arange(1, 9, dtype=float)) == math.inf
    assert conformal_quantile(np.arange(1, 101, dtype=float)) == 91
    with pytest.raises(ValueError):
        conformal_quantile(np.array([math.nan]))


def test_taxon_counts_union_and_insufficient_calibration_abstain() -> None:
    bins = np.array([0, 1, 2, 3, 4] * 10)
    taxa = ['one'] * 50
    groups, history = merge_bins(bins, taxa, 5)
    assert groups == [[0, 1, 2, 3, 4]]
    assert history[-1]['calibration_taxa'] == 1
    calibrated = mondrian(np.ones(50), bins.astype(float), taxa, np.array([0.5, 1.5, 2.5, 3.5]))
    assert calibrated['bins'][0]['q90'] is None
    assert not calibrated['bins'][0]['supported']
    # Count a taxon once for support while retaining its genome residuals for the quantile.
    scores = np.r_[np.ones(99), [0.2, 8.0]]
    taxa = [f't{i}' for i in range(99)] + ['large', 'large']
    calibrated = mondrian(scores, np.ones(101), taxa, np.array([]))
    assert calibrated['bins'][0]['calibration_taxa'] == 100
    assert calibrated['bins'][0]['q90'] == 1.0
    duplicated = mondrian(np.r_[np.zeros(99), np.ones(500)], np.ones(599),
                           [f't{i}' for i in range(99)] + ['large'] * 500, np.array([]))
    assert duplicated['bins'][0]['calibration_taxa'] == 100
    assert duplicated['bins'][0]['calibration_genomes'] == 599
    assert duplicated['bins'][0]['q90'] == 1.0


def test_abstention_and_oxygen_sets() -> None:
    assert not numeric_abstain(10, 20)
    assert numeric_abstain(10.0001, 20)
    assert numeric_abstain(math.inf, 20)
    assert numeric_abstain(1, 20, math.inf)
    assert oxygen_set(np.array([0.9, 0.1]), 0.2) == [0]
    assert oxygen_abstain(oxygen_set(np.array([0.5, 0.5]), 0.8))
    assert oxygen_abstain([])
    assert not oxygen_abstain([1])


def test_bootstrap_draws_taxa_and_retains_genome_multiplicity() -> None:
    values = np.r_[np.zeros(100), [1.0]]
    taxa = ['large'] * 100 + ['small']
    seen = set()
    def statistic(sample: np.ndarray) -> float:  # type: ignore[type-arg]
        seen.add((len(sample), float(sample.sum())))
        return float(np.mean(sample))
    assert taxon_bootstrap(values, taxa, statistic, repetitions=100) == (0, 1)
    assert seen == {(200, 0.0), (101, 1.0), (2, 2.0)}
    assert horizon([(0.1, 0.3), (-0.1, 0.4), (0.2, 0.5)]) == 1
    assert horizon([(0.1, 0.3)]) is None


def test_development_boundary_rejects_outer_rows_before_prediction() -> None:
    boundary = InnerBoundary(np.array([0, 1, 2, 3, 4]), 4)
    boundary.check(np.array([0, 1]), np.array([2]))
    with pytest.raises(ValueError, match='outer test'):
        boundary.check(np.array([0, 1]), np.array([4]))
    with pytest.raises(ValueError, match='overlaps'):
        boundary.check(np.array([0, 1]), np.array([1]))


def test_balanced_oxygen_error_and_paired_taxon_inference() -> None:
    from growth_horizon.metrics import accuracy_error, interval_summary, paired_improvement
    y = np.array([0, 1, 1, 1])
    assert accuracy_error(y, np.ones(4), oxygen=True) == 0.5
    interval = paired_improvement(np.array([1., 1.]), np.array([0., 0.]),
                                  np.array([1., 1.]), ['a', 'b'], repetitions=20)
    assert interval == (1., 1.)
    summary = interval_summary(np.array([1., 4.]), np.array([0., 0.]),
                               np.array([1., 1.]), np.array([True, False]))
    assert summary == {'coverage': 1., 'mean_width': 2., 'abstention_rate': 0.5}


def test_complete_synthetic_inner_run_never_queries_outer_test(tmp_path: object) -> None:
    from pathlib import Path
    from unittest.mock import patch

    import pandas as pd  # type: ignore[import-untyped]

    from growth_horizon import phase1
    from growth_horizon.models import COMPARTMENT_AA, ALL_AA

    rng = np.random.default_rng(17)
    n = 750
    features = sorted(set(COMPARTMENT_AA + ALL_AA))
    df = pd.DataFrame(rng.uniform(0, 1, (n, len(features))), columns=features,
                      index=[f'a{i:04d}' for i in range(n)])
    df['temperature_optimum'] = 10 + 3 * df['all_aa_A']
    df['genus'] = df.index
    df['leaf'] = df.index
    tree = TreeIndex([list(range(1, n + 1))] + [[] for _ in range(n)],
                     [0.0] + [1.0] * n, {str(a): i + 1 for i, a in enumerate(df.index)})
    outer = grouped_folds(df.index.tolist())
    test_accessions = set(df.index[outer == 0])
    base = Path(str(tmp_path))
    (base / 'data/gtdb-derived/local/analysis').mkdir(parents=True)
    from growth_horizon.models import prediction as actual_prediction
    def audited_prediction(model: object, x: object, trait: str) -> object:
        assert not test_accessions & set(x.index)  # type: ignore[attr-defined]
        return actual_prediction(model, x, trait)
    with patch.object(phase1, 'ROOT', base), patch.object(phase1, 'prediction', audited_prediction):
        result = phase1.run_fold(df, 'temperature_optimum', 'genus', outer, 0, [tree])
    assert result['status'] == 'inner_fitted_outer_unscored'
    assert set(result['methods']) == {'B1', 'B2', 'B3', 'method'}
    assert result['no_outer_fold_scoring']
    assert any(b['supported'] for b in result['methods']['B1']['mondrian']['bins'])
    saved = np.load(base / 'data/gtdb-derived/local/analysis/temperature_optimum/genus/fold0/membership-distances.npz')
    assert np.array_equal(saved['bin_training_rows'], saved['proper'])
    assert not set(saved['bin_training_rows']) & set(saved['calibration'])
    assert len(saved['training_side_distances']) == len(saved['proper'])


def test_oxygen_with_one_positive_taxon_is_explicitly_unsupported(tmp_path: object) -> None:
    from pathlib import Path
    from unittest.mock import patch

    import pandas as pd

    from growth_horizon import phase1

    n = 100
    df = pd.DataFrame({'genus': [f'g{i}' for i in range(n)],
                       'leaf': [f'l{i}' for i in range(n)], 'oxygen': np.zeros(n)})
    outer = grouped_folds(df['genus'].tolist())
    training, inner = nested_membership(df['genus'].tolist(), outer, 0, 20261012)
    positive = training[inner != 0][0]
    df.loc[positive, 'oxygen'] = 1
    tree = TreeIndex([list(range(1, n + 1))] + [[] for _ in range(n)],
                     [0.] + [1.] * n, {f'l{i}': i + 1 for i in range(n)})
    base = Path(str(tmp_path))
    (base / 'data/gtdb-derived/local/analysis').mkdir(parents=True)
    with patch.object(phase1, 'ROOT', base):
        result = phase1.run_fold(df, 'oxygen', 'genus', outer, 0, [tree])
    assert result['status'] == 'insufficient_oxygen_classes_in_inner_fitting_side'
    assert not result['methods']
    assert result['no_outer_fold_scoring']


def test_taxon_cap_keeps_nested_holdout_feasible_with_dominant_clades() -> None:
    groups = [f'large{i}' for i in range(4) for _ in range(500)] + [f'rare{i}' for i in range(30)]
    outer = grouped_folds(groups)
    assert max(len({groups[i] for i in np.flatnonzero(outer == f)}) for f in range(5)) <= 7
    for f in range(5):
        rows, inner = nested_membership(groups, outer, f, 20 + f)
        assert len({groups[rows[i]] for i in np.flatnonzero(inner != 0)}) >= 5

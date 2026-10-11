# SPDX-License-Identifier: Apache-2.0
"""Independent score inversion and the complete cross-fitted development boundary."""
from pathlib import Path
from typing import Any
from unittest.mock import patch

import joblib  # type: ignore[import-untyped]
import numpy as np
import pandas as pd  # type: ignore[import-untyped]
import pytest

from growth_horizon import crossfit, phase1
from growth_horizon.folds import grouped_folds
from growth_horizon.models import ALL_AA, COMPARTMENT_AA, prediction
from growth_horizon.tree import TreeIndex


def test_serialized_fit_is_independent_of_feature_name_object_sharing(tmp_path: Path) -> None:
    from growth_horizon.models import published
    from scripts.acquire import digest

    estimator, features = published('temperature_optimum')
    rng = np.random.default_rng(50)
    frame = pd.DataFrame(rng.normal(size=(80, len(features))), columns=features)
    estimator.fit(frame, 10 + frame[features[0]])
    original = np.array(estimator[-1].coef_, copy=True)
    first = {'estimator': estimator, 'features': features, 'proper_indices': np.arange(80)}
    # Force the alternative object-identity arrangement without changing a name.
    second = joblib.load(joblib.dump(first, tmp_path / 'source.joblib')[0])
    second['features'] = [('!' + f)[1:] for f in features]
    crossfit.save_calibration_fit(first, tmp_path / 'first.joblib')
    crossfit.save_calibration_fit(second, tmp_path / 'second.joblib')
    assert digest(tmp_path / 'first.joblib') == digest(tmp_path / 'second.joblib')
    assert np.array_equal(estimator[-1].coef_, original)


def test_class_scores_invert_randomized_sets_from_equation_five() -> None:
    probabilities = np.array([[0.7, 0.3], [0.2, 0.8], [0.5, 0.5], [0.5, 0.5], [1., 0.]])
    uniforms = np.array([0.15, 0.75, 0.25, 0.8, 0.4])
    ties = np.array([0, 1, 0, 1, 0])
    scores = crossfit.inverse_quantile_scores(probabilities, uniforms, ties)
    for row, (p, u, first) in enumerate(zip(probabilities, uniforms, ties, strict=True)):
        ordering = sorted(range(2), key=lambda c: (-p[c], c != first))
        for tau in np.linspace(0.001, 0.999, 501):
            cumulative = 0.
            selected = []
            for c in ordering:
                cumulative += p[c]
                selected.append(c)
                if cumulative >= tau:
                    if u <= (cumulative - tau) / p[c]:
                        selected.pop()
                    break
            assert selected == [c for c in ordering if scores[row, c] < tau]
    assert scores[-1, 1] == 1
    assert not np.allclose(scores, 1 - probabilities)
    with pytest.raises(ValueError):
        crossfit.inverse_quantile_scores(np.array([[0.8, 0.8]]), np.array([0.3]), np.array([0]))


def test_support_counts_distinct_taxon_unions_and_excludes_disconnected_rows() -> None:
    distances = np.r_[np.zeros(100), np.ones(49), [np.inf]]
    taxa = [f'a{i}' for i in range(100)] + [f'b{i}' for i in range(49)] + ['disconnected']
    merged = crossfit.crossfit_bins(distances, taxa, np.array([0.5]))
    assert len(merged['bins']) == 1
    assert merged['bins'][0]['calibration_taxa'] == 149
    assert merged['bins'][0]['strong_support']
    assert merged['nonfinite_distance_genomes'] == 1
    supported = crossfit.crossfit_bins(np.zeros(50), [f't{i}' for i in range(50)], np.array([]))
    assert supported['bins'][0]['supported']
    assert not supported['bins'][0]['strong_support']
    unsupported = crossfit.crossfit_bins(np.zeros(500), ['one'] * 500, np.array([]))
    assert not unsupported['bins'][0]['supported']


def test_five_crossfits_never_use_outer_or_current_calibration_labels(tmp_path: Path) -> None:
    rng = np.random.default_rng(33)
    n = 400
    features = sorted(set(ALL_AA + COMPARTMENT_AA))
    df = pd.DataFrame(rng.uniform(size=(n, len(features))), columns=features,
                      index=[f'a{i:04d}' for i in range(n)])
    df['temperature_optimum'] = 5 + 2 * df['all_aa_A']
    df['genus'] = df.index
    df['leaf'] = df.index
    tree = TreeIndex([list(range(1, n+1))] + [[] for _ in range(n)], [0.] + [1.] * n,
                     {str(a): i+1 for i, a in enumerate(df.index)})
    outer = grouped_folds(df.index.tolist())
    outer_accessions = set(df.index[outer == 0])
    original_tune = phase1.tune
    calibrations: list[set[str]] = []
    original_fit = crossfit.fit_calibration_fold
    def audited_fit(*args: Any, **kwargs: Any) -> object:
        current = set(df.index[args[4]])
        calibrations.append(current)
        with patch.object(crossfit, 'tune', audited_tune):
            return original_fit(*args, **kwargs)
    def audited_tune(*args: Any, **kwargs: Any) -> object:
        assert not calibrations[-1] & set(df.index[args[2]])
        return original_tune(*args, **kwargs)
    def audited_prediction(model: object, x: object, trait: str) -> object:
        assert not outer_accessions & set(x.index)  # type: ignore[attr-defined]
        return prediction(model, x, trait)
    with patch.object(crossfit, 'ROOT', tmp_path), \
         patch.object(crossfit, 'fit_calibration_fold', audited_fit), \
         patch.object(crossfit, 'prediction', audited_prediction), \
         patch('growth_horizon.phase1.prediction', audited_prediction):
        result, distances = crossfit.run_fold(df, 'temperature_optimum', 'genus', outer, 0, [tree])
    assert len(result['inner_fits']) == 5
    assert not set.union(*calibrations) & outer_accessions
    assert set.union(*calibrations) == set(df.index[outer != 0])
    assert sum(map(len, calibrations)) == len(set.union(*calibrations))
    assert len(distances) == 4 * sum(outer != 0)
    assert result['no_outer_fold_scoring']
    assert result['methods']['method']['bins'][0]['supported']
    base = tmp_path / 'data/gtdb-derived/local/crossfit/temperature_optimum/genus/fold0'
    for k in range(5):
        saved = np.load(base / f'inner{k}/membership-distances.npz')
        assert set(saved['proper']).isdisjoint(saved['calibration'])
        assert set(saved['proper']).isdisjoint(np.flatnonzero(outer == 0))
        assert np.array_equal(saved['tuning_rows'], saved['proper'])
    scores = np.load(base / 'method-oof.npz')
    assert np.array_equal(scores['calibration_rows'], np.flatnonzero(outer != 0))
    assert np.all(np.isfinite(scores['scores']))

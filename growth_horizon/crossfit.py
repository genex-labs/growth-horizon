# SPDX-License-Identifier: Apache-2.0
"""Cross-fitted calibration artefacts, with no outer prediction entry point."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

from joblib.numpy_pickle import NumpyPickler  # type: ignore[import-untyped]
import numpy as np
import pandas as pd  # type: ignore[import-untyped]
from threadpoolctl import threadpool_limits  # type: ignore[import-untyped]

from growth_horizon.calibration import assign_bins, distance_edges, merge_bins
from growth_horizon.folds import RANKS, SEED, grouped_folds, nested_membership
from growth_horizon.models import alternative, loss, nonconformity, prediction, published
from growth_horizon.phase1 import InnerBoundary, IntArray, nearest_prediction, nearest_rows, tune
from growth_horizon.population import TRAITS, load_trees
from growth_horizon.tree import TreeIndex
from scripts.acquire import ROOT, digest
from scripts.preflight_sample import check_space


def save_calibration_fit(payload: dict[str, Any], path: Path) -> None:
    """Canonicalise metadata identities without changing a fitted value.

    Pickle memoisation otherwise depends on shared string and dtype objects,
    which vary with earlier fits and unpickling in a process.
    """
    def canonical(value: Any) -> Any:
        if isinstance(value, str):
            return sys.intern(value)
        if isinstance(value, np.ndarray):
            result = np.empty(value.shape, dtype=np.dtype(value.dtype.str), order='C')
            if value.dtype.kind == 'O':
                result.flat[:] = [canonical(v) for v in value.flat]
            else:
                result[...] = value
            return result
        if isinstance(value, np.generic):
            return np.dtype(value.dtype.str).type(value)
        if isinstance(value, dict):
            return {canonical(k): canonical(value[k]) for k in sorted(value)}
        if isinstance(value, list):
            return [canonical(v) for v in value]
        if isinstance(value, tuple):
            return tuple(canonical(v) for v in value)
        if type(value).__module__.startswith('sklearn.'):
            attributes = {k: canonical(v) for k, v in sorted(vars(value).items())}
            vars(value).clear()
            vars(value).update(attributes)
        return value
    # Suppress pickle identity memoisation as well as ordering differences.
    # These fitted payloads are acyclic; no array or scalar value is changed.
    with path.open('wb') as stream:
        pickler = NumpyPickler(stream, protocol=4)
        pickler.fast = True
        pickler.dump(canonical(payload))


def inverse_quantile_scores(probabilities: Any, uniforms: Any, tie_first: Any) -> Any:
    """Equations 5 and 7: cumulative sorted mass minus U times class mass.

    Binary probability ties use an independent fair class ordering. A class
    with zero mass has the endpoint score 1. No probability is perturbed.
    """
    p = np.asarray(probabilities, dtype=float)
    u = np.asarray(uniforms, dtype=float)
    first = np.asarray(tie_first, dtype=int)
    if p.ndim != 2 or p.shape[1] != 2 or u.shape != (len(p),) or first.shape != u.shape:
        raise ValueError('Invalid binary class score shapes')
    if not np.all(np.isfinite(p)) or np.any(p < 0) or not np.allclose(p.sum(axis=1), 1):
        raise ValueError('Invalid class probabilities')
    if np.any((u < 0) | (u > 1)) or np.any((first < 0) | (first > 1)):
        raise ValueError('Invalid class randomisation')
    leading = np.where(p[:, 0] == p[:, 1], first, np.argmax(p, axis=1))
    rows = np.arange(len(p))
    scores = 1 - u[:, None] * p
    scores[rows, leading] = (1 - u) * p[rows, leading]
    return scores


def crossfit_bins(distances: Any, taxa: list[str], edges: Any) -> dict[str, Any]:
    initial = assign_bins(distances, edges)
    finite = np.isfinite(distances)
    valid_taxa = [t for t, valid in zip(taxa, finite, strict=True) if valid]
    groups, history = merge_bins(initial[finite], valid_taxa, len(edges) + 1, minimum=50)
    records = []
    for group in groups:
        selected = finite & np.isin(initial, group)
        count = len({taxa[i] for i in np.flatnonzero(selected)})
        records.append({'original_bins': group, 'calibration_taxa': count,
                        'calibration_genomes': int(sum(selected)), 'supported': count >= 50,
                        'strong_support': count >= 100})
    return {'bins': records, 'merges': history, 'minimum_taxa': 50,
            'strong_support_taxa': 100, 'nonfinite_distance_genomes': int(sum(~finite))}


def fit_calibration_fold(df: Any, trait: str, groups: list[str], proper: IntArray,
                         calibration: IntArray, trees: list[TreeIndex], boundary: InnerBoundary,
                         seed: int, directory: Path, uniforms: Any, tie_first: Any
                         ) -> tuple[dict[str, Any], Any, Any, dict[str, Any]]:
    y = df[trait].to_numpy(dtype=float)
    boundary.check(proper, calibration)
    partition = grouped_folds([groups[i] for i in proper], seed)
    tuning_distances = np.full(len(proper), math.inf)
    for f in range(5):
        fit, query = proper[partition != f], proper[partition == f]
        boundary.check(fit, query)
        d, _ = nearest_rows(df, fit, query, trees)
        tuning_distances[partition == f] = d
    distances, neighbours = nearest_rows(df, proper, calibration, trees)
    alphas, tuning = {}, {}
    for method, whole in [('B3', True), ('method', False)]:
        alphas[method], tuning[method] = tune(
            df, y, proper, groups, trait, boundary, seed, whole)
    published_losses = []
    for f in range(5):
        fit, query = proper[partition != f], proper[partition == f]
        boundary.check(fit, query)
        estimator, features = published(trait)
        estimator.fit(df.iloc[fit][features], y[fit])
        published_losses.append(loss(y[query], prediction(estimator, df.iloc[query][features], trait), trait))
    published_loss = float(np.mean(published_losses))
    alternative_loss = next(r['loss'] for r in tuning['method'] if r['alpha'] == alphas['method'])
    selected = 'B1' if published_loss <= alternative_loss else 'ridge_or_logistic'
    methods, scores = {}, {}
    for method in ('B1', 'B2', 'B3', 'method'):
        boundary.check(proper, calibration)
        if method == 'B2':
            pred = nearest_prediction(y, neighbours, trait)
            payload = {'training_indices': proper, 'trait': trait}
        else:
            if method == 'B1' or (method == 'method' and selected == 'B1'):
                estimator, features = published(trait)
            else:
                estimator, features = alternative(trait, alphas[method], method == 'B3')
            estimator.fit(df.iloc[proper][features], y[proper])
            pred = prediction(estimator, df.iloc[calibration][features], trait)
            payload = {'estimator': estimator, 'features': features, 'proper_indices': proper}
        save_calibration_fit(payload, directory / f'{method}.joblib')
        if trait == 'oxygen':
            all_scores = inverse_quantile_scores(pred, uniforms, tie_first)
            score = all_scores[np.arange(len(calibration)), y[calibration].astype(int)]
        else:
            score = nonconformity(y[calibration], pred, trait)
        if not np.all(np.isfinite(score)):
            raise ValueError('Nonfinite out-of-fold score')
        scores[method] = score
        # Only out-of-fold calibration predictions are saved.
        np.savez(directory / f'{method}-scores.npz', calibration_rows=calibration,
                 scores=score, calibration_predictions=pred, calibration_distances=distances)
        methods[method] = {'calibration_genomes': len(calibration),
                           'calibration_taxa': len({groups[i] for i in calibration})}
    np.savez(directory / 'membership-distances.npz', proper=proper, calibration=calibration,
             tuning_assignment=partition, tuning_rows=proper, tuning_distances=tuning_distances,
             calibration_distances=distances, uniforms=uniforms, tie_first=tie_first)
    record = {'proper_genomes': len(proper), 'calibration_genomes': len(calibration),
              'tuning_seed': seed, 'tuning': tuning, 'methods': methods,
              'predictor_selection': {'selected': selected, 'published_inner_loss': published_loss,
                                      'alternative_inner_loss': alternative_loss},
              'no_outer_fold_scoring': True}
    return record, distances, tuning_distances, scores


def run_fold(df: Any, trait: str, rank: str, outer: IntArray, fold: int,
             trees: list[TreeIndex]) -> tuple[dict[str, Any], Any]:
    check_space()
    groups = list(df.index.astype(str)) if rank == 'random' else df[rank].tolist()
    seed = SEED + 1000 * RANKS.index(rank) + 10 * fold
    training, inner = nested_membership(groups, outer, fold, seed + 1)
    boundary = InnerBoundary(outer, fold)
    directory = ROOT / f'data/gtdb-derived/local/crossfit/{trait}/{rank}/fold{fold}'
    directory.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed + 4)
    uniforms = rng.uniform(size=len(training))
    ties = rng.integers(0, 2, size=len(training))
    all_distances = np.full(len(training), math.inf)
    pooled_scores = {m: np.empty(len(training)) for m in ('B1', 'B2', 'B3', 'method')}
    tuning_distances, inner_records = [], []
    for k in range(5):
        proper, calibration = training[inner != k], training[inner == k]
        nested = directory / f'inner{k}'
        nested.mkdir(exist_ok=True)
        record, d, tuning_d, scores = fit_calibration_fold(
            df, trait, groups, proper, calibration, trees, boundary, seed + 3 + 100 * k,
            nested, uniforms[inner == k], ties[inner == k])
        record['inner_fold'] = k
        inner_records.append(record)
        tuning_distances.append(tuning_d)
        all_distances[inner == k] = d
        for method in pooled_scores:
            pooled_scores[method][inner == k] = scores[method]
    pooled_tuning = np.concatenate(tuning_distances)
    edges = distance_edges(pooled_tuning)
    calibrated = crossfit_bins(all_distances, [groups[i] for i in training], edges)
    for method, pooled_score in pooled_scores.items():
        np.savez(directory / f'{method}-oof.npz', calibration_rows=training,
                 inner_assignment=inner, scores=pooled_score, calibration_distances=all_distances,
                 distance_edges=edges)
    np.savez(directory / 'tuning-distances.npz', pooled_tuning_distances=pooled_tuning)
    record = {'trait': trait, 'rank': rank, 'outer_fold': fold, 'seed': seed,
              'randomisation_seed': seed + 4, 'calibration_genomes': len(training),
              'calibration_taxa': len({groups[i] for i in training}),
              'distance_edges': edges.tolist(), 'inner_fits': inner_records,
              'methods': {m: calibrated for m in pooled_scores},
              'no_outer_fold_scoring': True, 'status': 'crossfitted_outer_unscored'}
    (directory / 'calibration.json').write_text(json.dumps(record, indent=2, allow_nan=False)+'\n')
    return record, pooled_tuning


def refresh_manifest() -> None:
    artefacts = []
    for path in sorted((ROOT / 'data/gtdb-derived/local').rglob('*')):
        if (path.is_file() and '/evidence/' not in str(path)
                    and '/local/results/' not in str(path)
                    and '/local/measure-next/' not in str(path)):
            artefacts.append({'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
                              'sha256': digest(path)})
    (ROOT / 'data/artifact-manifest.json').write_text(json.dumps(artefacts, indent=2)+'\n')


def main() -> None:
    check_space()
    trees = load_trees()
    populations = {t: pd.read_pickle(ROOT / f'data/gtdb-derived/local/analysis/{t}.pkl').sort_index()
                   for t in TRAITS}
    all_leaves = set().union(*(set(df['leaf']) for df in populations.values()))
    trees = [tree.prune(all_leaves) for tree in trees]
    summary: dict[str, Any] = {'seed': SEED, 'minimum_taxa': 50, 'strong_support_taxa': 100,
                              'traits': {}, 'no_outer_fold_scoring': True}
    horizons: dict[str, Any] = {'quantiles': [0.2, 0.4, 0.6, 0.8], 'traits': {},
                               'no_outer_fold_scoring': True}
    with threadpool_limits(limits=1):
        for trait, df in populations.items():
            summary['traits'][trait], horizons['traits'][trait] = {}, {}
            for rank in RANKS:
                groups = list(df.index.astype(str)) if rank == 'random' else df[rank].tolist()
                outer = grouped_folds(groups, SEED + 1000 * RANKS.index(rank))
                records, pooled_distances = [], []
                for fold in range(5):
                    record, distances = run_fold(df, trait, rank, outer, fold, trees)
                    records.append(record)
                    pooled_distances.append(distances)
                    print(f'{trait} {rank} fold{fold}: {record["status"]}', flush=True)
                summary['traits'][trait][rank] = {'folds': records}
                pooled = np.concatenate(pooled_distances)
                cuts = distance_edges(pooled)
                horizons['traits'][trait][rank] = {
                    'distance_edges': cuts.tolist(), 'tuning_distances': len(pooled),
                    'finite_tuning_distances': int(sum(np.isfinite(pooled))),
                    'fold_tuning_distances': [len(d) for d in pooled_distances]}
                path = ROOT / f'data/gtdb-derived/local/crossfit/{trait}/{rank}/horizon-distances.npz'
                np.savez(path, pooled_tuning_distances=pooled, common_distance_edges=cuts)
                (ROOT / 'data/gtdb-derived/crossfit-summary.json').write_text(
                    json.dumps(summary, indent=2, allow_nan=False)+'\n')
                (ROOT / 'data/gtdb-derived/horizon-cutpoints.json').write_text(
                    json.dumps(horizons, indent=2, allow_nan=False)+'\n')
    refresh_manifest()


if __name__ == '__main__':
    main()

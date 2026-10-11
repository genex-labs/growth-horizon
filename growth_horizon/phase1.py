# SPDX-License-Identifier: Apache-2.0
"""Build nested development artefacts. Outer test predictions are inaccessible."""
from __future__ import annotations

import json
import math
from collections import Counter
from typing import Any

import joblib  # type: ignore[import-untyped]
import numpy as np
import numpy.typing as npt
import pandas as pd  # type: ignore[import-untyped]
from threadpoolctl import threadpool_limits  # type: ignore[import-untyped]

from growth_horizon.calibration import conformal_quantile, distance_edges, mondrian
from growth_horizon.folds import RANKS, SEED, grouped_folds, nested_membership
from growth_horizon.models import alternative, loss, nonconformity, prediction, published
from growth_horizon.population import TRAITS, load_population, load_trees
from growth_horizon.tree import TreeIndex
from scripts.acquire import ROOT, digest
from scripts.preflight_sample import check_space

IntArray = npt.NDArray[np.int64]


def nearest_rows(df: Any, sources: IntArray, queries: IntArray,
                 trees: list[TreeIndex]) -> tuple[Any, Any]:
    representative_to_row: dict[str, int] = {}
    leaves = df['leaf'].to_numpy()
    # Stable first accession breaks ties for identical representatives.
    for i in sorted(sources, key=lambda i: str(df.index[i])):
        representative_to_row.setdefault(str(leaves[i]), int(i))
    nearest = {}
    for tree in trees:
        nearest.update(tree.nearest(set(representative_to_row)))
    distances = []
    neighbours = []
    for i in queries:
        distance, leaf = nearest.get(str(leaves[i]), (math.inf, ''))
        distances.append(distance)
        neighbours.append(representative_to_row.get(leaf, -1))
    return np.array(distances), np.array(neighbours, dtype=np.int64)


def nearest_prediction(y: Any, neighbours: IntArray, trait: str) -> Any:
    good = neighbours >= 0
    if trait == 'oxygen':
        result = np.full((len(neighbours), 2), 0.5)
        for i in np.flatnonzero(good):
            result[i] = [0.0, 0.0]
            result[i, int(y[neighbours[i]])] = 1.0
        return result
    numeric_result = np.zeros(len(neighbours))
    numeric_result[good] = y[neighbours[good]]
    return numeric_result


class InnerBoundary:
    """The only development prediction entry point rejects every outer test row."""
    def __init__(self, outer: IntArray, fold: int):
        self.outer = outer
        self.fold = fold

    def check(self, sources: IntArray, queries: IntArray) -> None:
        if np.any(self.outer[sources] == self.fold) or np.any(self.outer[queries] == self.fold):
            raise ValueError('Phase 1 forbids outer test predictions')
        if set(sources) & set(queries):
            raise ValueError('Prediction query overlaps its fitting rows')


def tune(df: Any, y: Any, proper: IntArray, groups: list[str], trait: str,
         boundary: InnerBoundary, seed: int, whole: bool) -> tuple[float, list[dict[str, Any]]]:
    partition = grouped_folds([groups[i] for i in proper], seed)
    results: list[dict[str, Any]] = []
    for alpha in (0.1, 1.0, 10.0, 100.0):
        fold_losses = []
        for fold in range(5):
            fit, query = proper[partition != fold], proper[partition == fold]
            boundary.check(fit, query)
            if trait == 'oxygen' and len(set(y[fit])) != 2:
                continue
            model, features = alternative(trait, alpha, whole)
            model.fit(df.iloc[fit][features], y[fit])
            fold_losses.append(loss(y[query], prediction(model, df.iloc[query][features], trait), trait))
        results.append({'alpha': alpha, 'loss': float(np.mean(fold_losses))
                        if len(fold_losses) == 5 else None})
    viable = [r for r in results if r['loss'] is not None]
    if not viable:
        raise ValueError('No candidate has five valid inner tuning folds')
    selected = min(viable, key=lambda r: (r['loss'], r['alpha']))
    return float(selected['alpha']), results


def run_fold(df: Any, trait: str, rank: str, outer: IntArray, fold: int,
             trees: list[TreeIndex]) -> dict[str, Any]:
    check_space()
    y = df[trait].to_numpy(dtype=float)
    groups = list(df.index.astype(str)) if rank == 'random' else df[rank].tolist()
    boundary = InnerBoundary(outer, fold)
    seed = SEED + 1000 * RANKS.index(rank) + 10 * fold
    training, inner = nested_membership(groups, outer, fold, seed + 1)
    proper, calibration = training[inner != 0], training[inner == 0]
    # Training-side pseudo-test distances alone define bins, before any residual is inspected.
    bin_distances = np.full(len(training), math.inf)
    for inner_fold in range(5):
        fit, query = training[inner != inner_fold], training[inner == inner_fold]
        d, _ = nearest_rows(df, fit, query, trees)
        bin_distances[inner == inner_fold] = d
    edges = distance_edges(bin_distances)
    cal_distances, cal_neighbours = nearest_rows(df, proper, calibration, trees)
    # These outer test quantities are phenotype-free distances and memberships only.
    outer_rows = np.flatnonzero(outer == fold)
    outer_distances, _ = nearest_rows(df, proper, outer_rows, trees)
    outer_training_distances, _ = nearest_rows(df, training, outer_rows, trees)
    random_partition = grouped_folds([str(df.index[i]) for i in training], seed + 2)
    naive_fit, naive_cal = training[random_partition != 0], training[random_partition == 0]
    naive_distances, naive_neighbours = nearest_rows(df, naive_fit, naive_cal, trees)
    directory = ROOT / f'data/derived/{trait}/{rank}/fold{fold}'
    directory.mkdir(parents=True, exist_ok=True)
    np.savez(directory / 'membership-distances.npz', outer_test=outer_rows,
             outer_training=training, inner_assignment=inner, proper=proper,
             calibration=calibration, training_side_distances=bin_distances,
             calibration_distances=cal_distances, outer_distances=outer_distances,
             outer_training_distances=outer_training_distances,
             naive_fit=naive_fit, naive_calibration=naive_cal, distance_edges=edges)
    result: dict[str, Any] = {
        'trait': trait, 'rank': rank, 'outer_fold': fold, 'seed': seed,
        'outer_test_genomes': len(outer_rows), 'outer_training_genomes': len(training),
        'proper_training_genomes': len(proper), 'calibration_genomes': len(calibration),
        'calibration_taxa': len({groups[i] for i in calibration}),
        'distance_edges': edges.tolist(), 'training_distance_nonfinite': int(sum(~np.isfinite(bin_distances))),
        'outer_distance_nonfinite': int(sum(~np.isfinite(outer_distances))),
        'methods': {}, 'no_outer_fold_scoring': True}
    if len({groups[i] for i in proper}) < 5 or (trait == 'oxygen' and len(set(y[proper])) < 2):
        result['status'] = 'insufficient_proper_training_taxa_or_classes'
        return result
    alphas = {}
    tuning = {}
    for method, whole in [('B3', True), ('method', False)]:
        alpha, evidence = tune(df, y, proper, groups, trait, boundary, seed + 3, whole)
        alphas[method], tuning[method] = alpha, evidence
    # Select the proposed predictor using tuning data only, never calibration residuals.
    selected_alpha = alphas['method']
    proposed_model, proposed_features = alternative(trait, selected_alpha)
    tuning_partition = grouped_folds([groups[i] for i in proper], seed + 3)
    published_losses = []
    for tuning_fold in range(5):
        fit = proper[tuning_partition != tuning_fold]
        query = proper[tuning_partition == tuning_fold]
        boundary.check(fit, query)
        estimator, features = published(trait)
        estimator.fit(df.iloc[fit][features], y[fit])
        published_losses.append(loss(y[query], prediction(estimator, df.iloc[query][features], trait), trait))
    published_loss = float(np.mean(published_losses))
    alternative_loss = next(r['loss'] for r in tuning['method'] if r['alpha'] == selected_alpha)
    selected = 'B1' if published_loss <= alternative_loss else 'ridge_or_logistic'
    if selected == 'B1':
        proposed_model, proposed_features = published(trait)
    result['tuning'] = tuning
    result['predictor_selection'] = {'selected': selected, 'published_inner_loss': published_loss,
                                    'alternative_inner_loss': alternative_loss}
    for method in ('B1', 'B2', 'B3', 'method'):
        boundary.check(proper, calibration)
        boundary.check(naive_fit, naive_cal)
        if method == 'B2':
            cal_pred = nearest_prediction(y, cal_neighbours, trait)
            naive_pred = nearest_prediction(y, naive_neighbours, trait)
            # B2 stores only training-side accession indices, no outer phenotype query.
            joblib.dump({'training_indices': proper, 'trait': trait}, directory / 'B2.joblib')
        else:
            if method == 'B1':
                estimator, features = published(trait)
                naive_estimator, _ = published(trait)
            elif method == 'B3':
                estimator, features = alternative(trait, alphas['B3'], True)
                naive_estimator, _ = alternative(trait, alphas['B3'], True)
            else:
                estimator, features = proposed_model, proposed_features
                naive_estimator = (published(trait)[0] if selected == 'B1' else
                                   alternative(trait, selected_alpha)[0])
            estimator.fit(df.iloc[proper][features], y[proper])
            cal_pred = prediction(estimator, df.iloc[calibration][features], trait)
            naive_estimator.fit(df.iloc[naive_fit][features], y[naive_fit])
            naive_pred = prediction(naive_estimator, df.iloc[naive_cal][features], trait)
            joblib.dump({'estimator': estimator, 'features': features,
                         'proper_indices': proper}, directory / f'{method}.joblib')
            joblib.dump({'estimator': naive_estimator, 'features': features,
                         'proper_indices': naive_fit}, directory / f'{method}-naive.joblib')
        scores = nonconformity(y[calibration], cal_pred, trait)
        naive_scores = nonconformity(y[naive_cal], naive_pred, trait)
        naive_scores = naive_scores[np.isfinite(naive_distances)]
        naive_q = conformal_quantile(naive_scores)
        calibrated = mondrian(scores, cal_distances, [groups[i] for i in calibration], edges)
        result['methods'][method] = {'naive_q90': naive_q if math.isfinite(naive_q) else None,
            'naive_calibration_genomes': len(naive_scores), 'mondrian': calibrated,
            'inner_calibration_loss': loss(y[calibration], cal_pred, trait)}
    result['status'] = 'inner_fitted_outer_unscored'
    (directory / 'calibration.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    return result


def main() -> None:
    trees = load_trees()
    load_population(trees)
    all_leaves = set()
    for trait in TRAITS:
        all_leaves.update(pd.read_pickle(ROOT / f'data/derived/{trait}.pkl')['leaf'])
    trees = [tree.prune(all_leaves) for tree in trees]
    summary: dict[str, Any] = {'seed': SEED, 'folds_per_rank': 5, 'traits': {},
                              'no_outer_fold_scoring': True}
    with threadpool_limits(limits=1):
        for trait in TRAITS:
            df = pd.read_pickle(ROOT / f'data/derived/{trait}.pkl').sort_index()
            summary['traits'][trait] = {}
            for rank in RANKS:
                groups = list(df.index.astype(str)) if rank == 'random' else df[rank].tolist()
                if len(set(groups)) < 7:
                    summary['traits'][trait][rank] = {'status': 'insufficient_taxa_for_nested_five_folds',
                                                       'taxa': len(set(groups))}
                    continue
                outer = grouped_folds(groups, SEED + 1000 * RANKS.index(rank))
                folder = ROOT / f'data/gtdb-derived/local/{trait}'
                folder.mkdir(exist_ok=True)
                pd.DataFrame({'accession': df.index, 'taxon': groups, 'fold': outer}).to_csv(
                    folder / f'{rank}-folds.tsv', sep='\t', index=False)
                summaries = []
                for fold in range(5):
                    result = run_fold(df, trait, rank, outer, fold, trees)
                    summaries.append(result)
                    print(f'{trait} {rank} fold{fold}: {result["status"]}', flush=True)
                summary['traits'][trait][rank] = {
                    'taxa': len(set(groups)), 'fold_genomes': dict(Counter(map(int, outer))),
                    'fold_taxa': [len({groups[i] for i in np.flatnonzero(outer == f)}) for f in range(5)],
                    'folds': summaries}
                (ROOT / 'data/development-summary.json').write_text(
                    json.dumps(summary, indent=2, allow_nan=False)+'\n')
    artefacts = []
    for base in ('data/derived', 'data/gtdb-derived/local'):
        for path in sorted((ROOT / base).rglob('*')):
            if path.is_file():
                artefacts.append({'path': str(path.relative_to(ROOT)), 'bytes': path.stat().st_size,
                                  'sha256': digest(path)})
    (ROOT / 'data/artifact-manifest.json').write_text(json.dumps(artefacts, indent=2)+'\n')


if __name__ == '__main__':
    main()

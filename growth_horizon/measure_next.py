# SPDX-License-Identifier: Apache-2.0
"""Retrospective whole-order acquisition with fixed fitting choices."""
from __future__ import annotations

import json
from typing import Any

import joblib  # type: ignore[import-untyped]
import numpy as np
import pandas as pd  # type: ignore[import-untyped]
from sklearn.base import clone  # type: ignore[import-untyped]
from threadpoolctl import threadpool_limits  # type: ignore[import-untyped]

from growth_horizon.calibration import distance_edges
from growth_horizon.crossfit import crossfit_bins, inverse_quantile_scores
from growth_horizon.evaluation import summary
from growth_horizon.folds import SEED, grouped_folds
from growth_horizon.models import prediction
from growth_horizon.phase1 import nearest_rows
from growth_horizon.population import TRAITS, load_trees
from growth_horizon.scoring import LOCAL, RESULTS, calibrated, write_json
from scripts.acquire import ROOT
from scripts.preflight_sample import check_space

BUDGETS = [0, 25, 50, 75, 100]
STRATEGIES = ['widest', 'farthest', 'random']


def choose_order(candidates: Any, groups: Any, score: Any, remaining_budget: int,
                 random_order: list[str] | None = None) -> str | None:
    available = sorted(set(groups[candidates]))
    available = [g for g in available if int(np.sum(groups[candidates] == g)) <= remaining_budget]
    if not available:
        return None
    if random_order is not None:
        return str(next(g for g in random_order if g in available))
    return str(min(available, key=lambda g: (-float(np.mean(score[groups[candidates] == g])), str(g))))


def refit(df: Any, trait: str, fold: int, training: Any, query: Any, trees: Any
          ) -> dict[str, Any]:
    """Clone the frozen estimator specifications, refit, and recalibrate."""
    y, groups = df[trait].to_numpy(float), df['order'].to_numpy()
    base_seed = SEED+2000+10*fold
    inner = grouped_folds(groups[training].tolist(), base_seed+1)
    rng = np.random.default_rng(base_seed+4)
    uniforms, ties = rng.uniform(size=len(training)), rng.integers(0, 2, size=len(training))
    qrng = np.random.default_rng(base_seed+5)
    qu, qt = qrng.uniform(size=len(query)), qrng.integers(0, 2, size=len(query))
    all_scores, all_distances = np.empty(len(training)), np.full(len(training), np.inf)
    tuning, predictions = [], []
    for k in range(5):
        proper, cal = training[inner != k], training[inner == k]
        if set(groups[proper]) & set(groups[cal]) or set(proper) & set(query):
            raise ValueError('Acquisition fitting boundary violated')
        template = joblib.load(ROOT/f'data/gtdb-derived/local/crossfit/{trait}/order/fold{fold}/inner{k}/method.joblib')
        estimator, features = clone(template['estimator']), template['features']
        estimator.fit(df.iloc[proper][features], y[proper])
        pred = prediction(estimator, df.iloc[cal][features], trait)
        predictions.append(prediction(estimator, df.iloc[query][features], trait))
        if trait == 'oxygen':
            score = inverse_quantile_scores(pred, uniforms[inner == k], ties[inner == k])[
                np.arange(len(cal)), y[cal].astype(int)]
        else:
            score = np.abs(y[cal]-pred)
        distances, _ = nearest_rows(df, proper, cal, trees)
        all_scores[inner == k], all_distances[inner == k] = score, distances
        partition = grouped_folds(groups[proper].tolist(), base_seed+3+100*k)
        for f in range(5):
            d, _ = nearest_rows(df, proper[partition != f], proper[partition == f], trees)
            tuning.append(d)
    edges = distance_edges(np.concatenate(tuning))
    bins = crossfit_bins(all_distances, groups[training].tolist(), edges)
    record = {'distance_edges': edges.tolist(), 'methods': {'method': bins}}
    distances, _ = nearest_rows(df, training, query, trees)
    result = calibrated(np.array(predictions), all_scores, inner, all_distances,
                        distances, record, trait, qu, qt, y[query])
    template = joblib.load(ROOT/f'data/gtdb-derived/local/analysis/{trait}/order/fold{fold}/method.joblib')
    proper = training[inner != 0]
    estimator = clone(template['estimator'])
    estimator.fit(df.iloc[proper][template['features']], y[proper])
    pred = prediction(estimator, df.iloc[query][template['features']], trait)
    result.update({'y': y[query], 'point': pred.argmax(axis=1) if trait == 'oxygen' else pred,
                   'taxa': groups[query], 'distance': distances})
    return result


def curve_auc(points: list[dict[str, Any]], key: str) -> float | None:
    values = [p[key] for p in points]
    if any(v is None for v in values):
        return None
    return float(np.trapezoid(values, BUDGETS)/100)


def main() -> None:
    if not (RESULTS/'targets.json').exists():
        raise ValueError('Complete locked results required before acquisition')
    populations = {t: pd.read_pickle(ROOT/f'data/gtdb-derived/local/analysis/{t}.pkl').sort_index() for t in TRAITS}
    leaves = set().union(*(set(df['leaf']) for df in populations.values()))
    trees = [t.prune(leaves) for t in load_trees()]
    cuts = json.loads((ROOT/'data/gtdb-derived/horizon-cutpoints.json').read_text())
    output: dict[str, Any] = {'budgets': BUDGETS, 'maximum_organisms': 100,
        'whole_orders': True, 'original_hyperparameters_fixed': True, 'traits': {}}
    with threadpool_limits(limits=1):
        for trait, df in populations.items():
            output['traits'][trait] = {}
            locked = np.load(LOCAL/f'{trait}-order-method.npz', allow_pickle=True)
            for strategy in STRATEGIES:
                fold_curves = []
                for fold in range(5):
                    check_space()
                    groups = df['order'].to_numpy()
                    original_mask = locked['fold'] == fold
                    query = locked['row'][original_mask].copy()
                    training = np.setdiff1d(np.arange(len(df)), query)
                    original_far = set(query[locked['distance'][original_mask] >= cuts['traits'][trait]['order']['distance_edges'][-1]])
                    current = {k: locked[k][original_mask] for k in ('y', 'point', 'taxa', 'distance', 'supported', 'covered', 'size', 'abstain')}
                    orders = sorted(set(groups[query]))
                    random_order = np.random.default_rng(SEED+2000+10*fold).permutation(orders).tolist()
                    acquired: list[int] = []
                    selected_orders: list[str] = []
                    points: list[dict[str, Any]] = []
                    for budget in BUDGETS:
                        if budget:
                            before = len(acquired)
                            while len(acquired) < budget:
                                if strategy == 'farthest':
                                    current_distance, _ = nearest_rows(df, training, query, trees)
                                    score = current_distance
                                else:
                                    score = np.where(current['supported'], current['size'], np.inf)
                                order = choose_order(query, groups, score, budget-len(acquired),
                                                     random_order if strategy == 'random' else None)
                                if order is None:
                                    break
                                chosen = query[groups[query] == order]
                                remaining = groups[query] != order
                                acquired.extend(chosen.tolist())
                                selected_orders.append(str(order))
                                training = np.sort(np.concatenate((training, chosen)))
                                query = query[remaining]
                                current = {k: v[remaining] for k, v in current.items()}
                            if len(acquired) > before:
                                current = refit(df, trait, fold, training, query, trees)
                        far = np.array([int(i) in original_far for i in query])
                        metrics = summary(current, far, trait)
                        point = {'budget': budget, 'acquired_organisms': len(acquired),
                            'acquired_orders': len(selected_orders), 'unused_budget': budget-len(acquired),
                            'remaining_far_organisms': int(far.sum()), 'remaining_far_orders': len(set(groups[query][far])),
                            'mean_width': metrics['mean_size'], 'error': metrics['error']['value'],
                            'abstention_rate': metrics['abstention_rate'], 'metrics': metrics}
                        points.append(point)
                        print(f'{trait} {strategy} fold{fold} budget{budget}: acquired {len(acquired)}', flush=True)
                    fold_curves.append({'fold': fold, 'points': points,
                        'width_auc': curve_auc(points, 'mean_width'), 'error_auc': curve_auc(points, 'error')})
                    local = ROOT/f'data/gtdb-derived/local/measure-next/{trait}-{strategy}-fold{fold}.json'
                    write_json(local, {'selected_orders': selected_orders, 'acquired_rows': acquired})
                    write_json(RESULTS/f'measure-{trait}-{strategy}.json', fold_curves)
                output['traits'][trait][strategy] = {'folds': fold_curves,
                    'mean_width_auc': float(np.mean([f['width_auc'] for f in fold_curves]))
                        if all(f['width_auc'] is not None for f in fold_curves) else None,
                    'mean_error_auc': float(np.mean([f['error_auc'] for f in fold_curves]))
                        if all(f['error_auc'] is not None for f in fold_curves) else None}
    write_json(RESULTS/'measure-next.json', output)


if __name__ == '__main__':
    main()

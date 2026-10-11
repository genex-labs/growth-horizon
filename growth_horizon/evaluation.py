# SPDX-License-Identifier: Apache-2.0
"""Cluster sufficient statistics for the fixed empirical evaluation."""
from __future__ import annotations

from typing import Any

import numpy as np

from growth_horizon.folds import SEED

REPETITIONS = 2000


def estimate(values: Any, taxa: Any, oxygen: bool = False) -> dict[str, Any]:
    """Mean, or error from both class recalls, retaining each complete taxon."""
    values = np.asarray(values, dtype=float)
    unique, inverse = np.unique(taxa, return_inverse=True)
    if not len(values):
        return {'value': None, 'interval': None, 'taxa': 0, 'status': 'empty'}
    sums = np.zeros((len(unique), values.shape[1]))
    np.add.at(sums, inverse, values)
    def statistic(totals: Any) -> Any:
        if oxygen:
            denominators = totals[..., [1, 3]]
            recalls = np.divide(totals[..., [0, 2]], denominators,
                                out=np.full_like(denominators, np.nan), where=denominators > 0)
            return 1 - np.nanmean(recalls, axis=-1)
        return totals[..., 0] / totals[..., 1]
    value = float(statistic(sums.sum(axis=0)))
    if len(unique) < 2:
        return {'value': value, 'interval': None, 'taxa': len(unique),
                'status': 'insufficient_taxa'}
    rng = np.random.default_rng(SEED)
    draws = rng.integers(len(unique), size=(REPETITIONS, len(unique)))
    boot = statistic(sums[draws].sum(axis=1))
    valid = np.isfinite(boot)
    return {'value': value, 'interval': np.quantile(boot[valid], [.025, .975]).tolist()
            if np.any(valid) else None, 'taxa': len(unique), 'status': 'estimated',
            'valid_replicates': int(valid.sum())}


def error_values(y: Any, pred: Any, oxygen: bool) -> Any:
    if oxygen:
        return np.column_stack(((pred == y) & (y == 0), y == 0,
                                (pred == y) & (y == 1), y == 1)).astype(float)
    return np.column_stack((np.abs(y-pred), np.ones(len(y))))


def comparison(y: Any, reference: Any, proposed: Any, taxa: Any, oxygen: bool,
               weights: Any = None) -> dict[str, Any]:
    """Paired error reduction with the identical taxon draw for both methods."""
    a, b = error_values(y, reference, oxygen), error_values(y, proposed, oxygen)
    unique, inverse = np.unique(taxa, return_inverse=True)
    if not len(y):
        return {'value': None, 'interval': None, 'relative_reduction': None, 'taxa': 0}
    sa, sb = np.zeros((len(unique), a.shape[1])), np.zeros((len(unique), a.shape[1]))
    np.add.at(sa, inverse, a)
    np.add.at(sb, inverse, b)
    def error(t: Any) -> Any:
        if not oxygen:
            return t[..., 0]/t[..., 1]
        denominators = t[..., [1, 3]]
        return 1 - np.nanmean(np.divide(t[..., [0, 2]], denominators,
                             out=np.full_like(denominators, np.nan), where=denominators > 0), axis=-1)
    ea, eb = float(error(sa.sum(axis=0))), float(error(sb.sum(axis=0)))
    if len(unique) < 2:
        return {'value': ea-eb, 'interval': None,
                'relative_reduction': (ea-eb)/ea if ea else None, 'taxa': len(unique)}
    if weights is None:
        draws = np.random.default_rng(SEED).integers(len(unique),
                                                    size=(REPETITIONS, len(unique)))
        samples = error(sa[draws].sum(axis=1))-error(sb[draws].sum(axis=1))
    else:
        samples = error(weights @ sa)-error(weights @ sb)
    return {'value': ea-eb, 'interval': np.nanquantile(samples, [.025, .975]).tolist(),
            'relative_reduction': (ea-eb)/ea if ea else None, 'taxa': len(unique),
            'reference_error': ea, 'proposed_error': eb}


def summary(rows: dict[str, Any], mask: Any, trait: str) -> dict[str, Any]:
    """Coverage always excludes unsupported items and includes supported abstentions."""
    selected = np.asarray(mask, dtype=bool)
    taxa = rows['taxa'][selected]
    y, pred = rows['y'][selected], rows['point'][selected]
    oxygen = trait == 'oxygen'
    supported = selected & rows['supported']
    accepted = selected & ~rows['abstain']
    coverage = estimate(np.column_stack((rows['covered'][supported],
                                        np.ones(supported.sum()))), rows['taxa'][supported])
    coverage['abstention_rate'] = float(rows['abstain'][supported].mean()) if supported.any() else None
    coverage['supported_genomes'] = int(supported.sum())
    coverage['excluded_unsupported'] = int((selected & ~rows['supported']).sum())
    valid_taxa, inv = np.unique(rows['taxa'][supported], return_inverse=True)
    counts = np.bincount(inv)
    taxon_means = np.bincount(inv, weights=rows['covered'][supported])/counts if len(counts) else []
    taxon_coverage = estimate(np.column_stack((taxon_means, np.ones(len(valid_taxa)))), valid_taxa)
    taxon_coverage['abstention_rate'] = (float(np.mean(np.bincount(inv,
        weights=rows['abstain'][supported])/counts)) if len(counts) else None)
    sizes = rows['size'][supported]
    result = {'genomes': int(selected.sum()), 'taxa': len(set(taxa)),
              'error': estimate(error_values(y, pred, oxygen), taxa, oxygen),
              'coverage': coverage, 'taxon_weighted_coverage': taxon_coverage,
              'mean_size': float(sizes.mean()) if len(sizes) else None,
              'nonfinite_size_count': int((~np.isfinite(sizes)).sum()),
              'abstention_rate': float(rows['abstain'][selected].mean()) if selected.any() else None,
              'accepted_genomes': int(accepted.sum()),
              'coverage_accepted': estimate(np.column_stack((rows['covered'][accepted],
                  np.ones(accepted.sum()))), rows['taxa'][accepted]),
              'mean_size_accepted': float(rows['size'][accepted].mean()) if accepted.any() else None,
              'error_accepted': estimate(error_values(rows['y'][accepted], rows['point'][accepted],
                  oxygen), rows['taxa'][accepted], oxygen)}
    result['coverage_accepted']['abstention_rate'] = 0.0 if accepted.any() else None
    if oxygen:
        result['balanced_accuracy'] = 1-result['error']['value'] if result['error']['value'] is not None else None
        result['accuracy_accepted'] = float((rows['point'][accepted] == rows['y'][accepted]).mean()) if accepted.any() else None
        result['accepted_class_counts'] = {str(c): int((rows['y'][accepted] == c).sum()) for c in (0, 1)}
    return result

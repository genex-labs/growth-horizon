# SPDX-License-Identifier: Apache-2.0
"""Distance bins, residual conformal quantiles, sets and abstention."""
from __future__ import annotations

import math
from typing import Any

import numpy as np
import numpy.typing as npt

FloatArray = npt.NDArray[np.float64]


def distance_edges(distances: FloatArray) -> FloatArray:
    finite = distances[np.isfinite(distances)]
    if not len(finite):
        return np.array([], dtype=float)
    # Repeated cut points are removed, never split equal distances arbitrarily.
    return np.asarray(np.unique(np.quantile(finite, [0.2, 0.4, 0.6, 0.8])), dtype=np.float64)


def assign_bins(distances: FloatArray, edges: FloatArray) -> npt.NDArray[np.int64]:
    return np.searchsorted(edges, distances, side='right').astype(np.int64)


def conformal_quantile(scores: FloatArray, alpha: float = 0.1) -> float:
    if not 0 < alpha < 1 or not np.all(np.isfinite(scores)):
        raise ValueError('Invalid conformal inputs')
    k = math.ceil((len(scores) + 1) * (1 - alpha))
    return float(np.sort(scores)[k - 1]) if k <= len(scores) else math.inf


def merge_bins(bins: npt.NDArray[np.int64], taxa: list[str], n_bins: int,
               minimum: int = 100) -> tuple[list[list[int]], list[dict[str, Any]]]:
    groups = [[i] for i in range(n_bins)]
    history = []
    def count(group: list[int]) -> int:
        return len({taxa[i] for i in range(len(taxa)) if int(bins[i]) in group})
    while len(groups) > 1:
        small = next((i for i, g in enumerate(groups) if count(g) < minimum), None)
        if small is None:
            break
        candidates = [i for i in (small - 1, small + 1) if 0 <= i < len(groups)]
        neighbour = min(candidates, key=lambda i: (count(groups[i]), i))
        lo, hi = sorted([small, neighbour])
        merged = groups[lo] + groups[hi]
        history.append({'left': groups[lo], 'right': groups[hi], 'merged': merged,
                        'calibration_taxa': count(merged)})
        groups[lo:hi + 1] = [merged]
    return groups, history


def mondrian(scores: FloatArray, distances: FloatArray, taxa: list[str],
             edges: FloatArray, minimum: int = 100) -> dict[str, Any]:
    bins = assign_bins(distances, edges)
    finite = np.isfinite(distances)
    # No connected training leaf means an unsupported prediction, excluded from calibration.
    valid_bins = bins[finite]
    valid_taxa = [t for t, keep in zip(taxa, finite, strict=True) if keep]
    valid_scores = scores[finite]
    groups, history = merge_bins(valid_bins, valid_taxa, len(edges) + 1, minimum)
    output = []
    for group in groups:
        selected = np.isin(valid_bins, group)
        count = len({valid_taxa[i] for i in np.flatnonzero(selected)})
        bin_scores = valid_scores[selected]
        q = conformal_quantile(bin_scores) if count >= minimum else math.inf
        output.append({'original_bins': group, 'calibration_taxa': count,
                       'calibration_genomes': len(bin_scores),
                       'q90': q if math.isfinite(q) else None,
                       'supported': math.isfinite(q)})
    return {'bins': output, 'merges': history, 'minimum_taxa': minimum}


def numeric_abstain(half_width: float, limit: float, distance: float = 0.0) -> bool:
    return not math.isfinite(distance) or not math.isfinite(half_width) or 2 * half_width > limit


def oxygen_set(probabilities: FloatArray, q: float, distance: float = 0.0) -> list[int]:
    if not math.isfinite(distance) or not math.isfinite(q):
        return [0, 1]
    return [i for i, probability in enumerate(probabilities) if 1 - probability <= q]


def oxygen_abstain(prediction_set: list[int]) -> bool:
    return len(prediction_set) != 1

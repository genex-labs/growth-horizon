# SPDX-License-Identifier: Apache-2.0
"""Deterministic balanced grouped partitions, independent of phenotype values."""
from collections import Counter

import numpy as np
import numpy.typing as npt

SEED = 20261011
RANKS = ['genus', 'family', 'order', 'class', 'phylum', 'random']


def grouped_folds(groups: list[str], seed: int = SEED, k: int = 5) -> npt.NDArray[np.int64]:
    counts = Counter(groups)
    if len(counts) < k:
        raise ValueError('Fewer taxa than requested folds')
    rng = np.random.default_rng(seed)
    shuffled = list(np.array(sorted(counts))[rng.permutation(len(counts))])
    ordered = sorted(shuffled, key=lambda g: -counts[g])
    loads = [0] * k
    assignment = {}
    for group in ordered:
        fold = min(range(k), key=lambda f: (loads[f], f))
        assignment[group] = fold
        loads[fold] += counts[group]
    return np.array([assignment[group] for group in groups], dtype=np.int64)


def nested_membership(groups: list[str], outer: npt.NDArray[np.int64], fold: int,
                      seed: int) -> tuple[npt.NDArray[np.int64], npt.NDArray[np.int64]]:
    training = np.flatnonzero(outer != fold)
    inner = grouped_folds([groups[i] for i in training], seed)
    return training, inner

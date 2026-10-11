# SPDX-License-Identifier: Apache-2.0
"""Paired cluster bootstrap; a taxon draw retains all its genomes."""
from collections.abc import Callable

import numpy as np
import numpy.typing as npt

from growth_horizon.folds import SEED

Array = npt.NDArray[np.float64]


def taxon_bootstrap(values: Array, taxa: list[str], statistic: Callable[[Array], float],
                    repetitions: int = 2000, seed: int = SEED) -> tuple[float, float]:
    if len(values) != len(taxa) or not len(values):
        raise ValueError('Nonempty aligned bootstrap input required')
    unique = sorted(set(taxa))
    indices = {t: np.array([i for i, group in enumerate(taxa) if group == t]) for t in unique}
    rng = np.random.default_rng(seed)
    estimates = []
    for _ in range(repetitions):
        sample = rng.choice(unique, len(unique), replace=True)
        selected = np.concatenate([indices[t] for t in sample])
        estimates.append(statistic(values[selected]))
    return tuple(float(x) for x in np.quantile(estimates, [0.025, 0.975]))  # type: ignore[return-value]


def horizon(improvement_intervals: list[tuple[float, float]]) -> int | None:
    """First ordered bin whose paired improvement interval does not exclude zero."""
    return next((i for i, (low, _) in enumerate(improvement_intervals) if low <= 0), None)

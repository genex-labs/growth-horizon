# SPDX-License-Identifier: Apache-2.0
"""Pure metric functions for synthetic checks and the separately authorised run."""
from typing import Any

import numpy as np

from growth_horizon.statistics import taxon_bootstrap


def accuracy_error(y: Any, pred: Any, oxygen: bool = False) -> float:
    if not oxygen:
        return float(np.mean(np.abs(y - pred)))
    recalls = [float(np.mean(pred[y == c] == c)) for c in (0, 1) if np.any(y == c)]
    return 1 - float(np.mean(recalls))


def paired_improvement(y: Any, reference: Any, proposed: Any, taxa: list[str],
                       oxygen: bool = False, repetitions: int = 2000) -> tuple[float, float]:
    values = np.column_stack((y, reference, proposed)).astype(float)
    def statistic(sample: Any) -> float:
        return (accuracy_error(sample[:, 0], sample[:, 1], oxygen) -
                accuracy_error(sample[:, 0], sample[:, 2], oxygen))
    return taxon_bootstrap(values, taxa, statistic, repetitions=repetitions)


def interval_summary(y: Any, centres: Any, half_widths: Any, accepted: Any) -> dict[str, Any]:
    if not np.any(accepted):
        return {'coverage': None, 'mean_width': None, 'abstention_rate': 1.0}
    return {'coverage': float(np.mean(np.abs(y[accepted] - centres[accepted]) <= half_widths[accepted])),
            'mean_width': float(np.mean(2 * half_widths[accepted])),
            'abstention_rate': float(1 - np.mean(accepted))}

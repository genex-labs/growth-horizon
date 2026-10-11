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
    """Keep coverage over all items separate from selection-dependent coverage."""
    covered = np.abs(y - centres) <= half_widths
    return {'coverage_all': float(np.mean(covered)),
            'coverage_accepted': float(np.mean(covered[accepted])) if np.any(accepted) else None,
            'mean_width_all': float(np.mean(2 * half_widths)),
            'mean_width_accepted': float(np.mean(2 * half_widths[accepted]))
            if np.any(accepted) else None,
            'abstention_rate': float(1 - np.mean(accepted))}


def oxygen_summary(y: Any, prediction_sets: list[list[int]]) -> dict[str, Any]:
    """Set coverage includes abstentions; accepted accuracy is reported separately."""
    if len(y) != len(prediction_sets) or not len(y):
        raise ValueError('Labels and prediction sets must have the same nonzero length')
    covered = np.array([int(label) in classes
                        for label, classes in zip(y, prediction_sets, strict=True)])
    accepted = np.array([len(classes) == 1 for classes in prediction_sets])
    predictions = np.array([classes[0] if len(classes) == 1 else -1
                            for classes in prediction_sets])
    return {'coverage_all': float(np.mean(covered)),
            'mean_cardinality_all': float(np.mean([len(classes) for classes in prediction_sets])),
            'abstention_rate': float(1 - np.mean(accepted)),
            'accepted_count': int(np.sum(accepted)),
            'accuracy_accepted': float(np.mean(predictions[accepted] == y[accepted]))
            if np.any(accepted) else None,
            'balanced_accuracy_accepted': 1 - accuracy_error(y[accepted], predictions[accepted], True)
            if np.any(accepted) else None,
            'accepted_class_counts': {str(c): int(np.sum(y[accepted] == c)) for c in (0, 1)}}

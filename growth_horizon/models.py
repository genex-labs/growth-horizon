# SPDX-License-Identifier: Apache-2.0
"""Published baseline estimator specifications and inner-only alternatives."""
from functools import partial
from typing import Any

import numpy as np
from sklearn.feature_selection import SelectKBest, mutual_info_regression  # type: ignore[import-untyped]
from sklearn.linear_model import Lasso, LogisticRegression, Ridge  # type: ignore[import-untyped]
from sklearn.pipeline import make_pipeline  # type: ignore[import-untyped]
from sklearn.preprocessing import StandardScaler  # type: ignore[import-untyped]

from growth_horizon.folds import SEED

AA = list('ACDEFGHIKLMNPQRSTVWY')
ALL_AA = ['all_aa_' + aa for aa in AA]
COMPARTMENT_AA = [comp + '_aa_' + aa for comp in
                  ('extracellular_soluble', 'intracellular_soluble', 'membrane') for aa in AA]


def published(trait: str) -> tuple[Any, list[str]]:
    if trait == 'oxygen':
        return make_pipeline(StandardScaler(), SelectKBest(
            partial(mutual_info_regression, random_state=SEED), k=20),
            LogisticRegression(C=1.0, class_weight='balanced', max_iter=100000,
                               random_state=0, solver='lbfgs')), ALL_AA
    alpha = 0.001 if trait == 'temperature_optimum' else 0.01
    return make_pipeline(StandardScaler(), Lasso(alpha=alpha, max_iter=100000)), COMPARTMENT_AA


def alternative(trait: str, alpha: float, whole: bool = False) -> tuple[Any, list[str]]:
    estimator = (LogisticRegression(C=1.0 / alpha, class_weight='balanced', max_iter=100000,
                                   random_state=SEED) if trait == 'oxygen' else Ridge(alpha=alpha))
    return make_pipeline(StandardScaler(), estimator), ALL_AA if whole else COMPARTMENT_AA


def prediction(model: Any, x: Any, trait: str) -> Any:
    if trait == 'oxygen':
        probabilities = model.predict_proba(x)
        if list(model.classes_) != [0, 1]:
            raise ValueError('Both oxygen classes required in proper training')
        return probabilities
    return model.predict(x)


def loss(y: Any, pred: Any, trait: str) -> float:
    if trait == 'oxygen':
        labels = np.argmax(pred, axis=1)
        recalls = [float(np.mean(labels[y == c] == c)) for c in (0, 1) if np.any(y == c)]
        return 1.0 - float(np.mean(recalls))
    return float(np.mean(np.abs(y - pred)))


def nonconformity(y: Any, pred: Any, trait: str) -> Any:
    if trait == 'oxygen':
        return 1 - pred[np.arange(len(y)), y.astype(int)]
    return np.abs(y - pred)

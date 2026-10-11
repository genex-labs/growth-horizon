# SPDX-License-Identifier: Apache-2.0
"""Inspect fitting diagnostics only; never invoke prediction on a fitted estimator."""
import json
from typing import Any

import joblib  # type: ignore[import-untyped]
import numpy as np

from scripts.acquire import ROOT


def main() -> None:
    records: list[dict[str, Any]] = []
    base = ROOT / 'data/gtdb-derived/local/analysis'
    for file in sorted(base.rglob('*.joblib')):
        payload = joblib.load(file)
        if 'estimator' not in payload:
            continue
        estimator = payload['estimator'][-1]
        iterations = getattr(estimator, 'n_iter_', None)
        cap = getattr(estimator, 'max_iter', None)
        counts = [] if iterations is None else np.atleast_1d(iterations).astype(int).tolist()
        records.append({'path': str(file.relative_to(ROOT)), 'iterations': counts,
                        'iteration_cap': cap,
                        'reached_iteration_limit': bool(cap is not None and any(n >= cap for n in counts))})
    result = {'fitted_estimators_inspected': len(records),
              'estimators_at_iteration_limit': sum(r['reached_iteration_limit'] for r in records),
              'diagnostics': records, 'no_prediction_calls': True}
    (ROOT / 'data/gtdb-derived/optimisation-summary.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()

# SPDX-License-Identifier: Apache-2.0
"""Verify the fixed sample with the unchanged upstream feature implementation."""
import csv
import json
import sys
import time
from collections import defaultdict
from typing import Any

import numpy as np

from scripts.acquire import ROOT, acquire
from scripts.preflight_sample import LIMIT, check_space


def main() -> None:
    raw = ROOT / 'data/raw/verification'
    preflight = json.loads((ROOT / 'data/verification-plan.json').read_text())
    missing = sorted({r['accession'] for r in preflight['errors']})
    records = [r for r in preflight['records'] if r['accession'] not in missing]
    total = sum(r['bytes'] for r in records)
    if total > LIMIT:
        raise ValueError('Sequence download estimate exceeds 8 GB')
    (raw / 'resume3-size-gate.json').write_text(json.dumps({
        'available_genomes': 71, 'files': len(records), 'total_bytes': total,
        'limit_bytes': LIMIT, 'missing_accessions': missing,
        'rtol': 1e-7, 'atol': 1e-9}, indent=2) + '\n')
    paths: dict[str, dict[str, str]] = defaultdict(dict)
    for i, record in enumerate(records):
        acquire(record['url'], record['path'], record['bytes'])
        key = 'faa' if '_protein.faa' in record['path'] else 'fna'
        paths[record['accession']][key] = str(ROOT / record['path'])
        time.sleep(1)
        if i % 10 == 0:
            print(f'Acquired {i + 1}/{len(records)} sequence files', flush=True)
    sys.path.insert(0, str(raw / 'upstream'))
    from genome_spot.bioinformatics.genome import measure_genome_features  # type: ignore[import-not-found]
    with (ROOT / 'data/raw/labels/training_data.tsv').open() as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        assert reader.fieldnames is not None
        accession_col = reader.fieldnames[0]
        features = reader.fieldnames[1:231]
        rows = {r[accession_col]: r for r in reader}
    groups: dict[str, Any] = {}
    for name in ('all', 'extracellular_soluble', 'intracellular_soluble', 'membrane',
                 'diff_extra_intra'):
        groups[name] = {'comparisons': 0, 'agree': 0, 'max_absolute_difference': 0.0}
    output = raw / 'recomputed'
    output.mkdir(exist_ok=True)
    genome_results = []
    for i, (acc, pair) in enumerate(sorted(paths.items())):
        check_space()
        target = output / (acc + '.json')
        if target.exists():
            computed = json.loads(target.read_text())
        else:
            computed = measure_genome_features(faa_path=pair['faa'], fna_path=pair['fna'])
            target.write_text(json.dumps(computed, indent=2) + '\n')
        disagreement = []
        for f in features:
            group = next(g for g in groups if f.startswith(g + '_'))
            val = computed.get(group, {}).get(f[len(group) + 1:], 0.0)
            if val is None or not np.isfinite(val):
                val = 0.0
            original = float(rows[acc][f])
            match = bool(np.isclose(val, original, rtol=1e-7, atol=1e-9))
            groups[group]['comparisons'] += 1
            groups[group]['agree'] += int(match)
            groups[group]['max_absolute_difference'] = max(
                groups[group]['max_absolute_difference'], abs(val - original))
            if not match:
                disagreement.append(f)
        genome_results.append({'accession': acc, 'disagreeing_features': disagreement})
        result = {'seed': 20261011, 'rtol': 1e-7, 'atol': 1e-9,
                  'download_bytes': total, 'unavailable': missing,
                  'recomputed': len(genome_results), 'groups': groups, 'genomes': genome_results,
                  'status': 'complete' if len(genome_results) == 71 else 'running'}
        (ROOT / 'data/feature-verification.json').write_text(json.dumps(result, indent=2) + '\n')
        print(f'Recomputed {i + 1}/71: {acc}, disagreements={len(disagreement)}', flush=True)


if __name__ == '__main__':
    main()

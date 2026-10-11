# SPDX-License-Identifier: Apache-2.0
"""Count every label and map assemblies to the current species representative."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd  # type: ignore[import-untyped]

from growth_horizon.tree import TreeIndex
from scripts.acquire import ROOT

TRAITS = ['temperature_optimum', 'oxygen', 'salinity_optimum', 'ph_optimum']
TAXON_RANKS = ['domain', 'phylum', 'class', 'order', 'family', 'genus', 'species']


def canonical(accession: str) -> str:
    return accession.removeprefix('GB_').removeprefix('RS_').replace('GCF_', 'GCA_').split('.')[0]


def load_population(trees: list[TreeIndex]) -> tuple[Any, dict[str, Any]]:
    # Common species contain thousands of accessions in one official TSV field.
    csv.field_size_limit(10_000_000)
    df = pd.read_csv(ROOT / 'data/raw/labels/training_data.tsv', sep='\t', index_col=0)
    df.index = df.index.astype(str)
    features = list(df.columns[:230])
    wanted = set(df.index)
    mappings: dict[str, dict[str, str]] = {}
    tree_names = {name for tree in trees for name in tree.names}
    tree_canonical = {canonical(name): name for name in tree_names}
    with (ROOT / 'data/raw/gtdb/auxillary_files/sp_clusters_r232.tsv').open() as stream:
        reader = csv.DictReader(stream, delimiter='\t')
        for row in reader:
            representative = row['Representative genome']
            members = row['Clustered genomes'].split(',') + [representative]
            matches = {canonical(member): member for member in members if canonical(member) in wanted}
            leaf = tree_canonical.get(canonical(representative), '')
            lineage = row['GTDB taxonomy'].split(';') + [row['GTDB species']]
            for acc, member in matches.items():
                record = {'accession': acc, 'metadata_accession': member,
                          'representative': representative, 'leaf': leaf}
                record.update(dict(zip(TAXON_RANKS, lineage, strict=True)))
                if acc in mappings and mappings[acc]['leaf'] != leaf:
                    raise ValueError('Ambiguous assembly representative mapping')
                mappings[acc] = record
    mapping_df = pd.DataFrame.from_dict(mappings, orient='index')
    (ROOT / 'data/gtdb-derived/local/analysis').mkdir(parents=True, exist_ok=True)
    mapping_df.to_csv(ROOT / 'data/gtdb-derived/local/mapping.tsv', sep='\t', index=False)
    # Ignore the release's use flags: the primary population contains every usable nonmissing label.
    feature_good = np.isfinite(df[features].to_numpy(dtype=float)).all(axis=1)
    summary: dict[str, Any] = {'raw_genomes': len(df), 'mapped_genomes': len(mappings),
                              'traits': {}}
    for trait in TRAITS:
        reasons: Counter[str] = Counter()
        usable = []
        for i, (acc, row) in enumerate(df.iterrows()):
            y = row[trait]
            if pd.isna(y):
                reason = 'missing_label'
            elif not np.isfinite(float(y)):
                reason = 'nonfinite_label'
            elif trait == 'oxygen' and y not in (0, 1):
                reason = 'invalid_oxygen_class'
            elif acc not in mappings:
                reason = 'absent_from_release232_metadata'
            elif not mappings[acc]['leaf']:
                reason = 'species_representative_absent_from_reference_tree'
            elif not feature_good[i]:
                reason = 'nonfinite_published_feature'
            else:
                reason = 'usable'
                usable.append(acc)
            reasons[reason] += 1
        summary['traits'][trait] = {'usable': len(usable), 'counts_by_reason': dict(reasons),
            'taxa': {rank: len({mappings[a][rank] for a in usable})
                     for rank in TAXON_RANKS}}
        subset = df.loc[usable, features + [trait]].join(mapping_df[TAXON_RANKS + ['leaf']])
        subset.to_pickle(ROOT / f'data/gtdb-derived/local/analysis/{trait}.pkl')
    (ROOT / 'data/gtdb-derived/population-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    return df, summary


def load_trees(root: Path = ROOT) -> list[TreeIndex]:
    return [TreeIndex.read(root / f'data/raw/gtdb/{domain}_r232.tree.gz')
            for domain in ('ar53', 'bac120')]

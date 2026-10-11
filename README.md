# Growth Horizon

A draft open benchmark for growth-temperature, oxygen-tolerance, salinity and
pH predictions from microbial genomes under nested taxonomic holdout.

The exact release table has documented experimental-label provenance.
Phase 1C freezes amendment C in [pre-registration v2](PREREGISTRATION.md),
with five inner cross-fits, a 50-taxon calibration support rule and a
strong-support flag at 100 taxa. Family and order now have supported
calibration bins; these counts are calibration-side information, not measured
coverage. See [data provenance](DATA.md) and
`data/experimental-label-audit.json` for the source decision and residual risk.

A clean reconstruction reproduced all 7,257 frozen scientific artefacts,
548 source records and the v2 pre-registration byte for byte. The original
1,113 v1 scientific artefacts remain unchanged. See
[reconstruction details](docs/reproducibility.md).

Both versions were frozen before any outer-fold prediction or metric.
V2 supersedes v1 for the proposed locked run; scientific review and a separate
authorised phase-2 run remain required.

| Version | Local freeze commit | Freeze time | PREREGISTRATION.md SHA-256 |
| --- | --- | --- | --- |
| v1 | `22bc860563c0397e8ab935f6517892370f21afcd` | 2026-10-11 04:30:02 PT | `d7ae79e500b27fdea91693aa5bd7038e701ff84909b9b896eef000cb322b5c3d` |
| v2, amendment C | `54d803cefa1414a8aaec960d746cdc2463e59f84` | 2026-10-11 07:46:14 PT | `cabc7ecffdd2e11246c8ab7b08b3103b09819f3fde1bcae87ab9cb649330a179` |

Calibrated per-distance intervals for this matched growth-condition benchmark
were not found in our literature check of 2026-10-11. Related work includes
GenomeSPOT, Bac2Feature, out-of-clade phenotype prediction and CalPred; see
[related work](docs/related-work.md). The statement is a search finding, not a
priority claim or a measured result.

Phase 1 acquires and verifies inputs, counts every label and exclusion, builds
nested grouped folds, computes phenotype-free distances, fits baselines on
training sides and calibrates using inner holdouts. It does not compute any
outer-fold prediction or performance metric. Phase 2 requires a reviewed
pre-registration and a separate authorised locked run. No scientific outcome
is claimed here.

With Python 3.13 and the pinned `uv.lock`, rebuild every phase-1 artefact from
the source manifest with:

```sh
uv run --frozen python -m scripts.rebuild
```

The command accepts only the documented release-table provenance or verified
experimental provenance for another source. It verifies existing raw files
or reacquires missing downloadable sources, recomputes the authorised 71-genome feature check without resampling,
and rebuilds all local populations, folds, distances, fitted estimators,
naive calibration spreads, cross-fitted calibration scores and support bins,
and common horizon cut points. Source and derived
checksums are in `data/source-manifest.json` and `data/artifact-manifest.json`.
Historical incomplete-download and process receipts are provenance evidence,
not rebuild inputs. Downloads stay below the recorded 8 GB estimates and
stop if root-volume free space falls below 25 GB. No account or key is needed.

Raw labels, sequences, individual feature comparisons, fitted estimators and
individual derived records stay untracked. Published data files are aggregate
summaries and provenance. GTDB-derived tables stay in their own CC BY-SA 4.0
folder. Our code is Apache-2.0; upstream GenomeSPOT source retains MIT terms.
See [data provenance](DATA.md), [baseline specifications](docs/baselines.md),
and [integrity](docs/INTEGRITY.md).

Offline verification:

```sh
uv run --frozen pytest --basetemp=work-tmp/pytest-benchmark
uv run --frozen ruff check scripts growth_horizon tests
uv run --frozen mypy scripts growth_horizon tests
```

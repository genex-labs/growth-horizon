# Growth Horizon

A draft open benchmark for growth-temperature, oxygen-tolerance, salinity and
pH predictions from microbial genomes under nested taxonomic holdout.

Resume 5 accepts the documented experimental-label provenance for the exact
release table. Phase 1 is complete, with inner-only development artefacts and
[a locally committed pre-registration](PREREGISTRATION.md). A fresh
reconstruction reproduced all frozen scientific artefacts and the record
byte for byte. Family and order calibration remain unsupported under the
prescribed 100-calibration-taxon rule; the limitation is frozen for review.
See [data provenance](DATA.md) and
`data/experimental-label-audit.json` for the decision and residual risk.

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
naive intervals and Mondrian calibration summaries. Source and derived
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

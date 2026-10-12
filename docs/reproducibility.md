# Reconstructing the release candidate

## Offline verification of the committed aggregates

These commands read files already in the checkout. They do not download inputs, refit estimators or rescore folds.

```sh
uv run --project release --frozen python -m scripts.check_release
uv run --frozen pytest --basetemp=work-tmp.noindex/pytest-fixtures
```

The scan command uses the rendering project because it reads the PDF. It compares each path in `data/release-manifest.json` with its recorded size and SHA-256, then writes `data/checks/release-scan.json`. The fixture command runs the offline tests in the analysis environment. `data/raw/` and `data/gtdb-derived/local/` are not required for this check, and they are not redistributed.

## Full release (`scripts.release`)

```sh
uv run --project release --frozen python -m scripts.release
```

This command acquires missing official inputs, verifies cached source hashes, reconstructs the frozen analysis, verifies the pre-registration, scores the locked outer folds, runs measurement selection and generates the public package. Analysis and rendering locks are separate. It needs a network connection or a checksum-verified copy of the raw inputs. It is not an offline check.

`data/raw/` and `data/gtdb-derived/local/` (fitted trees and individual predictions) are not redistributed. The pinned replay inputs under `data/raw/labels/`, `data/raw/verification/` and `data/raw/gtdb/` total 254,404,224 bytes in `data/source-manifest.json`. Acquisition stops if free space on `/` is below 25 GB. Scratch is confined to `work-tmp.noindex/`, which is listed in `.gitignore`; the entry point also adds it to the local Git exclude list and sets TMPDIR there.

The recorded final replay used a fresh local clone with checksum-verified source-cache files only. No population, fitted estimator, fold, calibration score or individual prediction was copied. That replay does not claim a new from-empty-network download. Output hashes are in `data/release-manifest.json`; process, fixture and scan receipts are in `data/checks`. Committed outer-fold results are already in `data/gtdb-derived/results/`. `scripts.release` is the command that scores those folds. A later run is expected to match the pinned scientific outputs.

`uv.lock` allows any Python 3.13 (`requires-python = "==3.13.*"`). It does not pin 3.13.15 alone. The frozen numbers were produced with Python 3.13.15. A fresh export used Python 3.13.12 with the same lock.

## Phase 1 rebuild (`scripts.rebuild`)

```sh
uv run --frozen python -m scripts.rebuild
```

This command replays pinned sources and rebuilds phase 1 fits. It does not score outer folds. Numeric intervals and oxygen sets on outer genomes remain uncomputed by this command. Rebuilding is distinct from publishing, and phase 2's locked scoring is absent from this command. Those limits describe `scripts.rebuild` only. They do not describe `scripts.release` or the committed outer-fold results.

## Earlier frozen reconstructions


Table-level experimental provenance is accepted for the exact authorised
release checksum and documented chain. Other label sources retain the verified
experimental-label gate. The earlier v1 reconstruction matched 542 source
records, 1,113 scientific artefacts, aggregate records and the pre-registration
byte for byte. [CHANGELOG.md](../CHANGELOG.md) lists the v1 and v2 freezes with their
commits, times and the pre-registration checksum.

The v2 reconstruction used a fresh export of commit
`54d803cefa1414a8aaec960d746cdc2463e59f84`, seeded with 476 checksum-verified
source-cache files. Individual derived tables, fitted estimators and the
recomputed-feature cache were absent before rebuilding. All 71 feature
measurements were recomputed from sequences, all 120 v1 development folds
were rebuilt, and all 600 calibration fitting sides were reconstructed with
nested tuning. The host restarted after 60 calibration folds completed;
all 4,212 artefacts then present matched the frozen manifest. Those completed
folds were retained after checksum verification, and the remaining 60 folds
were rebuilt. The partially written next fold was rerun because its complete
fold record had not been saved. No scientific artefact was copied from the
main checkout to fill a reconstruction gap.

All 548 source records, 7,257 scientific artefacts, aggregate records and the
v2 pre-registration matched byte for byte. The original 1,113 v1 scientific
artefacts remain unchanged. The main environment used Python 3.13.15; the
fresh export selected Python 3.13.12 with the same pinned dependency lock.
The lock accepts any Python 3.13, as recorded above. This verifies
reconstruction from the source cache; a from-empty-network download was not
repeated. No outer-fold prediction, interval or metric was computed during
either of those earlier reconstructions. The current tree does contain
outer-fold results, produced later by `scripts.release`.

## What the phase 1 rebuild uses

The entry point is `uv run --frozen python -m scripts.rebuild`. Source replay
uses pinned labels, upstream feature code, sequences and GTDB files. It checks
SHA-256 against the manifest and never treats a tampered existing input as a
passing cache. Other historical source-audit records are not required inputs.
The versioned verification plan contains the fixed sample and the authorised
available subset, so local historical receipts need not exist in a new checkout.

Every fitted estimator is local and records its proper-training indices and
feature list. Membership-distance archives store outer training/test indices,
inner assignments, proper and calibration rows, naive random rows and both
outer-training and actual-fitting-side distances. No archive stores outer
predictions. The v1 calibration records retain their finite-sample quantiles
and merges for the unchanged point fits and naive comparator. V2 additionally
stores each of five calibration-side fitting memberships, nested tuning
distances, out-of-fold scores and every adjacent-bin merge, with support at
50 distinct taxa and strong support at 100. Common horizon cuts pool the
phenotype-free tuning distances over all five outer folds per trait and rank.
During this phase 1 rebuild, numeric intervals and oxygen sets on outer
genomes remain uncomputed.

Calibration fitted files use sorted metadata and omit identity memoisation
when serialising their acyclic payloads. This prevents shared string and
dtype identities from changing checksums between fresh and reloaded fits.
Two earlier v2 freezes were superseded after reconstruction exposed this
serialization difference; numerical fitted states, parameters, scores,
memberships, cuts and support rules were unchanged. Their commits preserve
the earlier versions.

NumPy generators, estimator seeds, the sample algorithm and every fold seed
are fixed. The runtime uses one numerical-library thread. A three-connection
GTDB range transfer retains each exact byte range and checks the assembled
file against the published MD5 plus its manifest SHA-256. NCBI downloads use
at most three connections with a shared one-second request-start spacing.
The default verification entry point uses one connection. The sequence
worker limit is an execution choice, not a change to inputs or analysis.

Raw tables, sequences, individual features and local estimator files remain
ignored. Aggregate records can be regenerated locally. Phase 2's locked
scoring is absent from `scripts.rebuild` and is present in `scripts.release`.

Historical failed transfers and superseded preflight receipts are preserved as
evidence under data/raw and labelled accordingly in the source manifest.
A stopped transfer has an owned-process-tree receipt that confirms no surviving
descendant. Test scratch stays under ignored scratch, not a system temporary
folder. No directory is removed by the build scripts.

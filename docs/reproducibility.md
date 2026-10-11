# Rebuilding phase 1

Table-level experimental provenance is accepted for the exact authorised
release checksum and documented chain. Other label sources retain the verified
experimental-label gate. The earlier v1 reconstruction matched 542 source
records, 1,113 scientific artefacts, aggregate records and the pre-registration
byte for byte. [README](../README.md) lists the v1 and v2 freezes with their
commits, times and checksums.

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
This verifies reconstruction from the source cache; a from-empty-network
download was not repeated. No outer-fold prediction, interval or metric was
computed during either reconstruction.

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
Numeric intervals and oxygen sets on outer genomes remain uncomputed.

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
ignored. Aggregate records can be regenerated locally. Rebuilding is distinct
from publishing, and phase 2's locked scoring is absent from this command.

Historical failed transfers and superseded preflight receipts are preserved as
evidence under data/raw and labelled accordingly in the source manifest.
A stopped transfer has an owned-process-tree receipt that confirms no surviving
descendant. Test scratch stays under ignored work-tmp, not a system temporary
folder. No directory is removed by the build scripts.

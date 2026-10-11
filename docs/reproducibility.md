# Rebuilding phase 1

Resume 5 accepts table-level experimental provenance for the exact authorised
release checksum and documented chain. Other label sources retain the verified
experimental-label gate. The earlier interrupted replay remains historical evidence. The completed
Resume 5 reconstruction used a fresh export of the pre-registration commit
and checksum-verified raw inputs. Individual derived tables, fitted estimators
and the recomputed-feature cache were absent before rebuilding. All 71 feature
measurements were recomputed from sequences, all 120 inner-only folds were
rebuilt, and all 542 source records, 1,113 scientific artefacts, aggregate
records and the pre-registration matched byte for byte. The main environment
used Python 3.13.15; the fresh export selected Python 3.13.12 with the same
pinned dependency lock. This verifies reconstruction from the source cache;
a from-empty-network download was not repeated.

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
predictions. Local calibration records store finite-sample quantiles and every
bin merge; aggregate development summaries reproduce those records.

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

# Rebuilding phase 1

Resume 4 adds an experimental-label gate before population construction,
development and pre-registration. The current receipt is unresolved for every
trait, so the rebuild intentionally stops. The earlier clean-checkout replay
was interrupted during verification and is not a completed reproducibility
check. Existing outputs remain historical until label provenance is verified.

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

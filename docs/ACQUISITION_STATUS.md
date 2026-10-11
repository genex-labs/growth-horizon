# Label-source acquisition gate

Current status: resumed from the licence decision and stopped at the mandatory
table-column source gate, 2026-10-11 PT. See the current inspection below.
The earlier record is retained as historical evidence.

## Current inspection after the Resume decision

The original checkout was clean at `86f5d17`. The owner authorised the release
`v1.0.0` training asset and supplied the licence basis now recorded word for word
in [DATA.md](../DATA.md). The asset's required size and checksum are verified by
`scripts/audit_labels.py`; actual verification results are in
`data/label-audit.json` and the source manifest.

The table has 267 fields including the accession: 230 sequence-derived feature
columns, 29 BacDive trait and derived-flag columns, seven GTDB taxonomy columns,
and the accession. The release README documents downloading GenBank genomic and
protein FASTA files from NCBI, then measuring features. The release construction
script confirms that these feature measurements are joined to the target table.
Examples are `all_nt_length`, `all_total_protein_length` and `all_aa_A`.

The Resume section says: "If any column comes from a source other than BacDive
or GTDB, stop and report." The NCBI sequence-derived block reaches this gate.
It was neither silently discarded nor substituted for the required recomputed
features. No downstream benchmark work was undertaken after the gate.

The incomplete clone mentioned in the earlier report was already absent at
resume. `work-tmp/` contained only an empty `source-audit/` directory. No clone
material existed to move to the Trash. Required construction sources were
downloaded again through GitHub. A redundant source-archive download was stopped
with its whole process tree; the receipt confirms no survivors. The partial
archive is preserved as acquisition evidence in `data/raw/source-audit/`.

The official GTDB release index was read and lists release 232 as its newest
numbered release. It is preserved as source evidence; no reference tree or
metadata file was selected or downloaded. No proteome size estimate or download
was attempted, and no feature fallback was taken. GTDB-derived data tables have
not been produced.

The inspection counts observed label values and upstream inclusion flags only.
Usable analysis populations and exclusions are not determined until the source
gate is resolved and the data are mapped to the selected GTDB release. No folds,
bins, baseline fitting, calibration or scoring have been performed. B4's code
and licence have not been assessed. No pre-registration exists.

Hub: no (the brief prohibits additional language-model calls). The root-session
override was used; no workers or external planning/review calls were made.

## Historical record before the Resume decision

Status at the earlier stop: before label-table acquisition, 2026-10-11 PT.

The binding design was read in full and its supplied SHA-256 matched:
`a424481648082a52fd05a4471b1d5f23d4d000ec262de33774b16eb3ae9b3b33`.
The baselines review and the Director's decisions were also read in full.

The repository at `https://github.com/cultivarium/GenomeSPOT` was inspected
through its public source and release records. Its complete recursive tree at
`f79f7d6fdece71b766ff47f4fb7114daae5287d7` has 115 entries and only one licence
notice, the root `LICENSE`. The MIT notice was read in full at both main and the
training-data release tag. It grants rights in software and associated
documentation. The README links training data to the release but does not state
separate data terms or explicitly apply MIT to the label table.

The `v1.0.0` pre-release, published on 2026-03-16 at 12:27:17 UTC, has one asset,
`training_data.tsv`, with an advertised size of 64,412,996 bytes and advertised
SHA-256 `19a9f888f06655e17e95c7110ab4ff5ace38ece121e6cb1ac3bcb7d3c087abcc`.
Its description is only "Training data in tsv format". The asset was not
downloaded, so its checksum and per-genome label structure are not locally
verified. The downloaded MIT notice has SHA-256
`3f6ae28036d1d671f0c97ee76cadab9c73a8379c1eaedb36b0c0a44872d16091`.

The repository software licence is MIT. The separate training-table data licence
is unclear from the inspected sources. This does not establish that the data
cannot be reused; it fails the brief's explicit requirement for a clear data
licence. The brief requires stopping and reporting at this gate.

The alternative BacDive API route was not attempted. It may need an account,
which requires the owner's authorization. BacDive attribution under CC BY 4.0
and GTDB-derived tables under CC BY-SA 4.0 are prescribed by the design, but no
such tables have been acquired or produced here.

The shallow source clone was stopped as soon as the gate was established. Its
entire owned process tree was terminated and all four process identifiers were
confirmed absent. Incomplete clone material is retained under `work-tmp/`.
The completed source records and process-stop receipt are retained in the raw
audit directory and indexed by actual sizes and checksums in the manifest.

No proteome was downloaded and no proteome size estimate was attempted. No GTDB
release was selected or downloaded. Per-trait counts and exclusions are unknown,
not zero. Folds, bins, features, baselines B1 to B4, calibration, bootstrap tests,
and DOI checks remain unstarted because of this mandatory stop. In particular,
B4's code and licence have not been assessed.

No outer-fold prediction or metric was computed. No integrity incident or
quarantine was required. No pre-registration was created or committed. The
repository remains a local acquisition record; nothing was pushed or published.

Resume requires a source-confirmed licence covering the release label table, or
an owner-authorised change to the label acquisition route. The planned build and
pre-registration must follow after that gate is resolved.

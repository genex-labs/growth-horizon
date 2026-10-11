# Label-source acquisition gate

Status: stopped before label-table acquisition, 2026-10-11 PT.

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

# Current phase-1 resume

Resume 5 supersedes the historical Resume 4 provenance stop. The exact release
table is accepted as experimental under the documented notebook/parser chain,
with residual risk retained in DATA.md and the per-trait audit. Inner-only
rebuilding and pre-registration are authorised; outer scoring remains forbidden.
All historical records below describe their earlier stops, not the current
permission state. Phase 1 is complete: the pre-registration is locally committed, all 120
inner-only folds are built, and the fresh reconstruction matches all frozen
inputs and outputs. No outer prediction or metric was computed. The phase-1
handoff records commit, time, checksum and verification receipts. Family and
order calibration remain unsupported under the prescribed 100-taxon rule;
this limitation is frozen for review rather than relaxed.

## Historical Resume 3 development status

Resume 3 resolves the unavailable-proteome stop and makes feature differences
a reportable finding. Acquisition and inner development are complete. The
following earlier status records are historical; they do not describe the
current permission or build state. Current aggregate receipts supersede them.

GTDB R11-RS232 maps the complete primary populations: temperature 4,715,
oxygen 7,230, salinity 2,347 and pH 3,513. Missing labels and current-release
mapping exclusions are recorded separately in the population summary.
The 71 available sampled genome pairs total 135,825,146 compressed bytes.
All were recomputed; agreement is 95.65% in each of five feature groups.
The 29 unavailable accessions and all tolerances remain recorded without
resampling. See DATA.md for the discrepancy finding.

The runner builds 120 nested folds across four traits and six ranks/references.
B1, B2 and B3 are fitted and calibrated only on inner queries. B4 is omitted
for the documented licence and input limitations. The 100-calibration-taxon
requirement leaves every family, order, class and phylum fold unsupported;
this prevents assessment of the family/order calibration target under the
prescribed design. No outer prediction or metric was computed. Pre-registration
and complete clean rebuild verification had not finished when the run stopped.

# Resume 2: feature-verification source blocker

Current status: blocked on unavailable sampled GenBank proteomes, 2026-10-11 PT.
Resume began from the clean commit `5e1c843`. Resume 2's prescribed licence
paragraph is recorded word for word in [DATA.md](../DATA.md). The training
asset was rechecked: 64,412,996 bytes, SHA-256
`19a9f888f06655e17e95c7110ab4ff5ace38ece121e6cb1ac3bcb7d3c087abcc`.

## Fixed verification sample and size audit

Seed `20261011` selects 100 genomes without replacement from the sorted 8,174
accessions with at least one nonmissing target label. Sample replay matched
under Python 3.13.15. The release's own feature code and signal-peptide parameters
were acquired again, unchanged, with source hashes in the manifest. Its MIT
notice is retained. Incomplete clone material was absent from `work-tmp/`;
the historical partial source archive remains preserved as acquisition evidence.

The official NCBI Datasets service resolved all 100 accession reports. The
preflight examines both protein FASTA and nucleotide FASTA because the full
feature implementation requires both. After correcting path formatting for
spaces and `#`, the final audit found 100 nucleotide files and 71 proteomes:
171 files totalling 170,786,627 compressed bytes. The remaining 29 proteomes
return HTTP 404. Their official assembly directories were each read and contain
no protein FASTA. Datasets summaries independently confirm no protein file for
three of these assemblies. The earlier path-audit receipt is preserved separately
and superseded by the corrected receipt.

The complete 100-genome download size cannot be established, so the size gate
is `size_unknown`, not exceeded or passed. No sequence was downloaded, no sampled
genome was substituted and no feature agreement was calculated. There is no
observed floating-point mismatch; the required comparison could not run. NCBI's
published unkeyed Datasets limit is five requests per second. Preflight requests
were serial and spaced by at least one second; supplemental source probes stayed
below the published limit. No account or key was used.

## Remaining phase 1 work

The source manifest records URLs, actual sizes and SHA-256 for every acquired
record, plus the available sequence URLs and estimated sizes in the raw preflight
receipt. Raw labels, sequences and individual feature records are untracked.
No GTDB-derived table has been produced. The earlier GTDB release index records
release 232 as the newest numbered release; reference trees and metadata have
not been acquired or selected for the benchmark.

Observed labels are temperature 4,783; oxygen 7,300; salinity 2,376; pH 3,549.
There are 15,596 distinct accessions and no duplicate or blank accession.
Analysis populations and exclusion counts remain unknown pending feature
verification and GTDB mapping. Upstream inclusion flags are inspection counts,
not adopted exclusions.

B1 and the proposed method's precomputed features await verification. B2 awaits
the tree. B3's 20 whole-proteome amino-acid frequency columns exist and need no
additional full-population sequence download, but B3 has not run. B4's code and
licence were not assessed after the source blocker. No folds, distances, bins,
training, calibration, bootstrap, DOI verification or pre-registration has been
completed. The full clean-checkout benchmark rebuild command is not implemented.
No outer-fold prediction or metric was computed, and no integrity incident or
quarantine was required.

The Python environment has a pinned lock. Four offline acquisition-gate tests,
Ruff and mypy pass with exit code 0. Tests of folds, distances, bins, conformal
quantiles, abstention and bootstrap remain unimplemented with those components.
Initial test imports and a duplicate-module typing error were corrected before
the passing run. No process was forcibly stopped in this resume. Free space
remained above 25 GB. No manually created `/private/tmp` test directory exists.

Hub: no (the brief prohibits additional language-model calls). Planning,
implementation and review stayed in the root session under the best-effort
routing override. No workers were started. Nothing was pushed or published.

Resume needs the original annotated proteomes for the 29 fixed-sample accessions
at permitted NCBI paths, or an explicit amendment to the verification protocol.
Current RefSeq annotations have not been substituted for original GenBank inputs.

## Historical records, superseded where stated

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

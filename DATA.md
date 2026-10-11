# Data provenance and permitted use

## Resume 5: accepted experimental-label provenance

GenomeSPOT's preparation notebook (last changed 2024-03-21, commit f994ef50450f3362a4d6f93ccd3260c80e8ca45c) names its output training_data_20231203.tsv, and its 15,596 rows and trait summaries match the release asset; the model-predicted BacDive values come from Koblitz et al. 2025 (doi 10.1038/s42003-025-08313-3) and are served only with the API parameter predictions=1, which GenomeSPOT's parser does not request. Decision: treat the table's labels as experimental records.

Residual risk: the release asset could in principle differ from the 2023 table in ways the matching checks did not cover.

The owner accepted this table-level chain on 2026-10-11 at 04:17 PDT. The
historical filename suggests 2023-12-03; the independently verified facts are
the notebook's last change and displayed row/trait summaries, not a checksum
of the entire historical table or an authenticated BacDive snapshot. The
release asset was created 2026-03-16T12:25:19Z, updated 12:25:50Z, and its
release published 12:27:17Z. These are upload dates, not table-build dates.
No per-value provenance is invented.

The per-trait audit accepts 4,783 temperature, 7,300 oxygen, 2,376 salinity
and 3,549 pH nonmissing labels as experimental under this documented decision.
No predicted record is identified or excluded under the accepted source
recipe. Individually confirmed experimental and predicted counts remain
unknown; accepted table-level counts are recorded separately. Mapping and
feature exclusions remain separately counted. Only the exact authorised
size/checksum and source chain bypass the snapshot-date requirement. The
experimental-label guard stays in force for every other label source.

`data/experimental-label-audit.json` freezes the chain, per-trait dispositions
and source-evidence hashes. The superseded Resume 4 stop and historical
artefacts are preserved in the preceding local commits and ignored work
records. The decision permits inner-only development and pre-registration;
no outer-fold prediction or metric is authorised.

BacDive's [About page](https://bacdive.dsmz.de/about) asks commercial users to
contact DSMZ. This request is recorded alongside the CC BY 4.0 licence basis;
no contact was made. GenomeSPOT's MIT notice remains preserved in
`docs/GenomeSPOT-MIT.txt`.

The sections below preserve the earlier decisions and acquisition findings.

GenomeSPOT's README states that its training data were downloaded from the BacDive API and the Genome Taxonomy Database. BacDive states: 'This work is licensed under a Creative Commons Attribution 4.0 International License' (https://bacdive.dsmz.de/about, read 2026-10-11). GTDB data are licensed under CC BY-SA 4.0. GenomeSPOT's code is under the MIT licence. We use the labels with attribution to BacDive (CC BY 4.0) and GTDB (CC BY-SA 4.0), and cite GenomeSPOT (Barnum et al., bioRxiv 2024, doi 10.1101/2024.03.22.586313).

The paragraph above is the owner's prescribed licence basis from the Resume
decision. Resume 2, recorded below, also accepts the sequence-derived features.

The authorised asset is GenomeSPOT release `v1.0.0`:

- Download: <https://github.com/cultivarium/GenomeSPOT/releases/download/v1.0.0/training_data.tsv>.
- Required size: 64,412,996 bytes.
- Required SHA-256: `19a9f888f06655e17e95c7110ab4ff5ace38ece121e6cb1ac3bcb7d3c087abcc`.
- Local raw path: `data/raw/labels/training_data.tsv`, excluded from version control.

To download and reproduce the local inspection, use Python 3.12 or later:

```sh
mkdir -p data/raw/labels
curl --fail --location --retry 3 --output data/raw/labels/training_data.tsv https://github.com/cultivarium/GenomeSPOT/releases/download/v1.0.0/training_data.tsv
python3.12 scripts/audit_labels.py
```

This command rebuilds the historical label inspection only. The complete
phase-1 rebuild is `uv run --frozen python -m scripts.rebuild`.
The raw table is never redistributed in the repository. Aggregate inspection
counts contain no individual label records.

## Historical additional-source gate (resolved by Resume 2)

The table contains 230 precomputed feature columns. The release README's
training recipe downloads genomic and protein FASTA files from GenBank using
`ncbi-genome-download -s genbank`, then measures features from those files.
The release construction script loads those feature measurements and joins them
with BacDive targets and GTDB taxonomy. Examples include `all_nt_length`,
`all_total_protein_length` and `all_aa_A`.

Sources checked at release `v1.0.0`:

- [Training recipe](https://github.com/cultivarium/GenomeSPOT/blob/v1.0.0/README.md), lines 173 to 198.
- [Table construction](https://github.com/cultivarium/GenomeSPOT/blob/v1.0.0/genome_spot/model_training/make_training_dataset.py), feature measurement and `make_training_df`.

These feature columns originate in NCBI sequence data. The Resume instruction
says: "If any column comes from a source other than BacDive or GTDB, stop and
report." Work therefore stops at this gate. The columns have not been silently
removed or reused. The supplied README's two-resource summary does not cover
the third source shown in its executable training recipe.

`ncbi_taxid` and `ncbi_species` alone do not establish this gate: the trait
parser obtains them from BacDive records. The gate is the sequence-derived
feature block, whose construction is separately documented.

No GTDB-derived data table has been produced or redistributed. Future such
tables must stay in their own folder under CC BY-SA 4.0 with GTDB attribution.
The upstream MIT notice is preserved as raw source-audit evidence; no upstream
code has been incorporated into the inspection script.

## Resume 2: accepted sequence-derived features

Feature columns were computed by GenomeSPOT from public NCBI sequence data. NCBI states: 'NCBI places no restrictions on the use or distribution of the GenBank data. However, some submitters may claim patent, copyright, or other intellectual property rights in all or a portion of the data they have submitted' (https://www.ncbi.nlm.nih.gov/genbank/about/, read 2026-10-11). We publish only derived aggregate results, never the raw table or sequences.

This decision supersedes the additional-source stop above. B1 and the proposed
calibration method may use the precomputed features after the prescribed
fixed-sample verification as amended in Resume 3. The sample uses seed `20261011`, sampled without
replacement from the sorted 8,174 accessions with at least one nonmissing target
label. No accession is substituted if its files are unavailable.

The upstream feature implementation needs both protein and nucleotide FASTA.
The sequence-size estimate therefore includes both compressed files for all
100 sampled genomes before any sequence download. The limit is 8,000,000,000
bytes. Request starts are spaced by at least one second, with at most three
connections, without a key or account.
Sample, source and acquisition receipts remain untracked under
`data/raw/verification/`. The upstream release's own code and signal-peptide
parameters are used unchanged. Verification compares all 230 flattened feature
columns, filling absent compartment statistics with zero as the upstream table
construction does, at relative tolerance `1e-7` and absolute tolerance `1e-9`.
Resume 3 supersedes the former discrepancy stop: differences are recorded
as findings and do not block the build.

The table includes `all_aa_A` through `all_aa_Y` for the 20 standard amino acids.
These are protein-length-weighted whole-proteome frequencies in the upstream
implementation, after its signal-peptide handling. B3 needs no further proteome
download; feature differences do not block its use under Resume 3.


## Resume 3: fixed-sample check and current GTDB mapping

The fixed sample remains 100 accessions. Only the 71 with both GenBank FASTA
files are downloaded and recomputed, without replacements. The 29 unavailable
protein accessions, the pre-comparison tolerances and agreement by feature
group are recorded in `data/feature-verification.json`. A mismatch may reflect
a changed sequence annotation or dependency implementation; it is an integrity
finding, not proof of its cause. All methods use the same published table.

The completed comparison contains 3,266 values in each of five feature groups;
3,124 agree in each group (95.65%). The two disagreeing descriptors are
`mean_zc` and `mean_nh2o` in every group for all 71 genomes. The other 220
feature columns agree for every available sampled genome, including all amino-acid
frequency columns used by B1, B3 and the proposed predictor. No genome agrees
on all 230 columns. Maximum absolute differences by group are recorded in
the aggregate receipt; individual comparisons stay untracked. These findings
do not establish whether annotation, descriptor code or another provenance
difference caused the discrepancies. No table feature was substituted.

GTDB R11-RS232 (232.0) is the newest numbered release observed at the official
release index on 2026-10-11. Its official `sp_clusters_r232.tsv` is the metadata
mapping each clustered accession to its species representative and full
lineage. This satisfies the mapping requirement without downloading all-genome
metadata or any GTDB genomes. The bacterial and archaeal reference trees come
from the same release. Published MD5 checksums and independently calculated
SHA-256 values are checked and recorded. The supplied file-descriptions notice
still names release 220; the release path, VERSION, release notes and checksum
list establish the selected version 232.

Assembly identifiers drop the version suffix and GTDB prefix. RefSeq `GCF_`
identifiers are normalised to the corresponding `GCA_` numeric identifier,
following the release's own taxonomy helper. Original cluster and representative
identifiers are preserved in the local mapping table. Genomes absent from these
cluster records, or whose representative is absent from its reference tree,
are counted as exclusions. No fallback to old taxonomy or tree is made.

Individual tables containing labels or sequences are never published. Local
GTDB-derived mapping and folds are under `data/gtdb-derived/local/`, ignored
by version control; their aggregate summaries and notices are in the parent
folder with CC BY-SA 4.0 attribution. Features, local fitted estimators and
calibration artefacts are also ignored. Counts and checksum manifests are
published. BacDive and GenomeSPOT attribution above applies to the labels.

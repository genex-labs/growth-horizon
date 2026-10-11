# Data provenance and permitted use

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

This command rebuilds the label inspection only. The benchmark rebuild command
has not been implemented because the mandatory source-column gate was reached.
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
100-genome verification. The sample uses seed `20261011`, sampled without
replacement from the sorted 8,174 accessions with at least one nonmissing target
label. No accession is substituted if its files are unavailable.

The upstream feature implementation needs both protein and nucleotide FASTA.
The sequence-size estimate therefore includes both compressed files for all
100 sampled genomes before any sequence download. The limit is 8,000,000,000
bytes. Requests are serial, at most one per second, without a key or account.
Sample, source and acquisition receipts remain untracked under
`data/raw/verification/`. The upstream release's own code and signal-peptide
parameters are used unchanged. Verification compares all 230 flattened feature
columns, filling absent compartment statistics with zero as the upstream table
construction does, at relative tolerance `1e-7` and absolute tolerance `1e-9`.
Any discrepancy beyond these tolerances requires stopping and reporting.

The table includes `all_aa_A` through `all_aa_Y` for the 20 standard amino acids.
These are protein-length-weighted whole-proteome frequencies in the upstream
implementation, after its signal-peptide handling. B3 needs no further proteome
download if feature verification passes.

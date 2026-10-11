# Data provenance and permitted use

GenomeSPOT's README states that its training data were downloaded from the BacDive API and the Genome Taxonomy Database. BacDive states: 'This work is licensed under a Creative Commons Attribution 4.0 International License' (https://bacdive.dsmz.de/about, read 2026-10-11). GTDB data are licensed under CC BY-SA 4.0. GenomeSPOT's code is under the MIT licence. We use the labels with attribution to BacDive (CC BY 4.0) and GTDB (CC BY-SA 4.0), and cite GenomeSPOT (Barnum et al., bioRxiv 2024, doi 10.1101/2024.03.22.586313).

The paragraph above is the owner's prescribed licence basis from the Resume
decision. It resolves the earlier label-licence gate. It does not authorise other
sources in the supplied table.

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

## Additional source found in the table

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

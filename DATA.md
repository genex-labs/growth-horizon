# Data sources, attribution and permitted use

## BacDive labels

BacDive is maintained by the Leibniz Institute DSMZ, German Collection of Microorganisms and Cell Cultures. The labels exported through GenomeSPOT are attributed to BacDive under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). The [BacDive About page](https://bacdive.dsmz.de/about) was read on 2026-10-11. This benchmark maps records to current taxonomy and publishes aggregate analyses; it does not redistribute the original table.

BacDive requests this citation: Schober, I., Koblitz, J., Sardà Carbasse, J., Ebeling, C., Schmidt, M. L., Podstawka, A., Gupta, R., Ilangovan, V., Chamanara, J., Overmann, J. and Reimer, L. C. (2025). *BacDive in 2025: the core database for prokaryotic strain data*. Nucleic Acids Research, database issue 2025. [doi 10.1093/nar/gkae959](https://doi.org/10.1093/nar/gkae959), as requested on the About page.

CC BY 4.0 permits attributed reuse. BacDive asks commercial users to contact DSMZ. We follow the stated condition that BacDive-derived data go into no paid product or service without contacting DSMZ first. This benchmark is open research; no outward contact has been made.

The [CBD Secretariat Cali Fund guide for databases](https://www.cbd.int/califund/guides/guide%20for%20database.pdf), read 2026-10-11, says contributions are expected only from large entities meeting at least two of three criteria, averaged over the preceding three years: total assets of at least USD 20 million, annual sales or revenue of at least USD 50 million, and annual profit of at least USD 5 million. GeneX Labs Inc. is pre-revenue and far below every threshold; no contribution is expected now. Reassess if those circumstances change. This records the guidance rather than a legal determination.

GenomeSPOT's README states that its training data were downloaded from the BacDive API and the Genome Taxonomy Database. BacDive states: 'This work is licensed under a Creative Commons Attribution 4.0 International License' (https://bacdive.dsmz.de/about, read 2026-10-11). GTDB data are licensed under CC BY-SA 4.0. GenomeSPOT's code is under the MIT licence. We use the labels with attribution to BacDive (CC BY 4.0) and GTDB (CC BY-SA 4.0), and cite GenomeSPOT (Barnum et al., bioRxiv 2024, doi 10.1101/2024.03.22.586313).

## Table-level experimental records

GenomeSPOT's preparation notebook (last changed 2024-03-21, commit f994ef50450f3362a4d6f93ccd3260c80e8ca45c) names its output training_data_20231203.tsv, and its 15,596 rows and trait summaries match the release asset; the model-predicted BacDive values come from Koblitz et al. 2025 (doi 10.1038/s42003-025-08313-3) and are served only with the API parameter predictions=1, which GenomeSPOT's parser does not request. Decision: treat the table's labels as experimental records.

Residual risk: the release asset could in principle differ from the 2023 table in ways the matching checks did not cover.

This table-level chain was accepted on 2026-10-11 at 04:17 PT. The
historical filename suggests 2023-12-03; the independently verified facts are
the notebook's last change and displayed row/trait summaries, not a checksum
of the entire historical table or an authenticated BacDive snapshot. The
release asset was created 2026-03-16T12:25:19Z, updated 12:25:50Z, and its
release published 12:27:17Z. These are upload dates, not table-build dates.
The predictions=1 parameter is documented in the data-availability section of
[Koblitz et al. 2025](https://www.nature.com/articles/s42003-025-08313-3), read
2026-10-11. BacDive's [API homepage](https://api.bacdive.dsmz.de/) and
[release announcements](https://bacdive.dsmz.de/news) were read on 2026-10-11;
the February 2023 announcement states that predicted data were not yet
available through the API. The current API homepage does not state that
parameter, so the parameter source is the paper, not that homepage. The labels
count as experimental because of BacDive's content as GenomeSPOT exported it
in 2023. These pages do not authenticate the historical snapshot.
`data/provenance-page-check.json` retains the page URLs, reading date and
checksums. No per-value provenance is invented.

The per-trait audit accepts 4,783 temperature, 7,300 oxygen, 2,376 salinity
and 3,549 pH nonmissing labels as experimental under this documented decision.
No predicted record is identified or excluded under the accepted source
recipe. Individually confirmed experimental and predicted counts remain
unknown; accepted table-level counts are recorded separately. Mapping and
feature exclusions remain separately counted. Only the exact authorised
size/checksum and source chain bypass the snapshot-date requirement. The
experimental-label guard stays in force for every other label source.

`data/experimental-label-audit.json` freezes the chain, per-trait dispositions
and source-evidence hashes. The audit is bound to the exact release checksum.

## Pinned input and complete population

GenomeSPOT v1.0.0 [training_data.tsv](https://github.com/cultivarium/GenomeSPOT/releases/download/v1.0.0/training_data.tsv) has 64,412,996 bytes and SHA-256 `19a9f888f06655e17e95c7110ab4ff5ace38ece121e6cb1ac3bcb7d3c087abcc`. The 15,596 accession rows have no duplicates. Counts and exclusions are pinned in `data/gtdb-derived/population-summary.json`. No upstream use flag discards an otherwise usable label.

## Sequence-derived features

Feature columns were computed by GenomeSPOT from public NCBI sequence data. NCBI states: 'NCBI places no restrictions on the use or distribution of the GenBank data. However, some submitters may claim patent, copyright, or other intellectual property rights in all or a portion of the data they have submitted' (https://www.ncbi.nlm.nih.gov/genbank/about/, read 2026-10-11). We publish only derived aggregate results, never the raw table or sequences.

The fixed 100-genome sample uses seed 20261011. Only the 71 with both original GenBank protein and nucleotide files were recomputed, with no replacements for the 29 unavailable protein accessions. The 142 compressed sequence files total 135,825,146 bytes, below the 8 GB acquisition limit. Comparisons use relative tolerance 1e-7 and absolute tolerance 1e-9. In each of five feature groups, 3,124 of 3,266 values agree. mean_zc and mean_nh2o disagree in every group for every sampled genome; the other 220 feature columns agree. The cause is unverified, and no published value was replaced. All frozen predictor feature lists use amino-acid frequencies, excluding those ten descriptors. The explicit refit after removing them is a secondary result. See `data/feature-verification.json` and `data/verification-plan.json`.

## GTDB taxonomy and branch distances

GTDB R11-RS232 (232.0) supplies the bacterial and archaeal reference trees and species-cluster metadata from the same release. GTDB data and derived aggregate analyses are attributed to the Genome Taxonomy Database under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), in `data/gtdb-derived/` with its own notice. Release paths, VERSION, release notes and published MD5 establish release 232; FILE_DESCRIPTIONS still names release 220. Independently computed SHA-256 verifies each acquired file.

Assemblies lose version suffixes and GTDB prefixes; GCF identifiers map to corresponding GCA numeric identifiers, following the upstream taxonomy helper. Nonrepresentatives use their species representative leaf. Absent assemblies or absent representative leaves are counted separately, with no historical-tree fallback. The full GTDB genome collection was never downloaded.

## Reconstruction and redistribution

Our code is Apache-2.0. GenomeSPOT's code is MIT, with its notice in `docs/GenomeSPOT-MIT.txt`; cite Barnum et al. (2024), doi 10.1101/2024.03.22.586313. The frozen source manifest field `repository_licence` still reads MIT. That field is a phase 1 record and was not edited. MIT names the GenomeSPOT upstream notice only. Raw labels, sequences, features, individual predictions, folds and fitted estimators remain untracked. `data/raw/` and `data/gtdb-derived/local/` are not redistributed. The pinned replay inputs under `data/raw/labels/`, `data/raw/verification/upstream/`, `data/raw/verification/sequences/` and `data/raw/gtdb/` total 254,404,224 bytes, and acquisition stops if free space on `/` is below 25 GB. Only aggregate analyses, provenance and checksum manifests are redistributed. `data/source-manifest.json` pins every input URL, size and hash. `data/artifact-manifest.json` pins the original fitted analysis. `data/release-manifest.json` pins aggregate outputs and figures. The README supplies the complete rebuild command.

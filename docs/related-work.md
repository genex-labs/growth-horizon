# Related work

Identifiers and paper titles below were checked on their public publisher or
preprint pages on 2026-10-11. This is a bounded literature check, not proof
that related studies do not exist.

- Fujiyoshi et al., *Bac2Feature: an easy-to-use interface to predict prokaryotic
  traits from 16S rRNA gene sequences*, Bioinformatics Advances (2025),
  [doi 10.1093/bioadv/vbaf136](https://academic.oup.com/bioinformaticsadvances/advance-article/doi/10.1093/bioadv/vbaf136/8162692).
  The publisher page confirms the DOI, title and June 14, 2025 publication.
  Its abstract describes phylogenetic-distance thresholds. Distance-based
  abstention therefore has prior art. This benchmark studies genome-derived
  growth-condition predictions and checks interval coverage by distance.
- *Data coherence over data volume drives generalisable genome-based
  prediction of microbial carbon utilisation*, bioRxiv (2026),
  [doi 10.64898/2026.08.06.743333](https://www.biorxiv.org/content/10.64898/2026.08.06.743333v1).
  The preprint page's citation metadata confirms the title and DOI. Its
  confidence-based applicability domain and uncertainty-led sampling are
  prior art for the proposed phase-2 measure-next experiment. That experiment
  is not run in phase 1.
- Li, Selim and Kuehn, *Statistical prediction of microbial metabolic traits
  from genomes*, PLOS Computational Biology (2023),
  [doi 10.1371/journal.pcbi.1011705](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011705).
  The article confirms the DOI, title and December 19, 2023 publication.
  It compares random and out-of-clade partitions and explains distance-related
  failures of phylogeny-based trait predictions.
- *Calibrated prediction intervals for polygenic scores across diverse
  contexts*, Nature Genetics (2024),
  [doi 10.1038/s41588-024-01792-w](https://www.nature.com/articles/s41588-024-01792-w).
  The publisher page confirms the title and DOI. CalPred motivates calibration
  across contexts in another field; it is not evidence of microbial coverage.
- Barnum et al., GenomeSPOT (bioRxiv, 2024),
  [doi 10.1101/2024.03.22.586313](https://www.biorxiv.org/content/10.1101/2024.03.22.586313v1).
  Its published features and estimator choices define B1. The release table
  and source implementation are from v1.0.0, with the MIT notice preserved.
- Koblitz et al., *Predicting bacterial phenotypic traits through improved
  machine learning using high-quality, curated datasets*, Communications
  Biology (2025),
  [doi 10.1038/s42003-025-08313-3](https://www.nature.com/articles/s42003-025-08313-3).
  The paper's title, DOI and code-availability statement were read at source.
  B4 is omitted for the repository licence and input reasons in baselines.md.

Mondrian split conformal provides within-bin coverage only under appropriate
exchangeability of calibration and test units in that bin. Taxonomic
holdouts, a distance axis, or bin merging alone do not establish that
assumption. The 100-taxon gate and taxon bootstrap do not themselves establish
exchangeability of residuals among genomes. Correlated genomes, population
shift and coverage among non-abstained predictions remain empirical questions.

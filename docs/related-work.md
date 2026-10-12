# Related work

Identifiers and paper titles below were checked on 2026-10-11 using public
publisher or preprint pages, Europe PMC full text or OpenAlex metadata as
noted below. This is a bounded literature check, not proof
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
  prior art for the retrospective measure-next experiment in this package.
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

- Vovk, V. (2013), *Conditional validity of inductive conformal predictors*,
  Machine Learning 92, 349 to 376,
  [doi 10.1007/s10994-013-5355-6](https://link.springer.com/article/10.1007/s10994-013-5355-6).
  The publisher confirms the journal reference. The earlier 2012 conference
  version remains historical prior art for the fixed-bin rationale.
- Barber, R. F., Candès, E. J., Ramdas, A. and Tibshirani, R. J. (2021),
  *Predictive inference with the jackknife+*, The Annals of Statistics 49(1),
  486 to 507, [doi 10.1214/20-AOS1965](https://doi.org/10.1214/20-AOS1965).
  DOI-deposited metadata confirms the reference. CV+ accounts for fitting
  variation when constructing numeric endpoints.
- Romano, Y., Sesia, M. and Candès, E. J. (2020), *Classification with Valid
  and Adaptive Coverage*, [arXiv 2006.02544v1](https://arxiv.org/html/2006.02544v1).
  Algorithm 2 uses the randomized inverse-quantile score and the strict
  comparison count in equation (11). Its score differs from the originally
  proposed one-minus-probability score, while its count threshold agrees.
  The classification-rule receipt records this source check.

Appropriate exchangeability is an assumption, not a consequence of taxonomic
holdout or phylogenetic distance. Grouped unequal-size folds and calibration
conditioned on distance bins do not inherit a demonstrated finite-sample
coverage guarantee from the cited unconditioned CV+ results. The 50-taxon
support rule, 100-taxon strong-support flag and taxon bootstrap do not establish
exchangeability among genomes. Correlated genomes, population shift and
coverage among non-abstained predictions remain empirical questions.

Adjacent conformal work also includes [Boger et al. (2025)](https://www.nature.com/articles/s41467-024-55676-y), *Functional protein mining with conformal guarantees*; [Fannjiang et al. (2022)](https://www.pnas.org/doi/10.1073/pnas.2204569119), *Conformal prediction under feedback covariate shift for biomolecular design*; and [Barber et al. (2023)](https://doi.org/10.1214/23-AOS2276), *Conformal prediction beyond exchangeability*. They are adjacent work on protein retrieval, adaptive selection and distribution shift, not direct proofs for this benchmark. The technical note gives full references, including Vovk (2013), with source checks in data/paper-source-checks.json.

- Gao, Y. and Wu, M. (2023), *Accounting for 16S rRNA copy number prediction
  uncertainty and its implications in bacterial diversity analyses*, ISME
  Communications 3:59,
  [doi 10.1038/s43705-023-00266-0](https://doi.org/10.1038/s43705-023-00266-0).
  Checked through Europe PMC PMC10257666 and OpenAlex metadata. Closest prior
  work: evaluates confidence estimates across phylogenetic-distance cutoffs.
  How it differs: copy number rather than growth conditions, 16S placement
  rather than whole-genome features, random 2% test tips with distance-threshold
  filtering rather than family or order hold-out, and model-based pulsed-evolution
  intervals rather than conformal intervals; Figure 3D coverage concerns derived
  relative cell abundance in simulated communities, while copy-number predictions
  are scored by precision and recall per bin.
- Gao, Y. and Wu, M. (2022), *Modeling Pulsed Evolution and Time-Independent
  Variation Improves the Confidence Level of Ancestral and Hidden State
  Predictions*, Systematic Biology, online 2022-02-23,
  [doi 10.1093/sysbio/syac016](https://doi.org/10.1093/sysbio/syac016).
  Checked at abstract level only. How it differs: phylogenetic hidden-state
  prediction of genomic traits rather than growth conditions; whether coverage
  is broken down by distance to observed taxa remains unchecked, because the
  full text was not read.
- Ding, K., Luo, J. and Luo, Y. (2024), *Leveraging conformal prediction to
  annotate enzyme function space with limited false positives*, PLOS
  Computational Biology 20(5):e1012135,
  [doi 10.1371/journal.pcbi.1012135](https://doi.org/10.1371/journal.pcbi.1012135).
  Checked in the PLOS full text and OpenAlex metadata. How it differs: protein
  function rather than organism phenotype, false discovery control within
  sequence-identity groups rather than interval coverage, and sequence identity
  rather than phylogenetic distance between organisms.
- Xu, L., Zakem, E. J. and Weissman, J. L. (2025), *Improved maximum growth
  rate prediction from microbial genomes by integrating phylogenetic
  information*, Nature Communications 16:4256,
  [doi 10.1038/s41467-025-59558-9](https://doi.org/10.1038/s41467-025-59558-9).
  Checked through Europe PMC PMC12059116 and OpenAlex metadata. Uses
  phylogenetically blocked cross-validation over tree-cutting scenarios and
  reports mean squared error by distance. How it differs: point error only;
  the checked main text contains no prediction intervals or coverage.

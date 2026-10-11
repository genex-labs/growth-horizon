# Pre-registration: Growth Horizon phase 1

This record is frozen by its local commit before any outer-fold prediction or
metric is computed. No outer scoring is authorised in this phase, including
after this commit. The separate reviewed phase-2 brief is required. This
record specifies targets rather than reporting scientific outcomes.

## Inputs and complete population

GenomeSPOT v1.0.0 training_data.tsv: 64,412,996 bytes, SHA-256
`19a9f888f06655e17e95c7110ab4ff5ace38ece121e6cb1ac3bcb7d3c087abcc`.
GTDB R11-RS232 (232.0): the official species-cluster metadata and bacterial
and archaeal reference trees from the same release. Every acquired input URL,
size and SHA-256 is in the frozen source manifest. Source attribution and
licence separation are in DATA.md. Python 3.13.15 and uv.lock pin the runtime.

### Experimental-label provenance accepted under Resume 5

GenomeSPOT's preparation notebook (last changed 2024-03-21, commit f994ef50450f3362a4d6f93ccd3260c80e8ca45c) names its output training_data_20231203.tsv, and its 15,596 rows and trait summaries match the release asset; the model-predicted BacDive values come from Koblitz et al. 2025 (doi 10.1038/s42003-025-08313-3) and are served only with the API parameter predictions=1, which GenomeSPOT's parser does not request. Decision: treat the table's labels as experimental records.

Residual risk: the release asset could in principle differ from the 2023 table in ways the matching checks did not cover.

The notebook's historical filename suggests 2023-12-03; it is not an
independently authenticated snapshot or build date for the 2026-03-16 asset.
The per-trait audit accepts temperature 4,783, oxygen 7,300, salinity 2,376
and pH 3,549 nonmissing labels at table level. No predicted record is identified
or excluded under that accepted recipe. This is a documented source decision,
not a per-value provenance claim. Any other label source retains the verified
experimental-label guard. The audit and source-evidence hashes are frozen.

Every nonmissing labelled assembly with a valid current representative and
finite published features is included for its trait. Upstream use flags are
not adopted as exclusions. Missing labels and every mapping/feature exclusion
are counted separately. Raw labels and sequences remain untracked. The fixed
100-genome verification seed is 20261011; the available 71 are recomputed with
upstream code at rtol 1e-7 and atol 1e-9, with no resampling. Differences are
recorded findings under Resume 3 and do not change the common feature table.

| Trait | Usable labelled genomes | Counts by disposition |
| --- | ---: | --- |
| temperature_optimum | 4715 | {"absent_from_release232_metadata": 68, "missing_label": 10813, "usable": 4715} |
| oxygen | 7230 | {"absent_from_release232_metadata": 70, "missing_label": 8296, "usable": 7230} |
| salinity_optimum | 2347 | {"absent_from_release232_metadata": 29, "missing_label": 13220, "usable": 2347} |
| ph_optimum | 3513 | {"absent_from_release232_metadata": 36, "missing_label": 12047, "usable": 3513} |

## Frozen artefacts

| File | SHA-256 |
| --- | --- |
| `data/source-manifest.json` | `edd6173d5a68010df4c3ea38d542c9b81d792d49644cea5057119f1a198e42e6` |
| `data/gtdb-derived/population-summary.json` | `6a4ca31f2e14a2e6700d2f2fe7efb0ec7f0a53385fefa0c88bc334333ba6b1f5` |
| `data/gtdb-derived/development-summary.json` | `56e9ac24419ce4d30f4be7b123ce96d58ae7b4d40ee598c5024b0db856958cb7` |
| `data/artifact-manifest.json` | `708baa5c427d2cf922ff441896f8e7b95444b051cac1119df44a47d917051d63` |
| `data/feature-verification.json` | `b60a732e52f74ece40e9c4bed3f402683128ddb13064074b60ec3590f29240a4` |
| `data/verification-plan.json` | `ffbd10de4c921932c40645aeebffb98c7d85f42a14810030d597c854bb49b69b` |
| `data/experimental-label-audit.json` | `06fb84b948434dd171133f0d795464779c307eee2e515ed9690fc30d11bf64e9` |
| `data/gtdb-derived/optimisation-summary.json` | `0a957da4cc2daece5e37f8668083aad9e8464222e388d424331368453e1e6588` |
| `uv.lock` | `c2a60aff5f1c62b452322ad8312c7f50f5177f3f9d33037ff705332517e2ceba` |

The artefact manifest freezes the individual local populations, mappings,
fold memberships, distances, fitted training-side estimators and calibration
records. Their raw and individual records are not redistributed. Aggregate
GTDB-derived summaries reside separately under CC BY-SA 4.0.

## Folds, distance axis and bins

Five outer grouped folds per eligible rank: genus, family, order, class and
phylum; a five-fold random partition is the optimistic reference. A taxon is
never divided. Groups are shuffled using a seeded generator and allocated
largest-first to the least loaded fold, subject to a cap of ceil(n_taxa / 5)
taxa per fold, breaking ties by fold number. The taxon cap repairs a structural
problem observed before freezing: genome balancing alone left only four
training phyla in one outer split. No prediction performance chose this rule. The
outer seed is 20261011 + 1000 * rank index, with rank order genus, family,
order, class, phylum, random. Fold f uses base seed outer seed + 10 * f; inner
calibration uses base + 1, naive random calibration base + 2, and proper-side
tuning base + 3. The sample uses Python random.Random.sample; folds use the
NumPy default generator. Fewer than seven taxa excludes a rank from the
nested design; a proper training side with fewer than five taxa or missing
oxygen classes is explicitly unsupported.

Within each outer training side, inner fold 0 at the same rank supplies
calibration taxa; inner folds 1 to 4 form proper training. Five further grouped
tuning folds live entirely inside proper training. Calibration labels never
select a model or tune regularisation. A separately random 20% calibration
holdout of the outer training side provides the naive spread for each method.
The remaining random 80% fits its separate naive estimator.

Distances are sums of GTDB branch lengths to the closest training-side
representative. Nonrepresentative assemblies use their representative leaf;
identical representatives have zero distance. Domains remain separate, with
infinite distance and abstention when no source exists in the domain. B2 ties
choose the smallest training representative and then assembly accession.
Both distances to all outer training rows and distances to actual proper
fitting rows are frozen. The calibrated prediction axis uses the latter,
matching its inner calibration fitting population. No query's own label enters
its nearest-source set.

For each trait/rank/outer fold, five initial quantile bins are fixed using
proper-training-side distances only: pool the distances of the five proper-side
tuning holdouts to their respective fitting sides, using base seed + 3.
Calibration covariates and residuals do not determine cut points.
Cut points are the 20th, 40th, 60th
and 80th percentiles of finite distances. Equal cut points collapse and equal
distances are never split arbitrarily. Right-side search assigns boundaries.
Outer test distances and labels never set cut points. Initial cut points,
all original-to-merged bin maps, and calibration-taxon counts are frozen in
data/gtdb-derived/development-summary.json and individual calibration records.

Require 100 distinct calibration taxa per merged bin. Merge a deficient bin
with an adjacent bin having the smaller distinct-taxon count, left on ties,
until supported or only one bin remains. Count unions of taxa, not sums.
If the remaining bin still has fewer than 100 taxa, its quantile is infinite
and all predictions in it abstain; no unsupported coverage claim is made.

| Trait | Rank | Total taxa | Taxa in each outer fold | Supported merged bins |
| --- | --- | ---: | --- | ---: |
| temperature_optimum | genus | 1766 | [350, 354, 354, 354, 354] | 10 |
| temperature_optimum | family | 469 | [94, 93, 94, 94, 94] | 0 |
| temperature_optimum | order | 194 | [38, 39, 39, 39, 39] | 0 |
| temperature_optimum | class | 75 | [15, 15, 15, 15, 15] | 0 |
| temperature_optimum | phylum | 34 | [6, 7, 7, 7, 7] | 0 |
| temperature_optimum | random | 4715 | [943, 943, 943, 943, 943] | 25 |
| oxygen | genus | 2407 | [480, 481, 482, 482, 482] | 13 |
| oxygen | family | 583 | [117, 116, 116, 117, 117] | 0 |
| oxygen | order | 242 | [48, 48, 48, 49, 49] | 0 |
| oxygen | class | 100 | [20, 20, 20, 20, 20] | 0 |
| oxygen | phylum | 38 | [6, 8, 8, 8, 8] | 0 |
| oxygen | random | 7230 | [1446, 1446, 1446, 1446, 1446] | 25 |
| salinity_optimum | genus | 1153 | [229, 231, 231, 231, 231] | 5 |
| salinity_optimum | family | 325 | [65, 65, 65, 65, 65] | 0 |
| salinity_optimum | order | 137 | [26, 28, 28, 28, 27] | 0 |
| salinity_optimum | class | 54 | [10, 11, 11, 11, 11] | 0 |
| salinity_optimum | phylum | 29 | [5, 6, 6, 6, 6] | 0 |
| salinity_optimum | random | 2347 | [470, 470, 469, 469, 469] | 10 |
| ph_optimum | genus | 1591 | [316, 318, 319, 319, 319] | 10 |
| ph_optimum | family | 445 | [89, 89, 89, 89, 89] | 0 |
| ph_optimum | order | 184 | [37, 37, 37, 37, 36] | 0 |
| ph_optimum | class | 71 | [11, 15, 15, 15, 15] | 0 |
| ph_optimum | phylum | 32 | [4, 7, 7, 7, 7] | 0 |
| ph_optimum | random | 3513 | [703, 703, 703, 702, 702] | 21 |

Under the prescribed 100-taxon support rule and the nested five-fold inner
holdout, family and order calibration have fewer than 100 taxa for every
trait. They are explicitly unsupported, even after merging. The calibration
breakthrough target at those ranks cannot be assessed with finite supported
intervals under this frozen design. This is a pre-scoring limitation for review,
not a result of outer performance. A future amended design would require a
new reviewed pre-registration before any scoring.

## Estimators and calibration

B1 uses GenomeSPOT's published estimator and feature specification, retrained
within each fitting side with a 100,000-iteration numerical budget; B2 is the nearest labelled tree relative; B3 is
ridge or balanced logistic regression on whole-proteome amino-acid frequencies.
B4 is not run for the licence and annotation/input conditions recorded in
docs/baselines.md. The proposed predictor selects B1 or a ridge/logistic
alternative on the published compartment features by proper-side tuning.
Regularisation candidates are 0.1, 1, 10 and 100; logistic C is reciprocal.
The numerical iteration cap was raised from 10,000 after inner-only convergence
warnings; the published penalties, solver and tolerance were not changed.
Ties favour B1, and tied regularisation scores favour the smaller value.
All available methods share the same primary population and outer folds.

Nominal coverage is 90%, alpha 0.10. Numeric nonconformity is absolute residual;
oxygen nonconformity is one minus the fitted probability of the observed class.
Within each merged distance bin, take the ceil((n_genomes + 1) * 0.9)-th
ordered calibration residual, exactly as the residual-based split-conformal
method. If that index exceeds n_genomes, use infinity. The 100-distinct-taxon
gate and taxon bootstrap do not establish genome-level exchangeability.
The naive comparator instead uses the genome-level scores of its random inner
calibration sample with the same finite-sample quantile rule and no distance
conditioning. No calibration labels are used to refit a calibrated estimator.

Numeric intervals are prediction plus or minus the bin quantile. Abstain when
full width exceeds 20 °C for temperature, 3 pH units or 8% NaCl for salinity.
Absolute-error scores give the same width throughout each fold/bin cell.
Width-based abstention therefore drops whole cells; report their identities,
support flags and counts, while retaining coverage over all items in every bin.
These design limits are retained, without evidence-based tightening. Oxygen
uses the binary classes 0 = not oxygen tolerant and 1 = oxygen tolerant from
the release table. Include class c when 1 - p(c) is at most the bin quantile.
Both classes, an empty set, a nonfinite distance or unsupported bin lead to
abstention. Empty sets are also counted as coverage failures in unconditional
coverage. Set cardinality replaces numeric width for oxygen.

Coverage is conditional on appropriate exchangeability of calibration and
test genome residuals within each fixed bin. That assumption is not established
by phylogenetic distance, and no conditional coverage guarantee among accepted
predictions is asserted. Correlations within taxa, across bins and unequal taxon sizes are
limitations. All nominal targets are evaluated empirically in phase 2.

## Metrics, bootstrap and horizon

Primary, per trait, per rank and per distance bin: mean absolute error
(balanced accuracy for oxygen), interval coverage and mean width, abstention
rate. Coverage is measured over all items in each bin, including abstentions.
Report numeric coverage and width among accepted items separately, whole-cell
width abstentions, counts and support flags, and coverage over all items per
phylum. Oxygen set coverage and mean cardinality include all items. Report
accuracy and balanced accuracy among accepted oxygen items separately, with
accepted class counts; nominal coverage among accepted oxygen items is never
asserted. Error for oxygen comparisons is one minus
balanced accuracy. Numeric errors retain their original units.

Use 2,000 paired bootstrap replicates with seed 20261011 and percentile 95%
intervals. Resample held-out taxa with replacement, retaining every genome
and its paired predictions whenever its taxon is drawn. Compute genome-weighted
MAE or balanced accuracy on the resampled clusters. Never bootstrap genomes
independently. For the random reference, use species as the statistical cluster.
Single-taxon groups are marked insufficient for uncertainty estimation.
No multiplicity-adjusted significance claim is planned; the four targets are
joint descriptive predeclared pass criteria, not independent discoveries.

The horizon of a trait is the smallest distance bin where the model no longer
beats B2 with a bootstrap interval that excludes zero, reported with its own
interval. Positive improvement means B2 error minus proposed error. Pool
outer-fold predictions within each rank while retaining each fold's frozen
bin ordinal; distance ranges across folds are reported, never presented as
identical cut points. A bin with an improvement interval whose lower endpoint
is at most zero defines the horizon. Empty or unsupported bins give an
unidentified horizon rather than fabricated evidence. If every supported bin
beats B2, the horizon is right-censored beyond the observed range; it is not
infinite. For the horizon interval, repeat the entire paired comparison and
first-failing-bin rule in each taxon bootstrap replicate, using the replicate
improvement and preserving missing and right-censored states. Report the
2.5th and 97.5th ordinal percentiles and their corresponding frozen distance
ranges, plus unidentified and right-censored replicate fractions. Taxa drawn
across bins remain paired. Horizon distributions are exploratory uncertainty
summaries and do not certify a continuous universal threshold.

## Breakthrough targets (pre-registered, not predictions)

1. Calibration: at family and order holdout, nominal 90% intervals cover within 3 points of 90% in every distance bin for all four traits, where the naive intervals of B1 and B2 under-cover by 10 points or more in the far bins.
2. Accuracy: at order holdout, error at least 10% lower than B1 on at least two traits, with the paired bootstrap interval (by held-out taxon) excluding zero.
3. A published horizon per trait from the full labelled population.
4. If B1 wins on accuracy, the release says so; the calibration result stands on its own.

## Phase boundary and rebuilding

`uv run --frozen python -m scripts.rebuild` replays the frozen manifest and
rebuilds all phase-1 artefacts. Synthetic offline tests cover nested membership,
branch distances, pruning, bins, cluster counts, conformal order statistics,
abstention, the paired bootstrap and the development prediction boundary.
No outer-fold prediction or metric has been computed. Phase 2's scoring,
figures, measure-next experiment, technical note and release package are
separate. Publication requires the Director's release check and the authorised
release action.

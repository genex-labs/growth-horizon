# SPDX-License-Identifier: Apache-2.0
"""Freeze the completed phase-1 inputs without querying any outer phenotype."""
import json

from scripts.acquire import ROOT, digest
from growth_horizon.label_gate import PROVENANCE_TEXT, require_experimental_labels

AMENDMENTS = {
    'C1': (
        'C1 Calibration (replaces the use of inner fold 0 alone for calibration; the naive '
        'comparator and all point predictions stay as in v1). Within each outer training side, '
        'each of the five inner folds at the same rank serves once as calibration. For inner '
        'fold k, the method is fitted on the other four inner folds, with tuning on grouped '
        'folds inside those four only, and each genome i in fold k receives one out-of-fold '
        "score R_i from that fit mu_-k(i) and its distance to that fit's training rows. Initial "
        'cut points per outer fold are the 20th, 40th, 60th and 80th percentiles of the '
        'phenotype-free tuning-holdout distances pooled from inside the five inner fitting '
        'sides; merging follows v1 with a support rule of 50 distinct calibration taxa per '
        'merged bin, and bins with 100 or more are flagged "strong support". A test genome\'s '
        'bin is set by its distance to the outer training side. Numeric intervals use CV+ '
        '(Barber, Candès, Ramdas and Tibshirani, Annals of Statistics 2021, doi '
        '10.1214/20-AOS1965) over the n calibration genomes in that bin: the lower end is the '
        'floor(0.1 (n + 1))-th smallest value of mu_-k(i)(x) - R_i, and the upper end is the '
        'ceil(0.9 (n + 1))-th smallest value of mu_-k(i)(x) + R_i; an index outside 1 to n '
        'gives an infinite end. For oxygen, use the randomized inverse-quantile score E of '
        'Romano, Sesia and Candès (arXiv 2006.02544, 2020, equations (5) and (7)), rather than '
        'one minus the fitted probability: R_i = E(X_i, Y_i, U_i; mu_-k(i)) and s_-k(i)(x, c) = '
        'E(x, c, U_x; mu_-k(i)). Class c is included exactly when the sum over the n '
        'calibration genomes in the bin of 1[R_i < s_-k(i)(x, c)] is less than 0.9 (n + 1), as '
        'in Algorithm 2, equation (11). Equivalently, it is included unless at least ceil(0.9 '
        '(n + 1)) such strict comparisons hold. The U values are independent Uniform(0, 1), and '
        'class-probability ties are broken at random. The guarantee is weaker than split '
        "conformal's in the worst case, so the claim rests on measured outer-fold coverage. "
        'Point predictions for every error metric, target 2 and the horizon are the v1 fits.'
    ),
    'C2': (
        'C2 Target 1 (replaces the v1 wording). Calibration: at family and order holdout, for '
        'all four traits, (a) no supported distance bin has a 95% taxon-bootstrap interval for '
        'coverage lying wholly below 87%, and (b) pooled over the supported bins of each trait '
        'and rank, the 95% taxon-bootstrap interval for coverage reaches 90%; and in the far '
        'bin (the farthest supported bin of each outer fold, pooled over folds) the naive '
        'intervals of B1 and B2 cover 80% or less, each with a 95% taxon-bootstrap upper limit '
        'below 90%. Coverage above nominal is reported with width and is not a failure. '
        'Unsupported bins are excluded from every coverage figure and reported as abstentions.'
    ),
    'C3': (
        'C3 Horizon (replaces the v1 horizon definition; the bootstrap of the horizon, '
        'censoring and unidentified states follow v1). Horizon bins: per trait and rank, common '
        'cut points at the 20th, 40th, 60th and 80th percentiles of the phenotype-free '
        'proper-side tuning distances pooled over all five outer folds, frozen before scoring '
        "and used by every fold. B0 is the outer training side's mean for numeric traits and "
        'its majority class for oxygen. The horizon of a method is the first horizon bin, from '
        'near to far, where (i) its improvement over B0 (B0 error minus method error; for '
        'oxygen, balanced accuracy minus 0.5) has a paired taxon-bootstrap 95% interval whose '
        "lower end is at or below zero, or (ii) more than half of the bin's items abstain under "
        'the calibrated method. Horizons are reported for the proposed predictor and for B1. '
        'The improvement over B2 (B2 error minus method error) is reported in every horizon bin '
        'with its interval, with no first-failure rule.'
    ),
    'C4': (
        'C4 Secondary figures. Coverage is also reported with each held-out taxon weighted '
        'once. An exploratory refit of B1 and the proposed predictor without the ten mean_zc '
        'and mean_nh2o columns is reported beside the primary results; no target uses it.'
    ),
}

TARGETS = (
    '1. Calibration: at family and order holdout, for all four traits, (a) no supported '
    'distance bin has a 95% taxon-bootstrap interval for coverage lying wholly below 87%, '
    'and (b) pooled over the supported bins of each trait and rank, the 95% taxon-bootstrap '
    'interval for coverage reaches 90%; and in the far bin (the farthest supported bin of '
    'each outer fold, pooled over folds) the naive intervals of B1 and B2 cover 80% or '
    'less, each with a 95% taxon-bootstrap upper limit below 90%. Coverage above nominal is '
    'reported with width and is not a failure. Unsupported bins are excluded from every '
    'coverage figure and reported as abstentions.\n'
    '2. Accuracy: at order holdout, error at least 10% lower than B1 on at least two '
    'traits, with the paired bootstrap interval (by held-out taxon) excluding zero.\n'
    '3. A published horizon per trait from the full labelled population.\n'
    '4. If B1 wins on accuracy, the release says so; the calibration result stands on its '
    'own.'
)

def main() -> None:
    require_experimental_labels(ROOT)
    population = json.loads((ROOT / 'data/gtdb-derived/population-summary.json').read_text())
    development = json.loads((ROOT / 'data/gtdb-derived/development-summary.json').read_text())
    crossfit = json.loads((ROOT / 'data/gtdb-derived/crossfit-summary.json').read_text())
    assert crossfit['no_outer_fold_scoring']
    verification = json.loads((ROOT / 'data/feature-verification.json').read_text())
    if verification['status'] != 'complete' or verification['recomputed'] != 71:
        raise ValueError('The verification comparison has not finished')
    assert development['no_outer_fold_scoring']
    files = ['data/source-manifest.json', 'data/gtdb-derived/population-summary.json',
             'data/gtdb-derived/development-summary.json', 'data/artifact-manifest.json',
             'data/feature-verification.json', 'data/verification-plan.json',
             'data/experimental-label-audit.json',
             'data/gtdb-derived/optimisation-summary.json',
             'data/gtdb-derived/crossfit-summary.json', 'data/gtdb-derived/horizon-cutpoints.json',
             'data/classification-rule-check.json', 'data/provenance-page-check.json',
             'data/gtdb-derived/crossfit-optimisation-summary.json', 'uv.lock']
    hashes = '\n'.join(f'| `{f}` | `{digest(ROOT / f)}` |' for f in files)
    counts = '\n'.join(f"| {t} | {r['usable']} | {json.dumps(r['counts_by_reason'], sort_keys=True)} |"
                       for t, r in population['traits'].items())
    ranks = []
    for trait, records in development['traits'].items():
        for rank, record in records.items():
            if 'folds' in record:
                supported = sum(sum(b['supported'] for b in f['methods']['method']['bins'])
                                for f in crossfit['traits'][trait][rank]['folds'])
                ranks.append(f"| {trait} | {rank} | {record['taxa']} | {record['fold_taxa']} | {supported} |")
            else:
                ranks.append(f"| {trait} | {rank} | {record['taxa']} | excluded: {record['status']} | 0 |")
    text = f'''# Pre-registration v2: Growth Horizon phase 1

This record is frozen by its local commit before any outer-fold prediction or
metric is computed. No outer scoring is authorised in this phase, including
after this commit. Phase 2 requires a reviewed pre-registration and a separate
authorised locked run. This record specifies pre-registered targets rather
than reporting scientific outcomes.

The earlier v1 freeze is commit `22bc860563c0397e8ab935f6517892370f21afcd`
(`22bc8605`), 2026-10-11 04:30:02 PT, SHA-256
`d7ae79e500b27fdea91693aa5bd7038e701ff84909b9b896eef000cb322b5c3d`.
Amendment C and v2 were made before any outer-fold prediction or metric existed.
Sections not replaced by C1 to C4 retain their v1 substance.

## Inputs and complete population

GenomeSPOT v1.0.0 training_data.tsv: 64,412,996 bytes, SHA-256
`19a9f888f06655e17e95c7110ab4ff5ace38ece121e6cb1ac3bcb7d3c087abcc`.
GTDB R11-RS232 (232.0): the official species-cluster metadata and bacterial
and archaeal reference trees from the same release. Every acquired input URL,
size and SHA-256 is in the frozen source manifest. Source attribution and
licence separation are in DATA.md. Python 3.13.15 and uv.lock pin the runtime.

### Experimental-label provenance accepted at table level

{PROVENANCE_TEXT}

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
recorded findings and do not change the common feature table.

| Trait | Usable labelled genomes | Counts by disposition |
| --- | ---: | --- |
{counts}

## Frozen artefacts

| File | SHA-256 |
| --- | --- |
{hashes}

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

{AMENDMENTS['C1']}

A separately random 20% calibration
holdout of the outer training side provides the naive spread for each method.
The remaining random 80% fits its separate naive estimator.

Distances are sums of GTDB branch lengths to the closest training-side
representative. Nonrepresentative assemblies use their representative leaf;
identical representatives have zero distance. Domains remain separate, with
infinite distance and abstention when no source exists in the domain. B2 ties
choose the smallest training representative and then assembly accession.
Both distances to all outer training rows and distances to actual proper
fitting rows are frozen. The calibrated test bin uses distance to all outer
training rows, as specified in C1. No query's own label enters
its nearest-source set.

Equal cut points collapse and equal distances are never split arbitrarily.
Right-side search assigns boundaries. Outer test distances and labels never
set cut points. Merge a deficient bin with an adjacent bin having the smaller
distinct-taxon count, left on ties, until supported or only one bin remains.
Count unions of taxa, not sums. Nonfinite calibration distances are excluded
from bin support. Initial cuts, all original-to-merged bin maps and support
counts are frozen in data/gtdb-derived/crossfit-summary.json and individual
calibration records. The v1 development summary remains the record of the
unchanged point-prediction fits and naive comparator.

For cross-fit k, tuning uses base seed + 3 + 100 * k; k = 0 reproduces the
v1 fitting side and tuning seed. Oxygen calibration randomisation uses base
seed + 4, drawing all Uniform(0, 1) values and then fair binary tie orderings
for sorted outer-training rows. Values are shared across methods. During the
authorised phase-2 run, query randomisation uses base seed + 5 for sorted
outer-test rows and is shared across the five fits and methods. These query
values have not been used to make any prediction. The binary E score is the
cumulative probability through a class in descending probability order minus
U times that class probability; a zero-probability class has endpoint score 1.
Calibration scores remain genome-weighted. No genome's calibration label
selects or tunes the fit that produces its score.

| Trait | Rank | Total taxa | Taxa in each outer fold | Supported merged bins |
| --- | --- | ---: | --- | ---: |
{chr(10).join(ranks)}

The supported-bin counts above are calibration-side counts, not outer
coverage or accuracy. Unsupported bins remain abstentions under C2.

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

Nominal coverage is 90%, alpha 0.10. Numeric nonconformity is absolute residual.
Calibrated numeric endpoints and oxygen scores and sets follow C1. The
50-distinct-taxon gate and taxon bootstrap do not establish genome-level
exchangeability. The naive comparator remains unchanged: absolute residual
for numeric traits and one minus the fitted probability of the observed
class for oxygen, with the genome-level random-inner scores and the
ceil((n_genomes + 1) * 0.9)-th order statistic; an index above n gives infinity.
It has no distance conditioning. No calibration labels refit their own fit.

Abstain when full width exceeds 20 °C for temperature, 3 pH units or 8% NaCl
for salinity. CV+ widths vary by genome, so width abstention is per genome.
Report support flags and counts; coverage includes abstentions in supported
bins only. These design limits remain unchanged. Oxygen uses the binary
classes 0 = not oxygen tolerant and 1 = oxygen tolerant from the release table.
Both classes, an empty set, a nonfinite distance or unsupported bin lead to
abstention. Empty sets are coverage failures. Set cardinality replaces width.

The calibration rationale assumes appropriate exchangeability of calibration
and test genomes within each fixed bin. The grouped, unequal-size folds and
distance-conditioned CV+ extension do not inherit a demonstrated finite-sample
guarantee from the cited unconditioned exchangeable-sample results. That assumption is not established
by phylogenetic distance, and no conditional coverage guarantee among accepted
predictions is asserted. Correlations within taxa, across bins and unequal taxon sizes are
limitations. All nominal targets are evaluated empirically in phase 2.

## Metrics, bootstrap and horizon

Primary, per trait, per rank and per distance bin: mean absolute error
(balanced accuracy for oxygen), interval coverage and mean width, abstention
rate. Coverage is measured over all items in each supported bin, including
abstentions; unsupported bins are excluded from every coverage figure.
Report numeric coverage and width among accepted items separately, per-genome
width abstentions, counts and support flags, and coverage over supported items
per phylum. Oxygen set coverage and mean cardinality include supported items. Report
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

{AMENDMENTS['C3']}

Empty or unsupported horizon bins give an unidentified horizon rather than
fabricated evidence. If every supported horizon bin has positive improvement
over B0 with its interval excluding zero and at most half its items abstain,
the horizon is right-censored beyond the observed range; it is not infinite. For the horizon interval, repeat the entire paired comparison and
first-failing-bin rule in each taxon bootstrap replicate, using the replicate
improvement over B0 and the majority-abstention condition, preserving missing
and right-censored states. Report the
2.5th and 97.5th ordinal percentiles and their corresponding frozen distance
ranges on the common cut points, plus unidentified and right-censored
replicate fractions. Taxa drawn
across bins remain paired. Horizon distributions are exploratory uncertainty
summaries and do not certify a continuous universal threshold.

## Pre-registered targets

{AMENDMENTS['C2']}

{chr(10).join(TARGETS.splitlines()[1:])}

{AMENDMENTS['C4']}

## Phase boundary and rebuilding

`uv run --frozen python -m scripts.rebuild` replays the frozen manifest and
rebuilds all phase-1 artefacts. Synthetic offline tests cover nested membership,
branch distances, pruning, bins, cluster counts, conformal order statistics,
abstention, the paired bootstrap and the development prediction boundary.
No outer-fold prediction or metric has been computed. Phase 2's scoring,
figures, measure-next experiment, technical note and release package are
separate. Publication requires scientific review and an authorised release
action.

## References

- Barber, R. F., Candès, E. J., Ramdas, A. and Tibshirani, R. J. (2021).
  *Predictive inference with the jackknife+*. The Annals of Statistics 49(1),
  486 to 507. [doi 10.1214/20-AOS1965](https://doi.org/10.1214/20-AOS1965).
- Romano, Y., Sesia, M. and Candès, E. J. (2020).
  *Classification with Valid and Adaptive Coverage*.
  [arXiv 2006.02544v1](https://arxiv.org/html/2006.02544v1),
  Algorithm 2, equations (5), (7) and (11).
- Vovk, V. (2013). *Conditional validity of inductive conformal predictors*.
  Machine Learning 92, 349 to 376.
  [doi 10.1007/s10994-013-5355-6](https://link.springer.com/article/10.1007/s10994-013-5355-6).

## Appendix: wording changes outside C1 to C4

- The title identifies v2. The opening records the earlier v1 freeze, its full
  commit, PT time and SHA-256, and the timing of amendment C before any outer
  prediction or metric. The phase-2 requirement is expressed as a reviewed
  record and a separate authorised locked run.
- The label-provenance heading names table-level acceptance. The feature-check
  paragraph describes recorded findings without an internal numbered-stage
  reference. Their provenance, populations and common-feature rule are unchanged.
- The frozen-file table includes the new calibration summary, common horizon
  cut points, classification-rule receipt and provenance-page receipt, and
  updates the artefact-manifest
  checksum, including newly read reference-source receipts. The original
  point-fit and naive scientific records retain their checksums.
- The cross-fit seed schedule, shared randomisation and binary inverse-score
  endpoint specify the resolved classification rule reproducibly. The v1
  point-fit and naive random-split seed schedules remain unchanged.
- The old support-limitation paragraph is replaced by a statement that the
  updated table reports calibration-side counts. It makes no outcome claim.
- The exchangeability paragraph explicitly limits the scope of the cited
  results for grouped unequal-size folds and distance-conditioned CV+. The
  empirical evaluation and absence of an accepted-coverage guarantee are unchanged.
- The target heading uses plain public terms. Targets 2 to 4 are unchanged.
  The final publication condition is stated as scientific review and an
  authorised release action.
- Full bibliographic references and public source links are supplied above,
  including the 2013 journal reference for Vovk. This appendix is new.
'''
    target = ROOT / 'PREREGISTRATION.md'
    if (target.exists() and target.read_text() != text
            and digest(target) != 'd7ae79e500b27fdea91693aa5bd7038e701ff84909b9b896eef000cb322b5c3d'):
        raise ValueError('Rebuilt inputs differ from the frozen pre-registration')
    target.write_text(text)


if __name__ == '__main__':
    main()

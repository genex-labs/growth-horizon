# Growth Horizon

GeneX Labs Inc. measures how growth-condition predictions behave as microbial genomes become more distant from labelled relatives. The benchmark combines taxonomic holdout, empirical interval coverage and abstention, so a laboratory can see both predictive error and how often uncertainty prevents a useful answer.

The locked calibration and accuracy targets failed. B1 has lower order-holdout error for temperature and salinity. The proposed predictor does not achieve the required accuracy improvement on any trait. These are descriptive results from the full usable labelled population; no estimator or target was changed after outer scoring.

- Target 1: failed. [data/gtdb-derived/results/public-results.tsv:L602](data/gtdb-derived/results/public-results.tsv)
- Target 2: failed. [data/gtdb-derived/results/public-results.tsv:L603](data/gtdb-derived/results/public-results.tsv)
- Target 3: failed. [data/gtdb-derived/results/public-results.tsv:L604](data/gtdb-derived/results/public-results.tsv)
- Target 4: passed. [data/gtdb-derived/results/public-results.tsv:L605](data/gtdb-derived/results/public-results.tsv)

## Order-holdout accuracy

Numeric error is mean absolute error in degrees C, percent NaCl or pH units. Oxygen error is one minus balanced accuracy. Positive paired reduction favours the proposed predictor. All intervals resample held-out taxa.

| Trait | B1 error [95% interval] | Proposed error [95% interval] | Paired reduction [95% interval] | Pinned source line |
| --- | --- | --- | --- | --- |
| Temperature | 4.4857 [4.0306, 4.9648] | 4.4886 [4.0228, 4.9747] | -0.0029 [-0.0251, 0.0177] | [data/gtdb-derived/results/public-results.tsv:L56](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L69](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L76](data/gtdb-derived/results/public-results.tsv) |
| Oxygen | 0.1415 [0.0904, 0.2003] | 0.1307 [0.0794, 0.1936] | 0.0108 [-0.0054, 0.0283] | [data/gtdb-derived/results/public-results.tsv:L206](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L219](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L226](data/gtdb-derived/results/public-results.tsv) |
| Salinity | 1.6909 [1.3177, 2.2457] | 1.7306 [1.3117, 2.4045] | -0.0397 [-0.1677, 0.0247] | [data/gtdb-derived/results/public-results.tsv:L356](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L369](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L376](data/gtdb-derived/results/public-results.tsv) |
| pH | 0.5250 [0.4789, 0.5832] | 0.5093 [0.4697, 0.5570] | 0.0157 [0.0006, 0.0407] | [data/gtdb-derived/results/public-results.tsv:L506](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L519](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L526](data/gtdb-derived/results/public-results.tsv) |

## Coverage and useful uncertainty

Coverage includes supported abstentions exactly when the computed interval or set contains the true label. Unsupported items are excluded from coverage and reported as abstentions. Width is in the trait's original units; oxygen uses set cardinality. Every coverage estimate is accompanied by abstentions.

| Trait / rank | Coverage [95% interval] | Abstention | Mean width or cardinality | Pinned source line |
| --- | --- | --- | --- | --- |
| Temperature / family | 90.07% [88.05%, 91.94%] | 8.06% | 17.8647 | [data/gtdb-derived/results/public-results.tsv:L44](data/gtdb-derived/results/public-results.tsv) |
| Temperature / order | 90.29% [87.99%, 92.25%] | 20.38% | 18.7015 | [data/gtdb-derived/results/public-results.tsv:L69](data/gtdb-derived/results/public-results.tsv) |
| Oxygen / family | 90.89% [89.20%, 92.39%] | 22.53% | 1.1141 | [data/gtdb-derived/results/public-results.tsv:L194](data/gtdb-derived/results/public-results.tsv) |
| Oxygen / order | 92.10% [89.46%, 94.37%] | 25.56% | 1.1779 | [data/gtdb-derived/results/public-results.tsv:L219](data/gtdb-derived/results/public-results.tsv) |
| Salinity / family | 90.63% [87.84%, 92.97%] | 6.69% | 6.8323 | [data/gtdb-derived/results/public-results.tsv:L344](data/gtdb-derived/results/public-results.tsv) |
| Salinity / order | 89.99% [82.28%, 94.97%] | 48.15% | 7.7806 | [data/gtdb-derived/results/public-results.tsv:L369](data/gtdb-derived/results/public-results.tsv) |
| pH / family | 90.35% [88.49%, 91.97%] | 0.06% | 2.2096 | [data/gtdb-derived/results/public-results.tsv:L494](data/gtdb-derived/results/public-results.tsv) |
| pH / order | 89.04% [86.64%, 91.07%] | 0.00% | 2.1944 | [data/gtdb-derived/results/public-results.tsv:L519](data/gtdb-derived/results/public-results.tsv) |

## Horizons and measurement selection

Horizon bins use the frozen common cuts. The first failure compares with a training-side constant and checks whether most predictions abstain. Zero-based bin ordinals and their exploratory bootstrap intervals are discrete summaries. A right-censored horizon extends beyond the observed bins; it is not an infinite or universal threshold.

| Trait | Proposed horizon | B1 horizon | Proposed ordinal interval | Pinned source line |
| --- | --- | --- | --- | --- |
| Temperature | Bin 1 (0.3736 to 0.4558) | Bin 1 (0.3736 to 0.4558) | [1, 4] | [data/gtdb-derived/results/public-results.tsv:L75](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L74](data/gtdb-derived/results/public-results.tsv) |
| Oxygen | Beyond observed range | Beyond observed range | [5, 5] | [data/gtdb-derived/results/public-results.tsv:L225](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L224](data/gtdb-derived/results/public-results.tsv) |
| Salinity | Bin 2 (0.4492 to 0.5172) | Bin 2 (0.4492 to 0.5172) | [1, 3] | [data/gtdb-derived/results/public-results.tsv:L375](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L374](data/gtdb-derived/results/public-results.tsv) |
| pH | Bin 2 (0.4577 to 0.5206) | Bin 1 (0.3674 to 0.4577) | [2, 5] | [data/gtdb-derived/results/public-results.tsv:L525](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L524](data/gtdb-derived/results/public-results.tsv) |

The retrospective measurement experiment acquires whole orders under the stated organism budget, refits and recalibrates, and measures error and width on the remaining far organisms. Evaluation populations change as orders are acquired. A smaller area under the budget curve is preferable; the estimates below average the fold curves and have no confirmatory target.

| Trait | Widest error AUC | Farthest error AUC | Random error AUC | Pinned source line |
| --- | --- | --- | --- | --- |
| Temperature | 5.1394 | 5.2161 | 5.5904 | [data/gtdb-derived/results/public-results.tsv:L606](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L607](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L608](data/gtdb-derived/results/public-results.tsv) |
| Oxygen | 0.1517 | 0.1750 | 0.1625 | [data/gtdb-derived/results/public-results.tsv:L609](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L610](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L611](data/gtdb-derived/results/public-results.tsv) |
| Salinity | 2.5746 | 2.6690 | 2.6345 | [data/gtdb-derived/results/public-results.tsv:L612](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L613](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L614](data/gtdb-derived/results/public-results.tsv) |
| pH | 0.5423 | 0.5075 | 0.5567 | [data/gtdb-derived/results/public-results.tsv:L615](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L616](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L617](data/gtdb-derived/results/public-results.tsv) |

## Limits and sources

Exchangeability within distance bins is assumed, not demonstrated. Grouped unequal-size folds and distance conditioning do not inherit a demonstrated finite-sample guarantee from unconditioned CV+ results. Labels are table-level experimental records exported through GenomeSPOT, with residual per-value provenance uncertainty. Correlated genomes, small distant taxa, changing annotations and unsupported ranks limit generalisation. Accepted-item coverage has no nominal guarantee.

Calibrated per-distance intervals for this matched growth-condition benchmark were not found in our literature check of 2026-10-11. This is a bounded search finding. Adjacent work includes GenomeSPOT, Bac2Feature, CalPred, Boger and colleagues on conformal protein retrieval, Fannjiang and colleagues on feedback covariate shift, and Barber and colleagues on nonexchangeability. See [related work](docs/related-work.md), [technical note](docs/TECHNICAL_NOTE.md) and [data attribution](DATA.md).

Secondary figures report taxon-weighted coverage, the mean of the five fit-specific distances, and explicit refits after removing the ten disputed descriptor columns. The frozen feature lists contain none of those descriptors; the refitted point predictions are identical. No target uses these secondary analyses. [data/gtdb-derived/results/public-results.tsv:L618](data/gtdb-derived/results/public-results.tsv)

## Rebuild and reuse

With Python and the pinned analysis and rendering dependencies, one command acquires missing official inputs, verifies cached source hashes, reconstructs the frozen analysis, scores all outer folds, runs measurement selection and regenerates every public table, figure, note and page:

```sh
uv run --project release --frozen python -m scripts.release
```

Scratch is confined to ignored `work-tmp.noindex/`. Raw labels, sequences, fitted estimators and individual predictions remain untracked. Aggregate GTDB-derived analyses and figures are under CC BY-SA 4.0; BacDive labels are attributed under CC BY 4.0. Code is Apache-2.0, with GenomeSPOT's MIT notice retained. DATA.md records the commercial-contact condition and Cali Fund guidance.

Every result shown above cites a repository-relative TSV line. [Output hashes](data/release-manifest.json) pin that table and its underlying JSON records. [Complete results](docs/RESULTS.md), [figures](data/gtdb-derived/figures), [PDF note](docs/TECHNICAL_NOTE.pdf), [static project page](docs/site/index.html) and [reconstruction details](docs/reproducibility.md) provide the rest of the package. The original [pre-registration](PREREGISTRATION.md) is unchanged; its chronology is in [CHANGELOG.md](CHANGELOG.md).

This is a local release candidate. Public release remains pending scientific review and an authorised publication action.

Offline fixture checks:

```sh
uv run --frozen pytest --basetemp=work-tmp.noindex/pytest-fixtures
uv run --frozen ruff check scripts growth_horizon tests
uv run --frozen mypy scripts growth_horizon tests
```

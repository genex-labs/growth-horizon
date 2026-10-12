# Growth Horizon

GeneX Labs Inc. measures how growth-condition predictions behave as microbial genomes become more distant from labelled relatives. The benchmark combines taxonomic holdout, empirical interval and prediction-set coverage and abstention, so the record shows both predictive error and how often uncertainty prevents a useful answer.

The locked calibration and accuracy targets failed. B1 has lower order-holdout error for temperature and salinity. The order-holdout accuracy target failed: it requires at least a 10% lower error than B1, with a paired interval that excludes zero, on at least two traits. Oxygen at phylum is a 12.9% reduction whose interval excludes zero, and oxygen on the random split is a 14.4% reduction whose interval excludes zero. Those splits are outside that target. These are descriptive results from the full usable labelled population; no estimator or target was changed after outer scoring.

- Target 1: failed. [data/gtdb-derived/results/public-results.tsv:L602](data/gtdb-derived/results/public-results.tsv)
- Target 2: failed. [data/gtdb-derived/results/public-results.tsv:L603](data/gtdb-derived/results/public-results.tsv)
- Target 3 (publication): pending external publication; horizon estimates for every trait are complete in the package. [data/gtdb-derived/results/public-results.tsv:L604](data/gtdb-derived/results/public-results.tsv)
- Target 4: passed. [data/gtdb-derived/results/public-results.tsv:L605](data/gtdb-derived/results/public-results.tsv)

Target 1 failed on two of its three parts. Pooled coverage intervals reached 90% in all eight trait and rank cells. Two supported bins had intervals wholly below 87% (temperature/order fold 2 bin 0; salinity/family fold 3 bin 2). The naive far-bin condition held in 1 of 8 cells, temperature/order, for both B1 and B2. Elsewhere at least one naive comparator covered more than 80%, or had an upper limit of 90% or more, in the far bin. [data/gtdb-derived/results/public-results.tsv:L602](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L618](data/gtdb-derived/results/public-results.tsv)

Target 4 counts order rank only. B1 has lower point error than the proposed predictor for order-holdout temperature and salinity; neither paired interval excludes zero. [data/gtdb-derived/results/public-results.tsv:L605](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L76](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L376](data/gtdb-derived/results/public-results.tsv) B1 also has lower point error for temperature at genus, phylum and the random split, salinity at family, class and phylum, and pH at phylum; none of those paired intervals excludes zero. Salinity at genus is identical. [data/gtdb-derived/results/public-results.tsv:L26](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L126](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L151](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L351](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L401](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L426](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L576](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L326](data/gtdb-derived/results/public-results.tsv)

## Order-holdout accuracy

Numeric error is mean absolute error in degrees C, percent NaCl or pH units. Oxygen error is one minus balanced accuracy. Positive paired reduction favours the proposed predictor. All intervals resample held-out taxa.

| Trait | B1 error [95% interval] | Proposed error [95% interval] | Paired reduction [95% interval] | Pinned source line |
| --- | --- | --- | --- | --- |
| Temperature | 4.4857 [4.0306, 4.9648] | 4.4886 [4.0228, 4.9747] | -0.0029 [-0.0251, 0.0177] | [data/gtdb-derived/results/public-results.tsv:L56](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L69](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L76](data/gtdb-derived/results/public-results.tsv) |
| Oxygen | 0.1415 [0.0904, 0.2003] | 0.1307 [0.0794, 0.1936] | 0.0108 [-0.0054, 0.0283] | [data/gtdb-derived/results/public-results.tsv:L206](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L219](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L226](data/gtdb-derived/results/public-results.tsv) |
| Salinity | 1.6909 [1.3177, 2.2457] | 1.7306 [1.3117, 2.4045] | -0.0397 [-0.1677, 0.0247] | [data/gtdb-derived/results/public-results.tsv:L356](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L369](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L376](data/gtdb-derived/results/public-results.tsv) |
| pH | 0.5250 [0.4789, 0.5832] | 0.5093 [0.4697, 0.5570] | 0.0157 [0.0006, 0.0407] | [data/gtdb-derived/results/public-results.tsv:L506](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L519](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L526](data/gtdb-derived/results/public-results.tsv) |

## Coverage and useful uncertainty

Coverage includes supported abstentions exactly when the computed interval or set contains the true label. Unsupported items are excluded from coverage and reported as abstentions. Width is in the trait's original units; oxygen is a class label with uncertainty represented by a prediction set, whose size is its cardinality. Every coverage estimate is accompanied by abstentions.

| Trait / rank | Pooled coverage [95% interval] | Accepted coverage [95% interval] | Abstention | Mean width or cardinality | Accepted mean width or cardinality | Pinned source line |
| --- | --- | --- | --- | --- | --- | --- |
| Temperature / family | 90.07% [88.05%, 91.94%] | 89.99% [88.01%, 91.86%] | 8.06% | 17.8647 | 17.5959 | [data/gtdb-derived/results/public-results.tsv:L44](data/gtdb-derived/results/public-results.tsv) |
| Temperature / order | 90.29% [87.99%, 92.25%] | 90.17% [87.61%, 92.38%] | 20.38% | 18.7015 | 17.5541 | [data/gtdb-derived/results/public-results.tsv:L69](data/gtdb-derived/results/public-results.tsv) |
| Oxygen / family | 90.89% [89.20%, 92.39%] | 95.41% [93.45%, 97.02%] | 22.53% | 1.1141 | 1.0000 | [data/gtdb-derived/results/public-results.tsv:L194](data/gtdb-derived/results/public-results.tsv) |
| Oxygen / order | 92.10% [89.46%, 94.37%] | 94.61% [91.64%, 97.16%] | 25.56% | 1.1779 | 1.0000 | [data/gtdb-derived/results/public-results.tsv:L219](data/gtdb-derived/results/public-results.tsv) |
| Salinity / family | 90.63% [87.84%, 92.97%] | 90.32% [87.56%, 92.69%] | 6.69% | 6.8323 | 6.7127 | [data/gtdb-derived/results/public-results.tsv:L344](data/gtdb-derived/results/public-results.tsv) |
| Salinity / order | 89.99% [82.28%, 94.97%] | 83.32% [71.31%, 91.84%] | 48.15% | 7.7806 | 6.7489 | [data/gtdb-derived/results/public-results.tsv:L369](data/gtdb-derived/results/public-results.tsv) |
| pH / family | 90.35% [88.49%, 91.97%] | 90.37% [88.36%, 91.87%] | 0.06% | 2.2096 | 2.2090 | [data/gtdb-derived/results/public-results.tsv:L494](data/gtdb-derived/results/public-results.tsv) |
| pH / order | 89.04% [86.64%, 91.07%] | 89.04% [86.64%, 91.07%] | 0.00% | 2.1944 | 2.1944 | [data/gtdb-derived/results/public-results.tsv:L519](data/gtdb-derived/results/public-results.tsv) |

Accepted-item coverage has no nominal guarantee. Accepted items exclude abstentions and unsupported rows.

## Order-holdout horizons

This table is the order rank only. Per-rank records are the JSON files under data/gtdb-derived/results/. At class, temperature already fails in the nearest bin for both predictors. At phylum, the horizons are unidentified. The B1 ordinal interval is shown beside the proposed interval because the two intervals are not the same for every trait. Horizon bins use the frozen common cuts. The first failure compares with a training-side constant and checks whether most predictions abstain. Zero-based bin ordinals and their exploratory bootstrap intervals are discrete summaries. A right-censored horizon extends beyond the observed bins; it is not an infinite or universal threshold.

| Trait | Proposed horizon | B1 horizon | Proposed ordinal interval | B1 ordinal interval | Pinned source line |
| --- | --- | --- | --- | --- | --- |
| Temperature | Bin 1 (0.3736 to 0.4558) | Bin 1 (0.3736 to 0.4558) | [1, 4] | [1, 4] | [data/gtdb-derived/results/public-results.tsv:L75](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L74](data/gtdb-derived/results/public-results.tsv) |
| Oxygen | Beyond observed range | Beyond observed range | [5, 5] | [0, 5] | [data/gtdb-derived/results/public-results.tsv:L225](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L224](data/gtdb-derived/results/public-results.tsv) |
| Salinity | Bin 2 (0.4492 to 0.5172) | Bin 2 (0.4492 to 0.5172) | [1, 3] | [1, 5] | [data/gtdb-derived/results/public-results.tsv:L375](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L374](data/gtdb-derived/results/public-results.tsv) |
| pH | Bin 2 (0.4577 to 0.5206) | Bin 1 (0.3674 to 0.4577) | [2, 5] | [1, 5] | [data/gtdb-derived/results/public-results.tsv:L525](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L524](data/gtdb-derived/results/public-results.tsv) |

## Exploratory measurement selection

The retrospective measurement experiment acquires whole orders under the stated organism budget, refits and recalibrates, and measures error and width on the remaining far organisms. Evaluation populations change as orders are acquired. A smaller area under the budget curve is preferable; the estimates below average the fold curves and have no confirmatory target.

| Trait / strategy | Mean error AUC | Mean width or cardinality AUC | Pinned source line |
| --- | --- | --- | --- |
| Temperature / widest | 5.1394 | 23.6409 | [data/gtdb-derived/results/public-results.tsv:L606](data/gtdb-derived/results/public-results.tsv) |
| Temperature / farthest | 5.2161 | 23.6662 | [data/gtdb-derived/results/public-results.tsv:L607](data/gtdb-derived/results/public-results.tsv) |
| Temperature / random | 5.5904 | 23.3881 | [data/gtdb-derived/results/public-results.tsv:L608](data/gtdb-derived/results/public-results.tsv) |
| Oxygen / widest | 0.1517 | 1.2486 | [data/gtdb-derived/results/public-results.tsv:L609](data/gtdb-derived/results/public-results.tsv) |
| Oxygen / farthest | 0.1750 | 1.2903 | [data/gtdb-derived/results/public-results.tsv:L610](data/gtdb-derived/results/public-results.tsv) |
| Oxygen / random | 0.1625 | 1.2788 | [data/gtdb-derived/results/public-results.tsv:L611](data/gtdb-derived/results/public-results.tsv) |
| Salinity / widest | 2.5746 | 9.1991 | [data/gtdb-derived/results/public-results.tsv:L612](data/gtdb-derived/results/public-results.tsv) |
| Salinity / farthest | 2.6690 | 8.9830 | [data/gtdb-derived/results/public-results.tsv:L613](data/gtdb-derived/results/public-results.tsv) |
| Salinity / random | 2.6345 | 8.8672 | [data/gtdb-derived/results/public-results.tsv:L614](data/gtdb-derived/results/public-results.tsv) |
| pH / widest | 0.5423 | 2.4999 | [data/gtdb-derived/results/public-results.tsv:L615](data/gtdb-derived/results/public-results.tsv) |
| pH / farthest | 0.5075 | 2.5501 | [data/gtdb-derived/results/public-results.tsv:L616](data/gtdb-derived/results/public-results.tsv) |
| pH / random | 0.5567 | 2.4505 | [data/gtdb-derived/results/public-results.tsv:L617](data/gtdb-derived/results/public-results.tsv) |

Random selection has the lowest mean width AUC for temperature, salinity and pH. Widest-first has the lowest mean set-cardinality AUC only for oxygen. [data/gtdb-derived/results/public-results.tsv:L606](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L607](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L608](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L609](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L610](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L611](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L612](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L613](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L614](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L615](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L616](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L617](data/gtdb-derived/results/public-results.tsv)

## Limits and sources

The training-mean baseline B0 has the lowest point error for temperature at phylum and for pH at class and phylum, limiting the value of genome-based predictions at these ranks. [data/gtdb-derived/results/public-results.tsv:L102](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L106](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L111](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L115](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L119](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L527](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L531](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L536](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L540](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L544](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L552](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L556](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L561](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L565](data/gtdb-derived/results/public-results.tsv); [data/gtdb-derived/results/public-results.tsv:L569](data/gtdb-derived/results/public-results.tsv)

Exchangeability within distance bins is assumed, not demonstrated. Grouped unequal-size folds and distance conditioning do not inherit a demonstrated finite-sample guarantee from unconditioned CV+ results. Labels are table-level experimental records exported through GenomeSPOT, with residual per-value provenance uncertainty. Correlated genomes, small distant taxa, changing annotations and unsupported ranks limit generalisation. Accepted-item coverage has no nominal guarantee.

In our literature check of 2026-10-11, we did not find a report of calibrated prediction intervals for genome-based prediction of microbial growth conditions that gives coverage separately for bins of phylogenetic distance to the training set, under whole-family or whole-order hold-out. The closest work we found reports interval coverage across phylogenetic-distance cutoffs for a different microbial trait, 16S rRNA gene copy number (Gao and Wu, 2023), and false discovery control within sequence-identity groups for enzyme function prediction (Ding, Luo and Luo, 2024). This is a bounded search finding, not a claim that no such work exists. Closest work includes Gao and Wu (2023) on distance-cutoff coverage for 16S copy number and Ding, Luo and Luo (2024) on sequence-identity-group false discovery control. Adjacent work includes GenomeSPOT, Bac2Feature, CalPred, Boger and colleagues on conformal protein retrieval, Fannjiang and colleagues on feedback covariate shift, and Barber and colleagues on nonexchangeability. See [related work](docs/related-work.md), [technical note](docs/TECHNICAL_NOTE.md) and [data attribution](DATA.md).

Secondary figures report taxon-weighted coverage, the mean of the five fit-specific distances, and explicit refits after removing the ten disputed descriptor columns. The frozen feature lists contain none of those descriptors; the refitted point predictions are identical. No target uses these secondary analyses. [data/gtdb-derived/results/public-results.tsv:L618](data/gtdb-derived/results/public-results.tsv)

## Rebuild and reuse

Offline checks read the committed aggregates. They do not download inputs, refit estimators or rescore folds:

```sh
uv run --project release --frozen python -m scripts.check_release
uv run --frozen pytest --basetemp=work-tmp.noindex/pytest-fixtures
```

That scan uses the rendering project because it reads the PDF. It compares each path in [data/release-manifest.json](data/release-manifest.json) with its recorded size and SHA-256, then writes `data/checks/release-scan.json`. The fixture command runs the offline tests in the analysis environment.

Full recomputation is a different command. With Python 3.13 and the pinned analysis and rendering dependencies, it acquires missing official inputs, verifies cached source hashes, reconstructs the frozen analysis, scores all outer folds, runs measurement selection and regenerates every public table, figure, note and page:

```sh
uv run --project release --frozen python -m scripts.release
```

That command needs a network connection or a checksum-verified copy of the raw inputs. It is not an offline check. `data/raw/` and `data/gtdb-derived/local/` (fitted trees and individual predictions) are not redistributed. The pinned replay inputs under `data/raw/labels/`, `data/raw/verification/` and `data/raw/gtdb/` total 254,404,224 bytes in `data/source-manifest.json`. Acquisition stops if free space on `/` is below 25 GB. Phase 1 rebuild without outer scoring is `uv run --frozen python -m scripts.rebuild`. That command leaves outer intervals and oxygen sets uncomputed. Outer scoring runs only in `scripts.release`.

`uv.lock` allows any Python 3.13. The frozen numbers were produced with Python 3.13.15. A fresh export used Python 3.13.12 with the same lock.

Scratch is confined to ignored `work-tmp.noindex/`. Raw labels, sequences, fitted estimators and individual predictions remain untracked. Aggregate GTDB-derived analyses and figures are under CC BY-SA 4.0; BacDive labels are attributed under CC BY 4.0. Code is Apache-2.0, with GenomeSPOT's MIT notice retained. DATA.md records the commercial-contact condition and Cali Fund guidance.

Every result shown above cites a repository-relative TSV line. [Output hashes](data/release-manifest.json) pin that table and its underlying JSON records. [Complete results](docs/RESULTS.md), [figures](data/gtdb-derived/figures), [PDF note](docs/TECHNICAL_NOTE.pdf), [static project page](docs/site/index.html) and [reconstruction details](docs/reproducibility.md) provide the rest of the package. The original [pre-registration](PREREGISTRATION.md) is frozen; outcomes are in [RESULTS.md](docs/RESULTS.md) and [current scoring status](docs/PHASE2_STATUS.md). Freeze commits are in [CHANGELOG.md](CHANGELOG.md).

Research prototype on this labelled GTDB-mapped table; not tested on prospective cultures, on organisms outside the table, or for clinical or production use.

Offline fixture checks:

```sh
uv run --frozen pytest --basetemp=work-tmp.noindex/pytest-fixtures
uv run --frozen ruff check scripts growth_horizon tests
uv run --frozen mypy scripts growth_horizon tests
```

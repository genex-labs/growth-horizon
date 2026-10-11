# Baseline specifications

All available baselines use identical primary populations and outer folds.
Phase 1 only fits models and predicts inside each outer training side.

B1 retrains GenomeSPOT's release v1.0.0 published specification. The three
numeric traits use 60 compartment-specific amino-acid frequencies, standard
scaling and Lasso with 100,000 maximum iterations. Temperature uses alpha
0.001 (published pipeline index 16); pH and salinity use 0.01 (index 17).
Oxygen uses the 20 whole-proteome amino-acid frequencies, standard scaling,
SelectKBest with mutual-information regression and k=20, and balanced logistic
regression with C=1, the lbfgs solver and 100,000 maximum iterations (index 2).
The published feature and pipeline instructions are acquired as manifest
sources. The iteration budget is increased from the upstream 10,000 limit
because inner-only fits issued convergence warnings. Features, penalty, solver
and default tolerance remain unchanged; no outer result motivated the change. The mutual-information estimator is seeded for reproducibility;
with k=20 of 20, it drops no features. The upstream taxonomic balancing and
use flags are not adopted: the binding population rule includes every usable
nonmissing label. This population change is explicit.

B2 returns the label of the closest proper-training representative by branch
length within its domain. Ties choose the lexicographically smallest training
representative, then the smallest assembly accession. Assemblies mapped to the
same representative have zero distance. The bacterial and archaeal trees are
separate: no artificial interdomain branch is added. Absence of a training
leaf in the domain leads to abstention, never an invented distance.

B3 uses the 20 `all_aa_*` whole-proteome frequencies: ridge for numeric traits
and balanced logistic regression for oxygen. Regularisation is selected from
0.1, 1, 10 and 100 on five grouped tuning folds strictly within the proper
training side. Logistic C is the reciprocal of that regularisation value.

The proposed predictor selects B1 or ridge/logistic on the 60 published
compartment features by the same five tuning folds. Ties favour B1. Neither
calibration residuals nor outer labels select the predictor. The selected
predictor receives distance-aware intervals; all baselines also receive that
procedure and the naive random-split interval for comparison.

B4 is not run. The paper (doi 10.1038/s42003-025-08313-3) names
`LeibnizDSMZ/bacdive-AI`. Its public repository tree and README were inspected
2026-10-11; the licence endpoint returned 404 and neither a licence file nor
an explicit licence declaration was present. No code or models from this
repository are reused. Its application consumes InterPro/Pfam annotation
files, which are absent from the authorised table; its eight binary traits
also do not supply the three numeric optima. Executability was therefore not
claimed or tested. This comparator's unmet licence/input conditions justify
its exclusion, as allowed by the binding design.

For distance-aware calibration, models fit only the proper side remaining
after holding out whole calibration taxa. A separate naive model fits a
random 80% of the outer training side; its residual spread comes from the
remaining random 20%. It never sees an outer test organism. These distinct
fitting populations are recorded, rather than refitting a calibrated model
on calibration labels.

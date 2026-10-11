# Scoring clarifications and secondary experiment

Fixed before any outer prediction or number. Pre-registration v2 remains binding.

An abstained item counts as covered exactly when its computed interval or set contains the true value; abstention rates are reported beside every coverage figure.

Unsupported calibration bins are excluded from every coverage figure and are reported as abstentions. A secondary figure bins test genomes by the mean of their five fit-specific distances, using the frozen calibration cuts and merges. It changes no target.

The two earlier v2-era freezes were 839b22f (2026-10-11 05:54:49 PT, amendment C and v2) and 3b1f6d2 (2026-10-11 07:04:00 PT, re-freeze after normalising calibration artefacts); both preceded any outer-fold number.

## Measure next

A retrospective, exploratory experiment on each of the five order holdouts, for each trait. Acquisition budgets are 0, 25, 50, 75 and 100 additional labelled organisms. Whole orders are acquired together, never split; a candidate larger than the remaining budget is skipped. Actual acquired counts and unused budget are reported. The three choices are widest calibrated intervals (mean supported width or set cardinality within an order, unsupported first), farthest-first (mean nearest distance within an order, recomputed after every selection), and seeded random order. Ties use lexical order names. No candidate label is consulted before acquisition.

After each acquisition batch, the predictor and its five calibration fits are refitted and recalibrated using the original estimator families and original fitting-side hyperparameters and selection choices. These choices are held fixed rather than selected using acquired or remaining test labels. New same-rank inner memberships use the original seed schedule. Distance cuts use phenotype-free nested fitting-side distances, with the same 50-taxon support rule and randomized inverse scores. Primary results are never changed.

The remaining far organisms have original outer-training distance at or above the original last common order cut point. Each strategy is scored on its remaining far set; this changing evaluation population is a limitation. Report supported mean width, error and abstentions after each batch, trapezoidal area under the budget curve divided by 100, and counts of remaining orders. Paired fold summaries are exploratory, with no pass target or laboratory claim.

The ten-column sensitivity refits B1 and the proposed point predictor after removing all mean_zc and mean_nh2o columns. Feature lists and fitted hyperparameters remain fixed. No target uses this refit.

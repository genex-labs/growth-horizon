# Current scoring status

`PREREGISTRATION.md` is a frozen phase 1 record. Its text is not updated when outer scores are computed. The outcomes are in [RESULTS.md](RESULTS.md) and `data/gtdb-derived/results/targets.json`.

Outer scoring has been run. Target 1 and target 2 failed. Target 3 horizon estimates are complete in the package, and the publication criterion is still unmet. Target 4 passed.

The source manifest status, the experimental-label audit flag, and the cross-fit and horizon-cutpoint records still say that outer scores had not been computed. Those files are hash-pinned in the frozen pre-registration. They are historical snapshots, not the status of this tree.

The repository licence is Apache-2.0 (`LICENSE` and `CITATION.cff`). GenomeSPOT's upstream licence is MIT (`NOTICE` and `docs/GenomeSPOT-MIT.txt`). The frozen source manifest field `repository_licence` still reads MIT and was not edited.

`uv.lock` allows any Python 3.13. The frozen numbers used Python 3.13.15. A fresh export used Python 3.13.12 with the same lock. The frozen pre-registration sentence that names 3.13.15 together with the lock was not edited.

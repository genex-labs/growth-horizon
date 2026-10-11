# Phase 1 scoring boundary

No outer-fold prediction or performance metric has been computed. The only
permitted predictions are tuning and calibration queries wholly inside an
outer training side. The development runner checks that boundary before every
such query. Outer memberships and phenotype-free branch distances are permitted
build artefacts and do not constitute prediction performance.

Resume 3 permits the fixed 71-genome sequence check and requires reporting
feature differences without treating them as a build blocker. It does not
relax the outer-scoring boundary. No integrity incident or quarantine has
occurred. Outer scoring remains prohibited in this phase, including after the
local pre-registration commit. The separate phase-2 brief and reviewed record
are required before any locked test is scored.

If an accidental outer prediction or metric occurs, stop, record its shell
clock time and file checksums here, and move all affected files to a named
quarantine outside this repository. Evidence must never go to the Trash.

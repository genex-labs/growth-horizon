# Growth Horizon

Phase 1 resumed from `5e1c843` under Resume 2. The three table sources are
accepted and the release asset checksum matches. Work is blocked at the required
100-genome feature verification because sampled GenBank assemblies lack protein
FASTA files on the official open-data service. No sampled genome has been
replaced, no sequence has been downloaded and no benchmark prediction or metric
has been computed. See [the acquisition record](docs/ACQUISITION_STATUS.md),
[the source manifest](data/source-manifest.json) and [DATA.md](DATA.md).

The planned benchmark examines growth-condition predictions and calibrated
uncertainty under taxonomic holdout. Calibrated per-distance intervals for these
traits were not found in our literature check of 2026-10-11. This is the supplied
design's bounded literature finding; source DOI verification remains pending.

Python 3.13 and the pinned `uv.lock` provide the acquisition environment:

```sh
uv sync --frozen --python python3.13
uv run --frozen python scripts/audit_labels.py
uv run --frozen python scripts/preflight_sample.py
uv run --frozen pytest --basetemp=work-tmp/pytest-acquisition
uv run --frozen ruff check scripts tests
uv run --frozen mypy scripts tests
```

The preflight command expects the preserved fixed sample and assembly reports
under `data/raw/verification/`; it resumes the preserved size audit without downloading sequences and exits
nonzero for unavailable files or an exceeded size limit. Existing source-file
receipts are reused rather than silently repeated.
These commands reproduce the current inspection only. The clean-checkout
benchmark rebuild command remains unimplemented pending verified features.

Raw evidence and the training table stay untracked under `data/raw/`.
Our code is Apache-2.0; the upstream MIT notice is preserved in
[docs/GenomeSPOT-MIT.txt](docs/GenomeSPOT-MIT.txt). Nothing has been published.

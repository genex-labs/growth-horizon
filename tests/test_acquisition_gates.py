# SPDX-License-Identifier: Apache-2.0
"""Offline tests of acquisition gates before any sequence download."""

import shutil
from unittest.mock import patch

import pytest

from scripts.preflight_sample import LIMIT, assembly_basename, check_space, gate_status


def test_ncbi_assembly_path_punctuation() -> None:
    assert assembly_basename("GCA_001053095.1", "5139_1#3") == "GCA_001053095.1_5139_1_3"
    assert assembly_basename("GCA_900103275.1", "IMG-taxon 2617270936 annotated assembly") == (
        "GCA_900103275.1_IMG-taxon_2617270936_annotated_assembly"
    )


def test_missing_file_prevents_passing_a_small_estimate() -> None:
    assert gate_status(123, [{"reason": "HTTP 404"}]) == "size_unknown"


def test_size_limit_boundary() -> None:
    assert gate_status(LIMIT, []) == "size_gate_passed"
    assert gate_status(LIMIT + 1, []) == "size_gate_exceeded"


def test_disk_space_stop_boundary() -> None:
    usage = shutil._ntuple_diskusage(100_000_000_000, 75_000_000_001, 24_999_999_999)
    with patch("scripts.preflight_sample.shutil.disk_usage", return_value=usage):
        with pytest.raises(SystemExit, match="below 25 GB"):
            check_space()
    usage = shutil._ntuple_diskusage(100_000_000_000, 75_000_000_000, 25_000_000_000)
    with patch("scripts.preflight_sample.shutil.disk_usage", return_value=usage):
        check_space()


def test_manifest_replay_requires_pinned_download_inputs_only(tmp_path: object) -> None:
    import hashlib
    import json
    from pathlib import Path
    from unittest.mock import patch

    from scripts import acquire

    root = Path(str(tmp_path))
    path = root / 'data/raw/labels/training_data.tsv'
    path.parent.mkdir(parents=True)
    path.write_bytes(b'fixture')
    manifest = root / 'manifest.json'
    expected = hashlib.sha256(b'fixture').hexdigest()
    manifest.write_text(json.dumps({'records': [
        {'path': 'data/raw/labels/training_data.tsv', 'sha256': expected,
         'url': 'https://github.com/example/release', 'bytes': 7, 'kind': 'verified_source'},
        {'path': 'data/raw/source-audit/historical.json', 'sha256': 'historical',
         'url': None, 'bytes': 1, 'kind': 'local_process_receipt'},
    ]}))
    with patch.object(acquire, 'ROOT', root), patch.object(acquire, 'MANIFEST', manifest):
        acquire.replay()
        path.write_bytes(b'tampered')
        with pytest.raises(ValueError, match='checksum mismatch'):
            acquire.replay()


def test_pinned_gtdb_rebuild_does_not_require_new_size_requests(tmp_path: object) -> None:
    import hashlib
    import json
    from pathlib import Path
    from typing import Any

    from scripts import acquire_gtdb

    root = Path(str(tmp_path))
    raw = root / 'data/raw/gtdb'
    raw.mkdir(parents=True)
    (raw / 'releases.html').write_text('<a href="release232/">release</a>')
    files = ['auxillary_files/sp_clusters_r232.tsv', 'ar53_r232.tree.gz', 'bac120_r232.tree.gz']
    base = 'https://data.gtdb.ecogenomic.org/releases/release232/232.0/'
    records = []
    md5s = []
    for file in files:
        target = raw / file
        target.parent.mkdir(parents=True, exist_ok=True)
        data = file.encode()
        target.write_bytes(data)
        records.append({'path': 'data/raw/gtdb/' + file, 'url': base + file, 'bytes': len(data)})
        md5s.append(hashlib.md5(data).hexdigest() + '  ' + file)
    (raw / 'MD5SUM.txt').write_text('\n'.join(md5s))
    (root / 'data/source-manifest.json').write_text(json.dumps({'records': records}))

    def cached(url: str, path: str, size: int | None = None) -> dict[str, Any]:
        if size is not None:
            assert (root / path).stat().st_size == size
        return {'path': path, 'url': url}

    with patch.object(acquire_gtdb, 'ROOT', root), \
            patch.object(acquire_gtdb, 'acquire', cached), \
            patch.object(acquire_gtdb, 'ranged_acquire', cached), \
            patch('scripts.acquire_gtdb.urllib.request.urlopen') as network:
        acquire_gtdb.main()
        network.assert_not_called()
    assert json.loads((raw / 'size-preflight.json').read_text()) == {
        file: len(file.encode()) for file in files}

# SPDX-License-Identifier: Apache-2.0
"""Size-gated, checksummed source acquisition on the authorised services."""
import hashlib
import fcntl
import json
import time
import urllib.request
from pathlib import Path
from typing import Any

from scripts.preflight_sample import check_space

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data/source-manifest.json'


def digest(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def acquire(url: str, path: str, expected_bytes: int | None = None,
            expected_sha256: str | None = None) -> dict[str, Any]:
    check_space()
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=120) as response, target.open('wb') as out:
                    while block := response.read(1024 * 1024):
                        check_space()
                        out.write(block)
                break
            except Exception:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
    size, sha = target.stat().st_size, digest(target)
    if expected_bytes is not None and size != expected_bytes:
        raise ValueError(f'Source size mismatch: {path}')
    if expected_sha256 is not None and sha != expected_sha256:
        raise ValueError(f'Source checksum mismatch: {path}')
    record = {'url': url, 'path': path, 'bytes': size, 'sha256': sha,
              'kind': 'verified_source'}
    with (ROOT / 'work-tmp.noindex/manifest.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        manifest = json.loads(MANIFEST.read_text())
        manifest['records'] = [r for r in manifest['records'] if r['path'] != path] + [record]
        MANIFEST.write_text(json.dumps(manifest, indent=2) + '\n')
    return record


def replay() -> None:
    required = ('data/raw/labels/', 'data/raw/verification/upstream/',
                'data/raw/verification/sequences/', 'data/raw/gtdb/')
    for record in json.loads(MANIFEST.read_text())['records']:
        if not record['path'].startswith(required):
            continue
        path = ROOT / record['path']
        if not path.exists():
            if record['url'] is None or 'incomplete' in record['kind']:
                continue
            acquire(record['url'], record['path'], record['bytes'], record['sha256'])
        elif digest(path) != record['sha256']:
            raise ValueError(f'Manifest checksum mismatch: {path}')


if __name__ == '__main__':
    replay()

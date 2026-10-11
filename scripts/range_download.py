# SPDX-License-Identifier: Apache-2.0
"""Bounded three-connection range transfer; each response is checked before assembly."""
import hashlib
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from scripts.acquire import ROOT, acquire
from scripts.preflight_sample import check_space


def ranged_acquire(url: str, path: str, size: int) -> dict[str, Any]:
    target = ROOT / path
    if target.exists() and target.stat().st_size == size:
        return acquire(url, path, size)
    chunks = ROOT / 'data/raw/transfer-parts' / target.name
    chunks.mkdir(parents=True, exist_ok=True)
    chunk_size = 262144
    def fetch(start: int) -> Path:
        check_space()
        end = min(size - 1, start + chunk_size - 1)
        output = chunks / f'{start}-{end}.bin'
        if output.exists() and output.stat().st_size == end - start + 1:
            return output
        for attempt in range(5):
            try:
                request = urllib.request.Request(url, headers={'Range': f'bytes={start}-{end}'})
                with urllib.request.urlopen(request, timeout=120) as response:
                    if response.status != 206 or response.headers['Content-Range'] != f'bytes {start}-{end}/{size}':
                        raise ValueError('Source does not support the requested byte range')
                    data = response.read()
                if len(data) != end - start + 1:
                    raise ValueError('Truncated range response')
                output.write_bytes(data)
                return output
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)
        raise AssertionError('Unreachable')
    starts = list(range(0, size, chunk_size))
    with ThreadPoolExecutor(max_workers=3) as pool:
        parts = list(pool.map(fetch, starts))
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('wb') as out:
        for part in parts:
            out.write(part.read_bytes())
    # Keep transfer parts as acquisition evidence; no deletion is needed.
    receipt = [{'start': start, 'bytes': part.stat().st_size,
                'sha256': hashlib.sha256(part.read_bytes()).hexdigest()} for start, part in zip(starts, parts, strict=True)]
    (chunks / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    return acquire(url, path, size)

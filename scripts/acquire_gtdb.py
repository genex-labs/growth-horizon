# SPDX-License-Identifier: Apache-2.0
"""Acquire only reference trees and metadata from the current official release."""
import hashlib
import json
import re
import urllib.request

from scripts.acquire import ROOT, acquire
from scripts.range_download import ranged_acquire


def main() -> None:
    index = acquire('https://data.gtdb.ecogenomic.org/releases/',
                    'data/raw/gtdb/releases.html')
    latest = max(map(int, re.findall(r'href="release(\d+)/"',
                                    (ROOT / index['path']).read_text())))
    if latest != 232:
        raise ValueError('Manifest release changed; re-register data version before rebuilding')
    base = 'https://data.gtdb.ecogenomic.org/releases/release232/232.0/'
    acquire(base, 'data/raw/gtdb/index.html')
    for file in ['VERSION.txt', 'RELEASE_NOTES.txt', 'MD5SUM.txt', 'FILE_DESCRIPTIONS.txt',
                 'METHODS.txt', 'auxillary_files/metadata_field_desc.tsv']:
        acquire(base + file, 'data/raw/gtdb/' + file)
    md5s = {line.split()[1].removeprefix('./'): line.split()[0]
            for line in (ROOT / 'data/raw/gtdb/MD5SUM.txt').read_text().splitlines()}
    files = ['auxillary_files/sp_clusters_r232.tsv',
             'ar53_r232.tree.gz', 'bac120_r232.tree.gz']
    estimates = {}
    for file in files:
        with urllib.request.urlopen(urllib.request.Request(base + file, method='HEAD')) as r:
            estimates[file] = int(r.headers['Content-Length'])
    (ROOT / 'data/raw/gtdb/size-preflight.json').write_text(json.dumps(estimates, indent=2)+'\n')
    assert sum(estimates.values()) < 8_000_000_000
    for file in files:
        r = ranged_acquire(base + file, 'data/raw/gtdb/' + file, estimates[file])
        with (ROOT / r['path']).open('rb') as stream:
            actual_md5 = hashlib.file_digest(stream, 'md5').hexdigest()
        assert actual_md5 == md5s[file], file
        print(json.dumps(r), flush=True)


if __name__ == '__main__':
    main()

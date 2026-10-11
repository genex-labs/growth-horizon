# SPDX-License-Identifier: Apache-2.0
"""Scan tracked files and validate pinned public output paths and hashes."""
from __future__ import annotations

from html.parser import HTMLParser
import json
import re
import subprocess
from typing import Any
from urllib.parse import unquote, urlsplit

from scripts.acquire import ROOT, digest


class PageLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.failures: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag in ('script', 'iframe'):
            self.failures.append('Active page element: '+tag)
        if tag == 'img' and not values.get('alt'):
            self.failures.append('Image without alternative text')
        for key in ('href', 'src'):
            if values.get(key):
                self.links.append(str(values[key]))


def main() -> None:
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).split(b'\0')
    patterns = {
        'home_path': re.compile(b'(?:/Us'+b'ers/|/ho'+b'me/|/private/'+b'tmp/|file'+b'://)'),
        'em_dash': re.compile('\u2014'.encode()),
        'assistant_name': re.compile(rb'\b(?:'+b'co'+b'dex|clau'+b'de|chat'+b'gpt|open'+b'ai|anthro'+b'pic|gemi'+b'ni|gr'+b'ok|copi'+b'lot|cur'+b'sor|g'+b'pt-[0-9])\b', re.I),
        'credential_or_signed_url': re.compile(rb'(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[A-Z0-9]{16}|-----BEGIN [A-Z ]*PRIVATE KEY-----|[?&](?:access_token|api_key|token|X-Amz-Signature|X-Goog-Signature)=)', re.I),
        'trailer': re.compile(rb'(?m)^\s*(?:Co-authored-by|Signed-off-by|Generated-by):', re.I),
    }
    failures: list[dict[str, Any]] = []
    for relative in tracked:
        if not relative:
            continue
        path = ROOT/relative.decode()
        data = path.read_bytes()
        for name, pattern in patterns.items():
            if pattern.search(data):
                failures.append({'path': str(path.relative_to(ROOT)), 'rule': name})
        if path.suffix == '.pdf':
            from pypdf import PdfReader 
            reader = PdfReader(path)
            text = '\n'.join(p.extract_text() for p in reader.pages).encode()
            for name, pattern in patterns.items():
                if pattern.search(text):
                    failures.append({'path': str(path.relative_to(ROOT)), 'rule': name+'_pdf_text'})
            if path.name == 'TECHNICAL_NOTE.pdf' and not 4 <= len(reader.pages) <= 6:
                failures.append({'path': str(path.relative_to(ROOT)), 'rule': 'page_count'})
    manifest = json.loads((ROOT/'data/release-manifest.json').read_text())
    for item in manifest:
        path = ROOT/item['path']
        if not path.exists() or digest(path) != item['sha256'] or path.stat().st_size != item['bytes']:
            failures.append({'path': item['path'], 'rule': 'output_hash'})
    page = ROOT/'docs/site/index.html'
    parser = PageLinks()
    parser.feed(page.read_text())
    for link in parser.links:
        url = urlsplit(link)
        if url.scheme or url.netloc:
            failures.append({'path': 'docs/site/index.html', 'rule': 'external_page_resource'})
        elif url.path and not (page.parent/unquote(url.path)).exists():
            failures.append({'path': url.path, 'rule': 'broken_page_link'})
    for failure in parser.failures:
        failures.append({'path': 'docs/site/index.html', 'rule': failure})
    frozen = digest(ROOT/'PREREGISTRATION.md') == 'cabc7ecffdd2e11246c8ab7b08b3103b09819f3fde1bcae87ab9cb649330a179'
    if not frozen:
        failures.append({'path': 'PREREGISTRATION.md', 'rule': 'changed'})
    for public_path in ('README.md', 'DATA.md', 'docs/TECHNICAL_NOTE.md', 'docs/site/index.html'):
        if re.search(r'\b(?:brief|Resume\s+\d|breakthrough|owner|Director|CEO|for review)\b', (ROOT/public_path).read_text()):
            failures.append({'path': public_path, 'rule': 'internal_wording'})
    receipt = {'tracked_files_scanned': sum(bool(p) for p in tracked), 'rules': list(patterns),
        'output_hashes_checked': len(manifest), 'site_links_checked': len(parser.links),
        'preregistration_unchanged': frozen, 'failures': failures, 'exit_code': int(bool(failures))}
    folder = ROOT/'data/checks'
    folder.mkdir(exist_ok=True)
    (folder/'release-scan.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))
    raise SystemExit(receipt['exit_code'])


if __name__ == '__main__':
    main()

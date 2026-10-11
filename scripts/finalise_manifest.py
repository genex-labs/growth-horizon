# SPDX-License-Identifier: Apache-2.0
"""Summarise acquired inputs once all phase-1 operations have completed."""
import json

from scripts.acquire import ROOT, digest


def main() -> None:
    path = ROOT / 'data/source-manifest.json'
    manifest = json.loads(path.read_text())
    page_urls = {
        'carbon.html': 'https://www.biorxiv.org/content/10.64898/2026.08.06.743333v1',
        'plos.html': 'https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011705',
        'calpred.html': 'https://www.nature.com/articles/s41588-024-01792-w',
        'koblitz.html': 'https://www.nature.com/articles/s42003-025-08313-3',
        'instructions.json': 'https://raw.githubusercontent.com/cultivarium/GenomeSPOT/v1.0.0/models/instructions.json',
        'run_model_selection.py': 'https://raw.githubusercontent.com/cultivarium/GenomeSPOT/v1.0.0/genome_spot/model_training/run_model_selection.py',
        'b4-readme.json': 'https://api.github.com/repos/LeibnizDSMZ/bacdive-AI/readme',
        'b4-tree.json': 'https://api.github.com/repos/LeibnizDSMZ/bacdive-AI/git/trees/main?recursive=1',
        'gtdb232-index.html': 'https://data.gtdb.ecogenomic.org/releases/release232/232.0/',
        'resume3-ar-metadata.partial.tsv.gz': 'https://data.gtdb.ecogenomic.org/releases/release232/232.0/ar53_metadata_r232.tsv.gz',
    }
    indexed = {r['path'] for r in manifest['records']}
    for folder in ('data/raw/source-audit', 'data/raw/verification', 'data/raw/gtdb',
                   'data/raw/transfer-parts'):
        for file in sorted((ROOT / folder).rglob('*')):
            relative = str(file.relative_to(ROOT))
            if not file.is_file() or relative in indexed or '__pycache__' in relative:
                continue
            url = page_urls.get(file.name)
            if 'transfer-parts' in relative and file.suffix == '.bin':
                filename = file.parent.name
                gtdb = next((r for r in manifest['records'] if r['path'].endswith(filename)), None)
                url = gtdb['url'] if gtdb else None
            manifest['records'].append({'path': relative, 'url': url,
                                       'bytes': file.stat().st_size, 'sha256': digest(file),
                                       'kind': ('incomplete_download_preserved_as_evidence' if '.partial.' in relative
                                                else 'source_audit_evidence' if url else 'local_acquisition_receipt')})
            indexed.add(relative)
    population = json.loads((ROOT / 'data/gtdb-derived/population-summary.json').read_text())
    verification = json.loads((ROOT / 'data/feature-verification.json').read_text())
    audit_path = ROOT / 'data/gtdb-derived/label-audit.json'
    audit = json.loads(audit_path.read_text())
    audit['status'] = 'primary_populations_established'
    audit['analysis_exclusions'] = population['traits']
    audit['analysis_exclusions_reason'] = 'Every disposition recorded in counts_by_reason'
    audit_path.write_text(json.dumps(audit, indent=2) + '\n')
    manifest['status'] = 'phase1_complete_outer_unscored'
    manifest['gtdb_release'] = 'R11-RS232 (232.0)'
    manifest['proteome_bytes'] = verification['download_bytes']
    manifest['feature_verification'] = verification
    for trait, record in population['traits'].items():
        original = manifest['trait_counts'][trait]
        original['analysis_usable'] = record['usable']
        original['excluded'] = sum(n for r, n in record['counts_by_reason'].items()
                                   if r not in ('usable', 'missing_label'))
        original['reason'] = 'See counts_by_reason for every analysis disposition'
        original['counts_by_reason'] = record['counts_by_reason']
    manifest['records'].sort(key=lambda r: r['path'])
    path.write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    main()

# SPDX-License-Identifier: Apache-2.0
"""Build pinned public tables, standard figures, note and static project page."""
from __future__ import annotations

import csv
import html
import json
import os
from pathlib import Path
import re
from typing import Any

os.environ.setdefault('MPLCONFIGDIR', str(Path.cwd()/'work-tmp.noindex/plot-config'))
import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_LEFT  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import inch  # noqa: E402
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
                               Table, TableStyle, Image)  # noqa: E402

from growth_horizon.folds import RANKS  # noqa: E402
from growth_horizon.population import TRAITS  # noqa: E402
from growth_horizon.scoring import RESULTS, write_json  # noqa: E402
from scripts.acquire import ROOT, digest  # noqa: E402

LABELS = {'temperature_optimum': 'Temperature', 'oxygen': 'Oxygen',
          'salinity_optimum': 'Salinity', 'ph_optimum': 'pH'}
PUBLIC = 'data/gtdb-derived/results/public-results.tsv'
FIG = ROOT/'data/gtdb-derived/figures'
REFERENCES = '''Boger, R. S., Chithrananda, S., Angelopoulos, A. N., Yoon, P. H., Jordan, M. I. and Doudna, J. A. (2025). Functional protein mining with conformal guarantees. Nature Communications 16, 85. doi 10.1038/s41467-024-55676-y.

Fannjiang, C., Bates, S., Angelopoulos, A. N., Listgarten, J. and Jordan, M. I. (2022). Conformal prediction under feedback covariate shift for biomolecular design. PNAS 119(43), e2204569119. doi 10.1073/pnas.2204569119.

Barber, R. F., Candes, E. J., Ramdas, A. and Tibshirani, R. J. (2023). Conformal prediction beyond exchangeability. The Annals of Statistics 51(2), 816 to 845. doi 10.1214/23-AOS2276.

Vovk, V. (2013). Conditional validity of inductive conformal predictors. Machine Learning 92, 349 to 376. doi 10.1007/s10994-013-5355-6.

Barber, R. F., Candes, E. J., Ramdas, A. and Tibshirani, R. J. (2021). Predictive inference with the jackknife+. The Annals of Statistics 49(1), 486 to 507. doi 10.1214/20-AOS1965.

Romano, Y., Sesia, M. and Candes, E. J. (2020). Classification with Valid and Adaptive Coverage. arXiv 2006.02544v1, Algorithm 2, equations (5), (7) and (11).

Barnum and colleagues (2024). Predicting microbial growth conditions from amino acid composition. bioRxiv. doi 10.1101/2024.03.22.586313.

The references above were checked against publisher pages or DOI-deposited bibliography. The PNAS publisher page was read publicly, while the local request returned an access refusal. The Annals publisher HTML was not treated as proof of full-text access. Source URLs, dates and checksums are in data/paper-source-checks.json and data/classification-rule-check.json. No access challenge was passed.'''


class PublicTable:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.lines: dict[str, int] = {}

    def add(self, key: str, value: Any, source: str, locator: str) -> None:
        self.lines[key] = len(self.rows)+2
        self.rows.append({'id': key, 'value': json.dumps(value, ensure_ascii=True, allow_nan=False),
                          'source': source, 'locator': locator})

    def cite(self, key: str, base: str = '') -> str:
        return f'[{PUBLIC}:L{self.lines[key]}]({base}{PUBLIC})'

    def save(self) -> None:
        with (ROOT/PUBLIC).open('w') as stream:
            writer = csv.DictWriter(stream, ['id', 'value', 'source', 'locator'], delimiter='\t', lineterminator='\n')
            writer.writeheader()
            writer.writerows(self.rows)


def number(value: Any, percent: bool = False) -> str:
    if value is None:
        return 'unsupported'
    return f'{value*100:.2f}%' if percent else f'{value:.4f}'


def interval(record: Any, percent: bool = False) -> str:
    v, ci = record['value'], record['interval']
    return number(v, percent)+(f' [{number(ci[0], percent)}, {number(ci[1], percent)}]' if ci else ' [uncertainty unavailable]')


def save_figure(fig: Any, name: str) -> None:
    svg = FIG/f'{name}.svg'
    fig.savefig(svg, metadata={'Date': None}, bbox_inches='tight')
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    fig.savefig(FIG/f'{name}.png', dpi=160, metadata={'Software': 'Growth Horizon'}, bbox_inches='tight')
    plt.close(fig)


def build_figures(records: Any, measure: Any) -> None:
    FIG.mkdir(exist_ok=True)
    plt.rcParams.update({'svg.hashsalt': 'growth-horizon', 'font.size': 9,
                        'axes.spines.top': False, 'axes.spines.right': False})
    for rank in ('family', 'order'):
        fig, axes = plt.subplots(4, 2, figsize=(12, 11), gridspec_kw={'width_ratios': [3, 1]})
        for row, trait in enumerate(TRAITS):
            cells = records[trait][rank]['methods']['method']['fold_bins']
            ax, abst = axes[row]
            valid = [c for c in cells if c['metrics']['coverage']['interval']]
            x: Any = np.arange(len(valid))
            vals = np.array([c['metrics']['coverage']['value'] for c in valid])
            low = np.array([c['metrics']['coverage']['interval'][0] for c in valid])
            high = np.array([c['metrics']['coverage']['interval'][1] for c in valid])
            ax.errorbar(x, vals, yerr=[vals-low, high-vals], fmt='o', ms=3, color='#176b75', capsize=2)
            ax.axhline(.9, color='#b34519', ls='--', label='nominal')
            ax.axhline(.87, color='#777777', ls=':', label='cell criterion')
            ax.set(ylim=(.2, 1.02), ylabel=LABELS[trait]+' coverage',
                   xticks=x, xticklabels=[f"{c['fold']}.{c['bin']}" for c in valid])
            ax.tick_params(axis='x', labelsize=6)
            abst.barh(x, [c['metrics']['coverage']['abstention_rate'] for c in valid], color='#b34519')
            abst.set(xlim=(0, 1), yticks=[], xlabel='Abstention rate')
        axes[-1, 0].set_xlabel('Outer fold . merged calibration bin, shown separately')
        fig.suptitle(rank.title()+' holdout: supported coverage and paired abstentions\n95% intervals resample held-out taxa; unsupported cells are omitted')
        fig.tight_layout(rect=(0, 0, 1, .94))
        save_figure(fig, 'coverage-'+rank)
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    labels, entries = [], []
    for trait in TRAITS:
        for rank in ('family', 'order'):
            m = records[trait][rank]['methods']['method']
            labels.append(LABELS[trait]+' / '+rank)
            entries.append([m['overall']['coverage'], m['overall']['taxon_weighted_coverage'],
                            m['mean_fit_distance']['coverage']])
    for j, (label, colour) in enumerate([('Genome weighted', '#176b75'), ('Taxon weighted', '#5f4778'), ('Mean fit distance', '#b34519')]):
        x = np.arange(len(entries))+(j-1)*.18
        vals = np.array([e[j]['value'] for e in entries])
        ci = np.array([e[j]['interval'] for e in entries])
        axes[0].errorbar(x, vals, yerr=[vals-ci[:, 0], ci[:, 1]-vals], fmt='o', color=colour, capsize=3, label=label)
        axes[1].plot(x, [e[j]['abstention_rate'] for e in entries], 'o', color=colour)
    axes[0].axhline(.9, ls='--', color='#777777')
    axes[0].set(ylabel='Supported coverage', ylim=(.75, 1))
    axes[0].legend()
    axes[1].set(ylabel='Abstention rate', ylim=(0, 1), xticks=np.arange(len(labels)), xticklabels=labels)
    axes[1].tick_params(axis='x', rotation=20)
    fig.suptitle('Secondary coverage checks, with abstentions beside the estimates')
    fig.tight_layout()
    save_figure(fig, 'secondary-coverage')
    fig, axes = plt.subplots(2, 2, figsize=(10, 7))
    for trait, ax in zip(TRAITS, axes.flat, strict=True):
        for m, colour in [('B1', '#5f4778'), ('method', '#176b75')]:
            bins = records[trait]['order']['horizons'][m]['bins']
            vals = np.array([c['improvement_over_B2']['value'] for c in bins])
            ci = np.array([c['improvement_over_B2']['interval'] for c in bins])
            x = np.arange(len(bins))+(.08 if m == 'method' else -.08)
            ax.errorbar(x, vals, yerr=[vals-ci[:, 0], ci[:, 1]-vals], fmt='o-', color=colour, capsize=3, label=m)
        ax.axhline(0, color='#777777', ls='--')
        ax.set(title=LABELS[trait], xlabel='Common horizon bin (zero based)', ylabel='Improvement over B2')
        ax.legend()
    fig.suptitle('Order holdout: value over the nearest labelled relative')
    fig.tight_layout(rect=(0, 0, 1, .95))
    save_figure(fig, 'nearest-relative-profile')
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    for trait, ax in zip(TRAITS, axes.flat, strict=True):
        for m, colour in [('B1', '#5f4778'), ('method', '#176b75')]:
            primary = [records[trait][r]['methods'][m]['overall']['error']['value'] for r in RANKS]
            refit = [records[trait][r]['methods'][m]['ten_column_refit']['error']['value'] for r in RANKS]
            ax.plot(RANKS, primary, 'o-', color=colour, label=m+' primary')
            ax.plot(RANKS, refit, 'x', color=colour, ms=9, label=m+' ten-column refit')
        ax.set(title=LABELS[trait], ylabel='Error')
        ax.tick_params(axis='x', labelsize=7)
        ax.legend(fontsize=7)
    fig.suptitle('Explicit descriptor-removal refits: identical point errors')
    fig.tight_layout(rect=(0, 0, 1, .94))
    save_figure(fig, 'ten-column-refit')
    fig, axes = plt.subplots(4, 3, figsize=(12, 11))
    for i, trait in enumerate(TRAITS):
        for strategy, colour in [('widest', '#176b75'), ('farthest', '#5f4778'), ('random', '#b34519')]:
            folds = measure['traits'][trait][strategy]['folds']
            for j, key in enumerate(('mean_width', 'error', 'abstention_rate')):
                data = np.array([[p[key] if p[key] is not None else np.nan for p in f['points']] for f in folds])
                axes[i, j].plot(measure['budgets'], np.nanmean(data, axis=0), 'o-', ms=3, color=colour, label=strategy)
                axes[i, j].set_ylabel(LABELS[trait]+' '+key.replace('_', ' '))
                if i == 3:
                    axes[i, j].set_xlabel('Maximum acquired organisms')
                if i == 0:
                    axes[i, j].legend(fontsize=7)
    fig.suptitle('Measure next: fold means on remaining far organisms\nEvaluation populations change after each whole-order acquisition')
    fig.tight_layout(rect=(0, 0, 1, .94))
    save_figure(fig, 'measure-next')


def pdf_note(pages: list[str], tables: dict[str, list[list[str]]]) -> None:
    style = ParagraphStyle('body', fontName='Helvetica', fontSize=9.0, leading=11.5,
        spaceAfter=7, textColor=colors.HexColor('#18323c'), alignment=TA_LEFT)
    heading = ParagraphStyle('heading', parent=style, fontSize=18, leading=22, spaceAfter=16)
    sub = ParagraphStyle('sub', parent=style, fontSize=12, leading=16, spaceAfter=10)
    small = ParagraphStyle('small', parent=style, fontSize=7.2, leading=9)
    story: list[Any] = []
    for i, page in enumerate(pages):
        if i:
            story.append(PageBreak())
        for block in page.split('\n\n'):
            if block.startswith('{{table:'):
                key = block.removeprefix('{{table:').removesuffix('}}')
                cells = [[Paragraph(html.escape(c), small) for c in row] for row in tables[key]]
                table = Table(cells, colWidths=[6.7*inch/len(cells[0])]*len(cells[0]), repeatRows=1)
                table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e4eeee')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LINEBELOW', (0, 0), (-1, 0), .5, colors.HexColor('#176b75'))]))
                story.extend([table, Spacer(1, 10)])
            elif block.startswith('{{figure:'):
                name = block.removeprefix('{{figure:').removesuffix('}}')
                image = Image(str(FIG/(name+'.png')))
                width, height = image.imageWidth, image.imageHeight
                image.drawWidth = 6.4*inch
                image.drawHeight = height*image.drawWidth/width
                story.append(image)
            else:
                text = re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'\1', block)
                text = re.sub(r'data/gtdb-derived/results/public-results.tsv:L(\d+)', r'TSV L\1', text)
                text = text.replace('`', '').replace('*', '')
                selected = heading if text.startswith('# ') else sub if text.startswith('## ') else style
                story.append(Paragraph(html.escape(text.lstrip('# ')).replace('\n', '<br/>'), selected))
    def footer(canvas: Any, doc: Any) -> None:
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#506b74'))
        canvas.drawString(42, 25, 'GeneX Labs Inc. | Growth Horizon | empirical benchmark')
        canvas.drawRightString(570, 25, str(doc.page))
    doc = SimpleDocTemplate(str(ROOT/'docs/TECHNICAL_NOTE.pdf'), pagesize=(612, 792),
        leftMargin=42, rightMargin=42, topMargin=40, bottomMargin=42,
        title='Growth Horizon: methods and empirical evaluation', author='GeneX Labs Inc.', invariant=1)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    records = {t: {r: json.loads((RESULTS/f'{t}-{r}.json').read_text()) for r in RANKS} for t in TRAITS}
    target = json.loads((RESULTS/'targets.json').read_text())
    measure = json.loads((RESULTS/'measure-next.json').read_text())
    table = PublicTable()
    for t in TRAITS:
        for rank in RANKS:
            for m, record in records[t][rank]['methods'].items():
                for metric in ('overall', 'naive', 'naive_far', 'mean_fit_distance', 'ten_column_refit'):
                    if metric in record:
                        table.add(f'{t}/{rank}/{m}/{metric}', record[metric], f'data/gtdb-derived/results/{t}-{rank}.json', f'methods.{m}.{metric}')
            for m, h in records[t][rank]['horizons'].items():
                table.add(f'{t}/{rank}/{m}/horizon', h, f'data/gtdb-derived/results/{t}-{rank}.json', f'horizons.{m}')
            table.add(f'{t}/{rank}/accuracy', records[t][rank]['accuracy_comparison'], f'data/gtdb-derived/results/{t}-{rank}.json', 'accuracy_comparison')
    for key, value in target.items():
        table.add(key, value, 'data/gtdb-derived/results/targets.json', key)
    for t in TRAITS:
        for s in ('widest', 'farthest', 'random'):
            table.add(f'{t}/measure/{s}', measure['traits'][t][s], 'data/gtdb-derived/results/measure-next.json', f'traits.{t}.{s}')
    table.add('protocol', {'coverage': .9, 'bin_floor': .87, 'minimum_taxa': 50, 'strong_support': 100,
        'bootstrap_replicates': 2000, 'bootstrap_seed': 20261011, 'folds': 5, 'outer_folds': 120,
        'width_limits': {'temperature': 20, 'pH': 3, 'salinity': 8}, 'measure_budgets': measure['budgets'],
        'ten_columns': 10}, 'PREREGISTRATION.md', 'Folds, estimators, metrics and targets; docs/SCORING_PROTOCOL.md')
    table.add('population', json.loads((ROOT/'data/gtdb-derived/population-summary.json').read_text()),
              'data/gtdb-derived/population-summary.json', 'traits')
    table.add('freezes', {'v1': '22bc8605', 'v1_time': '2026-10-11 04:30:02 PT',
        'v2_initial': '839b22f', 'v2_initial_time': '2026-10-11 05:54:49 PT',
        'v2_normalisation': '3b1f6d2', 'v2_normalisation_time': '2026-10-11 07:04:00 PT',
        'v2_final': '54d803ce', 'v2_final_time': '2026-10-11 07:46:14 PT',
        'preregistration_sha256': digest(ROOT/'PREREGISTRATION.md')}, 'CHANGELOG.md', 'Freeze chronology')
    table.save()
    figure_rows = []
    for t in TRAITS:
        for rank in RANKS:
            for m, record in records[t][rank]['methods'].items():
                for kind in ('fold_bins', 'secondary_fold_bins'):
                    for cell in record[kind]:
                        figure_rows.append({'trait': t, 'rank': rank, 'method': m, 'kind': kind, **cell})
    write_json(RESULTS/'figure-data.json', figure_rows)
    build_figures(records, measure)
    order_rows = [['Trait', 'B1 error [95% interval]', 'Proposed error [95% interval]', 'Paired reduction [95% interval]']]
    coverage_rows = [['Trait / rank', 'Pooled coverage [95% interval]', 'Accepted coverage [95% interval]', 'Abstention', 'Mean width or cardinality', 'Accepted mean width or cardinality']]
    horizon_rows = [['Trait', 'Proposed horizon', 'B1 horizon', 'Proposed ordinal interval', 'B1 ordinal interval']]
    measure_rows = [['Trait / strategy', 'Mean error AUC', 'Mean width or cardinality AUC']]
    md_order, md_coverage, md_horizon, md_measure = [], [], [], []
    for t in TRAITS:
        r = records[t]['order']
        cells = [LABELS[t], interval(r['methods']['B1']['overall']['error']),
                 interval(r['methods']['method']['overall']['error']), interval(r['accuracy_comparison'])]
        order_rows.append(cells)
        md_order.append('| '+' | '.join(cells)+' | '+table.cite(f'{t}/order/B1/overall')+'; '+table.cite(f'{t}/order/method/overall')+'; '+table.cite(f'{t}/order/accuracy')+' |')
        for rank in ('family', 'order'):
            c = records[t][rank]['methods']['method']['overall']
            cells = [LABELS[t]+' / '+rank, interval(c['coverage'], True), interval(c['coverage_accepted'], True), number(c['abstention_rate'], True), number(c['mean_size']), number(c['mean_size_accepted'])]
            coverage_rows.append(cells)
            md_coverage.append('| '+' | '.join(cells)+' | '+table.cite(f'{t}/{rank}/method/overall')+' |')
        hs = r['horizons']
        def htext(h: Any) -> str:
            return ('Beyond observed range' if h['state'] == 'right_censored' else 'Unidentified' if h['state'] == 'unidentified' else f"Bin {h['first_failing_bin']} ({h['distance_range'][0]:.4f} to "+(f"{h['distance_range'][1]:.4f})" if h['distance_range'][1] is not None else 'observed maximum)'))
        cells = [LABELS[t], htext(hs['method']), htext(hs['B1']),
                 str(hs['method']['ordinal_interval']), str(hs['B1']['ordinal_interval'])]
        horizon_rows.append(cells)
        md_horizon.append('| '+' | '.join(cells)+' | '+table.cite(f'{t}/order/method/horizon')+'; '+table.cite(f'{t}/order/B1/horizon')+' |')
        for strategy in ('widest', 'farthest', 'random'):
            acquisition = measure['traits'][t][strategy]
            cells = [LABELS[t]+' / '+strategy, number(acquisition['mean_error_auc']),
                     number(acquisition['mean_width_auc'])]
            measure_rows.append(cells)
            md_measure.append('| '+' | '.join(cells)+' | '+table.cite(f'{t}/measure/{strategy}')+' |')
    def md_table(headers: list[str], rows: list[str]) -> str:
        return '| '+' | '.join(headers+['Pinned source line'])+' |\n| '+' | '.join(['---']*(len(headers)+1))+' |\n'+'\n'.join(rows)
    order_md = md_table(order_rows[0], md_order)
    coverage_md = md_table(coverage_rows[0], md_coverage)
    horizon_md = md_table(horizon_rows[0], md_horizon)
    measure_md = md_table(measure_rows[0], md_measure)
    literature_text = 'In our literature check of 2026-10-11, we did not find a report of calibrated prediction intervals for genome-based prediction of microbial growth conditions that gives coverage separately for bins of phylogenetic distance to the training set, under whole-family or whole-order hold-out. The closest work we found reports interval coverage across phylogenetic-distance cutoffs for a different microbial trait, 16S rRNA gene copy number (Gao and Wu, 2023), and false discovery control within sequence-identity groups for enzyme function prediction (Ding, Luo and Luo, 2024). This is a bounded search finding, not a claim that no such work exists.'
    target3_text = ('Target 3 (publication): pending external publication; horizon estimates for every '
                    'trait are complete in the package.')
    statuses = '\n'.join('- '+target3_text+' '+table.cite('target3') if i == 3 else
        f"- Target {i}{' (report any B1 win)' if i == 4 else ''}: {'passed' if target['target'+str(i)]['passed'] else 'failed'}. {table.cite('target'+str(i))}" for i in range(1, 5))
    predictor_text = ("B0 is the training-side mean or majority class; B1 retrains GenomeSPOT v1.0.0's "
        "published specification on these folds (iteration cap raised, upstream balancing not used; "
        "docs/baselines.md); B2 copies the nearest labelled relative; the proposed predictor chooses "
        "between B1 and a regularised alternative by inner tuning.")
    cells = target['target1']['cells']
    failing_bins = [f"{LABELS[c['trait']].lower()}/{c['rank']} fold {b['fold']} bin {b['bin']}"
                    for c in cells for b in c['failing_bins']]
    naive_passes = [c for c in cells if all(c['naive_far'][b]['passed'] for b in ('B1', 'B2'))]
    pooled = [c['pooled_coverage'] for c in cells]
    words = {1: 'one', 2: 'two', 8: 'eight'}
    cell_count = len(cells)
    pooled_count = sum(c['interval'] is not None and c['interval'][1] >= .9 for c in pooled)
    pooled_scope = 'all ' if pooled_count == cell_count else ''
    failed_parts = sum((bool(failing_bins), pooled_count != cell_count, len(naive_passes) != cell_count))
    target1_text = (f"Target 1 failed on {words.get(failed_parts, str(failed_parts))} of its three parts. "
        'The pooled 95% coverage interval reached 90% '
        f"in {pooled_scope}{words.get(pooled_count, str(pooled_count))} trait and rank cells "
        f"(point estimates {number(min(c['value'] for c in pooled), True)} to "
        f"{number(max(c['value'] for c in pooled), True)}). "
        f"{words.get(len(failing_bins), str(len(failing_bins))).title()} supported bins had intervals wholly below 87% "
        f"({'; '.join(failing_bins)}). The naive far-bin condition "
        f"held in {len(naive_passes)} of {cell_count} cells, "
        +', '.join(f"{LABELS[c['trait']].lower()}/{c['rank']}" for c in naive_passes)
        +', for both B1 and B2. '
        f'So in {cell_count-len(naive_passes)} of {cell_count} cells this benchmark does not show that naive '
        'intervals under-cover in the far bin, or that distance conditioning is needed there. '
        'Elsewhere at least one naive '
        'comparator covered more than 80%, or had an upper limit of 90% or more, in the far bin. '
        +table.cite('target1')+'; '+table.cite('protocol'))
    other_cells = [(t, rank, records[t][rank]['accuracy_comparison'])
                   for t in TRAITS for rank in RANKS if rank != 'order']
    descriptive_wins = [(t, rank, c) for t, rank, c in other_cells
                        if c['relative_reduction'] is not None and c['relative_reduction'] >= .1
                        and c['interval'] is not None and c['interval'][0] > 0]
    win_names = [LABELS[t].lower()+(' on the random split, the optimistic reference' if rank == 'random'
                                  else ' at '+rank) for t, rank, _ in descriptive_wins]
    descriptive_text = (f'Outside the target, {len(descriptive_wins)} of the {len(other_cells)} other trait '
        'and rank cells meet the 10% bar with an interval excluding zero: '
        +' and '.join(win_names)+f'. These {len(other_cells)} comparisons are not adjusted for multiplicity '
        'and are descriptive only.')
    descriptive_values = ('The relative reductions are '
        +' and '.join(f"{c['relative_reduction']*100:.1f}% for {LABELS[t].lower()} "
                     +('on the random split' if rank == 'random' else 'at '+rank)
                     for t, rank, c in descriptive_wins)+'. '
        +'; '.join(table.cite(t+'/'+rank+'/accuracy') for t, rank, _ in descriptive_wins))
    b1_scope = ('Target 4 is a reporting duty whose B1 win list is computed from the order-rank records. '
        'B1 has lower point error than the proposed '
        'predictor for order-holdout temperature and salinity; neither paired interval excludes zero. '
        +table.cite('target4')+'; '+table.cite('temperature_optimum/order/accuracy')+'; '
        +table.cite('salinity_optimum/order/accuracy')+' B1 also has lower point error for temperature '
        'at genus, phylum and the random split, salinity at family, class and phylum, and pH at phylum; '
        'none of those paired intervals excludes zero. Salinity at genus is identical. '
        +'; '.join(table.cite(t+'/'+rank+'/accuracy') for t, rank in [
            ('temperature_optimum', 'genus'), ('temperature_optimum', 'phylum'),
            ('temperature_optimum', 'random'), ('salinity_optimum', 'family'),
            ('salinity_optimum', 'class'), ('salinity_optimum', 'phylum'),
            ('ph_optimum', 'phylum'), ('salinity_optimum', 'genus')]))
    b0_limits = ('The training-mean baseline B0 has the lowest point error for temperature at '
        'phylum and for pH at class and phylum, limiting the value of genome-based predictions '
        'at these ranks. '+ '; '.join(table.cite(t+'/'+rank+'/'+m+'/overall') for t, rank in [
            ('temperature_optimum', 'phylum'), ('ph_optimum', 'class'), ('ph_optimum', 'phylum')]
            for m in ('B0', 'B1', 'B2', 'B3', 'method')))
    width_text = ('Random selection has the lowest mean width AUC for temperature, salinity and pH. '
        'Widest-first has the lowest mean set-cardinality AUC only for oxygen. '
        +'; '.join(table.cite(t+'/measure/'+strategy) for t in TRAITS
            for strategy in ('widest', 'farthest', 'random')))
    accepted_text = 'Accepted-item coverage has no nominal guarantee. Accepted items exclude abstentions and unsupported rows.'
    def site_prose(text: str) -> str:
        return re.sub(r'\[([^]]+)\]\(([^)]+)\)',
            lambda m: '<a href="../../'+html.escape(m[2], quote=True)+'">'+html.escape(m[1])+'</a>', text)
    preface = f'''# Growth Horizon

GeneX Labs Inc. measures how growth-condition predictions behave as microbial genomes become more distant from labelled relatives. The benchmark combines taxonomic holdout, empirical interval and prediction-set coverage and abstention, so the record shows both predictive error and how often uncertainty prevents a useful answer.

The locked calibration and accuracy targets failed. B1 has lower order-holdout error for temperature and salinity. The order-holdout accuracy target failed: it requires at least a 10% lower error than B1, with a paired interval that excludes zero, on at least two traits. These are descriptive results from the full usable labelled population; no estimator, tuning choice, cut point or target was changed after outer scoring; two reporting corrections made after the first outer number are disclosed in docs/INTEGRITY.md and change no verdict.

{statuses}

{predictor_text}

{target1_text}

{b1_scope}

## Order-holdout accuracy

Numeric error is mean absolute error in degrees C, percent NaCl or pH units. Oxygen error is one minus balanced accuracy. Positive paired reduction favours the proposed predictor. All intervals resample held-out taxa.

{order_md}

{descriptive_text}

{descriptive_values}

## Coverage and useful uncertainty

Coverage includes supported abstentions exactly when the computed interval or set contains the true label. Unsupported items are excluded from coverage and reported as abstentions. Width is in the trait's original units; oxygen is a class label with uncertainty represented by a prediction set, whose size is its cardinality. Every coverage estimate is accompanied by abstentions.

{coverage_md}

{accepted_text}

## Order-holdout horizons

This table is the order rank only. Per-rank records are the JSON files under data/gtdb-derived/results/. At class, temperature already fails in the nearest bin for both predictors. At class, pH also fails in bin 0 for both predictors, and salinity is unidentified for both predictors. At phylum, the horizons are unidentified. The B1 ordinal interval is shown beside the proposed interval because the two intervals are not the same for every trait. Horizon bins use the frozen common cuts. The first failure compares with a training-side constant and checks whether most predictions abstain. Zero-based bin ordinals and their exploratory bootstrap intervals are discrete summaries. A right-censored horizon extends beyond the observed bins; it is not an infinite or universal threshold.

{horizon_md}

## Exploratory measurement selection

The retrospective measurement experiment acquires whole orders under the stated organism budget, refits and recalibrates, and measures error and width on the remaining far organisms. Evaluation populations change as orders are acquired. A smaller area under the budget curve is preferable; the estimates below average the fold curves and have no confirmatory target.

{measure_md}

{width_text}

## Limits and sources

{b0_limits}

Exchangeability within distance bins is assumed, not demonstrated. Grouped unequal-size folds and distance conditioning do not inherit a demonstrated finite-sample guarantee from unconditioned CV+ results. Labels are table-level experimental records exported through GenomeSPOT, with residual per-value provenance uncertainty. Correlated genomes, small distant taxa, changing annotations and unsupported ranks limit generalisation. Accepted-item coverage has no nominal guarantee.

{literature_text} Closest work includes Gao and Wu (2023) on distance-cutoff coverage for 16S copy number and Ding, Luo and Luo (2024) on sequence-identity-group false discovery control. Adjacent work includes GenomeSPOT, Bac2Feature, CalPred, Boger and colleagues on conformal protein retrieval, Fannjiang and colleagues on feedback covariate shift, and Barber and colleagues on nonexchangeability. See [related work](docs/related-work.md), [technical note](docs/TECHNICAL_NOTE.md) and [data attribution](DATA.md).

Secondary figures report taxon-weighted coverage, the mean of the five fit-specific distances, and explicit refits after removing the ten mean_zc and mean_nh2o columns, whose recomputed values differed from the published table (DATA.md). No frozen feature list uses them, so this refit cannot change any prediction; it is reported for completeness. No target uses these secondary analyses. {table.cite('protocol')}

## Rebuild and reuse

Offline checks read the committed aggregates. They do not download inputs, refit estimators or rescore folds:

```sh
uv run --project release --frozen python -m scripts.check_release
uv run --frozen pytest --basetemp=work-tmp.noindex/pytest-fixtures
```

That scan uses the rendering project because it reads the PDF. It compares each path in [data/release-manifest.json](data/release-manifest.json) with its recorded size and SHA-256, then writes `data/checks/release-scan.json`. The fixture command runs the offline tests in the analysis environment.

Full recomputation is a different command. With Python 3.13 and the pinned analysis and rendering dependencies, it acquires missing official inputs, verifies cached source hashes, reconstructs the frozen analysis, scores all outer folds, runs measurement selection and regenerates every public table, figure, note and page:

```sh
uv run --project release --frozen python -m scripts.release
```

That command needs a network connection or a checksum-verified copy of the raw inputs. It is not an offline check. `data/raw/` and `data/gtdb-derived/local/` (fitted trees and individual predictions) are not redistributed. The pinned replay inputs under `data/raw/labels/`, `data/raw/verification/upstream/`, `data/raw/verification/sequences/` and `data/raw/gtdb/` total 254,404,224 bytes in `data/source-manifest.json`. Acquisition stops if free space on `/` is below 25 GB. Phase 1 rebuild without outer scoring is `uv run --frozen python -m scripts.rebuild`. That command leaves outer intervals and oxygen sets uncomputed. Outer scoring runs only in `scripts.release`.

`uv.lock` allows any Python 3.13. The frozen numbers were produced with Python 3.13.15. A fresh export used Python 3.13.12 with the same lock.

Scratch is confined to ignored `work-tmp.noindex/`. Raw labels, sequences, fitted estimators and individual predictions remain untracked. Aggregate GTDB-derived analyses and figures are under CC BY-SA 4.0; BacDive labels are attributed under CC BY 4.0. Code is Apache-2.0, with GenomeSPOT's MIT notice retained. DATA.md records the commercial-contact condition and Cali Fund guidance.

Every result shown above cites a repository-relative TSV line. [Output hashes](data/release-manifest.json) pin that table and its underlying JSON records. [Complete results](docs/RESULTS.md), [figures](data/gtdb-derived/figures), [PDF note](docs/TECHNICAL_NOTE.pdf), [static project page](docs/site/index.html) and [reconstruction details](docs/reproducibility.md) provide the rest of the package. The original [pre-registration](PREREGISTRATION.md) is frozen by local git commit; not registered externally; outcomes are in [RESULTS.md](docs/RESULTS.md) and [current scoring status](docs/PHASE2_STATUS.md). Freeze commits are in [CHANGELOG.md](CHANGELOG.md).

Research prototype on this labelled GTDB-mapped table; not tested on prospective cultures, on organisms outside the table, or for clinical or production use.

Offline fixture checks:

```sh
uv run --frozen pytest --basetemp=work-tmp.noindex/pytest-fixtures
uv run --frozen ruff check scripts growth_horizon tests
uv run --frozen mypy scripts growth_horizon tests
```
'''
    (ROOT/'README.md').write_text(preface)
    chronology = 'The two earlier v2-era freezes were 839b22f (2026-10-11 05:54:49 PT, amendment C and v2) and 3b1f6d2 (2026-10-11 07:04:00 PT, re-freeze after normalising calibration artefacts); both preceded any outer-fold number. '+table.cite('freezes')
    pages = [f'''# Growth Horizon: methods and empirical evaluation

GeneX Labs Inc. | Research prototype on this labelled GTDB-mapped table; not tested on prospective cultures, on organisms outside the table, or for clinical or production use.

## Question and evidence

Growth predictions can carry different information for a close relative and a distant organism. This study evaluates that distinction using the full usable growth-labelled population, the published GenomeSPOT feature table and the current GTDB reference taxonomy. It measures error, interval or set coverage, uncertainty size and abstention without presenting any laboratory result. The labels are accepted as table-level experimental records, rather than independently authenticated measurements for every value.

The locked targets fail for calibration and accuracy. A useful empirical coverage level does not itself establish a guarantee or a pass: the calibration target jointly requires each supported cell, the pooled coverage and the naive far-bin comparison. This joint criterion matters when interpreting the results.

{chronology}

## Frozen analysis

Five grouped outer folds at genus, family, order, class and phylum keep each taxon together. A random split is an optimistic reference, with species as the bootstrap cluster. Every eligible labelled assembly is included for its trait; missing labels and release-mapping exclusions are counted separately. Current usable populations contain temperature, oxygen, salinity and pH records as documented in the pinned population table. {table.cite('population')}

Distances are sums of GTDB branch lengths to the nearest training representative, with bacterial and archaeal domains separate. Nonrepresentatives map to the representative leaf. Equal distances are not split artificially. Ties choose the smallest training representative and then accession. Missing-domain sources have infinite distance and cause abstention.

Five inner calibration fits score their held-out training taxa. Calibration-bin cuts pool phenotype-free tuning-holdout distances, and adjacent bins merge by distinct-taxon union until the fixed support floor is reached. The common horizon cuts pool the corresponding distances over outer folds. No outer phenotype selects an estimator, bin or threshold. {table.cite('protocol')}

## Predictors

B0 is the outer training mean or oxygen majority class. B1 retrains the GenomeSPOT estimator specification. B2 copies the nearest labelled relative from the frozen point-fit training rows. B3 uses whole-proteome amino-acid frequencies with ridge or balanced logistic regression. The proposed predictor selects B1 or a regularised compartment-frequency alternative solely by proper-side grouped tuning. Original point fits determine all primary errors and horizons. B4 is excluded for the documented licence and annotation-input limitations.''',
    f'''# Interval scoring and locked results

Numeric intervals use CV+ order statistics across the calibration rows of the selected distance bin, preserving each scoring fit's prediction at the query. Oxygen is a class label with uncertainty represented by a prediction set. It uses randomized inverse-quantile scores and the paper's strict comparison rule with one shared query randomisation across all fits and methods. The naive comparator retains its separately fitted random-inner calibration spread.

An abstained item counts as covered exactly when its computed interval or set contains the true value; abstention rates are reported beside every coverage figure. Unsupported bins are excluded from every coverage figure. Empty oxygen prediction sets are misses. Numeric intervals may cover while exceeding the usefulness limit. No accepted-item coverage guarantee is asserted.

Coverage is nominally at the protocol level, with fixed numeric width limits and the fixed calibration-taxon support rule. Error and coverage intervals use paired held-out-taxon bootstrap draws, retaining every genome whenever its taxon is drawn. Single-taxon cells have no uncertainty estimate. {table.cite('protocol')}

## Order-holdout accuracy

{{{{table:accuracy}}}}

Numeric error is mean absolute error. Oxygen error is one minus balanced accuracy. The paired column is B1 error minus proposed error; positive values favour the proposal. Pinned sources: temperature_optimum: {table.cite('temperature_optimum/order/B1/overall')}; {table.cite('temperature_optimum/order/method/overall')}; {table.cite('temperature_optimum/order/accuracy')}. oxygen: {table.cite('oxygen/order/B1/overall')}; {table.cite('oxygen/order/method/overall')}; {table.cite('oxygen/order/accuracy')}. salinity_optimum: {table.cite('salinity_optimum/order/B1/overall')}; {table.cite('salinity_optimum/order/method/overall')}; {table.cite('salinity_optimum/order/accuracy')}. ph_optimum: {table.cite('ph_optimum/order/B1/overall')}; {table.cite('ph_optimum/order/method/overall')}; {table.cite('ph_optimum/order/accuracy')}.

## Family and order coverage

{{{{table:coverage}}}}

Pinned coverage sources: {table.cite('temperature_optimum/family/method/overall')} {table.cite('temperature_optimum/order/method/overall')} {table.cite('oxygen/family/method/overall')} {table.cite('oxygen/order/method/overall')} {table.cite('salinity_optimum/family/method/overall')} {table.cite('salinity_optimum/order/method/overall')} {table.cite('ph_optimum/family/method/overall')} {table.cite('ph_optimum/order/method/overall')}

{accepted_text}

Unsupported phylum calibration and the unsupported salinity class bins remain visible as abstentions in the complete results. Taxon-weighted coverage provides a separate view of unequal taxon size; it changes no primary target.''',
    f'''# Target interpretation and baseline limits

{statuses}

{target1_text}

The order-holdout accuracy target fails because the required relative error reduction with a positive paired interval is not reached on the required number of traits.

## Accuracy beyond the target

{descriptive_text}

{descriptive_values} {table.cite('target2')}

{b1_scope}

{b0_limits}

## Literature finding

{literature_text}''',
    f'''# Order-holdout horizons and secondary checks

The table in this section is the order rank only. Per-rank records are the JSON files under data/gtdb-derived/results/. At class, temperature already fails in the nearest bin for both predictors. At class, pH also fails in bin 0 for both predictors, and salinity is unidentified for both predictors. At phylum, the horizons are unidentified. The B1 ordinal interval is shown beside the proposed interval because the two intervals are not the same for every trait. The horizon rule compares with B0, using the frozen common distance cuts. It is the first bin where the lower confidence limit for the improvement reaches zero or most items abstain. For oxygen, improvement is balanced accuracy minus chance. Value over B2 is reported in every bin without imposing a first-failure rule. Empty or unsupported horizon bins produce an unidentified state.

{{{{table:horizons}}}}

Pinned horizon sources: {table.cite('temperature_optimum/order/method/horizon')}; {table.cite('temperature_optimum/order/B1/horizon')} {table.cite('oxygen/order/method/horizon')}; {table.cite('oxygen/order/B1/horizon')} {table.cite('salinity_optimum/order/method/horizon')}; {table.cite('salinity_optimum/order/B1/horizon')} {table.cite('ph_optimum/order/method/horizon')}; {table.cite('ph_optimum/order/B1/horizon')}

Bin ordinals are zero based. The bootstrap repeats paired taxon draws across the bins, computes replicate gains and majority abstentions, and preserves missing and right-censored states. Its ordinal percentile interval is an exploratory uncertainty summary, not a universal continuous threshold. Censored ordinals in the upper end indicate that a replicate remained informative across the observed range. Full distance ranges and replicate fractions are in the pinned horizon records.

{{{{figure:nearest-relative-profile}}}}

## Secondary analyses

Taxon-weighted coverage counts each represented held-out taxon once, after unsupported rows are excluded. The mean-fit-distance secondary axis recomputes each query's assigned calibration bin from the mean of its five actual fitting-side distances, keeping frozen cuts and merges. Coverage and abstentions accompany both views.

The ten-column sensitivity analysis explicitly removes mean_zc and mean_nh2o in all compartments, clones the frozen B1 and proposed point specifications, and refits on the same proper training rows. None of those columns is in the frozen amino-acid-frequency feature lists, so predictions remain identical. This is a result of the specified feature lists, not evidence that the descriptors are scientifically irrelevant. The feature-recomputation discrepancy remains a provenance limitation. {table.cite('protocol')}''',
    f'''# Exploratory retrospective measurement selection and limits

The supporting experiment asks which labelled orders would be useful to acquire next, starting from each order-holdout training side. It compares widest calibrated uncertainty, farthest-first mean branch distance and seeded random order selection. Candidate labels are not consulted by selection. Acquisition is by whole order under the organism budget; orders that would exceed the remaining budget are skipped. Counts and unused budgets are recorded after every batch. {table.cite('protocol')}

Each batch refits the point predictor and its calibration fits, using the original estimator families, hyperparameters and selection choices. New inner memberships and phenotype-free distance bins use the original schedule and support rule. Calibration labels do not refit their own scoring fit. The primary locked results and fitted artefacts are never overwritten.

Far organisms are defined by their original distance beyond the last common order cut. Width, error and abstention are measured on remaining far taxa after each batch. Trapezoidal areas under the budget curve are divided by the total budget and averaged across folds. Lower values are preferable, but the sets left for evaluation differ by strategy. These retrospective comparisons have no confirmatory target.

{{{{table:measure}}}}

{width_text}

## Limits that govern interpretation

Exchangeability within fixed distance bins is assumed, not established by shared phylogeny. Unequal-size grouped folds, correlated genomes and distance-conditioned CV+ do not inherit a demonstrated finite-sample guarantee from unconditioned theory. Genome-weighted calibration can be dominated by large taxa; taxon-weighted coverage is a sensitivity check, not a replacement guarantee. Descriptive bootstrap intervals are not adjusted for multiplicity.

Table-level experimental provenance has a residual risk: the later release asset could differ from the older export in ways the matching checks did not detect. The labels do not preserve independent experimental citations for every row. Annotation changes and descriptor discrepancies are not resolved by this benchmark. The reference tree is an approximation to evolutionary relatedness; trait transfer may fail despite short distance.

Measurement selection is retrospective. It does not show that a laboratory can culture or assay the selected organisms, that records are exchangeable with a future collection, or that the strategy expands a future horizon. {target3_text} {table.cite('target3')}

Boger and colleagues provide adjacent protein-retrieval risk control. Fannjiang and colleagues examine adaptive-design covariate shift. Barber and colleagues analyse nonexchangeability, and Vovk develops conditional validity for inductive predictors. These works motivate careful calibration and boundary language; they do not prove this grouped distance-conditioned procedure valid.''',
    f'''# References and reconstruction

{REFERENCES}

## Rebuild and inspect

Offline verification reads the committed aggregates. `uv run --project release --frozen python -m scripts.check_release` compares pinned sizes and SHA-256 values and does not download or rescore. It uses the rendering project because it reads the PDF. The fixture command is `uv run --frozen pytest --basetemp=work-tmp.noindex/pytest-fixtures`.

Full recomputation is separate. It reconstructs the frozen source and fitted analysis, scores every eligible outer fold, runs the retrospective acquisition experiment and generates all aggregate tables, figures, this note and the static HTML page:

`uv run --project release --frozen python -m scripts.release`

That command needs a network connection or a checksum-verified raw cache. `data/raw/` and `data/gtdb-derived/local/` are not redistributed. The pinned replay inputs under `data/raw/labels/`, `data/raw/verification/upstream/`, `data/raw/verification/sequences/` and `data/raw/gtdb/` total 254,404,224 bytes. Acquisition stops if free space on `/` is below 25 GB. `uv run --frozen python -m scripts.rebuild` is phase 1 only and leaves outer intervals and oxygen sets uncomputed.

Both dependency locks are pinned separately so rendering dependencies do not alter the frozen analysis lock. `uv.lock` allows any Python 3.13. The frozen numbers used Python 3.13.15, and a fresh export used Python 3.13.12 with the same lock. The scientific data live under data/gtdb-derived with their separate CC BY-SA terms. Code is Apache-2.0; GenomeSPOT's MIT notice is retained. DATA.md records BacDive CC BY attribution, the commercial-contact condition and Cali Fund guidance.

Every displayed empirical number is linked to a line in data/gtdb-derived/results/public-results.tsv. That table names its source JSON and locator. data/release-manifest.json pins the aggregate results, figures and generated documents by SHA-256. The source and original scientific manifests remain the immutable references for rebuilding the earlier fitted analysis. No individual labels, fitted estimators or prediction records are redistributed.

Offline fixtures check complete-taxon resampling, disjoint fitting memberships, branch distances, conformal order statistics, strict oxygen-score comparisons, width abstention, supported-only coverage and whole-order acquisition budgets. A clean replay from the final local commit uses verified source cache files only, never copied fitted models or derived results. Its receipts and scan exit codes are in data/checks. Research prototype on this labelled GTDB-mapped table; not tested on prospective cultures, on organisms outside the table, or for clinical or production use.''']
    note = '\n\n<!-- page -->\n\n'.join(pages)
    substitutions = {'{{table:accuracy}}': order_md, '{{table:coverage}}': coverage_md,
                     '{{table:horizons}}': horizon_md, '{{table:measure}}': measure_md,
                     '{{figure:nearest-relative-profile}}': '![Paired improvements over B2, with taxon intervals.](../data/gtdb-derived/figures/nearest-relative-profile.svg)'}
    for marker, replacement in substitutions.items():
        note = note.replace(marker, replacement)
    # Markdown links resolve from docs rather than repository root.
    note = note.replace(']('+PUBLIC+')', '](../'+PUBLIC+')')
    (ROOT/'docs/TECHNICAL_NOTE.md').write_text(note+'\n')
    pdf_note(pages, {'accuracy': order_rows, 'coverage': coverage_rows, 'horizons': horizon_rows, 'measure': measure_rows})
    all_rows = ['# Complete aggregate results\n\nEvery row covers the full usable outer population for its trait and rank. Unsupported items are excluded from coverage and counted in abstention. Oxygen error is one minus balanced accuracy. All reported uncertainty intervals resample held-out taxa.\n',
                '| Trait | Rank | Method | Error [95% interval] | Pooled coverage [95% interval] | Accepted coverage [95% interval] | Abstention | Mean size | Accepted mean size | Pinned source line |',
                '| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for t in TRAITS:
        for rank in RANKS:
            for m, r in records[t][rank]['methods'].items():
                o = r['overall']
                all_rows.append('| '+' | '.join([LABELS[t], rank, m, interval(o['error']), interval(o['coverage'], True), interval(o['coverage_accepted'], True), number(o['abstention_rate'], True), number(o['mean_size']), number(o['mean_size_accepted']), table.cite(f'{t}/{rank}/{m}/overall', '../')])+' |')
    all_rows[0] += ('\n'+statuses+'\n\n'+predictor_text+'\n\nThe order-holdout horizon table in the README is the order rank only. '
        'Per-rank records are the JSON files under data/gtdb-derived/results/. At class, temperature '
        'already fails in the nearest bin for both predictors. At class, pH also fails in bin 0 for both '
        'predictors, and salinity is unidentified for both predictors. At phylum, the horizons are unidentified.\n\n'
        +target1_text+'\n\n'+b1_scope+'\n\n'+b0_limits+'\n\n'+accepted_text+'\n')
    all_rows[0] = all_rows[0].replace(']('+PUBLIC+')', '](../'+PUBLIC+')')
    (ROOT/'docs/RESULTS.md').write_text('\n'.join(all_rows)+'\n')
    site = ROOT/'docs/site'
    site.mkdir(exist_ok=True)
    def site_table(rows: Any, keys: list[str]) -> str:
        head = '<thead><tr>'+''.join('<th scope="col">'+html.escape(c)+'</th>' for c in rows[0])+ '<th scope="col">Source</th></tr></thead>'
        body = []
        for i, row in enumerate(rows[1:]):
            body.append('<tr>'+''.join(('<th scope="row">' if j == 0 else '<td>')+html.escape(c)+('</th>' if j == 0 else '</td>') for j, c in enumerate(row))+
                '<td>'+ ' / '.join(f'<a href="../../{PUBLIC}">TSV line {table.lines[k]}</a>' for k in keys[i].split(';'))+'</td></tr>')
        return '<div class="table-wrap"><table>'+head+'<tbody>'+''.join(body)+'</tbody></table></div>'
    page = f'''<!doctype html>
<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Growth Horizon | GeneX Labs</title><meta name="description" content="An empirical benchmark of microbial growth prediction, uncertainty and measurement selection."><link rel="stylesheet" href="style.css"></head>
<body><a class="skip" href="#main">Skip to content</a><header><a class="brand" href="#main">GeneX Labs <span>Research software</span></a><nav aria-label="Page navigation"><a href="#results">Results</a><a href="#horizons">Order horizons</a><a href="#measure">Measure next</a><a href="#rebuild">Rebuild</a></nav></header>
<main id="main"><section class="hero"><p class="eyebrow">Microbial growth / empirical benchmark</p><h1>How far can a growth prediction be trusted?</h1><p class="lead">Follow prediction error, coverage and abstention as genomes move away from labelled relatives.</p><p class="status">Research prototype on this labelled GTDB-mapped table; not tested on prospective cultures, on organisms outside the table, or for clinical or production use.</p></section>
<section id="results"><p class="eyebrow">The locked result</p><h2>The calibration and accuracy targets failed.</h2><p>B1 has lower order-holdout error for temperature and salinity. The order-holdout accuracy target failed. The full results retain failures, unsupported bins and uncertainty intervals.</p><p>{site_prose(target1_text)}</p><p>{site_prose(target3_text+" "+table.cite("target3"))}</p><p>{site_prose(b1_scope)}</p><p>{site_prose(predictor_text)}</p>{site_table(order_rows, [';'.join([t+'/order/B1/overall',t+'/order/method/overall',t+'/order/accuracy']) for t in TRAITS])}<p>{site_prose(descriptive_text)}</p><p>{site_prose(descriptive_values)}</p><h3>Coverage with abstentions</h3><p>Supported abstentions count as covered exactly when the computed interval or set contains the true label. Unsupported items are excluded from coverage and reported as abstentions.</p><p>{accepted_text}</p>{site_table(coverage_rows, [t+'/'+rank+'/method/overall' for t in TRAITS for rank in ('family','order')])}<figure><img src="../../data/gtdb-derived/figures/coverage-order.svg" alt="Every supported order-holdout cell has a coverage interval and an adjacent abstention bar, split by trait."><figcaption>Order holdout. Each fold and merged bin is shown separately. Underlying cells are pinned in <a href="../../data/gtdb-derived/results/figure-data.json">figure-data.json</a>.</figcaption></figure></section>
<section id="horizons"><p class="eyebrow">Beyond the average</p><h2>Order-holdout horizons</h2><p>This table is the order rank only. Per-rank records are the JSON files under data/gtdb-derived/results/. At class, temperature already fails in the nearest bin for both predictors. At class, pH also fails in bin 0 for both predictors, and salinity is unidentified for both predictors. At phylum, the horizons are unidentified. The B1 ordinal interval is shown beside the proposed interval because the two intervals are not the same for every trait. The horizon first fails against a training-side constant or when most predictions abstain. A right-censored estimate extends beyond the observed range. These discrete bootstrap summaries do not certify a universal distance threshold.</p>{site_table(horizon_rows, [';'.join([t+'/order/method/horizon',t+'/order/B1/horizon']) for t in TRAITS])}<figure><img src="../../data/gtdb-derived/figures/secondary-coverage.svg" alt="Genome-weighted, taxon-weighted and mean-fit-distance coverage intervals are shown above their abstention rates."><figcaption>Secondary coverage checks. Explicit refits remove the ten mean_zc and mean_nh2o columns, whose recomputed values differed from the published table (DATA.md). No frozen feature list uses them, so this refit cannot change any prediction; it is reported for completeness.</figcaption></figure></section>
<section id="measure"><p class="eyebrow">What to measure next</p><h2>Exploratory retrospective selection on the same pipeline.</h2><p>Widest uncertainty, farthest-first distance and random selection acquire whole orders, then refit and recalibrate. Lower error and mean width or cardinality areas under the budget curve are preferable. Remaining evaluation populations change by strategy, so this is exploratory evidence.</p>{site_table(measure_rows, [t+'/measure/'+strategy for t in TRAITS for strategy in ('widest','farthest','random')])}<p>{site_prose(width_text)}</p><figure><img src="../../data/gtdb-derived/figures/measure-next.svg" alt="Width, error and abstention curves compare the three acquisition strategies on the remaining far organisms."><figcaption>Fold means. No laboratory measurement or future-horizon gain is claimed.</figcaption></figure></section>
<section class="limits"><h2>What this evidence supports</h2><p>{site_prose(b0_limits)}</p><p>{html.escape(literature_text)}</p><p>Oxygen is a class label with uncertainty represented by a prediction set.</p><p>Exchangeability is assumed, not established. Labels are table-level experimental records with residual per-value provenance uncertainty. Correlated genomes, unequal taxon size, unsupported ranks and annotation changes limit generalisation. Accepted-item coverage has no nominal guarantee.</p><p>Read the <a href="../TECHNICAL_NOTE.pdf">technical note (PDF)</a>, <a href="../TECHNICAL_NOTE.md">Markdown note</a>, <a href="../RESULTS.md">complete results</a>, <a href="../../PREREGISTRATION.md">pre-registration</a> and <a href="../../DATA.md">data terms and attribution</a>.</p></section>
<section id="rebuild"><p class="eyebrow">Reproducible by design</p><h2>Check the committed aggregates, or recompute them.</h2><p>Offline verification compares pinned hashes and runs the fixture tests. It does not download or refit.</p><pre><code>uv run --project release --frozen python -m scripts.check_release
uv run --frozen pytest --basetemp=work-tmp.noindex/pytest-fixtures</code></pre><p>Full recomputation acquires missing inputs, rebuilds local fitted trees, scores outer folds and regenerates the public package. It needs a network connection or a checksum-verified raw cache, and it stops if free space on / is below 25 GB. The pinned replay inputs total 254,404,224 bytes. data/raw and the local fitted trees are not redistributed.</p><pre><code>uv run --project release --frozen python -m scripts.release</code></pre><p>Phase 1 rebuild without outer scoring is <code>uv run --frozen python -m scripts.rebuild</code>. Every empirical number links to a source-table line, and the <a href="../../data/release-manifest.json">release manifest</a> pins output hashes. Code is Apache-2.0; aggregate GTDB-derived analyses are CC BY-SA 4.0.</p></section></main><footer>GeneX Labs Inc. <a href="../../CITATION.cff">Cite this work</a> <a href="../../LICENSE">Code licence</a></footer></body></html>'''
    (site/'index.html').write_text(page+'\n')
    (site/'style.css').write_text('''*{box-sizing:border-box}html{scroll-behavior:auto}body{margin:0;background:#f6f5ef;color:#18323c;font:17px/1.6 system-ui,sans-serif}a{color:#145e69;text-underline-offset:.2em}a:focus-visible{outline:3px solid #b34519;outline-offset:5px}.skip{position:absolute;left:1rem;top:-5rem;background:white;padding:1rem}.skip:focus{top:1rem}header,footer{max-width:1180px;margin:auto;padding:28px 32px;display:flex;justify-content:space-between;gap:24px}header{border-bottom:1px solid #cad7d6}.brand{font-size:20px;font-weight:750;text-decoration:none}.brand span{display:block;font-size:12px;font-weight:500;letter-spacing:.05em}nav{display:flex;align-items:center;gap:25px}nav a{font-size:14px}main{max-width:1116px;margin:auto;padding:0 32px}.hero{padding:80px 0 70px;max-width:850px}h1{font-size:clamp(42px,6vw,76px);line-height:1.08;letter-spacing:-.055em;margin:16px 0 25px}h2{font-size:clamp(28px,4vw,42px);line-height:1.2;letter-spacing:-.03em;max-width:850px}h3{font-size:24px}.eyebrow{text-transform:uppercase;letter-spacing:.12em;font-size:12px;font-weight:750;color:#176b75}.lead{font-size:24px;max-width:690px}.status{font-size:14px;border-left:3px solid #b34519;padding-left:12px}section{padding:44px 0;border-bottom:1px solid #cad7d6}section p{max-width:800px}.table-wrap{overflow:auto;margin:28px 0}table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:13px 12px;text-align:left;vertical-align:top;border-bottom:1px solid #cad7d6}thead{background:#e4eeee}th[scope=row]{font-weight:650}figure{margin:40px 0}img{max-width:100%;height:auto;background:white}figcaption{font-size:13px;color:#49616a;margin-top:12px}.limits{background:#e4eeee;padding:32px;margin:40px -20px;border:0}pre{padding:22px;background:#18323c;color:#fff;overflow:auto;font-size:14px}footer{font-size:13px;flex-wrap:wrap}footer a{margin-left:15px}@media(max-width:650px){header{padding:22px;flex-direction:column}nav{gap:15px;flex-wrap:wrap}main{padding:0 22px}.hero{padding:55px 0}.lead{font-size:20px}section{padding:30px 0}th,td{padding:10px 8px}.limits{margin:25px 0;padding:20px}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto}}
''')
    files = [ROOT/'DATA.md', ROOT/'LICENSE', ROOT/'NOTICE', ROOT/'CITATION.cff', ROOT/'CHANGELOG.md',
             ROOT/'docs/reproducibility.md', ROOT/'docs/INTEGRITY.md', ROOT/'docs/related-work.md',
             ROOT/'data/paper-source-checks.json', ROOT/'data/checks/far-bin-aggregation-comparison.json', ROOT/'README.md', ROOT/'docs/TECHNICAL_NOTE.md', ROOT/'docs/TECHNICAL_NOTE.pdf', ROOT/'docs/RESULTS.md',
             site/'index.html', site/'style.css', *sorted(RESULTS.glob('*')), *sorted(FIG.glob('*'))]
    write_json(ROOT/'data/release-manifest.json', [{'path': str(p.relative_to(ROOT)),
        'bytes': p.stat().st_size, 'sha256': digest(p)} for p in files if p.is_file()])


if __name__ == '__main__':
    main()

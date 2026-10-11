# SPDX-License-Identifier: Apache-2.0
"""Locked scoring from checksum-verified fitted artefacts, with no tuning."""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import joblib  # type: ignore[import-untyped]
import numpy as np
import pandas as pd  # type: ignore[import-untyped]
from sklearn.base import clone  # type: ignore[import-untyped]
from threadpoolctl import threadpool_limits  # type: ignore[import-untyped]

from growth_horizon.calibration import assign_bins, conformal_quantile
from growth_horizon.crossfit import inverse_quantile_scores
from growth_horizon.evaluation import REPETITIONS, comparison, error_values, summary
from growth_horizon.folds import RANKS, SEED
from growth_horizon.models import nonconformity, prediction
from growth_horizon.phase1 import nearest_prediction, nearest_rows
from growth_horizon.population import TRAITS, load_trees
from scripts.acquire import ROOT, digest
from scripts.preflight_sample import check_space

METHODS = ('B0', 'B1', 'B2', 'B3', 'method')
LIMITS = {'temperature_optimum': 20, 'salinity_optimum': 8, 'ph_optimum': 3}
RESULTS = ROOT / 'data/gtdb-derived/results'
LOCAL = ROOT / 'data/gtdb-derived/local/results'


def write_json(path: Path, record: Any) -> None:
    def clean(v: Any) -> Any:
        if isinstance(v, dict):
            return {str(k): clean(x) for k, x in v.items()}
        if isinstance(v, (list, tuple)):
            return [clean(x) for x in v]
        if isinstance(v, np.generic):
            return clean(v.item())
        if isinstance(v, float) and not math.isfinite(v):
            return None
        return v
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(record), indent=2, sort_keys=True, allow_nan=False)+'\n')


def verify_frozen() -> None:
    check_space()
    if digest(ROOT/'PREREGISTRATION.md') != 'cabc7ecffdd2e11246c8ab7b08b3103b09819f3fde1bcae87ab9cb649330a179':
        raise ValueError('Pre-registration changed')
    for item in json.loads((ROOT/'data/artifact-manifest.json').read_text()):
        p = ROOT/item['path']
        if not p.exists() or p.stat().st_size != item['bytes'] or digest(p) != item['sha256']:
            raise ValueError('Frozen artefact mismatch: '+item['path'])


def fit_prediction(payload: Any, df: Any, query: Any, y: Any, trait: str,
                   trees: Any) -> Any:
    sources = payload.get('proper_indices', payload.get('training_indices'))
    if set(sources) & set(query):
        raise ValueError('Query overlaps fitted sources')
    if 'estimator' not in payload:
        _, neighbours = nearest_rows(df, sources, query, trees)
        return nearest_prediction(y, neighbours, trait)
    return prediction(payload['estimator'], df.iloc[query][payload['features']], trait)


def constant(y: Any, sources: Any, count: int, trait: str, probabilities: bool = False) -> Any:
    if trait == 'oxygen':
        p = float(y[sources].mean())
        return np.tile([1-p, p], (count, 1)) if probabilities else np.full(count, int(p > .5))
    return np.full(count, float(y[sources].mean()))


def cv_bounds(predictions: Any, scores: Any, assignments: Any, selected: Any,
              trait: str, uniforms: Any, ties: Any) -> tuple[Any, Any]:
    """Exact CV+ order statistics or Algorithm 2 strict score comparisons."""
    n_query = predictions.shape[1]
    if trait == 'oxygen':
        included = np.ones((n_query, 2), dtype=bool)
        count = np.zeros((n_query, 2), dtype=int)
        for k in range(5):
            r = np.sort(scores[selected & (assignments == k)])
            s = inverse_quantile_scores(predictions[k], uniforms, ties)
            count += np.searchsorted(r, s, side='left')
        included = count < .9*(int(selected.sum())+1)
        return included, included.sum(axis=1).astype(float)
    n = int(selected.sum())
    lo_index, hi_index = math.floor(.1*(n+1)), math.ceil(.9*(n+1))
    lower, upper = np.full(n_query, -np.inf), np.full(n_query, np.inf)
    for start in range(0, n_query, 128):
        stop = min(n_query, start+128)
        centres = predictions[assignments[selected], start:stop].T
        if lo_index >= 1:
            lower[start:stop] = np.partition(centres-scores[selected], lo_index-1, axis=1)[:, lo_index-1]
        if hi_index <= n:
            upper[start:stop] = np.partition(centres+scores[selected], hi_index-1, axis=1)[:, hi_index-1]
    return np.column_stack((lower, upper)), upper-lower


def calibrated(predictions: Any, scores: Any, assignments: Any, calibration_distances: Any,
               distances: Any, record: Any, trait: str, uniforms: Any, ties: Any,
               y_query: Any) -> dict[str, Any]:
    edges = np.array(record['distance_edges'])
    cal_bins, query_bins = assign_bins(calibration_distances, edges), assign_bins(distances, edges)
    n = len(distances)
    supported, covered = np.zeros(n, dtype=bool), np.zeros(n, dtype=bool)
    sizes, merged = np.full(n, np.inf), np.full(n, -1, dtype=int)
    intervals = np.full((n, 2), np.nan)
    sets = np.zeros((n, 2), dtype=bool)
    for b, item in enumerate(record['methods']['method']['bins']):
        q = np.isin(query_bins, item['original_bins']) & np.isfinite(distances)
        merged[q] = b
        if not item['supported'] or not q.any():
            continue
        selected = np.isin(cal_bins, item['original_bins']) & np.isfinite(calibration_distances)
        bounds, width = cv_bounds(predictions[:, q], scores, assignments, selected,
                                  trait, uniforms[q], ties[q])
        supported[q], sizes[q] = True, width
        if trait == 'oxygen':
            sets[q] = bounds
            covered[q] = bounds[np.arange(q.sum()), y_query[q].astype(int)]
        else:
            intervals[q] = bounds
            covered[q] = (y_query[q] >= bounds[:, 0]) & (y_query[q] <= bounds[:, 1])
    abstain = ~supported | ~np.isfinite(distances)
    abstain |= sizes != 1 if trait == 'oxygen' else sizes > LIMITS[trait]
    return {'supported': supported, 'covered': covered, 'size': sizes, 'abstain': abstain,
            'bin': merged, 'intervals': intervals, 'sets': sets}


def score_fold(df: Any, trait: str, rank: str, fold: int, trees: Any,
               analysis_root: Path | None = None, crossfit_root: Path | None = None,
               sensitivity: bool = True) -> dict[str, dict[str, Any]]:
    base = analysis_root or ROOT/'data/gtdb-derived/local/analysis'
    cross = crossfit_root or ROOT/'data/gtdb-derived/local/crossfit'
    directory, cdir = base/f'{trait}/{rank}/fold{fold}', cross/f'{trait}/{rank}/fold{fold}'
    membership = np.load(directory/'membership-distances.npz')
    original, record = json.loads((directory/'calibration.json').read_text()), json.loads((cdir/'calibration.json').read_text())
    query, training = membership['outer_test'], membership['outer_training']
    y = df[trait].to_numpy(dtype=float)
    taxa = df['species' if rank == 'random' else rank].to_numpy()[query]
    rng = np.random.default_rng(record['seed']+5)
    uniforms, ties = rng.uniform(size=len(query)), rng.integers(0, 2, size=len(query))
    inner_distances, inner_predictions, b0_scores, b0_assign = [], {m: [] for m in METHODS}, [], []
    for k in range(5):
        md = np.load(cdir/f'inner{k}/membership-distances.npz')
        proper, cal = md['proper'], md['calibration']
        distances, _ = nearest_rows(df, proper, query, trees)
        inner_distances.append(distances)
        for m in METHODS:
            if m == 'B0':
                inner_predictions[m].append(constant(y, proper, len(query), trait, True))
            else:
                inner_predictions[m].append(fit_prediction(joblib.load(cdir/f'inner{k}/{m}.joblib'), df, query, y, trait, trees))
        cal_pred = constant(y, proper, len(cal), trait, True)
        scores = (inverse_quantile_scores(cal_pred, md['uniforms'], md['tie_first'])[
            np.arange(len(cal)), y[cal].astype(int)] if trait == 'oxygen' else np.abs(y[cal]-cal_pred))
        b0_scores.append(scores)
        b0_assign.append(cal)
    mean_distance = np.mean(inner_distances, axis=0)
    output = {}
    for m in METHODS:
        if m == 'B0':
            oof = np.load(cdir/'method-oof.npz')
            scores = np.empty(len(training))
            for cal, values in zip(b0_assign, b0_scores, strict=True):
                scores[np.searchsorted(training, cal)] = values
            point = constant(y, training, len(query), trait)
            naive = constant(y, membership['naive_fit'], len(query), trait, True)
            naive_cal = constant(y, membership['naive_fit'], len(membership['naive_calibration']), trait, True)
            nd, _ = nearest_rows(df, membership['naive_fit'], membership['naive_calibration'], trees)
            q90 = conformal_quantile(nonconformity(y[membership['naive_calibration']], naive_cal, trait)[np.isfinite(nd)])
        else:
            oof = np.load(cdir/f'{m}-oof.npz')
            scores = oof['scores']
            p = fit_prediction(joblib.load(directory/f'{m}.joblib'), df, query, y, trait, trees)
            point = np.argmax(p, axis=1) if trait == 'oxygen' else p
            if m == 'B2':
                _, nn = nearest_rows(df, membership['naive_fit'], query, trees)
                naive = nearest_prediction(y, nn, trait)
            else:
                naive = fit_prediction(joblib.load(directory/f'{m}-naive.joblib'), df, query, y, trait, trees)
            q90 = original['methods'][m]['naive_q90']
            q90 = math.inf if q90 is None else q90
        ip = np.array(inner_predictions[m])
        result = calibrated(ip, scores, oof['inner_assignment'], oof['calibration_distances'],
            membership['outer_training_distances'], record, trait, uniforms, ties, y[query])
        secondary = calibrated(ip, scores, oof['inner_assignment'], oof['calibration_distances'],
            mean_distance, record, trait, uniforms, ties, y[query])
        result.update({'y': y[query], 'point': point, 'taxa': taxa, 'phylum': df['phylum'].to_numpy()[query],
            'fold': np.full(len(query), fold), 'row': query,
            'distance': membership['outer_training_distances'], 'mean_fit_distance': mean_distance})
        for key in ('supported', 'covered', 'size', 'abstain', 'bin'):
            result['secondary_'+key] = secondary[key]
        if trait == 'oxygen':
            nset = 1-naive <= q90
            result['naive_covered'] = nset[np.arange(len(query)), y[query].astype(int)]
            result['naive_size'] = nset.sum(axis=1).astype(float)
            result['naive_abstain'] = result['naive_size'] != 1
            result['naive_point'] = np.argmax(naive, axis=1)
        else:
            result['naive_covered'] = np.abs(y[query]-naive) <= q90
            result['naive_size'] = np.full(len(query), 2*q90)
            result['naive_abstain'] = result['naive_size'] > LIMITS[trait]
            result['naive_point'] = naive
        result['naive_supported'] = result['supported'].copy()
        if sensitivity and m in ('B1', 'method'):
            payload = joblib.load(directory/f'{m}.joblib')
            dropped = [c for c in df.columns if c.endswith(('_mean_zc', '_mean_nh2o'))]
            if len(dropped) != 10 or set(dropped) & set(payload['features']):
                raise ValueError('Unexpected ten-column feature specification')
            frame = df.drop(columns=dropped)
            estimator = clone(payload['estimator'])
            estimator.fit(frame.iloc[payload['proper_indices']][payload['features']], y[payload['proper_indices']])
            sp = prediction(estimator, frame.iloc[query][payload['features']], trait)
            result['sensitivity_point'] = np.argmax(sp, axis=1) if trait == 'oxygen' else sp
            result['sensitivity_identical'] = np.full(len(query), np.array_equal(result['sensitivity_point'], point))
        output[m] = result
    return output


def variant(rows: Any, prefix: str) -> Any:
    result = rows.copy()
    for key in ('supported', 'covered', 'size', 'abstain', 'bin', 'point'):
        if prefix+'_'+key in rows:
            result[key] = rows[prefix+'_'+key]
    return result


def horizon(rows: Any, b0: Any, b2: Any, edges: Any, trait: str) -> dict[str, Any]:
    bins = assign_bins(rows['distance'], np.array(edges))
    nbin = len(edges)+1
    oxygen = trait == 'oxygen'
    unique, inv = np.unique(rows['taxa'], return_inverse=True)
    draws = np.random.default_rng(SEED).integers(len(unique), size=(REPETITIONS, len(unique)))
    weights = np.zeros((REPETITIONS, len(unique)), dtype=int)
    np.add.at(weights, (np.repeat(np.arange(REPETITIONS), len(unique)), draws.ravel()), 1)
    entries, replicate_gains, replicate_abstentions, replicate_counts, supported_counts = [], [], [], [], []
    for bin_id in range(nbin):
        sel = bins == bin_id
        report = summary(rows, sel, trait)
        gain = comparison(rows['y'][sel], b0['point'][sel], rows['point'][sel], rows['taxa'][sel], oxygen)
        if oxygen and gain['value'] is not None:
            e = report['error']
            gain = {'value': .5-e['value'], 'interval': [.5-e['interval'][1], .5-e['interval'][0]] if e['interval'] else None, 'taxa': e['taxa']}
        relative = comparison(rows['y'][sel], b2['point'][sel], rows['point'][sel], rows['taxa'][sel], oxygen)
        entries.append({'bin': bin_id, 'range': [edges[bin_id-1] if bin_id else 0,
            edges[bin_id] if bin_id < len(edges) else None], 'metrics': report,
            'improvement_over_B0': gain, 'improvement_over_B2': relative})
        a = error_values(rows['y'][sel], rows['point'][sel], oxygen)
        ref = error_values(rows['y'][sel], b0['point'][sel], oxygen)
        sa, sr = np.zeros((len(unique), a.shape[1])), np.zeros((len(unique), a.shape[1]))
        np.add.at(sa, inv[sel], a)
        np.add.at(sr, inv[sel], ref)
        ta, tr = weights@sa, weights@sr
        if oxygen:
            recall = np.divide(ta[:, [0, 2]], ta[:, [1, 3]], out=np.full((REPETITIONS, 2), np.nan), where=ta[:, [1, 3]] > 0)
            gain_boot = np.nanmean(recall, axis=1)-.5
        else:
            gain_boot = np.divide(tr[:, 0]-ta[:, 0], ta[:, 1], out=np.full(REPETITIONS, np.nan), where=ta[:, 1] > 0)
        count = np.bincount(inv[sel], minlength=len(unique))
        abstain = np.bincount(inv[sel], weights=rows['abstain'][sel], minlength=len(unique))
        supported = np.bincount(inv[sel], weights=rows['supported'][sel], minlength=len(unique))
        replicate_gains.append(gain_boot)
        replicate_counts.append(weights@count)
        replicate_abstentions.append(weights@abstain)
        supported_counts.append(weights@supported)
    valid = all(e['metrics']['coverage']['supported_genomes'] > 0 and e['improvement_over_B0']['interval'] is not None for e in entries)
    first = next((e['bin'] for e in entries if e['improvement_over_B0']['interval'] is not None and (e['improvement_over_B0']['interval'][0] <= 0 or e['metrics']['abstention_rate'] > .5)), None)
    state = 'unidentified' if not valid else 'right_censored' if first is None else 'identified'
    gains, counts = np.array(replicate_gains).T, np.array(replicate_counts).T
    unknown = np.any((counts == 0) | (np.array(supported_counts).T == 0) | ~np.isfinite(gains), axis=1)
    failed = (gains <= 0) | (np.array(replicate_abstentions).T > counts/2)
    ordinals = np.where(failed.any(axis=1), failed.argmax(axis=1), nbin)
    finite_ordinals = ordinals[~unknown]
    bounds = np.quantile(finite_ordinals, [.025, .975], method='inverted_cdf').astype(int).tolist() if len(finite_ordinals) else None
    def interval_range(i: int) -> Any:
        return [edges[-1], None] if i == nbin else entries[i]['range']
    return {'state': state, 'first_failing_bin': first if valid else None,
            'distance_range': entries[first]['range'] if valid and first is not None else None,
            'ordinal_interval': bounds, 'interval_distance_ranges': [interval_range(i) for i in bounds] if bounds else None,
            'unidentified_replicate_fraction': float(unknown.mean()),
            'right_censored_replicate_fraction': float(((ordinals == nbin) & ~unknown).mean()),
            'bins': entries}


def aggregate(trait: str, rank: str, rows: Any, edges: Any) -> dict[str, Any]:
    output: dict[str, Any] = {'trait': trait, 'rank': rank, 'methods': {}, 'horizons': {}}
    for m, r in rows.items():
        all_mask = np.ones(len(r['y']), dtype=bool)
        record = {'overall': summary(r, all_mask, trait), 'naive': summary(variant(r, 'naive'), all_mask, trait),
                  'mean_fit_distance': summary(variant(r, 'secondary'), all_mask, trait), 'fold_bins': [],
                  'secondary_fold_bins': [], 'phylum': {}}
        for fold in range(5):
            for b in sorted(set(r['bin'][r['fold'] == fold])):
                sel = (r['fold'] == fold) & (r['bin'] == b)
                record['fold_bins'].append({'fold': fold, 'bin': int(b), 'metrics': summary(r, sel, trait)})
            sr = variant(r, 'secondary')
            for b in sorted(set(sr['bin'][r['fold'] == fold])):
                sel = (sr['fold'] == fold) & (sr['bin'] == b)
                record['secondary_fold_bins'].append({'fold': fold, 'bin': int(b), 'metrics': summary(sr, sel, trait)})
        far = np.zeros(len(r['y']), dtype=bool)
        for fold in range(5):
            supported_bins = r['bin'][(r['fold'] == fold) & r['supported']]
            if len(supported_bins):
                far |= (r['fold'] == fold) & (r['bin'] == supported_bins.max()) & r['supported']
        record['naive_far'] = summary(variant(r, 'naive'), far, trait)
        for phylum in sorted(set(r['phylum'])):
            record['phylum'][str(phylum)] = summary(r, r['phylum'] == phylum, trait)
        if m in ('method', 'B1'):
            sr = r.copy()
            sr['point'] = r['sensitivity_point']
            record['ten_column_refit'] = {'error': summary(sr, all_mask, trait)['error'],
                                        'all_predictions_identical': bool(r['sensitivity_identical'].all())}
            output['horizons'][m] = horizon(r, rows['B0'], rows['B2'], edges, trait)
        output['methods'][m] = record
    output['accuracy_comparison'] = comparison(rows['method']['y'], rows['B1']['point'], rows['method']['point'], rows['method']['taxa'], trait == 'oxygen')
    return output


def targets(records: Any) -> dict[str, Any]:
    cells, target1 = [], True
    for t in TRAITS:
        for rank in ('family', 'order'):
            m = records[t][rank]['methods']['method']
            bins = [c for c in m['fold_bins'] if c['metrics']['coverage']['supported_genomes']]
            low = [c for c in bins if c['metrics']['coverage']['interval'] is None or c['metrics']['coverage']['interval'][1] < .87]
            ci = m['overall']['coverage']['interval']
            pooled = ci is not None and ci[1] >= .9
            naive = {}
            for b in ('B1', 'B2'):
                c = records[t][rank]['methods'][b]['naive_far']['coverage']
                naive[b] = {'coverage': c, 'passed': c['value'] is not None and c['value'] <= .8 and c['interval'] is not None and c['interval'][1] < .9}
            passed = bool(bins) and not low and pooled and all(c['passed'] for c in naive.values())
            target1 &= passed
            cells.append({'trait': t, 'rank': rank, 'passed': passed, 'pooled_coverage': m['overall']['coverage'],
                          'failing_bins': [{'fold': c['fold'], 'bin': c['bin'], 'coverage': c['metrics']['coverage']} for c in low], 'naive_far': naive})
    accuracy = []
    for t in TRAITS:
        c = records[t]['order']['accuracy_comparison']
        passed = c['relative_reduction'] is not None and c['relative_reduction'] >= .1 and c['interval'] is not None and c['interval'][0] > 0
        accuracy.append({'trait': t, 'passed': passed, **c})
    return {'target1': {'passed': bool(target1), 'cells': cells},
            'target2': {'passed': sum(c['passed'] for c in accuracy) >= 2, 'traits': accuracy},
            'target3': {'passed': all(records[t]['order']['horizons']['method']['state'] != 'unidentified' for t in TRAITS),
                        'horizons': {t: records[t]['order']['horizons'] for t in TRAITS},
                        'meaning': 'Full-population horizon estimates supplied; publication pending.'},
            'target4': {'passed': True, 'B1_winning_traits': [c['trait'] for c in accuracy if c['value'] < 0],
                        'meaning': 'Report all B1 wins explicitly.'}}


def main() -> None:
    verify_frozen()
    populations = {t: pd.read_pickle(ROOT/f'data/gtdb-derived/local/analysis/{t}.pkl').sort_index() for t in TRAITS}
    leaves = set().union(*(set(df['leaf']) for df in populations.values()))
    trees = [t.prune(leaves) for t in load_trees()]
    cuts = json.loads((ROOT/'data/gtdb-derived/horizon-cutpoints.json').read_text())
    records: dict[str, Any] = {}
    LOCAL.mkdir(parents=True, exist_ok=True)
    with threadpool_limits(limits=1):
        for trait, df in populations.items():
            records[trait] = {}
            for rank in RANKS:
                fold_results = []
                for fold in range(5):
                    check_space()
                    fold_results.append(score_fold(df, trait, rank, fold, trees))
                    print(f'{trait} {rank} fold{fold}: scored', flush=True)
                rows = {m: {key: np.concatenate([f[m][key] for f in fold_results]) for key in fold_results[0][m]} for m in METHODS}
                for m, r in rows.items():
                    np.savez(LOCAL/f'{trait}-{rank}-{m}.npz', **r)
                record = aggregate(trait, rank, rows, cuts['traits'][trait][rank]['distance_edges'])
                records[trait][rank] = record
                write_json(RESULTS/f'{trait}-{rank}.json', record)
                print(f'{trait} {rank}: aggregated', flush=True)
    write_json(RESULTS/'targets.json', targets(records))
    write_json(RESULTS/'locked-run.json', {'preregistration_sha256': digest(ROOT/'PREREGISTRATION.md'),
        'scoring_protocol_sha256': digest(ROOT/'docs/SCORING_PROTOCOL.md'), 'bootstrap_replicates': REPETITIONS,
        'seed': SEED, 'traits': list(TRAITS), 'ranks': list(RANKS), 'methods': list(METHODS), 'outer_folds': 120,
        'no_tuning': True, 'result_files': [str(p.relative_to(ROOT)) for p in sorted(RESULTS.glob('*.json'))]})


if __name__ == '__main__':
    main()

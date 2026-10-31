#!/usr/bin/env python3
"""Exploratory quality analysis (not preregistered; chosen by the author on 26/10, option A + C).

Inputs: analysis/moodle/quality.jsonl (quality_scan.py), moodle/results.csv, moodle/issues.jsonl.
Output: analysis/quality_results.json

For each agent patch: debt added on the touched files (d_debt_min, SonarQube sqale_index, minutes) compared with
the debt added by the human fix on the same issue (paired, Wilcoxon signed-rank). "Clean success" = the patch passes the
developers' hidden tests AND adds no more debt than the human fix. Similarity to the human fix = normalised
Levenshtein similarity of the changed lines.
Primary set: strict run 1 for every model, and the 'tests' condition (latest run per issue and model, see deviazioni.txt).
"""
import json, math
import pandas as pd, numpy as np
from scipy.stats import wilcoxon, mannwhitneyu, spearmanr

from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # repository root
A = ROOT / 'analysis' / 'moodle'; S = ROOT / 'moodle'
q = pd.DataFrame(map(json.loads, open(f'{A}/quality.jsonl')))
ok = q[(q.get('scan_error', pd.Series(index=q.index, dtype=object)).isna()) & (q.apply_error.fillna('') == '')].copy()
hum = ok[ok.variant == 'human'].set_index('key')
ag = ok[ok.variant != 'human'].copy()
ag[['model', 'cond', 'run']] = ag.variant.str.rsplit('_', n=2, expand=True)
ag['run'] = ag.run.astype(int)
es = pd.read_csv(f'{S}/results.csv')
ag = ag.merge(es, on=['key', 'model', 'cond', 'run'], how='left')
hours = {d['key']: d['hours'] for d in map(json.loads, open(f'{S}/issues.jsonl')) if 'key' in d and 'hours' in d}
band = lambda h: '<=1h' if h <= 1 else ('1-4h' if h <= 4 else '>4h')
ag['hours'] = ag.key.map(hours); ag['band'] = ag.hours.map(lambda h: band(h) if pd.notna(h) else None)
ag['h_d_debt'] = ag.key.map(hum.d_debt_min); ag['h_added'] = ag.key.map(hum.added)
ag['diff_vs_human'] = ag.d_debt_min - ag.h_d_debt
ag['clean_success'] = ((ag.solved == 1) & (ag.diff_vs_human <= 0)).astype(int)

strict1 = ag[(ag.cond == 'strict') & (ag.run == 1)]
tests = ag[ag.cond == 'tests'].sort_values('run').drop_duplicates(['key', 'model'], keep='last')
sets = {'strict': strict1, 'tests': tests}

def summ(d):
    if not len(d): return None
    x = d.dropna(subset=['diff_vs_human'])
    nz = x.diff_vs_human[x.diff_vs_human != 0]
    try: p = round(float(wilcoxon(x.d_debt_min, x.h_d_debt).pvalue), 4) if len(nz) else None
    except ValueError: p = None
    return {'n': int(len(x)),
            'agent_d_debt_min': {'median': float(x.d_debt_min.median()), 'mean': round(float(x.d_debt_min.mean()), 1), 'sum': int(x.d_debt_min.sum())},
            'human_d_debt_min_same_issues': {'median': float(x.h_d_debt.median()), 'mean': round(float(x.h_d_debt.mean()), 1), 'sum': int(x.h_d_debt.sum())},
            'more_debt_than_human': int((x.diff_vs_human > 0).sum()), 'same': int((x.diff_vs_human == 0).sum()), 'less': int((x.diff_vs_human < 0).sum()),
            'wilcoxon_p_agent_vs_human': p,
            'd_smells_sum': int(x.d_smells.sum()), 'd_bugs_sum': int(x.d_bugs.sum()), 'd_vulns_sum': int(x.d_vulns.sum()),
            'lines_added_median': float(x.added.median()), 'human_lines_added_median': float(x.h_added.median()),
            'lev_sim_human_median': round(float(x.lev_sim_human.median()), 3)}

res = {'n_issues_scanned': int(q.key.nunique()), 'excluded_rows': {
    'apply_error': int((q.apply_error.fillna('') != '').sum()), 'scan_error': int(q.get('scan_error', pd.Series(dtype=object)).notna().sum())}}
res['human'] = {'n': int(len(hum)), 'd_debt_min_median': float(hum.d_debt_min.median()), 'd_debt_min_mean': round(float(hum.d_debt_min.mean()), 1),
                'added_debt_share': round(float((hum.d_debt_min > 0).mean()), 3)}
for name, d in sets.items():
    r = {}
    for m in sorted(d.model.unique()):
        dm = d[d.model == m]
        r[m] = {'all_patches': summ(dm), 'solved_patches': summ(dm[dm.solved == 1]),
                'solved': int(dm.solved.sum()), 'clean_success': int(dm.clean_success.sum()),
                'clean_by_band': {b: f"{int(dm[dm.band == b].clean_success.sum())}/{int(dm[dm.band == b].solved.sum())}/{int((dm.band == b).sum())} (clean/solved/n)" for b in ['<=1h', '1-4h', '>4h']}}
    res[name] = r
# Similarity to the human fix vs passing the hidden tests (strict run 1, all models pooled)
x = strict1.dropna(subset=['solved'])
u = mannwhitneyu(x[x.solved == 1].lev_sim_human, x[x.solved == 0].lev_sim_human)
res['lev_sim_vs_solved_strict'] = {'median_solved': round(float(x[x.solved == 1].lev_sim_human.median()), 3),
                                   'median_unsolved': round(float(x[x.solved == 0].lev_sim_human.median()), 3), 'mannwhitney_p': round(float(u.pvalue), 4)}
rho = spearmanr(x.hours, x.d_debt_min, nan_policy='omit')
res['debt_vs_hours_strict_spearman'] = {'rho': round(float(rho.statistic), 3), 'p': round(float(rho.pvalue), 4)}
json.dump(res, open(f'{A}/quality_results.json', 'w'), indent=1)
ag.to_csv(f'{A}/quality_rows.csv', index=False)
print(json.dumps(res, indent=1))

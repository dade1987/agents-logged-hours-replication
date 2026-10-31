#!/usr/bin/env python3
"""Study A+H analysis: AI agents re-solving Moodle issues vs logged human hours.

Inputs (moodle/): results.csv (key,model,cond,run,solved), issues.jsonl (hours, type),
runs.jsonl (tokens, duration, confidence); analysis/moodle/audit_runs.csv (isolation flags).
Output: analysis/moodle/results.json.

Primary sample: condition 'strict', run 1 of every model, runs whose transcript shows the
evaluation checkout or another workspace (moodle_seen / other_ws_seen) excluded.
"""
import csv, json, math, os, sys
from collections import defaultdict
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.inter_rater import fleiss_kappa
from statsmodels.stats.contingency_tables import mcnemar

from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # repository root
S = ROOT / 'moodle'
A = ROOT / 'analysis' / 'moodle'
SEED, NBOOT = 2026, 2000
MODELS = ['haiku', 'sonnet', 'opus', 'fable']

hours = {}; itype = {}
for l in open(f'{S}/issues.jsonl'):
    r = json.loads(l); hours[r['key']] = r['hours']; itype[r['key']] = r['type']
valid = open(f'{S}/issues.txt').read().split()
out = pd.read_csv(f'{S}/results.csv')
out = out[out.key.isin(valid)].copy()
out['run'] = out.run.astype(int)
out['hours'] = out.key.map(hours); out['log2h'] = np.log2(out.hours); out['type'] = out.key.map(itype)
runs = pd.DataFrame([json.loads(l) for l in open(f'{S}/runs.jsonl')])
runs['run'] = runs.run.astype(int)
out = out.merge(runs[['key', 'model', 'cond', 'run', 'tokens', 'duration_ms', 'confidence']], how='left', on=['key', 'model', 'cond', 'run'])
aud = pd.read_csv(f'{A}/audit_runs.csv').fillna('')
aud['run'] = aud.run.astype(int)
out = out.merge(aud[['key', 'model', 'cond', 'run', 'flags']], how='left', on=['key', 'model', 'cond', 'run'])
out['flags'] = out['flags'].fillna('')
out['leak'] = out['flags'].str.contains('seen')
out['any_flag'] = out['flags'] != ''

res = {'n_issues': len(valid), 'notes': []}

def band(h): return '<=1h' if h <= 1 else ('1-4h' if h <= 4 else '>4h')

def describe(d):
    t = {}
    for m in MODELS:
        x = d[d.model == m]
        t[m] = {'n': int(len(x)), 'solved': int(x.solved.sum()), 'rate': round(x.solved.mean(), 3) if len(x) else None}
    return t

def gee(d):
    d = d.copy(); d['model'] = pd.Categorical(d.model, categories=MODELS)
    m = smf.gee('solved ~ log2h + model', groups='key', data=d, family=sm.families.Binomial(),
                cov_struct=sm.cov_struct.Exchangeable()).fit()
    ci = m.conf_int()
    return {k: {'OR': round(math.exp(m.params[k]), 3), 'CI95': [round(math.exp(ci.loc[k, 0]), 3), round(math.exp(ci.loc[k, 1]), 3)],
                'p': round(float(m.pvalues[k]), 4)} for k in m.params.index}

def h50(d):
    """Hours at which P(solved)=0.5 from logit(solved) ~ log2h; None if slope >= 0 or fit fails."""
    try:
        m = smf.glm('solved ~ log2h', data=d, family=sm.families.Binomial()).fit()
    except Exception:
        return None, None
    b0, b1 = m.params['Intercept'], m.params['log2h']
    return (2 ** (-b0 / b1) if b1 < 0 else None), b1

def horizon(d):
    rng = np.random.default_rng(SEED); out_ = {}
    for mo in MODELS:
        x = d[d.model == mo]
        if x.empty: continue
        est, slope = h50(x)
        keys = x.key.unique(); bs = []
        for _ in range(NBOOT):
            samp = rng.choice(keys, len(keys), replace=True)
            b = pd.concat([x[x.key == k] for k in samp])
            v, _s = h50(b)
            bs.append(v if v is not None else np.inf)
        bs = np.array(bs)
        out_[mo] = {'h50': None if est is None else round(est, 2), 'slope_log2h': round(float(slope), 3) if slope is not None else None,
                    'CI95': [round(float(np.percentile(bs, 2.5)), 2), (round(float(np.percentile(bs, 97.5)), 2) if np.isfinite(np.percentile(bs, 97.5)) else 'inf')],
                    'share_boot_no_decline': round(float(np.mean(~np.isfinite(bs))), 3)}
    return out_

def labour_share(d):
    """Share of logged human hours in issues the agent solved (run-level average for Sonnet's repeats)."""
    r = {}
    per = d.groupby(['key', 'model']).solved.mean().unstack()
    tot = sum(hours[k] for k in per.index)
    for mo in MODELS:
        if mo in per: r[mo] = round(float(sum(hours[k] * per.loc[k, mo] for k in per.index if not pd.isna(per.loc[k, mo]))) / tot, 3)
    anym = per.fillna(0).max(axis=1)
    r['any_model'] = round(float(sum(hours[k] * (anym[k] > 0) for k in per.index)) / tot, 3)
    r['total_hours'] = round(tot, 1)
    by = defaultdict(dict)
    for name, f in [('type', lambda k: itype[k]), ('band', lambda k: band(hours[k]))]:
        g = defaultdict(list)
        for k in per.index: g[f(k)].append(k)
        for lev, ks in g.items():
            th = sum(hours[k] for k in ks)
            by[name][lev] = {'issues': len(ks), 'hours': round(th, 1),
                             'share_any_model': round(sum(hours[k] * (anym[k] > 0) for k in ks) / th, 3),
                             **{mo: round(sum(hours[k] * per.loc[k, mo] for k in ks if mo in per and not pd.isna(per.loc[k, mo])) / th, 3) for mo in MODELS}}
    r['by'] = by
    return r

def confidence(d):
    r = {}
    for mo in MODELS:
        x = d[(d.model == mo) & d.confidence.notna()]
        if x.empty: continue
        p = x.confidence / 100
        brier = float(np.mean((p - x.solved) ** 2)); base = float(np.mean((x.solved.mean() - x.solved) ** 2))
        pos, neg = p[x.solved == 1].values, p[x.solved == 0].values
        auc = float(np.mean([(a > b) + 0.5 * (a == b) for a in pos for b in neg])) if len(pos) and len(neg) else None
        r[mo] = {'n': int(len(x)), 'brier': round(brier, 3), 'brier_base_rate': round(base, 3), 'auc': None if auc is None else round(auc, 3),
                 'mean_conf_solved': round(float(pos.mean() * 100), 1) if len(pos) else None,
                 'mean_conf_failed': round(float(neg.mean() * 100), 1) if len(neg) else None}
    return r

def reliability(d):
    x = d[(d.model == 'sonnet') & (d.cond == 'strict')].pivot_table(index='key', columns='run', values='solved')
    x = x.dropna()
    if x.shape[1] < 3 or x.empty: return {'note': 'fewer than 3 complete Sonnet runs'}
    table = np.column_stack([(x == 0).sum(axis=1), (x == 1).sum(axis=1)])
    return {'issues': int(len(x)), 'fleiss_kappa': round(float(fleiss_kappa(table)), 3),
            'per_run_solved': {int(c): int(x[c].sum()) for c in x.columns},
            'always': int((x.sum(axis=1) == 3).sum()), 'never': int((x.sum(axis=1) == 0).sum()), 'mixed': int(((x.sum(axis=1) > 0) & (x.sum(axis=1) < 3)).sum())}

def iface_vs_strict(df):
    ik = open(f'{S}/iface_issues.txt').read().split()
    r = {}
    for mo in MODELS:
        s = df[(df.model == mo) & (df.cond == 'strict') & (df.run == 1) & df.key.isin(ik)].set_index('key').solved
        i = df[(df.model == mo) & (df.cond == 'iface') & (df.run == 1) & df.key.isin(ik)].set_index('key').solved
        k = s.index.intersection(i.index)
        if not len(k): continue
        b = int(((s[k] == 0) & (i[k] == 1)).sum()); c = int(((s[k] == 1) & (i[k] == 0)).sum())
        r[mo] = {'issues': int(len(k)), 'strict': int(s[k].sum()), 'iface': int(i[k].sum()), 'only_iface': b, 'only_strict': c,
                 'mcnemar_p': round(float(mcnemar([[0, c], [b, 0]], exact=True).pvalue), 4)}
    return r

strict = out[out.cond == 'strict']
primary = strict[(strict.run == 1) & ~strict.leak]
res['coverage'] = {'strict_rows': int(len(strict)), 'sonnet_runs_present': {int(r): int(((strict.model == 'sonnet') & (strict.run == r)).sum()) for r in (1, 2, 3)},
                   'excluded_leak_run1': int((strict.run == 1).sum() - len(primary))}
res['descriptive_primary'] = describe(primary)
res['gee_primary'] = gee(primary)
res['horizon_primary'] = horizon(primary)
res['labour_share_primary'] = labour_share(primary)
res['confidence_primary'] = confidence(primary)
res['reliability_sonnet'] = reliability(strict[~strict.leak])
res['reliability_sonnet_all'] = reliability(strict)
res['sensitivity'] = {
    'include_leak_runs': {'descriptive': describe(strict[strict.run == 1]), 'gee': gee(strict[strict.run == 1])},
    'exclude_any_flag': {'descriptive': describe(strict[(strict.run == 1) & ~strict.any_flag]), 'gee': gee(strict[(strict.run == 1) & ~strict.any_flag])},
    'sonnet_all_runs_pooled': describe(strict[(strict.model == 'sonnet') & ~strict.leak]),
    'hour_bands_primary': {b_: describe(primary[primary.hours.map(band) == b_]) for b_ in ['<=1h', '1-4h', '>4h']},
}
res['iface_vs_strict'] = iface_vs_strict(out)

def interaction(d):
    """Exploratory (not preregistered): does the hours effect differ by model? solved ~ log2h * model."""
    d = d.copy(); d['model'] = pd.Categorical(d.model, categories=MODELS)
    full = smf.gee('solved ~ log2h * model', groups='key', data=d, family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit()
    terms = [k for k in full.params.index if ':' in k]
    # Wald test that all interaction terms are zero
    R = np.zeros((len(terms), len(full.params))); idx = list(full.params.index)
    for i, t in enumerate(terms): R[i, idx.index(t)] = 1
    w = full.wald_test(R, scalar=True)
    ci = full.conf_int()
    return {'wald_chi2': round(float(w.statistic), 3), 'df': len(terms), 'p': round(float(w.pvalue), 4),
            'terms': {k: {'OR': round(math.exp(full.params[k]), 3), 'CI95': [round(math.exp(ci.loc[k, 0]), 3), round(math.exp(ci.loc[k, 1]), 3)],
                          'p': round(float(full.pvalues[k]), 4)} for k in terms},
            'slope_by_model_OR_per_doubling': {m: round(math.exp(full.params['log2h'] + (full.params.get(f'log2h:model[T.{m}]', 0))), 3) for m in MODELS}}

def by_band_model(d):
    t = {}
    for b_ in ['<=1h', '1-4h', '>4h']:
        x = d[d.hours.map(band) == b_]
        t[b_] = {m: f"{int(x[x.model == m].solved.sum())}/{int((x.model == m).sum())}" for m in MODELS}
    return t

res['exploratory_size_by_model'] = {'interaction_gee_primary': interaction(primary), 'solved_by_band_primary': by_band_model(primary)}
def tests_vs_strict(tests):
    r = {}
    for mo in ['fable', 'opus']:
        tt = tests[tests.model == mo].set_index('key').solved
        ss = strict[(strict.model == mo) & (strict.run == 1)].set_index('key').solved
        k = tt.index.intersection(ss.index)
        b = int(((ss[k] == 0) & (tt[k] == 1)).sum()); c = int(((ss[k] == 1) & (tt[k] == 0)).sum())
        r[mo] = {'issues': int(len(k)), 'strict': int(ss[k].sum()), 'tests': int(tt[k].sum()), 'only_tests': b, 'only_strict': c,
                 'mcnemar_p': round(float(mcnemar([[0, c], [b, 0]], exact=True).pvalue), 4) if len(k) else None,
                 'by_band': {b_: f"{int(tt[[x for x in k if band(hours[x]) == b_]].sum())}/{int(ss[[x for x in k if band(hours[x]) == b_]].sum())}/{len([x for x in k if band(hours[x]) == b_])} (tests/strict/n)" for b_ in ['<=1h', '1-4h', '>4h']}}
    return r
# Two opus 'tests' runs (MDL-89893, MDL-89913) hit a model fallback in run 1 and were redone as run 2 (deviazioni.txt):
# primary = latest run per (key, model); sensitivity = run 1 only.
tall = out[out.cond == 'tests'].sort_values('run')
tests = tall.drop_duplicates(['key', 'model'], keep='last')
if len(tests):
    res['tests_vs_strict'] = tests_vs_strict(tests)
    res['tests_vs_strict_sens_run1'] = tests_vs_strict(tall[tall.run == 1])
if False:
    r = {}
    for mo in ['fable', 'opus']:
        tt = tests[tests.model == mo].set_index('key').solved
        ss = strict[(strict.model == mo) & (strict.run == 1)].set_index('key').solved
        k = tt.index.intersection(ss.index)
        b = int(((ss[k] == 0) & (tt[k] == 1)).sum()); c = int(((ss[k] == 1) & (tt[k] == 0)).sum())
        r[mo] = {'issues': int(len(k)), 'strict': int(ss[k].sum()), 'tests': int(tt[k].sum()), 'only_tests': b, 'only_strict': c,
                 'mcnemar_p': round(float(mcnemar([[0, c], [b, 0]], exact=True).pvalue), 4) if len(k) else None,
                 'by_band': {b_: f"{int(tt[[x for x in k if band(hours[x]) == b_]].sum())}/{int(ss[[x for x in k if band(hours[x]) == b_]].sum())}/{len([x for x in k if band(hours[x]) == b_])} (tests/strict/n)" for b_ in ['<=1h', '1-4h', '>4h']}}
    res['tests_vs_strict'] = r
res['agent_cost'] = {mo: {'median_tokens': int(primary[primary.model == mo].tokens.median()), 'median_seconds': round(primary[primary.model == mo].duration_ms.median() / 1000, 1)}
                     for mo in MODELS if (primary.model == mo).any()}
res['human_hours'] = {'median': round(float(np.median(list(hours[k] for k in valid))), 2), 'min': min(hours[k] for k in valid), 'max': max(hours[k] for k in valid)}

json.dump(res, open(f'{A}/results.json', 'w'), indent=1, default=str)
print(json.dumps({k: res[k] for k in ['coverage', 'descriptive_primary', 'gee_primary', 'horizon_primary', 'reliability_sonnet']}, indent=1, default=str))

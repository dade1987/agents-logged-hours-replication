#!/usr/bin/env python3
"""Further exploratory analyses for the revision (2 November 2026; not preregistered).
Same primary samples as robustness.py. Extra inputs: worklog_roles.csv, mariadb/clarity/ratings.json,
failure_audit/*_final_codes.json and *_results.json, mariadb/results.jsonl (all runs).
Output: analysis/robustness/robustness2.json.

1. Hours logged by the developer who wrote the fix, instead of all logged hours.
2. Small-sample corrected (Mancl-DeRouen, bias-reduced) sandwich standard errors for H1, H3 and the Moodle primary model.
3. H2 on all three MariaDB runs (GEE clustered by issue, run as a factor).
4. Excluding issues rated unclear or partly clear (extension of sensitivity analysis b).
5. Moodle omnibus Wald test for the model terms.
6. Failure audit: Newcombe 95% CIs for the short-minus-long difference in the M share and in the W share;
   Moodle M share without the cases that failed only because a fixture file was not copied.
7. Working correlation of the primary GEEs."""
import json, math
import numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
from scipy.stats import norm, spearmanr
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'analysis' / 'robustness'
MODELS = ['haiku', 'sonnet', 'opus', 'fable']
SEED = 2026

# primary samples
mh = {};
for l in open(ROOT / 'moodle' / 'issues.jsonl'):
    r = json.loads(l); mh[r['key']] = r['hours']
mv = open(ROOT / 'moodle' / 'issues.txt').read().split()
mo = pd.read_csv(ROOT / 'moodle' / 'results.csv'); mo = mo[(mo.cond == 'strict') & (mo.run == 1) & mo.key.isin(mv)].copy()
ma = pd.read_csv(ROOT / 'analysis' / 'moodle' / 'audit_runs.csv').fillna(''); ma = ma[(ma.cond == 'strict') & (ma.run == 1)]
leak = {(r.key, r.model) for r in ma.itertuples() if 'seen' in r.flags}
mo = mo[[(k, m) not in leak for k, m in zip(mo.key, mo.model)]].copy()
mo['hours'] = mo.key.map(mh); mo['project'] = 'moodle'
fz = json.load(open(ROOT / 'mariadb' / 'frozen_sample.json')); dh = {x['key']: x['hours'] for x in fz}; fdate = {x['key']: x['fix_date'] for x in fz}
rows = []
for l in open(ROOT / 'mariadb' / 'results.jsonl'):
    r = json.loads(l); k, m, c, run = r['run'].split('_')
    rows.append(dict(key=k, model=m, run=int(run), solved=int(r['result'] == 'PASS')))
md = pd.DataFrame(rows).drop_duplicates(['key', 'model', 'run'], keep='last')
md = md[(md.run == 1) & md.key.isin(dh)].copy(); md['hours'] = md.key.map(dh); md['project'] = 'mariadb'
fs = pd.read_csv(OUT / 'fix_size.csv'); fl = {(r.project, r.key): r.fix_lines for r in fs.itertuples()}
cr = pd.read_csv(OUT / 'issue_created.csv'); created = {(r.project, r.key): r.created[:10] for r in cr.itertuples()}
for d in (mo, md):
    d['log2h'] = np.log2(d.hours)
    d['fix_lines'] = [fl[(p, k)] for p, k in zip(d.project, d.key)]
    d['log2fix'] = np.log2(d.fix_lines + 1)
    d['created'] = [created[(p, k)] for p, k in zip(d.project, d.key)]
pool = pd.concat([mo, md], ignore_index=True)

def fit(formula, x):
    x = x.copy(); x['model'] = pd.Categorical(x.model, categories=MODELS)
    if 'project' in formula: x['project'] = pd.Categorical(x.project, categories=['moodle', 'mariadb'])
    return smf.gee(formula, groups='key', data=x, family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit()
def orr(m, k, level=0.95):
    ci = m.conf_int(alpha=1 - level)
    return {'OR': round(math.exp(m.params[k]), 3), f'CI{int(level*100)}': [round(math.exp(ci.loc[k, 0]), 3), round(math.exp(ci.loc[k, 1]), 3)], 'p': round(float(m.pvalues[k]), 4)}
res = {}
def wald_models(m):
    idx = list(m.params.index); terms = [k for k in idx if k.startswith('model')]
    R = np.zeros((len(terms), len(idx)))
    for i, k in enumerate(terms): R[i, idx.index(k)] = 1
    w = m.wald_test(R, scalar=True); return {'chi2': round(float(w.statistic), 3), 'df': len(terms), 'p': round(float(w.pvalue), 4)}
def fit_br(formula, x):
    x = x.copy(); x['model'] = pd.Categorical(x.model, categories=MODELS)
    if 'project' in formula: x['project'] = pd.Categorical(x.project, categories=['moodle', 'mariadb'])
    return smf.gee(formula, groups='key', data=x, family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit(cov_type='bias_reduced')

# 1. developer-only hours
wr = pd.read_csv(OUT / 'worklog_roles.csv')
dev = {(r.project, r.key): r.hours_developer for r in wr.itertuples()}
res['developer_hours'] = {'share_of_hours_by_developer': {p: round(float(g.hours_developer.sum() / g.hours_all.sum()), 3) for p, g in wr.groupby('project')},
                          'issues_with_developer_hours': {p: int((g.hours_developer > 0).sum()) for p, g in wr.groupby('project')},
                          'issues': {p: int(len(g)) for p, g in wr.groupby('project')},
                          'method_counts': {f'{p}/{m}': int(n) for (p, m), n in wr.groupby(['project', 'method']).size().items()}}
for name, x, extra in [('moodle', mo, ''), ('mariadb', md, ''), ('pooled', pool, ' + project')]:
    y = x.copy(); y['devh'] = [dev[(p, k)] for p, k in zip(y.project, y.key)]
    y = y[y.devh > 0].copy(); y['log2dev'] = np.log2(y.devh)
    res['developer_hours'][name] = {'issues': int(y.key.nunique()),
        'developer_hours': orr(fit('solved ~ log2dev + model' + extra, y), 'log2dev'),
        'all_hours_same_issues': orr(fit('solved ~ log2h + model' + extra, y), 'log2h')}

# 2. bias-reduced sandwich SEs
res['bias_reduced_se'] = {}
for name, x, f, k in [('moodle_primary', mo, 'solved ~ log2h + model', 'log2h'), ('mariadb_H1', md, 'solved ~ log2h + model', 'log2h'),
                      ('H3_pooled', pool, 'solved ~ log2h + project + model', 'log2h'), ('H3_interaction', pool, 'solved ~ log2h * project + model', 'log2h:project[T.mariadb]')]:
    m = fit_br(f, x); r = orr(m, k)
    if name in ('mariadb_H1', 'H3_pooled'): r['p_one_sided'] = round(float(norm.cdf(m.params[k] / m.bse[k])), 4)
    if name == 'mariadb_H1': r['H2_wald'] = wald_models(m)
    res['bias_reduced_se'][name] = r

# 3. H2 on all runs
rows = []
for l in open(ROOT / 'mariadb' / 'results.jsonl'):
    r = json.loads(l); k, m, c, run = r['run'].split('_')
    rows.append(dict(key=k, model=m, run=int(run), solved=int(r['result'] == 'PASS')))
al = pd.DataFrame(rows).drop_duplicates(['key', 'model', 'run'], keep='last'); al = al[al.key.isin(dh)].copy()
al['log2h'] = np.log2(al.key.map(dh)); al['run'] = al.run.astype(str)
m = fit('solved ~ log2h + model + C(run)', al)
res['mariadb_all_runs'] = {'n': int(len(al)), 'log2h': orr(m, 'log2h'), 'H2_wald': wald_models(m),
                           'models': {k: orr(m, k) for k in m.params.index if k.startswith('model')}}

# 4. excluding unclear and partly clear issues
rt = json.load(open(ROOT / 'mariadb' / 'clarity' / 'ratings.json'))
keep = {k for k, v in rt.items() if v.get('giudizio') == 'chiara'}
x = md[md.key.isin(keep)]; m = fit('solved ~ log2h + model', x)
res['b_extended_clear_only'] = {'issues': int(x.key.nunique()), 'log2h': orr(m, 'log2h'), 'H1_p_one_sided': round(float(norm.cdf(m.params['log2h'] / m.bse['log2h'])), 4), 'H2_wald': wald_models(m)}

# 5. Moodle omnibus Wald for models
m = fit('solved ~ log2h + model', mo); res['moodle_models_wald'] = wald_models(m)
res['working_correlation'] = {'moodle': round(float(m.cov_struct.dep_params), 3), 'mariadb': round(float(fit('solved ~ log2h + model', md).cov_struct.dep_params), 3)}

# 6. failure audit CIs
def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h
def newcombe(k1, n1, k2, n2):
    p1, p2 = k1 / n1, k2 / n2; l1, u1 = wilson(k1, n1); l2, u2 = wilson(k2, n2)
    d = p1 - p2
    return [round(d, 3), round(d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), 3), round(d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2), 3)]
res['failure_audit'] = {}
for proj in ('moodle', 'mariadb'):
    bs = json.load(open(ROOT / 'failure_audit' / f'{proj}_results.json'))['by_stratum']
    S, L = bs['S'], bs['L']
    out = {}
    for c in ('M', 'W'):
        out[f'{c}_share_short'] = [S['counts'].get(c, 0), S['n']]; out[f'{c}_share_long'] = [L['counts'].get(c, 0), L['n']]
        out[f'{c}_diff_short_minus_long_CI95'] = newcombe(S['counts'].get(c, 0), S['n'], L['counts'].get(c, 0), L['n'])
    res['failure_audit'][proj] = out
fx = json.load(open(ROOT / 'failure_audit' / 'moodle_fixture_recheck.json'))
fixed = {(k, r.split('_')[0]) for k, r in fx['now_pass'] if r.endswith('_strict_1')}
codes = json.load(open(ROOT / 'failure_audit' / 'moodle_final_codes.json'))
fixture_cases = [c['case'] for c in codes if (c['key'], c['model']) in fixed]
rest = [c for c in codes if c['case'] not in fixture_cases]
cnt = {st: {'n': sum(c['stratum'] == st for c in rest), 'M': sum(c['stratum'] == st and c['final'] == 'M' for c in rest)} for st in ('S', 'L')}
res['failure_audit']['moodle_without_fixture_cases'] = {'fixture_cases': fixture_cases, 'fixture_case_codes': [c['final'] for c in codes if c['case'] in fixture_cases],
    'M_short': [cnt['S']['M'], cnt['S']['n']], 'M_long': [cnt['L']['M'], cnt['L']['n']],
    'M_total': [cnt['S']['M'] + cnt['L']['M'], cnt['S']['n'] + cnt['L']['n']],
    'M_diff_short_minus_long_CI95': newcombe(cnt['S']['M'], cnt['S']['n'], cnt['L']['M'], cnt['L']['n'])}
json.dump(res, open(OUT / 'robustness2.json', 'w'), indent=1)
print(json.dumps(res, indent=1))

"""Preregistered analysis, MariaDB replication of study A+H (preregistration_mariadb_v1.md, OSF de6g3).
Inputs (mariadb/): frozen_sample.json, results.jsonl, runs.tsv, clarity/solution_in_text.json,
clarity/ratings.json (blind clarity ratings by an independent rater, see mariadb/deviations.txt);
analysis/mariadb/audit_runs.csv; Moodle rows for H3 from the moodle/ inputs.
Output: analysis/mariadb/results_mdb.json."""
import json, math, os, sys
from collections import defaultdict
import numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
from statsmodels.stats.inter_rater import fleiss_kappa
from scipy.stats import norm
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # repository root
S = ROOT / 'mariadb'; MS = ROOT / 'moodle'; MA = ROOT / 'analysis' / 'moodle'; A = ROOT / 'analysis' / 'mariadb'
SEED, NBOOT = 2026, 2000
MODELS = ['haiku', 'sonnet', 'opus', 'fable']
frozen = json.load(open(f'{S}/frozen_sample.json')); hours = {x['key']: x['hours'] for x in frozen}
rows = []
for l in open(f'{S}/results.jsonl'):
    try: r = json.loads(l)
    except Exception: continue
    k, mo, cond, run = r['run'].split('_')
    rows.append(dict(key=k, model=mo, cond=cond, run=int(run), result=r['result'], solved=int(r['result'] == 'PASS')))
d = pd.DataFrame(rows).drop_duplicates(['key', 'model', 'run'], keep='last')
d = d[d.key.isin(hours)].copy()
d['hours'] = d.key.map(hours); d['log2h'] = np.log2(d.hours)
conf = pd.read_csv(f'{S}/runs.tsv', sep='\t', header=None, names=['key', 'model', 'cond', 'run', 'confidence', 'ts']).drop_duplicates(['key', 'model', 'run'], keep='last')
d = d.merge(conf[['key', 'model', 'run', 'confidence']], how='left', on=['key', 'model', 'run'])
aud = pd.read_csv(f'{A}/audit_runs.csv').fillna('')
d = d.merge(aud[['key', 'model', 'run', 'flags']].drop_duplicates(['key', 'model', 'run'], keep='last'), how='left', on=['key', 'model', 'run'])
d['flags'] = d['flags'].fillna('')
res = {'n_frozen': len(hours), 'coverage': {'results': int(len(d)), 'expected': len(hours) * 12,
       'run1_issues_complete': int((d[d.run == 1].groupby('key').model.nunique() == 4).sum()),
       'result_counts': d.result.value_counts().to_dict()}}
def band(h): return '<=1h' if h <= 1 else ('1-4h' if h <= 4 else '>4h')
def fit(formula, x):
    x = x.copy(); x['model'] = pd.Categorical(x.model, categories=MODELS)
    return smf.gee(formula, groups='key', data=x, family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit()
def ortab(m):
    ci = m.conf_int()
    return {k: {'OR': round(math.exp(m.params[k]), 3), 'CI95': [round(math.exp(ci.loc[k, 0]), 3), round(math.exp(ci.loc[k, 1]), 3)], 'p': round(float(m.pvalues[k]), 4)} for k in m.params.index}
def primary_tests(x):
    m = fit('solved ~ log2h + model', x); t = ortab(m)
    z = m.params['log2h'] / m.bse['log2h']; t['H1_p_one_sided'] = round(float(norm.cdf(z)), 4)
    idx = list(m.params.index); terms = [k for k in idx if k.startswith('model')]
    R = np.zeros((len(terms), len(idx)))
    for i, k in enumerate(terms): R[i, idx.index(k)] = 1
    w = m.wald_test(R, scalar=True); t['H2_wald'] = {'chi2': round(float(w.statistic), 3), 'df': len(terms), 'p': round(float(w.pvalue), 4)}
    return t
def describe(x):
    return {mo: {'n': int((x.model == mo).sum()), 'solved': int(x[x.model == mo].solved.sum()),
                 'rate': round(float(x[x.model == mo].solved.mean()), 3) if (x.model == mo).any() else None} for mo in MODELS}
def h50(x):
    try: m = smf.glm('solved ~ log2h', data=x, family=sm.families.Binomial()).fit()
    except Exception: return None, None
    b0, b1 = m.params['Intercept'], m.params['log2h']
    return (2 ** (-b0 / b1) if b1 < 0 else None), b1
def horizon(x):
    rng = np.random.default_rng(SEED); o = {}
    for mo in MODELS:
        y = x[x.model == mo]
        if y.empty: continue
        est, slope = h50(y); ks = y.key.unique(); g = {k: y[y.key == k] for k in ks}; bs = []
        for _ in range(NBOOT):
            v, _ = h50(pd.concat([g[k] for k in rng.choice(ks, len(ks), replace=True)])); bs.append(v if v is not None else np.inf)
        bs = np.array(bs); hi = np.percentile(bs, 97.5)
        o[mo] = {'h50': None if est is None else round(est, 2), 'slope_log2h': None if slope is None else round(float(slope), 3),
                 'CI95': [round(float(np.percentile(bs, 2.5)), 2), round(float(hi), 2) if np.isfinite(hi) else 'inf'], 'share_boot_no_decline': round(float(np.mean(~np.isfinite(bs))), 3)}
    return o
def labour(x):
    per = x.groupby(['key', 'model']).solved.mean().unstack(); tot = sum(hours[k] for k in per.index)
    r = {mo: round(float(sum(hours[k] * per.loc[k, mo] for k in per.index if not pd.isna(per.loc[k, mo]))) / tot, 3) for mo in MODELS if mo in per}
    anym = per.fillna(0).max(axis=1); r['any_model'] = round(float(sum(hours[k] * (anym[k] > 0) for k in per.index)) / tot, 3); r['total_hours'] = round(tot, 1)
    r['by_band'] = {}
    for b in ['<=1h', '1-4h', '>4h']:
        ks = [k for k in per.index if band(hours[k]) == b]; th = sum(hours[k] for k in ks)
        if ks: r['by_band'][b] = {'issues': len(ks), 'hours': round(th, 1), 'share_any_model': round(sum(hours[k] * (anym[k] > 0) for k in ks) / th, 3)}
    return r
def reliability(x):
    o = {}
    for mo in MODELS:
        p = x[x.model == mo].pivot_table(index='key', columns='run', values='solved').dropna()
        if p.shape[1] < 3 or p.empty: o[mo] = {'note': 'fewer than 3 complete runs'}; continue
        tab = np.column_stack([(p == 0).sum(axis=1), (p == 1).sum(axis=1)])
        o[mo] = {'issues': int(len(p)), 'fleiss_kappa': round(float(fleiss_kappa(tab)), 3), 'per_run_solved': {int(c): int(p[c].sum()) for c in p.columns},
                 'always': int((p.sum(axis=1) == 3).sum()), 'never': int((p.sum(axis=1) == 0).sum())}
    return o
def calibration(x):
    o = {}
    for mo in MODELS:
        y = x[(x.model == mo) & x.confidence.notna()]
        if y.empty: continue
        p = y.confidence / 100; br = float(np.mean((p - y.solved) ** 2)); base = float(np.mean((y.solved.mean() - y.solved) ** 2))
        o[mo] = {'n': int(len(y)), 'brier': round(br, 3), 'brier_base_rate': round(base, 3)}
    return o
p1 = d[d.run == 1]
res['descriptive_primary'] = describe(p1)
res['primary'] = primary_tests(p1)
res['horizon_primary'] = horizon(p1)
res['labour_share_primary'] = labour(p1)
res['reliability'] = reliability(d)
res['calibration_primary'] = calibration(p1)
# H3: pooled with Moodle primary rows (strict, run 1, leak runs excluded, as in the Moodle primary analysis)
mh = {json.loads(l)['key']: json.loads(l)['hours'] for l in open(f'{MS}/issues.jsonl')}
mv = open(f'{MS}/issues.txt').read().split()
mo_ = pd.read_csv(f'{MS}/results.csv'); mo_ = mo_[(mo_.cond == 'strict') & (mo_.run == 1) & mo_.key.isin(mv)].copy()
ma = pd.read_csv(f'{MA}/audit_runs.csv').fillna(''); ma = ma[(ma.cond == 'strict') & (ma.run == 1)]
leak = {(r.key, r.model) for r in ma.itertuples() if 'seen' in r.flags}
mo_ = mo_[[(k, m) not in leak for k, m in zip(mo_.key, mo_.model)]]
mo_['log2h'] = np.log2(mo_.key.map(mh)); mo_['project'] = 'moodle'
pool = pd.concat([mo_[['key', 'model', 'solved', 'log2h', 'project']], p1.assign(project='mariadb')[['key', 'model', 'solved', 'log2h', 'project']]])
pool['project'] = pd.Categorical(pool.project, categories=['moodle', 'mariadb'])
mi = fit('solved ~ log2h * project + model', pool); mp = fit('solved ~ log2h + project + model', pool)
res['H3'] = {'interaction': ortab(mi)['log2h:project[T.mariadb]'], 'pooled_log2h': ortab(mp)['log2h'],
             'pooled_p_one_sided': round(float(norm.cdf(mp.params['log2h'] / mp.bse['log2h'])), 4)}
# Holm over H1 (one-sided), H2 (two-sided), H3 (pooled log2h, one-sided)
ps = {'H1': res['primary']['H1_p_one_sided'], 'H2': res['primary']['H2_wald']['p'], 'H3': res['H3']['pooled_p_one_sided']}
order = sorted(ps, key=ps.get); adj = {}; run_max = 0
for i, h in enumerate(order): run_max = max(run_max, min(1, (len(ps) - i) * ps[h])); adj[h] = round(run_max, 4)
res['holm_adjusted_p'] = adj
# Sensitivity analyses (a)-(e)
sens = {}
mv3 = d.groupby(['key', 'model']).filter(lambda g: g.run.nunique() == 3).groupby(['key', 'model']).agg(solved=('solved', lambda s: int(s.sum() >= 2)), log2h=('log2h', 'first')).reset_index()
if len(mv3): sens['a_majority_vote'] = {'n': int(len(mv3)), 'descriptive': describe(mv3), 'gee': primary_tests(mv3)}
cr = f'{S}/clarity/ratings.json'
if os.path.exists(cr):
    rt = json.load(open(cr)); unclear = {k for k, v in rt.items() if v.get('giudizio') == 'poco_chiara'}
    x = p1[~p1.key.isin(unclear)]; sens['b_exclude_unclear'] = {'excluded_issues': sorted(unclear), 'n': int(len(x)), 'gee': primary_tests(x)}
else: sens['b_exclude_unclear'] = 'pending: clarity ratings not yet collected'
x = p1[p1['flags'] == '']; sens['c_exclude_audit_flags'] = {'excluded_runs': int((p1['flags'] != '').sum()), 'gee': primary_tests(x)}
x = p1.copy(); x['band'] = pd.Categorical(x.hours.map(band), categories=['<=1h', '1-4h', '>4h']); x['model'] = pd.Categorical(x.model, categories=MODELS)
mb = smf.gee('solved ~ C(band) + model', groups='key', data=x, family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit()
sens['d_hour_bands'] = {'gee': {k: v for k, v in ortab(mb).items() if 'band' in k}, 'descriptive': {b: describe(x[x.band == b]) for b in ['<=1h', '1-4h', '>4h']}}
sol = set(json.load(open(f'{S}/clarity/solution_in_text.json'))['flagged'])
x = p1[~p1.key.isin(sol)]; sens['e_exclude_solution_in_text'] = {'excluded_issues': sorted(sol & set(p1.key)), 'gee': primary_tests(x)}
res['sensitivity'] = sens
json.dump(res, open(f'{A}/results_mdb.json', 'w'), indent=1, default=str)
print(json.dumps({k: res[k] for k in ['coverage', 'descriptive_primary', 'primary', 'H3', 'holm_adjusted_p']}, indent=1, default=str))

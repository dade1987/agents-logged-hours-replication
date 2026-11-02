#!/usr/bin/env python3
"""Exploratory robustness analyses requested by the simulated EMSE review (2 November 2026; not preregistered).
Inputs: the primary samples of both studies (as in analysis_moodle.py / analysis_mariadb.py), fix_size.csv, issue_created.csv,
failure_audit/moodle_fixture_recheck.json.
Output: analysis/robustness/robustness.json and figure_hours_curve.png.

1. Human fix size (non-test lines changed) next to logged hours, per project and pooled.
2. Moodle restricted to the MariaDB hour range (<= 8 h) and to <= 40 h.
3. H3 interaction read with a 90% CI (equivalence-style reading).
4. Power of the H1 test for the MariaDB design, by simulation.
5. Spline in log2(hours) (pooled) and a figure of the fitted curves with binned observed rates.
6. Influence: leave-one-issue-out range of the Moodle hours odds ratio.
7. Moodle primary results with the test-support files copied (fixture re-check).
8. Contamination: issues created in 2026, issues created after 1 June 2026, MariaDB without the issue whose fix commit predates July 2026.
9. Uncertainty of the share of plausibly correct failures carried into the Moodle odds ratio (bootstrap over audited cases)."""
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

# 1. fix size
res['fix_size'] = {}
for name, x, extra in [('moodle', mo, ''), ('mariadb', md, ''), ('pooled', pool, ' + project')]:
    iss = x.drop_duplicates('key')
    rho = spearmanr(iss.hours, iss.fix_lines)
    res['fix_size'][name] = {
        'issues': int(len(iss)), 'fix_lines_median': float(iss.fix_lines.median()),
        'spearman_hours_fix_lines': [round(float(rho.statistic), 3), round(float(rho.pvalue), 4)],
        'hours_only': orr(fit('solved ~ log2h + model' + extra, x), 'log2h'),
        'fix_only': orr(fit('solved ~ log2fix + model' + extra, x), 'log2fix'),
        'both': {k: orr(m, k) for m in [fit('solved ~ log2h + log2fix + model' + extra, x)] for k in ('log2h', 'log2fix')}}

# 2. Moodle in the MariaDB hour range
res['moodle_restricted'] = {}
for cap in (8, 40):
    x = mo[mo.hours <= cap]
    res['moodle_restricted'][f'<= {cap} h'] = {'issues': int(x.key.nunique()), 'log2h': orr(fit('solved ~ log2h + model', x), 'log2h')}

# 3. H3 interaction, 90% CI
mi = fit('solved ~ log2h * project + model', pool)
res['H3_interaction_90'] = orr(mi, 'log2h:project[T.mariadb]', 0.90)

# 4. power of H1 (one-sided 0.05) for the MariaDB design: 68 issues with their hours, 4 models, run 1
rng = np.random.default_rng(SEED)
iss = md.drop_duplicates('key')[['key', 'log2h']].reset_index(drop=True)
base = md.solved.mean(); model_or = {'haiku': 1.0, 'sonnet': 0.81, 'opus': 1.50, 'fable': 2.02}
res['power_H1'] = {}
for true_or in (0.75, 0.6):
    for sd in (1.0, 2.0):
        hits = 0; nsim = 300
        for _ in range(nsim):
            u = rng.normal(0, sd, len(iss))
            b0 = math.log(base / (1 - base)) - math.log(true_or) * iss.log2h.mean()
            sim = []
            for i, r in iss.iterrows():
                for m in MODELS:
                    eta = b0 + math.log(true_or) * r.log2h + math.log(model_or[m]) + u[i]
                    sim.append(dict(key=r.key, model=m, log2h=r.log2h, solved=int(rng.random() < 1 / (1 + math.exp(-eta)))))
            s = pd.DataFrame(sim)
            try:
                m = fit('solved ~ log2h + model', s)
                if norm.cdf(m.params['log2h'] / m.bse['log2h']) < 0.05: hits += 1
            except Exception: pass
        res['power_H1'][f'OR {true_or}, issue sd {sd}'] = round(hits / nsim, 3)

# 5. spline (pooled) and figure
from patsy import dmatrix
ms = fit('solved ~ bs(log2h, df=3) + project + model', pool)
ml = fit('solved ~ log2h + project + model', pool)
res['spline_pooled'] = {'QIC_linear': round(float(ml.qic()[0]), 2), 'QIC_spline': round(float(ms.qic()[0]), 2)}
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.4, 3.8))
col = {'moodle': '#1f6fb2', 'mariadb': '#c2571a'}
for p in ('moodle', 'mariadb'):
    x = pool[pool.project == p]
    grid = np.linspace(x.log2h.min(), x.log2h.max(), 60)
    for f, ls in ((ml, '-'), (ms, '--')):
        g = pd.DataFrame({'log2h': grid, 'project': p, 'model': 'haiku'})
        g['project'] = pd.Categorical(g.project, categories=['moodle', 'mariadb']); g['model'] = pd.Categorical(g.model, categories=MODELS)
        pr = np.mean([f.predict(g.assign(model=pd.Categorical([mm] * len(g), categories=MODELS))) for mm in MODELS], axis=0)
        ax.plot(2 ** grid, pr, ls, color=col[p], lw=1.6, label=f'{p} ({"linear" if ls == "-" else "spline"})')
    bins = pd.qcut(x.log2h, 5, duplicates='drop')
    b = x.groupby(bins, observed=True).agg(h=('hours', 'median'), s=('solved', 'mean'), n=('solved', 'size'))
    ax.scatter(b.h, b.s, color=col[p], s=18 + b.n / 3, alpha=0.7)
ax.set_xscale('log', base=2); ax.set_xlabel('Hours logged by the developers (log scale)'); ax.set_ylabel('Share of patches that pass')
ax.set_ylim(0, 1); ax.legend(fontsize=8, frameon=False); ax.grid(alpha=0.25)
fig.tight_layout(); fig.savefig(OUT / 'figure_hours_curve.png', dpi=200)

# 6. leave-one-issue-out, Moodle
ors = [math.exp(fit('solved ~ log2h + model', mo[mo.key != k]).params['log2h']) for k in mo.key.unique()]
res['moodle_leave_one_issue_out'] = {'min': round(min(ors), 3), 'max': round(max(ors), 3)}

# 7. fixture re-check applied to the Moodle primary sample
rc = json.load(open(ROOT / 'failure_audit' / 'moodle_fixture_recheck.json'))
now = {(k, p.split('_')[0]) for k, p in rc['now_pass'] if p.endswith('_strict_1')}
mf = mo.copy(); mf['solved'] = [1 if (k, m) in now else s for k, m, s in zip(mf.key, mf.model, mf.solved)]
res['moodle_with_fixtures'] = {'solved': {m: int(mf[mf.model == m].solved.sum()) for m in MODELS},
                               'n': {m: int((mf.model == m).sum()) for m in MODELS},
                               'log2h': orr(fit('solved ~ log2h + model', mf), 'log2h'),
                               'with_fix_size': {k: orr(mm, k) for mm in [fit('solved ~ log2h + log2fix + model', mf)] for k in ('log2h', 'log2fix')}}
pf = pd.concat([mf, md], ignore_index=True)
res['pooled_with_moodle_fixtures'] = {'log2h': orr(fit('solved ~ log2h + project + model', pf), 'log2h'),
                                      'interaction': orr(fit('solved ~ log2h * project + model', pf), 'log2h:project[T.mariadb]')}

# 8. contamination sensitivity
res['contamination'] = {}
for lab, cond in (('created_2026', lambda d: d.created >= '2026-01-01'), ('created_after_2026-06-01', lambda d: d.created >= '2026-06-01')):
    x1, x2 = mo[cond(mo)], md[cond(md)]
    res['contamination'][lab] = {'moodle_issues': int(x1.key.nunique()), 'mariadb_issues': int(x2.key.nunique()),
                                 'moodle': orr(fit('solved ~ log2h + model', x1), 'log2h'),
                                 'mariadb': orr(fit('solved ~ log2h + model', x2), 'log2h'),
                                 'pooled': orr(fit('solved ~ log2h + project + model', pd.concat([x1, x2])), 'log2h')}
early = sorted(k for k, d in fdate.items() if d < '2026-07-01')
x = md[~md.key.isin(early)]
res['contamination']['mariadb_without_early_fix_commit'] = {'excluded': early, 'log2h': orr(fit('solved ~ log2h + model', x), 'log2h')}

# 9. uncertainty of the plausibly-correct share (Moodle, M counted as solved), bootstrap over audited cases per stratum
codes = json.load(open(ROOT / 'failure_audit' / 'moodle_final_codes.json'))
fails = mo[mo.solved == 0]
boot = []
for b in range(500):
    shares = {}
    for st in 'SL':
        cs = [c['final'] for c in codes if c['stratum'] == st]
        sm_ = rng.choice(cs, len(cs)); shares[st] = float(np.mean(sm_ == 'M'))
    y = mo.copy()
    flip = [(s == 0) and (rng.random() < shares['S' if h <= 4 else 'L']) for s, h in zip(y.solved, y.hours)]
    y['solved'] = np.where(flip, 1, y.solved)
    boot.append(fit('solved ~ log2h + model', y).params['log2h'])
res['moodle_M_as_solved_bootstrap'] = {'OR_median': round(math.exp(float(np.median(boot))), 3),
                                       'CI95': [round(math.exp(float(np.quantile(boot, 0.025))), 3), round(math.exp(float(np.quantile(boot, 0.975))), 3)]}

json.dump(res, open(OUT / 'robustness.json', 'w'), indent=1)
print(json.dumps(res, indent=1))

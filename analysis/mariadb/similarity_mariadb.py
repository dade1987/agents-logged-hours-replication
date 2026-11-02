#!/usr/bin/env python3
"""Preregistered exploratory analysis (MariaDB, Section 5 of the preregistration): similarity of each agent patch to the human fix.
Normalised Levenshtein similarity (rapidfuzz, 1 = identical) between the changed lines (+/-, stripped) of the agent patch and
those of the human fix, non-test files only (files under mysql-test/ excluded), as in the Moodle quality scan.
Needs a MariaDB clone in MARIADB (default /home/user/mariadb) for the human diffs.
Output: analysis/mariadb/similarity_mariadb.json (and similarity_mariadb.csv per run)."""
import csv, json, os, subprocess
import numpy as np
from rapidfuzz.distance import Levenshtein
from scipy.stats import mannwhitneyu
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; S = ROOT / 'mariadb'; A = ROOT / 'analysis' / 'mariadb'
MA = os.environ.get('MARIADB', '/home/user/mariadb')
def is_test(p): return p.startswith('mysql-test/') or '/mysql-test/' in p
def changed(text):
    out = []; cur = None
    for ln in text.splitlines():
        if ln.startswith('+++ '): cur = ln[6:] if ln.startswith('+++ b/') else None; continue
        if ln.startswith('--- ') or ln.startswith('diff --git'): continue
        if cur and not is_test(cur) and ln[:1] in '+-': out.append(ln[0] + ln[1:].strip())
    return '\n'.join(out)
fz = {x['key']: x for x in json.load(open(S / 'frozen_sample.json'))}
human = {k: changed(subprocess.run(['git', '-C', MA, 'diff', x['commit'] + '^', x['commit']], capture_output=True, text=True, errors='replace').stdout) for k, x in fz.items()}
res = {}
for l in open(S / 'results.jsonl'):
    r = json.loads(l); res[r['run']] = r['result']
rows = []
for run, out in sorted(res.items()):
    k, m, c, n = run.split('_')
    if k not in fz: continue
    p = S / 'patches' / f'{run}.diff'
    t = open(p, errors='replace').read() if p.exists() else ''
    rows.append(dict(run=run, key=k, model=m, rep=int(n), solved=int(out == 'PASS'), sim=round(Levenshtein.normalized_similarity(changed(t), human[k]), 4)))
with open(A / 'similarity_mariadb.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
r1 = [r for r in rows if r['rep'] == 1]
s1 = [r['sim'] for r in r1 if r['solved']]; s0 = [r['sim'] for r in r1 if not r['solved']]
out = {'run1_median_by_model': {m: round(float(np.median([r['sim'] for r in r1 if r['model'] == m])), 3) for m in ('haiku', 'sonnet', 'opus', 'fable')},
       'run1_median_solved': round(float(np.median(s1)), 3), 'run1_median_unsolved': round(float(np.median(s0)), 3),
       'mannwhitney_p': round(float(mannwhitneyu(s1, s0).pvalue), 4), 'n_run1': len(r1)}
json.dump(out, open(A / 'similarity_mariadb.json', 'w'), indent=1); print(out)

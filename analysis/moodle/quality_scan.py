#!/usr/bin/env python3
"""Exploratory quality analysis (not preregistered): technical debt added by each patch.

For every issue, U = union of the production code files (PHP/JS, no tests) touched by the human
fix or by any agent patch. One SonarQube project per issue holds one folder per variant:
  before/  U at the parent of the fix commit (A^)
  human/   U after the human fix (A^ -> B, production files only)
  <patch>/ U after the agent patch (moodle/patches/<KEY>/<patch>.patch, production files only)
Debt = SonarQube sqale_index (remediation effort of code smells, minutes) of each variant folder, as in SQALE.
Delta = variant - before on the same files. Duplication detection is disabled (folders are copies).
Similarity to the human fix: normalised Levenshtein similarity (rapidfuzz, 1 = identical) between the
changed lines (+/-, production files only) of the agent patch and those of the human fix.

Usage: python3 quality_scan.py <out.jsonl> [KEY ...]   (default: all keys in issues.txt)
Needs a local SonarQube Community 26.9 on :9000, a Moodle clone (MOODLE), sonar-scanner (SONAR_SCANNER)
and an admin token in the environment variable SONAR_TOKEN.
"""
from rapidfuzz.distance import Levenshtein
import json, os, re, shutil, subprocess, sys, urllib.request, base64, urllib.parse
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # repository root
S = ROOT / 'moodle'
REPO = os.environ.get('MOODLE', '/home/user/moodle')
WORK = os.environ.get('SONAR_WORK', '/tmp/sonar_work')
SCAN = os.environ.get('SONAR_SCANNER', 'sonar-scanner')
TOK = os.environ['SONAR_TOKEN']
AUTH = {'Authorization': 'Basic ' + base64.b64encode((TOK + ':').encode()).decode()}

def api(path, method='GET'):
    body = urllib.request.urlopen(urllib.request.Request('http://localhost:9000' + path, method=method, headers=AUTH)).read()
    return json.loads(body) if body.strip() else {}

def G(*a, **k):
    return subprocess.run(['git', '-C', REPO, *a], capture_output=True, **k)

def is_code(f):
    fl = f.lower()
    if '/tests/' in fl or fl.startswith('tests/') or fl.endswith('_test.php') or '/fixtures/' in fl:
        return False
    return fl.endswith(('.php', '.js', '.mjs')) and not fl.endswith('.min.js') and '/build/' not in fl and '/yui/' not in fl

def effort_min(s):
    if not s: return 0
    d = dict((u, int(v)) for v, u in re.findall(r'(\d+)(d|h|min)', s))
    return d.get('d', 0) * 480 + d.get('h', 0) * 60 + d.get('min', 0)

def patch_files(text):
    return sorted({m for m in re.findall(r'^diff --git a/(\S+) b/', text, re.M)} | {m for m in re.findall(r'^\+\+\+ b/(\S+)', text, re.M)})

def churn(text, files):
    add = rem = 0; cur = None
    for ln in text.splitlines():
        if ln.startswith('+++ '): cur = ln[6:] if ln.startswith('+++ b/') else None; continue
        if ln.startswith('--- ') or ln.startswith('diff --git'): continue
        if cur in files:
            if ln.startswith('+'): add += 1
            elif ln.startswith('-'): rem += 1
    return add, rem

def changed_lines(text, files):
    out = []; cur = None
    for ln in text.splitlines():
        if ln.startswith('+++ '): cur = ln[6:] if ln.startswith('+++ b/') else None; continue
        if ln.startswith('--- ') or ln.startswith('diff --git'): continue
        if cur in files and ln[:1] in '+-': out.append(ln[0] + ln[1:].strip())
    return '\n'.join(out)

def extract(commit, files, dst):
    os.makedirs(dst, exist_ok=True)
    present = [ln.split('\t', 1)[1] for ln in G('ls-tree', commit, '--', *files, text=True).stdout.splitlines() if ' blob ' in ln]
    if present:
        subprocess.run(['tar', '-x', '-C', dst], input=G('archive', commit, '--', *present).stdout, check=True)

def apply(text, dst, files):
    """Apply only the hunks of `files` from a unified diff to the copy in dst. Returns '' or the error."""
    if not files: return ''
    args = ['git', 'apply', '--whitespace=nowarn', '--unsafe-paths'] + [f'--include={f}' for f in files]
    r = subprocess.run(args, input=text.encode(), cwd=dst, capture_output=True, env={**os.environ, 'GIT_DIR': '/nonexistent'})
    return r.stderr.decode()[:300] if r.returncode else ''

def scan_issue(key, a, b):
    A0 = G('rev-parse', f'{a}^', text=True).stdout.strip()
    variants = {'human': G('diff', '--no-renames', A0, b, text=True, errors='replace').stdout}
    pd = f'{S}/patches/{key}'
    for p in sorted(os.listdir(pd)) if os.path.isdir(pd) else []:
        if p.endswith('.patch'): variants[p[:-6]] = open(f'{pd}/{p}', errors='replace').read()
    vf = {v: [f for f in patch_files(t) if is_code(f)] for v, t in variants.items()}
    U = sorted(set().union(*vf.values()))
    hlines = changed_lines(variants['human'], set(vf['human']))
    rows = []
    base = f'{WORK}/{key}'; shutil.rmtree(base, ignore_errors=True)
    extract(A0, U, f'{base}/before')
    for v, t in variants.items():
        shutil.copytree(f'{base}/before', f'{base}/{v}')
        err = apply(t, f'{base}/{v}', vf[v])
        add, rem = churn(t, set(vf[v]))
        sim = Levenshtein.normalized_similarity(changed_lines(t, set(vf[v])), hlines)
        rows.append({'key': key, 'variant': v, 'files': vf[v], 'added': add, 'removed': rem, 'apply_error': err,
                     'lev_sim_human': round(sim, 4)})
    pk = 'q_' + key.replace('-', '_')
    try: api(f'/api/projects/delete?project={pk}', 'POST')
    except Exception: pass
    r = subprocess.run([SCAN, f'-Dsonar.projectKey={pk}', '-Dsonar.sources=.', '-Dsonar.host.url=http://localhost:9000',
                        f'-Dsonar.token={TOK}', '-Dsonar.cpd.exclusions=**/*', '-Dsonar.scm.disabled=true',
                        '-Dsonar.javascript.node.maxspace=4096', '-Dsonar.qualitygate.wait=true', '-Dsonar.qualitygate.timeout=1800'],
                       cwd=base, capture_output=True, text=True)
    if 'EXECUTION SUCCESS' not in r.stdout and 'QUALITY GATE STATUS' not in r.stdout:
        for x in rows: x['scan_error'] = r.stdout[-400:]
        return rows
    # Per-variant totals from the measures of each top folder (the issues API cannot page past 10,000 issues).
    agg = {}
    page = 1
    while True:
        q = urllib.parse.urlencode({'component': pk, 'metricKeys': 'sqale_index,code_smells,bugs,vulnerabilities',
                                    'strategy': 'children', 'ps': 500, 'p': page})
        res = api(f'/api/measures/component_tree?{q}')
        for c in res['components']:
            folder = c['path'].split('/', 1)[0] if 'path' in c else c['name'].split('/', 1)[0]
            g = agg.setdefault(folder, {'debt_min': 0, 'smells': 0, 'bugs': 0, 'vulns': 0})
            m = {x['metric']: int(float(x.get('value', 0))) for x in c['measures']}
            g['debt_min'] += m.get('sqale_index', 0); g['smells'] += m.get('code_smells', 0)
            g['bugs'] += m.get('bugs', 0); g['vulns'] += m.get('vulnerabilities', 0)
        if page * 500 >= res['paging']['total']: break
        page += 1
    b0 = agg.get('before', {'debt_min': 0, 'smells': 0, 'bugs': 0, 'vulns': 0})
    for x in rows:
        g = agg.get(x['variant'], {'debt_min': 0, 'smells': 0, 'bugs': 0, 'vulns': 0})
        x.update({k: g[k] for k in g}, **{'d_' + k: g[k] - b0[k] for k in g}, before_debt_min=b0['debt_min'], n_union_files=len(U))
    api(f'/api/projects/delete?project={pk}', 'POST')
    shutil.rmtree(base, ignore_errors=True)
    return rows

if __name__ == '__main__':
    out = sys.argv[1]
    keys = sys.argv[2:] or open(f'{S}/issues.txt').read().split()
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)['key'] for l in open(out)}
    commits = {l.split()[0]: l.split()[1:] for l in open(f'{S}/commits.txt') if l.strip()}
    for k in keys:
        if k in done: continue
        rows = scan_issue(k, *commits[k])
        with open(out, 'a') as f:
            for x in rows: f.write(json.dumps(x) + '\n')
        print(k, len(rows), rows[0].get('scan_error', 'ok')[:80], flush=True)

"""Freeze the MariaDB study sample from the oracle check (rule in preregistration section 3)."""
import json, random, hashlib
from pathlib import Path
P = Path(__file__).resolve().parents[1] / 'pilot'
OUT = Path(__file__).resolve().parents[1]
cand = {x['key']: x for x in json.load(open(f'{P}/candidates_mariadb.json'))}
orc = {}
for l in open(f'{P}/oracle_full.jsonl'):
    r = json.loads(l); orc[r['issue']] = r      # last line per issue wins (reruns)
excluded = {'MDEV-23086': 'pilot', 'MDEV-28922': 'pilot', 'MDEV-41667': 'issue page not public'}
rows, excl = [], []
for k, c in cand.items():
    if c['sanitizer']: excl.append((k, 'sanitizer-only')); continue
    if k in excluded: excl.append((k, excluded[k])); continue
    r = orc.get(k)
    if r is None: excl.append((k, 'no oracle result')); continue
    if not (r['before'] == 'FAIL' and r['after'] == 'PASS'):
        excl.append((k, f"oracle {r['before']}->{r['after']}")); continue
    rows.append({'key': k, 'commit': c['c'], 'hours': c['h'], 'fix_date': c['date'], 'tests': r['tests'].split()})
rows.sort(key=lambda x: x['key'])
if len(rows) > 80:
    rows = sorted(random.Random(20261027).sample(rows, 80), key=lambda x: x['key'])
txt = json.dumps(rows, indent=1)
open(OUT / 'frozen_sample.json', 'w').write(txt)
json.dump(excl, open(OUT / 'excluded.json', 'w'), indent=1)
print(len(rows), 'issues; excluded', len(excl)); print('sha256', hashlib.sha256(txt.encode()).hexdigest())
from collections import Counter; print(Counter(e[1].split(' ')[0] for e in excl))

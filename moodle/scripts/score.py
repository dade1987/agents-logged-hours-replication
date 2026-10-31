#!/usr/bin/env python3
# Reads moodle/eval_logs/*.log and writes moodle/results.csv: key,model,cond,run,solved
# Solved = every test file passes (no Errors/Failures, no fatal error), as with the human fix.
# Log markers: PRIMA = before the fix (oracle), DOPO = with the human fix, AGENTE <model_cond_run> = agent patch.
import glob, os, re, csv, sys
S = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # moodle/
def ok(line):
    r = line.split(': ', 1)[1] if ': ' in line else ''
    return (r.startswith('OK') or re.match(r'Tests: \d+, Assertions: \d+', r)) and not re.search(r'Errors:|Failures:', r)
rows = []
for f in sorted(glob.glob(f'{S}/eval_logs/*.log')):
    k = os.path.basename(f)[:-4]; sec = None; blocks = {}
    for l in open(f, errors='replace'):
        l = l.rstrip('\n')
        if l in ('PRIMA:', 'DOPO:'): sec = l[:-1]; blocks[sec] = []
        elif l.startswith('AGENTE '): sec = l[7:-1]; blocks[sec] = []
        elif l.startswith('TEST ') and sec: blocks[sec].append(l)
    if not blocks.get('DOPO') or not all(ok(t) for t in blocks['DOPO']):
        print('oracle check failed with the human fix', k, file=sys.stderr); continue
    for a, ts in blocks.items():
        if a in ('PRIMA', 'DOPO'): continue
        m, c, r = a.split('_')
        rows.append([k, m, c, r, int(len(ts) == len(blocks['DOPO']) and all(ok(t) for t in ts))])
with open(f'{S}/results.csv', 'w', newline='') as o:
    w = csv.writer(o); w.writerow(['key', 'model', 'cond', 'run', 'solved']); w.writerows(rows)
from collections import defaultdict
d = defaultdict(list)
for k, m, c, r, x in rows: d[(c, m)].append(x)
for (c, m), v in sorted(d.items()): print(f'{c} {m}: {sum(v)}/{len(v)}')

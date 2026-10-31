#!/usr/bin/env python3
"""For runs flagged moodle_seen/other_ws_seen in audit_runs.csv, list which leaked paths
match files changed by the human fix of that issue (relevant leak)."""
import csv, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # repository root
import gzip
def lines(p):
    with gzip.open(p, 'rt', errors='replace') as f: yield from f
T = ROOT / 'transcripts' / 'moodle'
S = ROOT / 'moodle'
A = ROOT / 'analysis' / 'moodle'
fix = {}
for l in open(f'{S}/issues.jsonl'):
    r = json.loads(l); fix[r['key']] = set(r['files'])
def txt(x):
    if isinstance(x, str): return x
    if isinstance(x, list): return '\n'.join(txt(i) for i in x)
    if isinstance(x, dict): return txt(x.get('text', '')) if 'text' in x else txt(x.get('content', ''))
    return ''
pat = re.compile(r'(?:/home/user/|(?<![\w/.-])(?:\./)?)(?:moodle|ws/MDL-\d+_[a-z]+_[a-z]+_\d)/(public/[\w./-]+?\.(?:php|js|mustache|xml|scss|feature))')
rows = []
for r in csv.DictReader(open(A / 'audit_runs.csv')):
    if 'seen' not in r['flags']: continue
    seen = set()
    for l in lines(f"{T}/{r['agent_id']}.jsonl.gz"):
        ev = json.loads(l); m = ev.get('message') or ev
        c = m.get('content') if isinstance(m, dict) else None
        if not isinstance(c, list): continue
        for x in c:
            if isinstance(x, dict) and x.get('type') == 'tool_result':
                seen |= set(pat.findall(txt(x.get('content', ''))))
    rel = sorted(seen & fix.get(r['key'], set()))
    rows.append([r['agent_id'], r['key'], r['model'], r['cond'], r['run'], len(seen), len(rel), ' '.join(rel)])
with open(A / 'leak_check.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['agent_id', 'key', 'model', 'cond', 'run', 'paths_seen', 'fix_files_seen', 'fix_files']); w.writerows(rows)
for r in rows: print(*r[:7])

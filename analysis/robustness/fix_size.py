#!/usr/bin/env python3
"""Size of the human fix (non-test files) for every issue, from the project Git histories.
Moodle: diff A^..B (moodle/commits.txt), test files = paths containing /tests/.
MariaDB: diff B^..B (mariadb/frozen_sample.json), test files = paths under mysql-test/ or */mysql-test/.
Needs clones in MOODLE (default /home/user/moodle) and MARIADB (default /home/user/mariadb).
Output: analysis/robustness/fix_size.csv (project,key,fix_lines,fix_files), so later scripts need no clone."""
import csv, json, os, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
MO = os.environ.get('MOODLE', '/home/user/moodle'); MA = os.environ.get('MARIADB', '/home/user/mariadb')
def size(repo, a, b, is_test):
    out = subprocess.run(['git', '-C', repo, 'diff', '--numstat', '--no-renames', a, b], capture_output=True, text=True, check=True).stdout
    lines = files = 0
    for l in out.splitlines():
        ad, de, p = l.split('\t', 2)
        if is_test(p) or ad == '-': continue
        lines += int(ad) + int(de); files += 1
    return lines, files
rows = []
valid = set(open(ROOT / 'moodle' / 'issues.txt').read().split())
for l in open(ROOT / 'moodle' / 'commits.txt'):
    k, a, b = l.split()
    if k in valid: rows.append(['moodle', k, *size(MO, a + '^', b, lambda p: '/tests/' in p)])
for x in json.load(open(ROOT / 'mariadb' / 'frozen_sample.json')):
    rows.append(['mariadb', x['key'], *size(MA, x['commit'] + '^', x['commit'], lambda p: p.startswith('mysql-test/') or '/mysql-test/' in p)])
with open(ROOT / 'analysis' / 'robustness' / 'fix_size.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['project', 'key', 'fix_lines', 'fix_files']); w.writerows(rows)
print(len(rows))

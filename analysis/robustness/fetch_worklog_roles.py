#!/usr/bin/env python3
"""Split the logged hours of every issue into the hours logged by the developer who wrote the fix
and the hours logged by anyone else (peer review, integration, testing, help).
Developer = a worklog author whose Jira display name equals the Git author name of a fix commit
(Moodle: commits A^..B of moodle/commits.txt; MariaDB: the fix commit); if no name matches, the
issue's assignee (when the API returns one); otherwise the developer is unknown.
Needs clones in MOODLE (default /home/user/moodle) and MARIADB (default /home/user/mariadb).
Source: public Jira REST APIs (moodle.atlassian.net, jira.mariadb.org), read on 2 November 2026.
Only role labels and hours are stored, no names.
Output: analysis/robustness/worklog_roles.csv (project,key,hours_all,hours_developer,n_loggers,method)."""
import csv, json, os, subprocess, time, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
MO = os.environ.get('MOODLE', '/home/user/moodle'); MA = os.environ.get('MARIADB', '/home/user/mariadb')
def norm(n): return ' '.join((n or '').lower().split())
def git_authors(repo, rng):
    return {norm(a) for a in subprocess.run(['git', '-C', repo, 'log', '--format=%an', rng], capture_output=True, text=True, check=True).stdout.splitlines()}
def get(url):
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'Accept': 'application/json'}), timeout=60) as r: return json.load(r)
        except Exception:
            time.sleep(2 ** (i + 1))
    raise RuntimeError(url)
def ident(u): return u.get('accountId') or u.get('name') or u.get('key')
def roles(base, api, key, authors):
    iss = get(f'{base}/rest/api/{api}/issue/{key}?fields=assignee')
    ass = iss['fields'].get('assignee'); ass = ident(ass) if ass else None
    wl, start = [], 0
    while True:
        d = get(f'{base}/rest/api/{api}/issue/{key}/worklog?startAt={start}&maxResults=100')
        wl += d['worklogs']; start += len(d['worklogs'])
        if not d['worklogs'] or start >= d['total']: break
    tot = sum(w['timeSpentSeconds'] for w in wl) / 3600
    devs = {ident(w['author']) for w in wl if norm(w['author'].get('displayName')) in authors}; method = 'git_author'
    if not devs and ass: devs, method = {ass}, 'assignee'
    if not devs: return round(tot, 3), '', len({ident(w['author']) for w in wl}), 'unknown'
    dev = sum(w['timeSpentSeconds'] for w in wl if ident(w['author']) in devs) / 3600
    return round(tot, 3), round(dev, 3), len({ident(w['author']) for w in wl}), method
rows = []
valid = set(open(ROOT / 'moodle' / 'issues.txt').read().split())
for l in open(ROOT / 'moodle' / 'commits.txt'):
    k, a, b = l.split()
    if k in valid: rows.append(['moodle', k, *roles('https://moodle.atlassian.net', 3, k, git_authors(MO, f'{a}^..{b}'))])
for x in json.load(open(ROOT / 'mariadb' / 'frozen_sample.json')):
    rows.append(['mariadb', x['key'], *roles('https://jira.mariadb.org', 2, x['key'], git_authors(MA, f"{x['commit']}^..{x['commit']}"))])
with open(ROOT / 'analysis' / 'robustness' / 'worklog_roles.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['project', 'key', 'hours_all', 'hours_developer', 'n_loggers', 'method']); w.writerows(rows)
print(len(rows))

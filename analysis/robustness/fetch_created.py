#!/usr/bin/env python3
"""Fetch the creation date of every issue from the public Jira instances (no login).
Output: analysis/robustness/issue_created.csv (project,key,created)."""
import csv, json, urllib.parse, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
mo = open(ROOT / 'moodle' / 'issues.txt').read().split()
ma = [x['key'] for x in json.load(open(ROOT / 'mariadb' / 'frozen_sample.json'))]
def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={'Accept': 'application/json'}), timeout=60))
rows = []
for i in range(0, len(mo), 50):
    q = urllib.parse.quote('key in (%s)' % ','.join(mo[i:i + 50]))
    for x in get(f'https://moodle.atlassian.net/rest/api/3/search/jql?jql={q}&fields=created&maxResults=100')['issues']:
        rows.append(['moodle', x['key'], x['fields']['created']])
for i in range(0, len(ma), 50):
    q = urllib.parse.quote('key in (%s)' % ','.join(ma[i:i + 50]))
    for x in get(f'https://jira.mariadb.org/rest/api/2/search?jql={q}&fields=created&maxResults=100')['issues']:
        rows.append(['mariadb', x['key'], x['fields']['created']])
with open(ROOT / 'analysis' / 'robustness' / 'issue_created.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['project', 'key', 'created']); w.writerows(sorted(rows))
print(len(rows))

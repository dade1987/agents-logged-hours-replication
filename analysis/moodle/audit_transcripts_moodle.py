#!/usr/bin/env python3
"""Audit agent transcripts for isolation breaches.
For each launched agent, scan its JSONL transcript and flag:
  moodle_seen   - a tool result contains a path inside /home/user/moodle (evaluation checkout)
  other_ws_seen - a tool result contains another workspace path (/home/user/ws/<other>)
  git_cmd       - a Bash command runs git
  test_run      - a Bash command runs phpunit/behat
Reads the sanitized transcripts in transcripts/moodle/<agent_id>.jsonl.gz.
Writes analysis/moodle/audit_runs.csv (agent_id,key,model,cond,run,flags)."""
import csv, json, os, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # repository root
import gzip
def lines(p):
    with gzip.open(p, 'rt', errors='replace') as f: yield from f
T = sys.argv[1] if len(sys.argv) > 1 else ROOT / 'transcripts' / 'moodle'
S = ROOT / 'moodle'
def txt(x):
    if isinstance(x, str): return x
    if isinstance(x, list): return '\n'.join(txt(i) for i in x)
    if isinstance(x, dict): return txt(x.get('text', '')) if 'text' in x else txt(x.get('content', ''))
    return ''
out = []
missing = 0
for row in csv.reader(open(f'{S}/agents_launched.tsv'), delimiter='\t'):
    aid, key, model, cond, run = row
    ws = f'{key}_{model}_{cond}_{run}'
    p = f'{T}/{aid}.jsonl.gz'
    if not os.path.exists(p): missing += 1; out.append([aid, key, model, cond, run, 'transcript_missing']); continue
    flags = set()
    for line in lines(p):
        try: ev = json.loads(line)
        except Exception: continue
        msg = ev.get('message') or ev
        content = msg.get('content') if isinstance(msg, dict) else None
        if not isinstance(content, list): continue
        for c in content:
            if not isinstance(c, dict): continue
            if c.get('type') == 'tool_use':
                if c.get('name') != 'Bash': continue
                s = (c.get('input') or {}).get('command', '')
                if re.search(r'(^|[;&|(]\s*)git\s', s): flags.add('git_cmd')
                if re.search(r'(^|[;&|(]\s*)(\S*/)?(phpunit|behat)\b', s): flags.add('test_run')
            elif c.get('type') == 'tool_result':
                s = txt(c.get('content', ''))
                if re.search(r'(/home/user/|(?<![\w/.-])(\./)?)moodle/(public|lib|admin|mod)/', s): flags.add('moodle_seen')
                for w in set(re.findall(r'(?:/home/user/|(?<![\w/.-])(?:\./)?)ws/(MDL-\d+_[a-z]+_[a-z]+_\d)', s)):
                    if w != ws: flags.add('other_ws_seen')
    out.append([aid, key, model, cond, run, ';'.join(sorted(flags))])
with open(ROOT / 'analysis' / 'moodle' / 'audit_runs.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['agent_id', 'key', 'model', 'cond', 'run', 'flags']); w.writerows(out)
print('agents', len(out), 'missing transcripts', missing)
from collections import Counter
print(Counter(fl for r in out for fl in r[5].split(';') if fl))

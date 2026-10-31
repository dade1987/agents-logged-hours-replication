#!/usr/bin/env python3
"""Audit MariaDB agent transcripts for isolation breaches (same logic as the Moodle audit).
Flags: src_seen (a tool result shows a path in the evaluation checkout /home/user/mdb_src, /home/user/mariadb or the build dir),
other_ws_seen (a tool result shows another issue's workspace), git_cmd, build_or_test_run (cmake/ninja/make/mtr), web_tool (web/Jira/GitHub tools, even if they failed), project_tool (project messaging tools), docs_tool (environment/docs help tools; no issue data).
Reads the sanitized transcripts in transcripts/mariadb/<agent_id>.jsonl.gz.
Writes analysis/mariadb/audit_runs.csv (agent_id,key,model,cond,run,flags)."""
import csv, json, os, re, sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]  # repository root
import gzip
def lines(p):
    with gzip.open(p, 'rt', errors='replace') as f: yield from f
T = sys.argv[1] if len(sys.argv) > 1 else ROOT / 'transcripts' / 'mariadb'
S = ROOT / 'mariadb'
def txt(x):
    if isinstance(x, str): return x
    if isinstance(x, list): return '\n'.join(txt(i) for i in x)
    if isinstance(x, dict): return txt(x.get('text', '')) if 'text' in x else txt(x.get('content', ''))
    return ''
out = []; missing = 0
for row in csv.reader(open(f'{S}/agents_launched.tsv'), delimiter='\t'):
    aid, key, model, cond, run = row
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
                n = c.get('name', '')
                nl = n.lower()
                if nl in ('webfetch', 'websearch') or 'atlassian' in nl or 'github' in nl: flags.add('web_tool')
                elif 'no_reply' in nl: pass
                elif 'hearthbot' in nl: flags.add('project_tool')
                elif nl.startswith('mcp__'): flags.add('docs_tool')
                if n != 'Bash': continue
                s = (c.get('input') or {}).get('command', '')
                if re.search(r'(^|[;&|(]\s*)git\s', s): flags.add('git_cmd')
                if re.search(r'(^|[;&|(]\s*)(\S*/)?(cmake|ninja|make|mysql-test-run(\.pl)?|mtr)\b', s): flags.add('build_or_test_run')
            elif c.get('type') == 'tool_result':
                s = txt(c.get('content', ''))
                if re.search(r'/home/user/(mdb_src|mariadb|mdb_build_dbg)/', s): flags.add('src_seen')
                for w in set(re.findall(r'/home/user/ws_mdb/(?:git_)?(MDEV-\d+)', s)):
                    if w != key: flags.add('other_ws_seen')
    out.append([aid, key, model, cond, run, ';'.join(sorted(flags))])
with open(ROOT / 'analysis' / 'mariadb' / 'audit_runs.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['agent_id', 'key', 'model', 'cond', 'run', 'flags']); w.writerows(out)
print('agents', len(out), 'missing transcripts', missing)
print(Counter(fl for r in out for fl in r[5].split(';') if fl))

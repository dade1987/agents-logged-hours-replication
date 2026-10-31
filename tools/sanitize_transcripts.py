"""Write sanitized agent transcripts: only user/assistant messages (no attachments, no meta/context),
tool results truncated, emails/tokens/session links removed."""
import csv, gzip, json, os, re, sys
# Usage: sanitize_transcripts.py <raw transcript dir (<agent_id>.output)> <output dir>
T, OUT = sys.argv[1], sys.argv[2]
LIM = None
SUBS = [(re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+'), '[email]'),
        (re.compile(r'(?i)bearer\s+[A-Za-z0-9._-]{8,}'), 'Bearer [redacted]'),
        (re.compile(r'\b(sk-ant-[\w-]+|ghp_\w+|gho_\w+|squ_\w+|sqp_\w+|sqa_\w+)'), '[redacted]'),
        (re.compile(r'https://claude\.ai/code/session_\w+'), '[session]'),
        (re.compile(r'session_\w{20,}'), '[session]')]
def scrub(s):
    for r, t in SUBS: s = r.sub(t, s)
    return s
def txt(x):
    if isinstance(x, str): return x
    if isinstance(x, list): return '\n'.join(txt(i) for i in x)
    if isinstance(x, dict): return txt(x.get('text', '')) if 'text' in x else txt(x.get('content', ''))
    return ''
PROJ = set()  # tool_use ids of project/environment tools whose outputs are not published
def clean(c):
    t = c.get('type')
    if t == 'tool_use' and (c.get('name') or '').startswith('mcp__'): PROJ.add(c.get('id'))
    if t == 'tool_result' and c.get('tool_use_id') in PROJ:
        return {'type': 'tool_result', 'is_error': bool(c.get('is_error')), 'content': '[output of a project/environment tool removed for privacy]'}
    if t == 'text': return {'type': 'text', 'text': scrub(c.get('text', ''))}
    if t == 'tool_use': return {'type': 'tool_use', 'name': c.get('name'), 'input': json.loads(scrub(json.dumps(c.get('input'))))}
    if t == 'tool_result':
        s = txt(c.get('content'))
        if LIM and len(s) > LIM: s = s[:LIM] + f'\n[... truncated, {len(s)} chars total]'
        return {'type': 'tool_result', 'is_error': bool(c.get('is_error')), 'content': scrub(s)}
    return None  # thinking and other blocks are dropped
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
for tsv, proj in [(ROOT / 'moodle' / 'agents_launched.tsv', 'moodle'), (ROOT / 'mariadb' / 'agents_launched.tsv', 'mariadb')]:
    os.makedirs(f'{OUT}/{proj}', exist_ok=True); n = 0
    for row in csv.reader(open(tsv), delimiter='\t'):
        aid = row[0]; p = f'{T}/{aid}.output'
        if not os.path.exists(p): continue
        recs = []
        for line in open(p, errors='replace'):
            try: e = json.loads(line)
            except Exception: continue
            if e.get('type') not in ('user', 'assistant') or e.get('isMeta'): continue
            m = e.get('message') or {}
            cont = m.get('content')
            if isinstance(cont, str): blocks = [{'type': 'text', 'text': scrub(cont)}]
            else: blocks = [b for b in (clean(c) for c in cont or [] if isinstance(c, dict)) if b]
            if not blocks: continue
            recs.append({'ts': e.get('timestamp'), 'role': m.get('role', e['type']), 'model': m.get('model'), 'content': blocks})
        with gzip.open(f'{OUT}/{proj}/{aid}.jsonl.gz', 'wt') as f:
            f.write(json.dumps({'agent_id': aid, 'issue': row[1], 'model': row[2], 'condition': row[3], 'run': row[4]}) + '\n')
            for r in recs: f.write(json.dumps(r, ensure_ascii=False) + '\n')
        n += 1
    print(proj, n)

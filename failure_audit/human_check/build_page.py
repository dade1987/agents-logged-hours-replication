"""Blind human check of the failure audit (24 cases): builds audit_gianluigi.html from the packets.
Case order and the id -> case map: failure_audit/human_check/sample_keys.json in the package (seed 20261103)."""
import json
rows = json.load(open('rows.json'))
html = open('template_audit.html').read().replace('__DATA__', json.dumps(rows, ensure_ascii=False).replace('</', '<\\/'))
open('audit_gianluigi.html', 'w').write(html); print(len(rows), len(html))

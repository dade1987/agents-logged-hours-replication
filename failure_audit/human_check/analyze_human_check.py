#!/usr/bin/env python3
"""Agreement between the blind human rater (human_ratings.json, 24 cases; filled in a spreadsheet copy of the page,
without AI) and the final AI codes of the failure audit. Output: human_check_results.json."""
import json, math
from collections import Counter
from pathlib import Path
H = Path(__file__).resolve().parent; FA = H.parent
keys = {c['id']: c for c in json.load(open(H / 'sample_keys.json'))['cases']}
codes = {c['case']: c for f in ('moodle_final_codes.json', 'mariadb_final_codes.json') for c in json.load(open(FA / f))}
hum = {r['id']: r['code'] for r in json.load(open(H / 'human_ratings.json'))}
pairs = [(i, keys[i]['project'], hum[i], codes[keys[i]['case']]['final']) for i in sorted(hum)]
def stats(ps, cats):
    n = len(ps); po = sum(h == a for _, _, h, a in ps) / n
    ch, ca = Counter(h for *_, h, _ in ps), Counter(a for *_, a in ps)
    pe = sum(ch[c] / n * ca[c] / n for c in cats); kappa = (po - pe) / (1 - pe) if pe < 1 else None
    pi = [(ch[c] + ca[c]) / (2 * n) for c in cats]; pe2 = sum(p * (1 - p) for p in pi) / (len(cats) - 1)
    return {'n': n, 'agree': sum(h == a for _, _, h, a in ps), 'observed': round(po, 3), 'kappa': round(kappa, 3), 'AC1': round((po - pe2) / (1 - pe2), 3)}
def wilson(k, n, z=1.959964):
    p = k / n; d = 1 + z * z / n; c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(c - h, 3), round(c + h, 3)]
bin_ = lambda x: 'W' if x == 'W' else 'notW'
res = {'four_codes': stats(pairs, ['W', 'M', 'A', 'U']),
       'wrong_vs_not_wrong': stats([(i, p, bin_(h), bin_(a)) for i, p, h, a in pairs], ['W', 'notW']),
       'confusion_human_x_ai': {f'{h}/{a}': n for (h, a), n in sorted(Counter((h, a) for *_, h, a in pairs).items())},
       'disagreements': [{'id': i, 'project': p, 'case': keys[i]['case'], 'human': h, 'ai': a} for i, p, h, a in pairs if h != a]}
for proj in ('moodle', 'mariadb', 'all'):
    ps = [x for x in pairs if proj in ('all', x[1])]; n = len(ps)
    kh = sum(h != 'W' for *_, h, _ in ps); ka = sum(a != 'W' for *_, a in ps)
    res[f'not_wrong_share_{proj}'] = {'n': n, 'human': [kh, wilson(kh, n)], 'ai': [ka, wilson(ka, n)],
                                      'human_M': sum(h == 'M' for *_, h, _ in ps), 'ai_M': sum(a == 'M' for *_, a in ps)}
ai_not_w = [x for x in pairs if x[3] != 'W']
res['ai_not_wrong_confirmed_by_human'] = [sum(h != 'W' for *_, h, _ in ai_not_w), len(ai_not_w)]
res['ai_wrong_confirmed_by_human'] = [sum(h == 'W' for *_, h, a in pairs if a == 'W'), sum(a == 'W' for *_, a in pairs)]
json.dump(res, open(H / 'human_check_results.json', 'w'), indent=1)
print(json.dumps(res, indent=1))

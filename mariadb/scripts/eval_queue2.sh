#!/bin/bash
# Evaluate saved patches that have no result yet, one issue at a time (one rebuild per issue).
# Priority: issues with all 12 patches (4 models x 3 runs) saved; otherwise the issue with the most pending patches.
S=$(cd "$(dirname "$0")/.." && pwd)
while [ ! -f $S/STOP_EVAL ]; do
  k=$(S=$S python3 - <<'PY'
import json,glob,os,collections
import os; S=os.environ['S']
done=set()
for l in open(S+'/results.jsonl'):
    try: done.add(json.loads(l)['run'])
    except Exception: pass
allp=collections.Counter(); pend=collections.Counter()
for d in glob.glob(S+'/patches/*.diff'):
    i=os.path.basename(d)[:-5]; k=i.split('_')[0]; allp[k]+=1
    if i not in done: pend[k]+=1
full=[k for k in pend if allp[k]>=12]
c=sorted(full) or sorted(pend,key=lambda k:-pend[k])
print(c[0] if c else '')
PY
)
  if [ -z "$k" ]; then sleep 60; continue; fi
  B=$(python3 -c "import json;print([x['commit'] for x in json.load(open('$S/frozen_sample.json')) if x['key']=='$k'][0])")
  for d in $S/patches/${k}_*.diff; do
    id=$(basename $d .diff); grep -q "\"run\":\"$id\"" $S/results.jsonl 2>/dev/null && continue
    bash $S/scripts/eval_patch.sh $k $B $d; rm -rf /home/mtr/var/t
  done
done

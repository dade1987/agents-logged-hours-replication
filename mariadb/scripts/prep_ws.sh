#!/bin/bash
# prep_ws.sh KEY : source at the parent of the fix commit, no Git history inside the workspace
set -eu
K=$1; S=$(cd "$(dirname "$0")/.." && pwd)
B=$(python3 -c "import json;print([x['commit'] for x in json.load(open('$S/frozen_sample.json')) if x['key']=='$K'][0])")
WS=/home/user/ws_mdb/$K; GD=/home/user/ws_mdb/git_$K
rm -rf $WS $GD; mkdir -p $WS
git -C /home/user/mariadb archive $B^ | tar -x -C $WS
sed "s|{WS}|$WS|g" $S/prompts/${K}_strict.txt > $WS/.issue_prompt.txt
git --git-dir=$GD --work-tree=$WS init -q && git --git-dir=$GD --work-tree=$WS add -A && git --git-dir=$GD --work-tree=$WS -c user.email=x@x -c user.name=x commit -qm base
echo $WS

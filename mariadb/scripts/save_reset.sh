#!/bin/bash
# save_reset.sh KEY MODEL RUN [confidence] : save the agent's diff, reset the workspace to the base state
set -eu
K=$1; M=$2; R=$3; C=${4:-}; S=$(cd "$(dirname "$0")/.." && pwd)
WS=/home/user/ws_mdb/$K; GD=/home/user/ws_mdb/git_$K
git --git-dir=$GD --work-tree=$WS add -A
git --git-dir=$GD --work-tree=$WS diff --cached > $S/patches/${K}_${M}_strict_${R}.diff
git --git-dir=$GD --work-tree=$WS reset -q --hard HEAD && git --git-dir=$GD --work-tree=$WS clean -qfdx
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$K" "$M" strict "$R" "$C" "$(date -u +%FT%TZ)" >> $S/runs.tsv
echo "saved $(wc -l < $S/patches/${K}_${M}_strict_${R}.diff) lines"

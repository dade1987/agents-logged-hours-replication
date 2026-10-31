#!/bin/bash
# Usage: close_agent.sh <KEY> <model> <condition> <run>  -> saves the patch to moodle/patches/<KEY>/ and deletes the workspace
set -eu
K=$1; M=$2; C=$3; R=$4; S=$(cd "$(dirname "$0")/.." && pwd); WSROOT=${WSROOT:-/home/user/ws}
A=$(grep "^$K " $S/commits.txt | cut -d' ' -f2)
mkdir -p $S/patches/$K
bash $S/scripts/save_patch.sh $WSROOT/${K}_${M}_${C}_${R} $A $S/patches/$K/${M}_${C}_${R}.patch

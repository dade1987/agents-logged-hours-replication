#!/bin/bash
# Usage: start_agent.sh <KEY> <model> <condition> <run>  -> prepares the agent's workspace and prints its path
set -eu
K=$1; M=$2; C=$3; R=$4; S=$(cd "$(dirname "$0")/.." && pwd); WSROOT=${WSROOT:-/home/user/ws}
A=$(grep "^$K " $S/commits.txt | cut -d' ' -f2)
WS=$WSROOT/${K}_${M}_${C}_${R}
P=$(mktemp); sed "s|{WS}|$WS|g" $S/prompts/${K}_${C}.txt > $P
bash $S/scripts/prepare_workspace.sh $K $A $WS $P; rm -f $P
echo $WS

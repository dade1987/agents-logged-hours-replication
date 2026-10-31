#!/bin/bash
# Usage: record_run.sh <agentId> <tokens> <tool_uses> <duration_ms> <confidence>  -> saves the patch and appends a row to runs.jsonl
set -eu
S=$(cd "$(dirname "$0")/.." && pwd)
read id K M C R < <(grep "^$1	" $S/agents_launched.tsv)
bash $S/scripts/close_agent.sh $K $M $C $R
echo "{\"key\":\"$K\",\"model\":\"$M\",\"cond\":\"$C\",\"run\":$R,\"tokens\":$2,\"tool_uses\":$3,\"duration_ms\":$4,\"confidence\":${5:-null}}" >> $S/runs.jsonl

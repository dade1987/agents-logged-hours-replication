#!/bin/bash
# Runs evaluate_fixtures.sh over moodle/fixture_recheck_queue.txt, skipping patches already in the log.
S=$(cd "$(dirname "$0")/.." && pwd); cd $S
while read k p; do
  L=eval_logs_fixture_recheck/$k.log; grep -qx "AGENTE $p FIXTURES:" $L 2>/dev/null && continue
  read _ a b < <(grep "^$k " commits.txt)
  timeout 5400 bash scripts/evaluate_fixtures.sh $k $a $b patches/$k/$p.patch $L
done < fixture_recheck_queue.txt

#!/bin/bash
# Usage: eval_patch.sh <issue> <commit B> <diff file>
# Diff of the agent's workspace (without its own mysql-test changes) applied on B^ plus B's tests; run B's mtr tests.
set -u
ISSUE=$1; B=$2; DIFF=$3; S=$(cd "$(dirname "$0")/.." && pwd); OUT=$S/pilot; WS=$(basename $DIFF .diff)
SRC=/home/user/mdb_src; BLD=/home/user/mdb_build_dbg; LOG=$S/eval_logs/$WS; mkdir -p $LOG
cd $SRC && git checkout -q -f --detach $B^ && git submodule update -q --init libmariadb && git clean -qfd -e libmariadb
rec(){ printf '{"issue":"%s","run":"%s","result":"%s"}\n' $ISSUE $WS $1 >> $S/results.jsonl; echo "$ISSUE $WS $1"; }
grep -q '^diff --git' $DIFF || { rec EMPTY; exit; }
git apply --exclude='mysql-test/*' --exclude='*/mysql-test/*' $DIFF || { rec APPLY_FAIL; exit; }
git checkout -q $B -- $(git -C /home/user/mariadb diff --name-only $B^ $B -- mysql-test '*/mysql-test/*')
names=$(python3 -c "import json,sys;print([json.loads(l)['tests'] for l in open('$OUT/oracle_full.jsonl') if json.loads(l)['issue']=='$ISSUE'][0])")
(cd $BLD && ninja -j4 > $LOG/build_agent.log 2>&1) || { bash $S/scripts/fresh_build.sh; cd $BLD && ninja -j4 > $LOG/build_agent_fresh.log 2>&1; } || { rec BUILD_FAIL; exit; }
(cd $BLD/mysql-test && timeout 1800 su mtr -s /bin/bash -c "perl mysql-test-run.pl --vardir=/home/mtr/var/t --force --parallel=4 --retry=0 $names" > $LOG/mtr_agent.log 2>&1)
r=FAIL; grep -q "All [0-9]* tests were successful" $LOG/mtr_agent.log && r=PASS
rec $r

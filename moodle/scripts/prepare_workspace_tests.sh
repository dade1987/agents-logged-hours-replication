#!/bin/bash
# Usage: prepare_workspace_tests.sh <KEY> <model> <run> <slot 1-9>
# Workspace for condition "tests": code at A^ (no git history) plus a working PHPUnit environment
# (own prefix phpa_ and dataroot), so the agent can run Moodle's existing tests. Hidden developer tests are not included.
set -eu
K=$1; M=$2; R=$3; SL=$4; S=$(cd "$(dirname "$0")/.." && pwd)
# PostgreSQL stops when the container restarts: make sure it is up before init.
su postgres -c "/usr/lib/postgresql/17/bin/pg_isready -p 5433 -q" || su postgres -c "/usr/lib/postgresql/17/bin/pg_ctl -D /home/user/pg/data17 -l /home/user/pg/log17 -o '-p 5433' -w start" >/dev/null
PT=$(mktemp)
A=$(grep "^$K " $S/commits.txt | cut -d' ' -f2)
WS=/home/user/ws/${K}_${M}_tests_${R}
sed "s|{WS}|$WS|g" $S/prompts/${K}_tests.txt > $PT
bash $S/scripts/prepare_workspace.sh $K $A $WS $PT; rm -f $PT
cat > $WS/config.php <<C
<?php
unset(\$CFG); global \$CFG; \$CFG = new stdClass();
\$CFG->dbtype='pgsql'; \$CFG->dblibrary='native'; \$CFG->dbhost='localhost'; \$CFG->dbname='moodle';
\$CFG->dbuser='moodle'; \$CFG->dbpass='moodle'; \$CFG->prefix='mda${SL}_'; \$CFG->dboptions=['dbport'=>5433];
\$CFG->wwwroot='http://localhost'; \$CFG->dataroot='/home/user/mdata_a${SL}'; \$CFG->directorypermissions=02777;
\$CFG->phpunit_prefix='phpa${SL}_'; \$CFG->phpunit_dataroot='/home/user/phpa${SL}';
require_once(__DIR__ . '/lib/setup.php');
C
mkdir -p /home/user/mdata_a$SL /home/user/phpa$SL
cd $WS
# vendor: one install per composer.lock, cached and copied (flock so parallel preps share it)
H=$(sha1sum composer.lock | cut -c1-12); VC=/home/user/vendor_cache/$H; mkdir -p /home/user/vendor_cache
(
  flock 9
  if [ ! -d $VC ]; then
    # disk allowance is small: keep at most 2 cached vendor trees (least recently used evicted)
    ls -1dt /home/user/vendor_cache/*/ 2>/dev/null | tail -n +2 | xargs -r rm -rf
    composer install --no-interaction -q >/dev/null 2>&1
    find vendor -name .git -type d -prune -exec rm -rf {} + 2>/dev/null
    cp -a vendor $VC
  fi
  touch $VC
  [ -d vendor ] || cp -a $VC vendor
) 9>/home/user/vendor_cache/.lock
INIT=public/admin/tool/phpunit/cli; [ -d $INIT ] || INIT=admin/tool/phpunit/cli
php $INIT/init.php >/dev/null 2>&1 || { php $INIT/util.php --drop >/dev/null 2>&1; php $INIT/init.php >/dev/null 2>&1; }
echo $WS

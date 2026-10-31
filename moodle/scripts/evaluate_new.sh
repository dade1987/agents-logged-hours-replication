#!/bin/bash
# Usage: evaluate_new.sh <KEY> <commit A> <commit B> <patch dir> <log>
# Evaluates only the patches not yet in the log (oracle already run) and appends their "AGENTE <name>:" blocks.
set -u
K=$1; A=$(git -C ${MOODLE:-/home/user/moodle} rev-parse "$2"); B=$(git -C ${MOODLE:-/home/user/moodle} rev-parse "$3"); PD=$(realpath "$4"); LOG=$(realpath "$5")
cd ${MOODLE:-/home/user/moodle}
reset() { git checkout -q -f "$A^" && git clean -qfd -e config.php -e vendor; }
init() { composer install --no-interaction -q >/dev/null 2>&1; php public/admin/tool/phpunit/cli/init.php >/dev/null 2>&1 || { php public/admin/tool/phpunit/cli/util.php --drop >/dev/null 2>&1; php public/admin/tool/phpunit/cli/init.php >/dev/null 2>&1; }; }
TESTS=$(git diff --name-only "$A^" "$B" | grep '_test\.php$' | while read f; do git cat-file -e "$B:$f" 2>/dev/null && echo "$f"; done)
run() { init; for t in $TESTS; do echo "TEST $t: $(vendor/bin/phpunit "$t" 2>&1 | tail -1)"; done; }
for p in "$PD"/*.patch; do
  [ -e "$p" ] || continue
  n=$(basename "$p" .patch)
  grep -qx "AGENTE $n:" "$LOG" && continue
  reset; git apply --whitespace=nowarn --exclude='*_test.php' "$p" 2>&1 | head -2 >> "$LOG"
  git checkout -q "$B" -- $TESTS; { echo "AGENTE $n:"; run; } >> "$LOG"
done
reset

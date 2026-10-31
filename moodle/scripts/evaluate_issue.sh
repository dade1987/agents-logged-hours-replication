#!/bin/bash
# Usage: evaluate_issue.sh <KEY> <commit A> <commit B> <patch dir>
# 1) oracle: developer tests (from B) on the parent of A must fail ("PRIMA:" = before); with the fix A^..B they must pass ("DOPO:" = after)
# 2) each agent patch ("AGENTE <name>:" = agent): applied to the parent of A, test files overwritten from B, then run
# The Italian block markers are kept because the published logs in moodle/eval_logs use them (scripts/score.py parses them).
set -u
K=$1; A=$(git -C ${MOODLE:-/home/user/moodle} rev-parse "$2"); B=$(git -C ${MOODLE:-/home/user/moodle} rev-parse "$3"); PD=$(realpath "$4")
cd ${MOODLE:-/home/user/moodle}
reset() { git checkout -q -f "$A^" && git clean -qfd -e config.php -e vendor; }
init() { composer install --no-interaction -q >/dev/null 2>&1; php public/admin/tool/phpunit/cli/init.php >/dev/null 2>&1 || { php public/admin/tool/phpunit/cli/util.php --drop >/dev/null 2>&1; php public/admin/tool/phpunit/cli/init.php >/dev/null 2>&1; }; }
TESTS=$(git diff --name-only "$A^" "$B" | grep '_test\.php$' | while read f; do git cat-file -e "$B:$f" 2>/dev/null && echo "$f"; done)
run() { init; for t in $TESTS; do echo "TEST $t: $(vendor/bin/phpunit "$t" 2>&1 | tail -1)"; done; }
echo "== $K"
reset; git checkout -q "$B" -- $TESTS; echo "PRIMA:"; run
reset; git diff --binary "$A^" "$B" | git apply --whitespace=nowarn; echo "DOPO:"; run
for p in "$PD"/*.patch; do
  [ -e "$p" ] || continue
  reset; git apply --whitespace=nowarn --exclude='*_test.php' "$p" 2>&1 | head -2
  git checkout -q "$B" -- $TESTS; echo "AGENTE $(basename "$p" .patch):"; run
done
reset

#!/bin/bash
# Sensitivity re-check (failure audit): like evaluate_new.sh, but after applying the agent patch it also copies from the
# fix commit ALL test-support files the developers changed under tests/ directories (fixtures, generators), not only *_test.php.
# Usage: evaluate_fixtures.sh <KEY> <commit A> <commit B> <patch file> <log>
set -u
K=$1; A=$(git -C ${MOODLE:-/home/user/moodle} rev-parse "$2"); B=$(git -C ${MOODLE:-/home/user/moodle} rev-parse "$3"); P=$(realpath "$4"); LOG=$(realpath -m "$5")
cd ${MOODLE:-/home/user/moodle}
reset() { git checkout -q -f "$A^" && git clean -qfd -e config.php -e vendor; }
init() { composer install --no-interaction -q >/dev/null 2>&1; php public/admin/tool/phpunit/cli/init.php >/dev/null 2>&1 || { php public/admin/tool/phpunit/cli/util.php --drop >/dev/null 2>&1; php public/admin/tool/phpunit/cli/init.php >/dev/null 2>&1; }; }
TESTS=$(git diff --name-only "$A^" "$B" | grep '_test\.php$' | while read f; do git cat-file -e "$B:$f" 2>/dev/null && echo "$f"; done)
SUPPORT=$(git diff --name-only "$A^" "$B" | grep '/tests/' | grep -v '_test\.php$' | while read f; do git cat-file -e "$B:$f" 2>/dev/null && echo "$f"; done)
reset; git apply --whitespace=nowarn --exclude='*_test.php' "$P" 2>&1 | head -2 >> "$LOG"
git checkout -q "$B" -- $TESTS $SUPPORT
TMP=$(mktemp); { echo "AGENTE $(basename $P .patch) FIXTURES:"; init; for t in $TESTS; do echo "TEST $t: $(vendor/bin/phpunit "$t" 2>&1 | tail -1)"; done; } > "$TMP" && cat "$TMP" >> "$LOG"; rm -f "$TMP"
reset

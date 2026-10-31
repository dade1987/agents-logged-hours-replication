#!/bin/bash
# Usage: save_patch.sh <agent workspace> <commit A> <output patch file>
# Saves the agent's changes against the parent of A (new files included), then deletes the workspace.
set -u
WS=$1; A=$(git -C ${MOODLE:-/home/user/moodle} rev-parse "$2"); OUT=$3
export GIT_DIR=${MOODLE:-/home/user/moodle}/.git GIT_INDEX_FILE=$(mktemp -u)
git read-tree "$A^"
X=(':!.issue_prompt.txt' ':!vendor' ':!config.php' ':!**/phpunit.xml' ':!phpunit.xml' ':!.phpunit.cache' ':!composer.phar')
git --work-tree="$WS" add -A -- . "${X[@]}" 2>/dev/null
git --work-tree="$WS" diff --cached --binary "$A^" -- . "${X[@]}" > "$OUT"
rm -f "$GIT_INDEX_FILE"
echo "$(grep -c '^diff --git' "$OUT") files changed"
rm -rf "$WS"

#!/bin/bash
# Usage: prepare_workspace.sh <KEY> <first fix commit A> <workspace dir> <prompt file>
# Exports the source at the parent of A, without Git history, and puts the prompt in the workspace.
set -eu
K=$1; A=$2; WS=$3; P=$4
rm -rf "$WS"; mkdir -p "$WS"
git -C ${MOODLE:-/home/user/moodle} archive "$A^" | tar -x -C "$WS"
cp "$P" "$WS/.issue_prompt.txt"

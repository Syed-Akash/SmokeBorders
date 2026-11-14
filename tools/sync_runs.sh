#!/usr/bin/env bash
# Every scheduled run pushes to its own branch (ccr-* for FlagBomb, claude/* for Smoke & Borders) because sessions can't push
# to main. Run this FIRST in every run (both runbooks, step 0): it merges every run branch that isn't in the checkout yet, oldest
# first, so the run builds on everything earlier runs did (uploads, queues, plans).
# The GitHub workflow .github/workflows/runs.yml does the same on GitHub, so main also stays current.
set -u
cd "$(git rev-parse --show-toplevel)"
git fetch -q origin '+refs/heads/*:refs/remotes/origin/*' 2>/dev/null || git fetch -q origin
git merge -q --no-edit origin/main 2>/dev/null || { git merge --abort 2>/dev/null; git merge -q --no-edit -X theirs origin/main; }
# Only branches that moved in the last 36 hours: old branches can't be deleted (the git proxy refuses), and merging a stale one
# with "theirs" rolled the plan back twice (12 and 13 Nov 2026: Rome showed as unpublished, uploads were forgotten).
# A conflict is never settled automatically any more: the branch is skipped and named, for a person to look at.
cut=$(( $(date +%s) - 36*3600 ))
for b in $(git for-each-ref --sort=committerdate --format='%(committerdate:unix) %(refname:short)' 'refs/remotes/origin/ccr-*' 'refs/remotes/origin/claude/*' | awk -v c=$cut '$1>=c{print $2}'); do
  git merge-base --is-ancestor "$b" HEAD && continue
  echo "merging $b"
  git merge -q --no-edit "$b" || { echo "CONFLICT merging $b: skipped (left for review, nothing changed)"; git merge --abort 2>/dev/null; }
done
git log --oneline -3

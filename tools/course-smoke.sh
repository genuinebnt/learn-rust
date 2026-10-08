#!/bin/sh
# End-to-end smoke test of `anneal course` as a learner uses it (docs/BUSTUB.md §4), plus the whole-course checks.
# Needs the reference tree (courses/<id>/reference, kept out of the public repo). Run from the repo root after
# `cargo build -p anneal-cli`. Usage: tools/course-smoke.sh [course]
set -eu
COURSE=${1:-bustub}
ROOT=$(pwd)
A="$ROOT/target/debug/anneal"
C="--courses $ROOT/courses"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

echo "== every stage fails before it and passes after it; earlier stages stay green (regression)"
"$A" course verify --course "$COURSE" $C | tail -4

echo "== the whole solution passes every test in the repo (integration)"
"$A" course build --full "$WORK/full" --course "$COURSE" $C
(cd "$WORK/full" && cargo test 2>&1 | grep -E "^test result|FAILED|panicked" | sort | uniq -c)
(cd "$WORK/full" && cargo build --release 2>&1 | tail -1)

echo "== the template compiles and its first stage fails (smoke)"
"$A" course init "$COURSE" "$WORK/learner" $C
cd "$WORK/learner"
git config user.email t@example.com
git config user.name t
"$A" course status | head -6
if "$A" course test | grep -q "complete"; then echo "BUG: stage 1 passed on the stub"; exit 1; fi

echo "== a learner solves stage 1; the pre-push hook records it"
"$A" course build --stage "$(sed -n 's/^id = "\(.*\)"/\1/p' "$ROOT/courses/$COURSE/modules/"*/stages/01-*/stage.toml | head -1)" "$WORK/learner" --course "$COURSE" $C >/dev/null
git add -A
git commit -q -m "first stage"
.git/hooks/pre-push
grep -q passed .anneal/progress.json && echo "progress recorded: $(cat .anneal/progress.json | tr -d '\n ')"
echo "== update with an unchanged template leaves the learner's work alone"
"$A" course update --course "$COURSE" $C
test -z "$(git status --porcelain src tests Cargo.toml)" || { echo "BUG: update changed the learner's files"; exit 1; }
echo "== smoke test passed"

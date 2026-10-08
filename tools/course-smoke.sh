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

if [ -z "${SKIP_VERIFY:-}" ]; then
    echo "== every stage fails before it and passes after it; earlier stages stay green (regression)"
    "$A" course verify --course "$COURSE" $C | tail -4
else
    echo "== (verify skipped: SKIP_VERIFY is set)"
fi

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
if "$A" course test | grep -q "^✓ Stage .* complete"; then echo "BUG: stage 1 passed on the stub"; exit 1; fi

echo "== only the first module is in the learner's repo"
test ! -e src/storage/disk/disk_scheduler.rs || { echo "BUG: module 1b's file is visible at the start"; exit 1; }
test ! -e tests/stages_1b.rs || { echo "BUG: module 1b's tests are visible at the start"; exit 1; }
grep -q "disk_manager" src/storage/disk/mod.rs && ! grep -q "disk_scheduler" src/storage/disk/mod.rs || { echo "BUG: mod.rs names a hidden module"; exit 1; }
cargo test --no-run 2>&1 | tail -1

echo "== a learner solves module 1a stage by stage; the pre-push hook records it, and module 1b unlocks"
LAST="$(ls "$ROOT/courses/$COURSE/modules/"01-*/stages | wc -l | tr -d ' ')"
"$A" course build --stage "$(sed -n 's/^id = "\(.*\)"/\1/p' "$ROOT/courses/$COURSE/modules/"01-*/stages/"$(printf '%02d' "$LAST")"-*/stage.toml | head -1)" "$WORK/solved" --course "$COURSE" $C >/dev/null
# the solved files, except mod.rs and lib.rs: those name only the modules unlocked so far
find src tests -type f ! -name mod.rs ! -name lib.rs | while read -r f; do cp "$WORK/solved/$f" "$f"; done
git add -A
git commit -q -m "module 1a"
for _ in $(seq 1 "$LAST"); do .git/hooks/pre-push >/dev/null; done
grep -q passed .anneal/progress.json && echo "progress recorded: $(cat .anneal/progress.json | tr -d '\n ' | cut -c1-120)..."
test -e src/storage/disk/disk_scheduler.rs || { echo "BUG: module 1b did not unlock"; exit 1; }
test -e tests/stages_1b.rs || { echo "BUG: module 1b's tests did not arrive"; exit 1; }
grep -q "disk_scheduler" src/storage/disk/mod.rs || { echo "BUG: mod.rs does not name the unlocked module"; exit 1; }
cargo test --no-run 2>&1 | tail -1

git add -A
git commit -q -m "module 1b arrived"
echo "== update with an unchanged template leaves the learner's work alone"
"$A" course update --course "$COURSE" $C
test -z "$(git status --porcelain src tests Cargo.toml)" || { echo "BUG: update changed the learner's files"; exit 1; }
echo "== smoke test passed"

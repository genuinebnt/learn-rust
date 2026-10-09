#!/bin/sh
# A learner's journey through `anneal course`, scripted: start a repo, read, fail, solve, pass, unlock the next module, solve a challenge,
# reset, and check that the web app saw all of it. Complements tools/course-smoke.sh (which checks the whole course); this one checks how the
# CLI and the app behave together.
#
# Needs: the reference tree (courses/<id>/reference), `cargo build -p anneal-cli`, and an anneal API on a THROWAWAY database
# (never your real one: the script reports runs to it and resets progress), e.g. the e2e instance:
#     ANNEAL_DATABASE_URL=postgres://anneal:anneal@localhost:5435/anneal_e2e ANNEAL_SANDBOX=host ANNEAL_ADDR=127.0.0.1:8791 cargo run -q -p anneal-api &
# Usage: tools/course-journey.sh [http://127.0.0.1:8791]
set -eu
URL=${1:-http://127.0.0.1:8791}
ROOT=$(pwd)
A="$ROOT/target/debug/anneal"
C="--courses $ROOT/courses"
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
# the CLI keeps its sign-in under XDG_CONFIG_HOME: keep it away from the real one
export XDG_CONFIG_HOME="$WORK/config"
# a throwaway app has login off, and any passphrase is fine
export ANNEAL_PASSPHRASE=journey
FAILS=0

step() { printf '\n== %s\n' "$*"; }
ok() { printf '   ok   %s\n' "$*"; }
bad() { printf '   FAIL %s\n' "$*"; FAILS=$((FAILS + 1)); }
expect() { # expect "what" command...   passes when the command succeeds
    what=$1; shift
    if "$@" >/dev/null 2>&1; then ok "$what"; else bad "$what"; fi
}
api() { curl -sf "$URL/api/courses/bustub${1:-}"; }
json() { python3 -c "import json,sys; d=json.load(sys.stdin); print($1)"; }

curl -sf "$URL/api/health" >/dev/null || { echo "no anneal API at $URL (see the header of this script)"; exit 2; }

step "a new learner: init, status, show"
"$A" course init bustub "$WORK/learner" $C >/dev/null
cd "$WORK/learner"
git config user.email t@example.com && git config user.name t
STATUS=$("$A" course status --json)
[ "$(echo "$STATUS" | json 'd["current"]')" = "1a-01" ] && ok "the first stage is 1a-01 (the optional Rust on-ramp is skipped)" || bad "current is not 1a-01"
echo "$STATUS" | json 'd["modules"][0]["code"]' | grep -q '^r$' && ok "the on-ramp is listed first" || bad "the on-ramp is not first"
echo "$STATUS" | json 'd["challenges"] > 0' | grep -q True && ok "challenges have their own tally" || bad "no challenge tally"
echo "$STATUS" | json 'd["total"]' | grep -qv '^0$' && ok "challenges are not part of the total" || bad "total is 0"
"$A" course show --no-pager | grep -q "Where to work" && ok "show says where to work" || bad "show has no 'Where to work'"
"$A" course show r-c1 --no-pager | grep -qi "challenge" && ok "a challenge page opens" || bad "challenge page"

step "a failing run is reported, and the page knows nothing is running"
if "$A" course test r-01 >/dev/null 2>&1; then bad "r-01 passed on the stub"; else ok "r-01 fails on the stub, with a non-zero exit"; fi
"$A" course login "$URL" >/dev/null 2>&1 && ok "signed in to the throwaway app" || bad "login"
"$A" course test r-01 >/dev/null 2>&1 || true
[ "$(api /stages/r-01 | json 'd["last_run"]["ok"]')" = "False" ] && ok "the app has the failing run" || bad "the app has no failing run"
[ "$(api /stages/r-01 | json 'd["running"]')" = "None" ] && ok "nothing is shown as running after the report" || bad "still running"

step "the app shows a run in flight until its report arrives"
curl -sf -X POST "$URL/api/courses/bustub/runs/start" -H 'content-type: application/json' -d '{"stage_id":"r-02"}' >/dev/null
[ "$(api /stages/r-02 | json 'd["running"] is not None')" = "True" ] && ok "a started run shows as running" || bad "a started run does not show"
"$A" course test r-02 >/dev/null 2>&1 || true
[ "$(api /stages/r-02 | json 'd["running"]')" = "None" ] && ok "its report ends it" || bad "report did not end the running state"

step "solve a stage: the tests pass and progress moves, the main path does not"
"$A" course build "$WORK/solved" --stage r-05 $C >/dev/null
cp "$WORK/solved/src/rust_primer/bytes.rs" src/rust_primer/bytes.rs
"$A" course test r-01 >/dev/null 2>&1 && ok "r-01 passes with the solution" || bad "r-01 does not pass with the solution"
[ "$("$A" course status --json | json 'd["done"]')" = "1" ] && ok "one stage done" || bad "progress did not move"
[ "$("$A" course status --json | json 'd["current"]')" = "1a-01" ] && ok "the next stage is still 1a-01, not r-02" || bad "the optional module became the current one"
[ "$(api /stages/r-01 | json 'd["state"]')" != "todo" ] && ok "the app has it solved" || bad "the app did not record the pass"

step "a challenge: no solution in the app, own tally, never the next stage"
[ "$(api /stages/r-c1 | json 'd["solution"]["available"]')" = "False" ] && ok "no solution for a challenge" || bad "a challenge has a solution"
"$A" course build "$WORK/solved2" --stage r-c1 $C >/dev/null
cp "$WORK/solved2/src/rust_primer/varint.rs" src/rust_primer/varint.rs
"$A" course test r-c1 >/dev/null 2>&1 && ok "the challenge passes with a solution" || bad "the challenge does not pass"
S2=$("$A" course status --json)
[ "$(echo "$S2" | json 'd["challenges_done"]')" = "1" ] && [ "$(echo "$S2" | json 'd["done"]')" = "1" ] && ok "the challenge is in its own tally, not in the course's" || bad "tallies wrong"
[ "$(api | json 'd["challenges_done"]')" = "1" ] && ok "the app's tally matches" || bad "the app's tally differs"

step "finishing a module unlocks the next one"
[ ! -e src/storage/disk/disk_scheduler.rs ] && ok "module 1b's files are not there yet" || bad "1b is visible too early"
"$A" course build "$WORK/solved3" --stage 1a-05 $C >/dev/null
cp -R "$WORK/solved3/src/." src/
for s in 1a-01 1a-02 1a-03 1a-04 1a-05; do
    "$A" course test "$s" --only >/dev/null 2>&1 && ok "$s passes" || bad "$s does not pass"
done
[ -e src/storage/disk/disk_scheduler.rs ] && ok "module 1b's files arrived" || bad "1b did not unlock"
[ "$("$A" course status --json | json 'd["current"]')" = "1b-01" ] && ok "the next stage is 1b-01" || bad "current is not 1b-01"

step "reset: asks first, then forgets one module, here and in the app"
if "$A" course reset --module 1a </dev/null >/dev/null 2>&1; then bad "reset went ahead without asking"; else ok "reset needs a terminal or --yes"; fi
"$A" course reset --module 1a --yes >/dev/null 2>&1 && ok "reset --module 1a --yes" || bad "reset failed"
S3=$("$A" course status --json)
[ "$(echo "$S3" | json 'd["current"]')" = "1a-01" ] && ok "back at 1a-01" || bad "current did not go back"
[ "$(echo "$S3" | json 'd["done"]')" = "1" ] && ok "the on-ramp stage is still done" || bad "other modules were reset too"
[ "$(api /stages/1a-01 | json 'd["state"]')" = "todo" ] && ok "the app forgot 1a too" || bad "the app still has 1a"
[ "$(api /stages/r-01 | json 'd["state"]')" != "todo" ] && ok "and kept r-01" || bad "the app lost r-01"
"$A" course reset --all --yes >/dev/null 2>&1 && ok "reset --all --yes" || bad "reset --all failed"
[ "$("$A" course status --json | json 'd["done"]')" = "0" ] && ok "everything forgotten" || bad "progress left"

echo
if [ "$FAILS" -eq 0 ]; then echo "the journey works"; else echo "$FAILS step(s) failed"; exit 1; fi

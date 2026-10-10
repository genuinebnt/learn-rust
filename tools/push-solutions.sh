#!/bin/bash
# Uploads every stage's solution diff (from courses/bustub/reference) to a running anneal app, so the Solution tab can reveal it.
# Normally NOT needed: CI generates courses/bustub/solutions.json at deploy time and the app loads it at start-up (docs/BUSTUB.md §8).
# Use it for a local app whose checkout is newer than the last start, or to push to an app that was not restarted.
#   ANNEAL_PASSPHRASE=... tools/push-solutions.sh [https://anneal.genuinebasil.dev]   (the app's address; default is the local one)
set -euo pipefail
cd "$(dirname "$0")/.."
url=${1:-http://127.0.0.1:8787}
cargo build -q -p anneal-cli
./target/debug/anneal course template
./target/debug/anneal course login "$url"
./target/debug/anneal course solutions

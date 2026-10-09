#!/bin/bash
# Uploads every stage's solution diff (from the gitignored courses/bustub/reference) to the anneal web app, so the Solution tab can reveal it.
# Run it after a module ships, because the diffs follow the stage ids and the template.
#   ANNEAL_PASSPHRASE=... tools/push-solutions.sh [https://anneal.genuinebasil.dev]   (the app's address; default is the local one)
set -euo pipefail
cd "$(dirname "$0")/.."
url=${1:-http://127.0.0.1:8787}
cargo build -q -p anneal-cli
./target/debug/anneal course template
./target/debug/anneal course login "$url"
./target/debug/anneal course solutions

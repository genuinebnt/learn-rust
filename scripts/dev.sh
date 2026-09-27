#!/usr/bin/env bash
# Development mode: the API restarts whenever Rust code, content or Cargo files change, and the web app
# hot-reloads through Vite. Anything that changes files (editing, `git pull`, switching branches) is picked up.
#
#   ./scripts/dev.sh        then open http://127.0.0.1:5180 (Vite; /api is proxied to the API on :8787)
#
# Ctrl-C stops both.
set -euo pipefail
cd "$(dirname "$0")/.."

# Hooks in .githooks reinstall web dependencies after a pull that changes them.
git config core.hooksPath .githooks

for port in 8787 5180; do
  if lsof -nP -iTCP:$port -sTCP:LISTEN >/dev/null 2>&1; then
    echo "Something is already listening on :$port. Stop it first." >&2
    exit 1
  fi
done

docker compose up -d --wait postgres >/dev/null
[ -d web/node_modules ] || pnpm -C web install --frozen-lockfile

cleanup() { trap - INT TERM EXIT; kill 0 2>/dev/null || true; }
trap cleanup INT TERM EXIT

# cargo-watch kills and restarts the server on every change (.cargo holds the database URL).
cargo watch -q -w crates -w content -w Cargo.toml -w Cargo.lock -w .cargo -x "run -q -p anneal-api" &
pnpm -C web dev &
wait

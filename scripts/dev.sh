#!/usr/bin/env bash
# Development mode: the API restarts whenever Rust code, content or Cargo files change, and the web app
# hot-reloads through Vite. Anything that changes files (editing, `git pull`, switching branches) is picked up.
#
#   ./scripts/dev.sh        then open the web URL it prints (normally http://127.0.0.1:5180)
#
# The API's own port (normally :8787) serves web/dist, which dev mode rebuilds on every change too, so either URL
# is current; only the Vite one hot-reloads without a page refresh.
#
# The API wants :8787 and the web app :5180. When another program holds one of them, a random free port is used
# instead, and the web app's /api proxy follows the API wherever it lands. ANNEAL_API_PORT / ANNEAL_WEB_PORT
# choose different preferred ports. scripts/restart.sh stops a running instance, pulls, and starts this.
#
# Ctrl-C stops everything.
set -euo pipefail
cd "$(dirname "$0")/.."

# Hooks in .githooks reinstall web dependencies after a pull that changes them.
git config core.hooksPath .githooks

# Local secrets such as GEMINI_API_KEY (docs/AI.md) live in .env.local, which git ignores.
if [ -f .env.local ]; then
  set -a
  # shellcheck disable=SC1091
  . ./.env.local
  set +a
fi

in_use() { lsof -nP -iTCP:"$1" -sTCP:LISTEN >/dev/null 2>&1; }
free_port() { python3 -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])'; }
pick() {
  if in_use "$1"; then
    local port
    port=$(free_port)
    echo "anneal: :$1 is in use, using :$port for the $2" >&2
    echo "$port"
  else
    echo "$1"
  fi
}
api_port=$(pick "${ANNEAL_API_PORT:-8787}" API)
web_port=$(pick "${ANNEAL_WEB_PORT:-5180}" "web app")
export ANNEAL_ADDR="127.0.0.1:$api_port" ANNEAL_API_PORT="$api_port" ANNEAL_WEB_PORT="$web_port"

docker compose up -d --wait postgres >/dev/null
[ -d web/node_modules ] || pnpm -C web install --frozen-lockfile

# restart.sh reads this to find and stop the instance.
echo $$ >| .dev.pid
cleanup() { trap - INT TERM EXIT; rm -f .dev.pid; kill 0 2>/dev/null || true; }
trap cleanup INT TERM EXIT

echo "anneal: web http://127.0.0.1:$web_port   api http://127.0.0.1:$api_port"

# cargo-watch kills and restarts the server on every change (.cargo holds the database URL).
cargo watch -q -w crates -w content -w Cargo.toml -w Cargo.lock -w .cargo -x "run -q -p anneal-api" &
pnpm -C web dev &
# The API also serves the built app from web/dist at the API's port; keep that copy current too.
pnpm -C web exec vite build --watch --logLevel warn >/dev/null &
wait

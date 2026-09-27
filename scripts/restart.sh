#!/usr/bin/env bash
# Pull the latest code and restart dev mode, e.g. after the cloud agent pushed:
#
#   ./scripts/restart.sh
#
# 1. Stops the running anneal dev server: the one recorded in .dev.pid, plus anything else of ours still holding
#    :8787 or :5180 (only processes whose working directory is inside this repo; other programs are left alone,
#    and dev.sh moves to a random free port instead).
# 2. `git pull --rebase --autostash`, so local edits are kept. The .githooks run `pnpm install` if needed.
# 3. Starts scripts/dev.sh in this terminal, with hot reload.
set -euo pipefail
cd "$(dirname "$0")/.."
root=$(pwd -P)
own_pgid=$(ps -o pgid= -p $$ | tr -d ' ')

stop_group() {
  local pgid
  pgid=$(ps -o pgid= -p "$1" 2>/dev/null | tr -d ' ')
  [ -z "$pgid" ] && return 0
  # dev.sh, cargo-watch, the API and Vite share one process group; never signal our own.
  if [ "$pgid" != "$own_pgid" ]; then kill -TERM -- "-$pgid" 2>/dev/null || true; else kill -TERM "$1" 2>/dev/null || true; fi
}
ours() {
  local cwd
  cwd=$(lsof -a -p "$1" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p')
  case "$cwd" in "$root" | "$root"/*) return 0 ;; *) return 1 ;; esac
}

stopped=false
if [ -f .dev.pid ] && kill -0 "$(cat .dev.pid)" 2>/dev/null; then
  stop_group "$(cat .dev.pid)"
  stopped=true
fi
for port in 8787 5180; do
  for pid in $(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null); do
    if ours "$pid"; then
      stop_group "$pid"
      stopped=true
    fi
  done
done
if $stopped; then
  echo "anneal: stopping the running dev server…"
  for _ in $(seq 1 40); do
    busy=false
    for port in 8787 5180; do
      for pid in $(lsof -tiTCP:"$port" -sTCP:LISTEN 2>/dev/null); do ours "$pid" && busy=true; done
    done
    $busy || break
    sleep 0.25
  done
fi

echo "anneal: pulling…"
git pull --rebase --autostash

exec ./scripts/dev.sh

#!/usr/bin/env bash
# Dumps the production database to /srv/anneal/backups (custom format, restore with pg_restore) and keeps the newest
# 30 dumps. deploy.sh runs it before every deploy; cron runs it daily (see docs/DEPLOY.md).
#
#   deploy/backup.sh [label]
set -euo pipefail
cd "$(dirname "$0")/.."
dir=/srv/anneal/backups
mkdir -p "$dir"
compose() { docker compose -f deploy/compose.prod.yml --env-file deploy/.env "$@"; }
if [ -z "$(compose ps --status running -q postgres 2>/dev/null)" ]; then
  echo "backup: postgres isn't running; nothing to back up"
  exit 0
fi
file="$dir/anneal-$(date -u +%Y%m%dT%H%M%SZ)${1:+-$1}.dump"
compose exec -T postgres pg_dump -U anneal -Fc anneal > "$file.part"
mv "$file.part" "$file"
ls -1t "$dir"/anneal-*.dump | tail -n +31 | xargs -r rm -f
echo "backup: $file ($(du -h "$file" | cut -f1))"

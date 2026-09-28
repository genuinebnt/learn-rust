#!/usr/bin/env bash
# Forced command for the CI deploy key in ~deploy/.ssh/authorized_keys:
#
#   command="/home/deploy/anneal/deploy/ssh-deploy.sh",restrict ssh-ed25519 AAAA… anneal-ci
#
# Whatever the client asks to run, the key can only do this: `deploy <sha>` runs deploy.sh for that commit.
set -euo pipefail
read -r verb tag extra <<<"${SSH_ORIGINAL_COMMAND:-}"
if [ "${verb:-}" != deploy ] || [ -n "${extra:-}" ]; then
  echo "only 'deploy <git-sha>' is allowed" >&2
  exit 2
fi
exec "$(dirname "$0")/deploy.sh" "${tag:-latest}"

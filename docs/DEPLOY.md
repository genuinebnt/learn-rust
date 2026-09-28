# anneal · production

anneal runs at **https://anneal.genuinebasil.dev** on the Hetzner VM (`deploy@46.224.108.227`, Ubuntu, 2 vCPU,
4 GB). Every push to `master` that passes CI is deployed automatically.

## How it fits together

```
push to master ──► GitHub Actions (.github/workflows/ci.yml)
                   ├─ rust: clippy -D warnings, cargo test (Postgres service), anneal validate
                   ├─ web: pnpm install, tsc + vite build
                   └─ deploy (master only, after both pass)
                        ├─ build + push ghcr.io/genuinebnt/anneal:<sha>         (Dockerfile)
                        ├─ build + push ghcr.io/genuinebnt/anneal-runner:<sha>  (docker/runner.Dockerfile)
                        └─ ssh deploy@VM "deploy <sha>"  ─► deploy/ssh-deploy.sh ─► deploy/deploy.sh

VM
  genuinedev-caddy-1  the shared gateway for *.genuinebasil.dev (repo genuinebnt/genuine.dev, its Caddyfile)
     │ edge network: anneal.{$DOMAIN} → reverse_proxy anneal-app:8787 (TLS by Caddy, behind Cloudflare)
  anneal stack (deploy/compose.prod.yml, project "anneal", checkout at ~/anneal)
     ├─ anneal-app   API + built web app + rust-analyzer; talks to the host Docker daemon via the socket
     │     └─ starts sandbox containers from anneal-runner:<sha> (--network none, read-only, unprivileged)
     └─ postgres     postgres:18-alpine, volume anneal_pgdata
```

- **Images** are built in CI, never on the VM (a release build would starve the other sites of memory).
  Dependencies are cached with cargo-chef and the GitHub Actions cache, so a code-only change rebuilds quickly.
- **The deploy key** in the `DEPLOY_SSH_KEY` secret is a dedicated key, not anyone's personal one. On the VM,
  `~/.ssh/authorized_keys` pins it to `command="/home/deploy/anneal/deploy/ssh-deploy.sh",restrict`, so all it can
  do is deploy a commit. `DEPLOY_KNOWN_HOSTS` pins the VM's host keys; `DEPLOY_HOST` is its address.
- **Registry access:** the deploy job pipes its short-lived `GITHUB_TOKEN` to `deploy.sh`, which logs in to ghcr.io,
  pulls, and logs out. Nothing long-lived is stored on the VM, and it works whether the packages are public or not.
- **Secrets on the VM** live in `~/anneal/deploy/.env` (mode 600, git-ignored; template `deploy/.env.example`):
  `POSTGRES_PASSWORD`, `ANNEAL_PASSPHRASE_HASH`, `DOCKER_GID`, `DEPLOY_UID`, `DEPLOY_GID`. The repo is public, so
  they must never be committed.
- **Sandbox paths:** the runner bind-mounts work directories into sandbox containers, and the host's daemon resolves
  those paths. So the work root is `/srv/anneal/work` both inside the app container and on the host.
  `/srv/anneal/cargo` (crate downloads for rust-analyzer) and `/srv/anneal/home` persist across deploys.
- **Disk hygiene:** `deploy.sh` removes dangling layers and every anneal image except the deployed one after each
  deploy. Container logs use Docker's `local` driver (5 × 10 MB, compressed) instead of the unbounded default.
- **Caching:** the app sends `Cache-Control: public, max-age=31536000, immutable` for `/assets/*` (content-hashed
  by Vite, so browsers and Cloudflare never re-ask) and `no-cache` for pages, so a deploy shows up on the next load.
  A missing asset is a 404, never the SPA fallback.
- **Host tuning:** `vm.swappiness = 10` (`/etc/sysctl.d/60-swappiness.conf`), so idle memory isn't swapped out while
  RAM is free.

## Everyday operations (on the VM, in `~/anneal`)

```sh
docker compose -f deploy/compose.prod.yml --env-file deploy/.env ps          # status
docker compose -f deploy/compose.prod.yml --env-file deploy/.env logs -f app # logs
deploy/deploy.sh                    # redeploy the latest images by hand (needs `docker login ghcr.io` if private)
deploy/deploy.sh <sha>              # roll back or forward to a specific commit's images
```

If the new app isn't healthy within 3 minutes, `up --wait` fails and so does the workflow run. Compose has already
replaced the old container by then, so roll back with `deploy/deploy.sh <previous sha>` (the image of the last good
commit is kept until the next successful deploy's cleanup).

## One-time setup (done 2026-09-28)

1. DNS: a Cloudflare record `anneal` → `46.224.108.227`, proxied like the other subdomains.
2. Gateway: the `anneal.{$DOMAIN}` block in genuinebnt/genuine.dev's Caddyfile, applied with
   `docker compose -f docker-compose.prod.yml restart caddy` in `~/genuine.dev`. A restart rather than a reload,
   because the Caddyfile is a single-file bind mount that keeps pointing at the old file after `git pull`.
3. VM: `git clone https://github.com/genuinebnt/learn-rust.git ~/anneal`, `/srv/anneal/{work,cargo,home}` owned by
   deploy, and `deploy/.env` filled in.
4. Passphrase (prompts locally; only the argon2 hash leaves your machine):

   ```sh
   cargo run -q -p anneal-cli -- passphrase |
     ssh deploy@46.224.108.227 "sed -i '/^ANNEAL_PASSPHRASE_HASH=/d' ~/anneal/deploy/.env && cat >> ~/anneal/deploy/.env"
   ```

   then redeploy (re-run the latest workflow, or `deploy/deploy.sh` on the VM).
5. GitHub secrets `DEPLOY_SSH_KEY`, `DEPLOY_KNOWN_HOSTS`, `DEPLOY_HOST`, and the authorized_keys line above.

The same VM used to run Marginal; it was shut down on 2026-09-28 (containers, images and volumes removed) and its
host now redirects to its project page.

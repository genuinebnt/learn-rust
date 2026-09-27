# anneal

A personal Rust interview-prep platform for SDE-2 / SDE-3 backend roles: DSA, Rust depth, and
build-it tracks, each running easy → hard, with a sandboxed runner and an in-browser workspace.

- Plan and decisions: [docs/PLAN.md](docs/PLAN.md)
- Curriculum: [docs/CURRICULUM.md](docs/CURRICULUM.md)
- Designs: [docs/design_handoff_anneal/designs/anneal-screens.html](docs/design_handoff_anneal/designs/anneal-screens.html)
  (opens directly in a browser; the original 1a–1d designs need `./serve.sh` in that folder)

## Run it

Needs Rust with the `rust-analyzer` and `rust-src` components (`rustup component add rust-analyzer rust-src`),
pnpm, and OrbStack (the sandbox is pinned to the `orbstack` Docker context).

```sh
docker compose up -d                                                    # Postgres on :5434
docker build -t anneal-runner:1.98 -f docker/runner.Dockerfile docker   # sandbox image (rebuild after changing docker/deps)
(cd web && pnpm install && pnpm build)
cargo run -p anneal-api                                                 # http://localhost:8787
```

For UI work with hot reload, run `cargo run -p anneal-api` and `cd web && pnpm dev`, then open
http://localhost:5180 (Vite proxies `/api` to the server).

The server reads its settings from the environment; `cargo run` fills in local defaults from
`.cargo/config.toml`. See the table at the top of [crates/api/src/main.rs](crates/api/src/main.rs).

### Login

Without `ANNEAL_PASSPHRASE_HASH` there's no login, and the server only starts on a loopback address.
To require a passphrase (and before listening anywhere else):

```sh
cargo run -p anneal-cli -- passphrase        # prompts twice, prints ANNEAL_PASSPHRASE_HASH='$argon2id$…'
export ANNEAL_PASSPHRASE_HASH='$argon2id$…'  # single quotes: the hash contains $
export ANNEAL_COOKIE_SECURE=true             # when served over HTTPS
cargo run -p anneal-api
```

Sessions last 30 days in an HttpOnly, SameSite=Strict cookie; only a SHA-256 of each token is stored. Five wrong
passphrases in a row pause logins for a minute. Editor settings (the **Aa** button above the editor: font size, font family, Vim mode with `jk`/`kj` to leave insert mode) are saved
on the server.

### Crates in problems

A problem may use crates from the fixed set in [docker/deps/Cargo.toml](docker/deps/Cargo.toml) by listing them in
`problem.toml`: `crates = ["tokio", "serde"]`. The runner adds those dependency lines (versions pinned by
`docker/deps/Cargo.lock`). In the Docker sandbox they come from the copy vendored into the image, so runs stay
offline; host runs fetch from crates.io. To change the set, edit the manifest, run `cargo generate-lockfile` in
`docker/deps`, and rebuild the image.

## Content

Problems live in `content/tracks/<track>/problems/<slug>/` as a `problem.toml`, `statement.md`,
`starter.rs`, `solution.rs` and `tests/{visible,hidden}.rs`. Tests use `check!(input, got, expected)`
so failures show input / expected / got.

```sh
cargo run -p anneal-cli -- validate                  # check every track and problem
cargo run -p anneal-cli -- list d9                   # problems in a track
cargo run -p anneal-cli -- run d9-network-delay-time --solution --submit --docker
```

## Tests

```sh
cargo test --workspace                               # needs the compose Postgres
cargo test -p anneal-runner -- --ignored             # the Docker sandbox test
```

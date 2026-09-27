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
docker build -t anneal-runner:1.98 -f docker/runner.Dockerfile docker   # sandbox image, once
(cd web && pnpm install && pnpm build)
cargo run -p anneal-api                                                 # http://localhost:8787
```

For UI work with hot reload, run `cargo run -p anneal-api` and `cd web && pnpm dev`, then open
http://localhost:5180 (Vite proxies `/api` to the server).

The server reads its settings from the environment; `cargo run` fills in local defaults from
`.cargo/config.toml`. See the table at the top of [crates/api/src/main.rs](crates/api/src/main.rs).

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

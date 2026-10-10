# The CLI on another computer

The owner wants to stop at any point, sit down at another laptop, install the CLI from the web app and carry on from the last
commit. Progress and code travel separately:

| What | Where it lives | How it reaches the new laptop |
|---|---|---|
| Stage progress, hints, solutions opened | the app's Postgres (one owner) | sign in with `anneal course login` |
| The learner's code, the stage definitions and `.anneal/progress.json` | the learner's own git repo (`bustub-rs`), **on GitHub** | `anneal course restore` clones it |
| The CLI itself | built by CI, served by the app at `/downloads/anneal-<os>-<arch>` | `curl -fsSL https://<app>/install.sh | sh` |

Only what was committed **and pushed** is restored; uncommitted work stays on the old laptop (accepted by the owner).

## First laptop, once

```
anneal course init bustub          # makes bustub-rs with its own git repo
anneal course login https://anneal.genuinebasil.dev
anneal course remote git@github.com:YOU/bustub-rs.git     # origin + tells the app (create the private repo on GitHub first)
git push -u origin HEAD            # the pre-push hook runs the current stage's tests and reports them
```

`anneal course remote` with no URL records the current `origin`. Later `git push` is all it takes.

## Any other laptop

```
curl -fsSL https://anneal.genuinebasil.dev/install.sh | sh     # ~/.local/bin/anneal (ANNEAL_INSTALL_DIR to change it)
anneal course login https://anneal.genuinebasil.dev
anneal course restore              # asks the app for the repo URL, clones it, installs the hooks, shows the next stage
```

`restore` also takes the URL (`anneal course restore <url> [dir]`), which works without signing in. The laptop needs git, curl and a
Rust toolchain, and its git must be able to read the repository (an SSH key, or `gh auth login` for HTTPS). The CLI runs on macOS
(Apple silicon and Intel) and Linux x86-64; there is no Windows build.

## How the pieces are wired

- **CI** (`.github/workflows/ci.yml`, job `cli`): on every push to master it builds `anneal` in release mode for
  `x86_64-unknown-linux-gnu`, `aarch64-apple-darwin` and `x86_64-apple-darwin`, and uploads them as `anneal-linux-x64`,
  `anneal-macos-arm64`, `anneal-macos-x64`. The `deploy` job needs `cli`, downloads the artifacts into `dist-cli/`, and the
  Dockerfile copies them to `/app/downloads` (`ANNEAL_DOWNLOADS`). `dist-cli/.gitkeep` keeps a local `docker build` working.
- **API** (`crates/api/src/lib.rs`): `GET /install.sh` (public; `crates/api/src/install.sh` with its own address filled in from the
  `Host` / `X-Forwarded-*` headers) and `GET /downloads/*` (public static files). `GET`/`PUT /api/courses/{course}/repo` store the
  repository URL in `course_repos` (migration 0016).
- **CLI** (`crates/cli/src/course.rs`): `remote` and `restore`; `course_sync.rs` has the two calls to the app.
- **Web**: the Get started panel on the Courses page shows the install line as step 1, and an "Another laptop" panel.

The binary embeds the course template, so a downloaded CLI matches the app it came from; after a new module ships, the learner runs
`anneal course update` (the CLI of a new deploy has the new stages).

## Test it without a deploy

Start the API on a throwaway database with `ANNEAL_DOWNLOADS=/some/dir` holding a file named `anneal-<os>-<arch>`, then
`curl -fsSL http://127.0.0.1:8791/install.sh | ANNEAL_INSTALL_DIR=/tmp/bin sh`, `anneal course remote <bare repo>`, and
`anneal course restore` on a second `XDG_CONFIG_HOME`. The API tests `the_repository_of_a_course_is_recorded_and_read_back` and
`the_installer_names_the_address_it_was_fetched_from` cover the server half.

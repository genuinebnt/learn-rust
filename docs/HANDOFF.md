# anneal · handoff

Last updated 2026-09-27. Read this first if you're picking the project up, whether you're working locally or
in a cloud session. It covers where things stand, how to run and check the work, how the owner likes to work,
and what's next, in order.

## 1. What this is

**anneal** is a personal Rust interview-prep platform for SDE-2/SDE-3 backend interviews, with one user, the owner. It has:

- an axum + sqlx API (`crates/api`) on Postgres;
- a sandboxed Rust runner (`crates/runner`);
- file-based content (`content/tracks`);
- a Vite + React SPA (`web`).

| Doc | What it holds |
|---|---|
| [PLAN.md](PLAN.md) | Decisions and architecture (D1–D8), phases |
| [CURRICULUM.md](CURRICULUM.md) | Every section, track and stage, and what each problem teaches |
| [ROADMAP.md](ROADMAP.md) | Everything beyond the curriculum, and **§7, the agreed order of work** |
| [design_handoff_anneal/designs/](design_handoff_anneal/designs/) | HTML mockups. `anneal-screens.html` is every screen; `workspace-layout.html` is the approved layout controls |
| [README.md](../README.md) | Run, login, crates, content CLI, tests |

## 2. Where things stand

**Content:** 13 tracks, 252 problems, all passing `anneal verify`:

| Track | Problems |
|---|---|
| D1 Arrays & hashing | 24 |
| D2 Two pointers & windows | 18 |
| D3 Stacks & queues | 14 |
| D4 Binary search | 14 |
| D5 Linked lists | 15 |
| D9 Graphs | 35 |
| L1 Ownership & moves | 18 |
| L2 Borrowing | 35 |
| L3 Lifetimes | 20 |
| S1 Option & Result | 10 |
| S2 Strings & text | 18 |
| S3 Vec & slices | 20 |
| S4 Maps & sets | 11 |

**Built:**
- **Catalog:** the section catalog pages (Rustfinity-style) and the track page.
- **Workspace:**
  - three panels, with the console below the editor;
  - Run (scratch `main.rs`), Run tests and Submit;
  - rust-analyzer, borrow lanes and rule checks;
  - hidden tests revealed once solved.
- **Progress dashboards:** overview, Rust stats, reviews.
- **Spaced repetition.**
- **Login:** a single-user passphrase.
- **Settings:** editor (font, size, Vim with `jk`/`kj`) and accent colour.
- **Crates in problems:** vendored into the runner image.

**Designed but not built** (all in `anneal-screens.html`): Today, Library, Mock interview, Readiness, the project pages.

**Workspace layout as of the last session** (each point was a separate request from the owner; keep them):
- Left panel: Problem, Hints, Solution, Related. Centre: the editor, with the console under it. Right panel: Tests only, with Submit at the bottom.
- The editor tab bar has a single run button that depends on the tab. On `main.rs SCRATCH` it's **▷ Run** (⌘'). On every other tab it's **Run tests** (⌘↵).
  - Both buttons show a spinner while busy.
  - Run tests and Submit reopen the right panel if it's hidden.
- Layout icons at the **top right of the problem bar** show or hide the left panel (⌘B), the console (⌘J) and the right panel (⌥⌘B). Hidden panels disappear completely: no rails, no strips.
- The status bar holds clickable toggles: rust-analyzer, autocomplete, and borrow lanes (lanes only on problems that have them).
- The problem bar never scrolls. Tag pills drop out first, then the breadcrumb truncates.
- The console hides until the next run, then opens on whichever tab has something to show.
- The Borrows tab was **removed** on request. Borrow lanes live in the editor only.

## 3. Running it

### Locally (macOS, OrbStack)

```sh
docker compose up -d                                                    # Postgres 18 on :5434
docker build -t anneal-runner:1.98 -f docker/runner.Dockerfile docker   # sandbox image
(cd web && pnpm install && pnpm build)
cargo run -p anneal-api                                                 # http://127.0.0.1:8787
```

`.cargo/config.toml` supplies `ANNEAL_DATABASE_URL` and `DATABASE_URL` for local runs. The full list of
environment variables is in the doc comment at the top of `crates/api/src/main.rs`. The main ones:

| Variable | Purpose |
|---|---|
| `ANNEAL_SANDBOX=host` | Runs code without Docker |
| `ANNEAL_DOCKER_CONTEXT` | Docker context; defaults to `orbstack` |
| `ANNEAL_PASSPHRASE_HASH` | Turns on login |

Restart the API after backend changes. It serves `web/dist`, so rebuild the web app after frontend changes, or
use `pnpm dev`.

### In a cloud session (no Docker, maybe no Postgres)

| What | Needs | Command |
|---|---|---|
| Content authoring and checking | a Rust toolchain only (edition 2024, so rustc ≥ 1.85; the image uses 1.98) | `cargo run -q -p anneal-cli -- validate`, then `cargo run -q -p anneal-cli -- verify <track>` |
| Unit tests (content, runner, rules) | Rust | `cargo test -p anneal-content -p anneal-runner -p anneal-rules` |
| API tests | Postgres | `cargo test -p anneal-api` (`DATABASE_URL` is forced to localhost:5434 in `.cargo/config.toml`, so start Postgres there or edit the config) |
| Web type-check and build | Node + pnpm/npm | `cd web && npx tsc -b --noEmit && npm run build` |

Notes on the cloud setup:
- `anneal verify` always uses the **host** runner, so it doesn't need Docker.
- Problems that list `crates = [...]` fetch them from crates.io when run on the host, so they need network access.
- In a cloud session, content work and backend code are the safest things to do. UI work needs the owner's
  review anyway (§4).

### Checking UI without screenshots

`node tools/ui-check.mjs <url> "<js expression>" [width]` loads a page in headless Chrome and prints the
expression's value. Use it to check widths, overflow and which elements exist, at 1280px and 1440px. Two
things to watch:
- **1280px is the tight case.** The centre column is about 580px there.
- **Clean up test data.** Checks that run or submit code create attempts in the dev database. Clear them with:

```sh
psql postgres://anneal:anneal@127.0.0.1:5434/anneal -c "TRUNCATE attempts, reviews, focus_time, scratch CASCADE"
```

## 4. How the owner works (follow these)

- **Do exactly what's asked.** Put extra ideas in a proposal with a recommendation and wait for an answer. Unrequested
  changes were reverted twice. Never drop an existing control while moving things around. "do recommended" means go
  ahead with your recommendations.
- **Mockups first for new screens and big UI changes.** Publish an HTML mockup and wait for approval. Small
  requested tweaks can be built directly.
- **No visible scrollbars anywhere** (app.css hides them). Content must fit without them.
- Editor indent is **4 spaces**. The editor font, size and Vim mode are user settings.
- **Difficulty colours:** easy = `--grn`, medium = `--warn`, hard = `--bad`. **Area colours:** DSA = `--acc`,
  Rust = `--vio`, Build = `--grn`.
- **Commits:**
  - go on `master`;
  - push to `origin` (github.com/genuinebnt/learn-rust) when asked;
  - end each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (or your model's line);
  - update the status in this file and in ROADMAP §0 when something lands.
- **No prettier config exists.** Don't run prettier over files; it reformats everything to 80 columns. Match the
  surrounding style (about 160 columns, double quotes).

## 5. Content authoring

`content/tracks/<track>/problems/<slug>/` is the source of truth. Each problem folder holds:
- `problem.toml`
- `statement.md`
- `starter.rs`
- `solution.rs`
- `tests/visible.rs`
- `tests/hidden.rs`

`tools/author/` holds the Python specs the 13 tracks were generated from: `author.py` has the helpers, and there's
one script per track. They **reproduce the committed content exactly**, which was checked on 2026-09-27 by
regenerating into a copy and diffing.

To change a track:

```sh
cd tools/author && python3 d9.py                       # rewrites content/tracks/d9-graphs
cargo run -q -p anneal-cli -- verify d9                # from the repo root
```

The script and the folder must stay in sync. Either edit the spec and rerun it, or hand-edit the files and stop
using that script. Don't mix the two. `ANNEAL_CONTENT_ROOT=/tmp/x python3 d9.py` writes into a scratch copy instead.

The test conventions:
- Tests use the `check!(input_description, got, expected)` macro. The runner injects it (`crates/runner/src/project.rs`).
- The workspace parses `check!` calls to show input and expected values per test (`web/src/workspace/testcases.ts`).
- Problem crates use edition 2021, and the package is named `solution`.

## 6. What's next, in order (ROADMAP §7)

### 6.1 Test hardening (step 2a): in progress, start here

The owner asked for real unit tests, not a handful of trivial cases. Today's audit:
- the median problem has 4 tests, and the median hidden count is 2;
- 62 problems have only 3 tests;
- 62 have a large-input test;
- only 5 have randomized comparisons.

Plan (approved):

1. **Verifier support for wrong solutions.** Add an optional `wrong/<name>.rs` in a problem folder: a plausible but incorrect
   solution (off-by-one, wrong complexity, missed edge case). `anneal verify` must fail if any wrong solution passes
   Submit. The code is `verify` in `crates/cli/src/main.rs`, which today checks the reference solution passes and the
   starter fails. Also teach `tools/author/author.py` to write `wrong` entries.
2. **A seeded RNG in the test prelude**, next to `check!` in `crates/runner/src/project.rs`: a tiny splitmix/xorshift with
   no crate dependency. Hidden tests use it for randomized comparisons against a brute-force reference written
   inside the test.
3. **Raise the bar, track by track.** The targets:
   - ≥ 3 visible and ≥ 8 hidden tests;
   - an edge-case checklist per problem type (empty, single, duplicates, negatives, bounds/overflow, max size,
     Unicode for strings);
   - one randomized brute-force comparison where there's a simple reference;
   - one scale test sized so a wrong-complexity solution times out.

   Start with D1 and work down the table in §2. Rerun `anneal verify <track>` after each track.
4. When every track meets the bar, raise the verifier minimums (today they're 2 visible and 1 hidden, in `verify`).

### 6.2 Then, per ROADMAP §7

- **Step 1 content:**
  - D6 Trees, D7, D8, D12 DP, D10, D11, D13, D14;
  - L4–L8;
  - S5–S9.

  Track outlines are in CURRICULUM.md. Include the §10.2 additions for L4, L5, S4, S6 and S7.
- **Step 2b, Q concept cards** (ROADMAP §10.3): needs a card-mode mockup first.
- **Step 2c, AI assistant with Gemini** (ROADMAP §11): the key stays server-side, and AI help before a solve marks the
  attempt assisted. Build in the order of §11.3. New UI needs mockups.
- Designed screens still to build: Today, Readiness, Library, Mock interview, project pages.

## 7. Known rough edges

- The Run tests button changes width by about 3px between idle and busy.
- With five file tabs open at 1280px, the tab list scrolls sideways (the scrollbar is hidden). It works, but
  isn't obvious.
- `cargo test -p anneal-runner -- --ignored` (the Docker sandbox test) only runs where the runner image exists.
- The web bundle is over 500 kB (Vite warns). Code-splitting CodeMirror would fix it; it's low priority.

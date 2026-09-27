# anneal — build plan

Personal Rust interview-prep platform for SDE-2 / SDE-3 Rust backend roles.
Source material: `docs/design_handoff_anneal/` (objectives, tokens, 4 designed screens),
`docs/rust_learning_platform_curriculum.html` (long-range curriculum),
`docs/rust template/` (old study packet — content bank to import).

## Decisions

| # | Decision | Why |
|---|---|---|
| D1 | **Workspace = hybrid 1a + 1c.** 1a's three-pane Split layout; 1c's borrow lanes, inline rustc lens and run timeline + diff are added inside the centre pane. Lanes toggle appears only on problems tagged `borrowck`. | Densest layout for grinding; keeps the teaching visuals where they matter. |
| D2 | **Local-first, on OrbStack.** `docker compose up` on the Mac for Postgres; `anneal-api` (axum) runs on the host. User code runs in throwaway containers, pinned to the `orbstack` Docker context (`ANNEAL_DOCKER_CONTEXT` overrides). Single user, no auth. | One user. A public deploy needs gVisor/Firecracker + auth; deferred (see Later). |
| D3 | **Frontend = Vite + React 19 SPA**, TypeScript strict, TanStack Router + Query, CodeMirror 6. Plain CSS with the handoff tokens as custom properties (no Tailwind — the tokens *are* the design system). | Matches marginal ADR-004. axum owns all data; the SPA is a static bundle served by the API. |
| D4 | **Content lives in files, progress lives in Postgres.** Problem folders are loaded and validated at API start (hot-reloaded in dev). The DB stores only user state keyed by stable problem ids. | Agents author content in bulk via git; no sync layer between files and tables. |
| D5 | **rust-analyzer runs on the host**, one process per open workspace, bridged to the browser over a WebSocket (`/lsp/:session`). Toggle = connect / disconnect the LSP client. | Local-first makes this safe and fast. RA-in-WASM can't resolve std well. |
| D6 | **Missing screens are mocked in HTML first** (`designs/anneal-screens.html`), reviewed, then implemented. | User choice. |

## Architecture

```
learn-rust/                      (cargo workspace)
├─ crates/
│  ├─ content/     problem.toml schema, folder loader, validation, in-memory catalog
│  ├─ runner/      materialise a cargo project, run clippy + tests in Docker, parse results
│  ├─ rules/       syn-based fix-this rule checker + changed-line diff
│  ├─ lanes/       borrow lanes derived from rustc diagnostic spans
│  └─ api/         axum: REST + LSP WebSocket bridge + serves web/dist
├─ web/            Vite React SPA
├─ content/        tracks/, concepts/, projects/ — one folder per problem
├─ docker/         runner image (rust:1.x-slim + warm registry of allowed crates)
└─ docs/
```

### Runner (crates/runner)

1. Materialise `/work/<run-id>/` : `Cargo.toml` (edition 2021, allowed deps only), `src/lib.rs` (user code),
   `tests/visible.rs`, and on Submit `tests/hidden.rs`. Tests use a tiny `anneal_check!` macro that prints
   `ANNEAL {"input":…,"expected":…,"got":…}` before panicking, so the UI can show input / expected / got.
2. `docker run --rm --network none --memory 768m --cpus 2 --pids-limit 256 --read-only`
   with `/work` bind-mounted rw, a named volume for `CARGO_TARGET_DIR` per problem (warm incremental builds),
   and a hard wall-clock timeout (compile 60 s, tests 10 s).
3. Inside: `cargo clippy --all-targets --message-format=json` → rustc diagnostics (spans, codes, labels).
   If there are errors, stop. Else `RUSTC_BOOTSTRAP=1 cargo test -- -Z unstable-options --format json --report-time`
   → per-test events with captured stdout (verified on rustc 1.98).
4. Return `RunResult { status: CompileError | TestsRan | RuleViolation | Timeout, diagnostics[], tests[], clippy[], duration }`.

Fix-this rules (`crates/rules`) run in the API process before the container: parse with `syn`, walk for forbidden
method calls / paths (`.clone()`, `RefCell`, `unsafe`), count changed lines against the starter with `similar`.
A violation is recorded as a run with `status = RuleViolation` (timeline label `rule: clone`).

Borrow lanes (`crates/lanes`): from E0499/E0502/E0505/E0506/E0597 diagnostics, each span label becomes a lane event
("first mutable borrow occurs here" → lane start, "first borrow later used here" → lane end, primary span → conflict).
Good enough for drills; MIR/Polonius facts are a Later item.

### Data model (Postgres, sqlx migrations)

| Table | Holds |
|---|---|
| `attempts` | one per (problem, started_at): mode `practice / mock / resolve`, `assisted`, `hints_revealed`, `solution_revealed`, `solved_at`, `elapsed_ms` |
| `runs` | every Run/Submit: attempt id, code snapshot, status, passed/total, diagnostics json, rule hits, duration |
| `drafts` | latest editor buffer per (problem, file) — autosave |
| `reviews` | spaced repetition: problem, due_on, interval_days, streak, last_result |
| `project_repos` | per project: current stage, file tree snapshot per stage (jsonb), stage diffs |
| `mock_sessions` | round type, problem ids, started/ended, rubric scores, self-check answers |
| `readiness_snapshots` | daily per-area % for the trend line |

### Learning rules

- Hints reveal one at a time. Any hint or early solution → attempt is **assisted**.
- Solution unlocks at all tests passing (visible + hidden), or "Reveal anyway" (assisted).
- Review schedule: assisted solve → due in 3 days; each unassisted re-solve moves 3 → 7 → 21 → 60; an assisted
  re-solve resets to 3. Unassisted first solves get one retention check at 21 days.
- Readiness per track = Σ weight(problem) × credit / Σ weight(all problems in the track).
  weight: easy 1, medium 2, hard 3. credit: unassisted 1.0, tested out 0.8, assisted 0.5, unsolved 0.
  Credit decays 10 % per week a review is overdue (floor 0.25).
  Overall = mean over tracks, weighted ×2 for tracks marked core in `CURRICULUM.md` and ×1 for light and SDE-3 tracks
  (SDE-3 tracks move to ×2 once the SDE-2 gate passes). The readiness page groups track tiles by section.

## Routes (SPA)

| Route | Screen | Design |
|---|---|---|
| `/` | Today: due re-solves, resume points, readiness summary | new (mock) |
| `/dsa` , `/rust` , `/build` | Section pages: the tracks in each section (nav: DSA copper · Rust violet · Build green) | re-cut of the Tracks index + Concepts mocks |
| `/t/:track` | Track page: stages Easy → Hard, problem table, readiness | 1d TrackGraphs, used for every track |
| `/p/:problem` | Workspace (hybrid) | 1a + 1c, hybrid mocked |
| `/projects/:project` | Project stage map | new (mock) |
| `/projects/:project/:stage` | Project stage workspace (file tree, carried-forward tests) | new (mock) |
| `/library` | All problems, filterable | new (mock) |
| `/mock` , `/mock/:session` | Mock interview setup → in session → rubric | new (mock) |
| `/readiness` | Readiness by section and track, trend, review queue | new (mock), tiles to re-cut |

## Content map

The full curriculum is in **`CURRICULUM.md`**: 9 sections, 54 tracks plus 5 projects, every track ordered Easy → Medium → Hard, with an
SDE-2 path, an SDE-3 path, a week-by-week schedule and readiness gates.

| Section | Tracks | Nav |
|---|---|---|
| L Rust Language | 10 | Rust |
| S Rust Standard Library | 11 | Rust |
| C Concurrency & Async | 6 | Rust |
| Y Systems Rust | 5 | Rust |
| D Data Structures & Algorithms | 14 (Graphs seeded from TrackGraphs, + 3 Blind 75 problems) | DSA |
| B Backend Rust | 6 | Build |
| M Design in Rust (machine coding) | 2 | Build |
| P Projects | shortline, jobq, kvlite, minirt, raft-lite | Build |
| H System design | reading + spoken mocks (practice mode deferred) | — |

**Import from the old template** (`docs/rust template/scripts/exercise_extract.json`): 98 write exercises (starter + solution)
and 490 harden sub-problems with assertion harnesses → drafted into `content/` by an import script, marked `status = "draft"`
until each has visible + hidden tests. `CURRICULUM.md` §11 says which track each one lands in.

## Phases

Each phase ends with a check you can run.

**Progress (2026-09-27):** phases 0 and 2–6 are done, and phase 1's shell exists: runner (host + OrbStack sandbox),
content loader, API, workspace with rust-analyzer, rule checker, error lens, borrow lanes and run timeline.
Phase 7 is partly done: the section pages and track page exist, without the design's topology panel and readiness
tiles. Today, Library, Mock interview and Readiness (8, 10) are not started, projects (9) are not started, and content
(11) is 2 of 70 seeded problems.

| Phase | Deliverable | Done when |
|---|---|---|
| 0 | Plan + missing-screen mockups | mockups reviewed |
| 1 | Workspace + tokens + app shell (header, theme persisted, grid ground) | shell matches mockups in both themes |
| 2 | `content` crate + problem folder format (section / track / stage / problem) + D9 Graphs seed + L2 Borrowing | `GET /api/tracks/d9-graphs` returns 7 stages / 35 problems |
| 3 | `runner` crate + Docker image | Network delay: mock code → 4/6, reference → 6/6 |
| 4 | Workspace (hybrid): editor, tabs, tests panel, Run/Submit, hints/solution gating, assisted flag, drafts | all 1a interactions work against the real runner |
| 5 | rust-analyzer bridge + autocomplete toggles | inlay hints, lenses, diagnostics on; word completion when RA is off |
| 6 | Fix-this: rules, error lens, borrow lanes, run timeline + diff | 1c flow incl. a `rule: clone` run |
| 7 | Section pages + track page (all tracks) | stage click filters table; tag chips filter |
| 8 | Reviews + readiness + Today page | stat strips computed from data |
| 9 | Projects: stage repos, carried-forward tests, snapshots | shortline stages 1–3 playable |
| 10 | Library, Mock interview, Readiness page | per mockups |
| 11 | Content waves per `CURRICULUM.md` §11 + old-template import | wave 1 (L1, L2, S1, S3, S4, D1, D2) out of draft |

## Later

Public deploy (gVisor runner, auth, rate limits) · MIR-based borrow lanes · "Depth" section from the long curriculum ·
voice-recorded explanations for mock rounds.

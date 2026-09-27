# Handoff: anneal — Rust interview-prep platform

## Objective
Build an interactive Rust learning platform that gets one engineer (the owner) interview-ready for **SDE-2 / SDE-3 Rust backend roles**. Users solve problems in a full in-browser editor against test cases, with hints, solutions and concept teaching. Level: intermediate → advanced, plus beginner practice.

Working name **anneal**, intended to live at `anneal.genuinebasil.dev`, visually a sibling of genuinebasil.dev (see `reference/`).

## About the design files
Files in `designs/` are **design references built in HTML** (open `Anneal Mockups.dc.html` in a browser; `support.js` must sit next to it). They show intended look and behaviour. They are **not production code**. Recreate them in the target stack (recommended below). Fidelity: **high** — colours, type, spacing and copy are final unless noted.

## Product scope

### Content types
| Type | Description | Accent |
|---|---|---|
| **Write it** | Signature + hidden/visible tests; user writes the implementation. | copper |
| **Fix this** | Non-compiling or wrong program; user fixes it under rules (e.g. "no `.clone()`", "max 2 lines changed"). | violet |
| **Project stage** | One stage of a multi-stage project; only tests are given; each stage builds on the previous repo state. | green |

Every problem has: id, title, mode, level (beginner/intermediate/advanced), **multiple tags**, statement (markdown), signature, examples, constraints, "what this teaches" bullets, 1–3 hints, reference solution + explanation + complexity, interview follow-up question, linked concepts, visible + hidden tests.

### Sections
1. **Tracks (DSA prep series)** — ordered tracks (arrays & hashing, two pointers, trees, **graphs**, heaps, tries, backtracking, **DP**, …). Each track = ordered stages from basics → advanced, each stage = problems. Ends with a capstone mock round. *Designed: Graphs track (`TrackGraphs`).*
2. **Concepts** — drills per Rust area: ownership & moves, borrowing / borrow checker, lifetimes, traits & dispatch, generics & bounds, iterators & closures, error handling, smart pointers, collections, pattern matching, concurrency (Send/Sync, Mutex, channels), async & Pin, macros, unsafe & FFI. Mix of Fix-this and Write-it. *Designed: Fix-this drill in `WorkspaceTrace`.*
3. **Projects** — build one project from scratch across ~9 stages (suggested: `shortline`, a URL-shortener API in axum + sqlx + Postgres: health route → typed errors → create link → persistence → redirects → API-key auth → rate limiting (tower) → background jobs + graceful shutdown → tracing/metrics). Only tests are provided per stage; earlier-stage tests must keep passing. *Not yet designed — reuse the stage-card + phase-bar language from `TrackGraphs`.*
4. **Library** — all problems, filter by tag / mode / level / status. *Not designed; use the TrackGraphs table.*
5. **Mock interview** — timed, hints off, rust-analyzer off, rubric after. *Not designed; capstone card in TrackGraphs describes it.*
6. **Readiness** — interview-readiness map across the 14 Rust areas (% per area, drills solved). *Designed as a section in TrackGraphs; promote to its own page.*

### Editor requirements
- Full code editor (Monaco or CodeMirror 6), Rust syntax, multi-file tabs (`src/lib.rs` editable, `tests.rs` read-only).
- **Toggle: autocomplete on/off.** When rust-analyzer is off, completion falls back to buffer words.
- **Toggle: rust-analyzer on/off.** On: inlay type hints, code lenses ("▸ Run 6 tests | Debug"), live diagnostics. Off: errors only on Run.
- **Toggle: borrow lanes** (Fix-this / borrow problems): per-line visualisation of live borrows beside the code; conflicts drawn in red.
- Inline annotated compiler errors (rustc "error lens" block under the failing line).
- Run tests (⌘↵) and Submit (runs hidden tests). Clippy on run. Edition 2021, stable rustc.
- Interview timer; prev/next problem.
- Run timeline: every run recorded (compile error code / tests passed / rule violation), with diff between consecutive runs.

### Learning rules
- Hints are revealed one at a time; any hint or early solution reveal marks the attempt **assisted** and schedules a **re-solve** (spaced repetition: e.g. 3 days, then 7, 21).
- Solution unlocks at all tests passing, or "Reveal anyway" (assisted).
- Fix-this rules are enforced by a checker (AST/lint), reported as "rule: clone" in the timeline.
- Readiness % per area = weighted solved drills (unassisted > assisted, advanced > beginner), decays if re-solves are overdue.

## Screens (designed)

### Shared chrome
- Header 52px: 2×2 square logo mark (copper, violet, green, outline) + `anneal.genuinebasil.dev` (JetBrains Mono 13/500). Nav in mono 12/500: **Tracks** (copper), **Concepts** (violet), **Projects** (green), `|`, Library / Mock interview / Readiness (dim). Active item: 1px underline in its colour. Right: `READINESS 62%`, theme toggle (half-filled circle), avatar ring "gb".
- Section headers: mono 12/500, letter-spacing .26em, dim; flex rule line; right-aligned mono caption (e.g. `read → write → run → review`).
- Page background: 56px grid of 1px lines in `--grid`.
- Chunky phase bar: 30–36px tall, solid accent, mono 11–12/600 label, letter-spacing .16em, text `--on-acc` (e.g. `SOLVED · 4 OF 4`, `IN PROGRESS · 0 OF 6`); under it a 4–5px segmented bar with one segment per item.
- Cards: `--panel`, 1px `--line2`, radius 8, padding 28; mono 15/600 title top-left, colour tag top-right (mono 10.5/600, .2em); outlined-box mini diagram centred; body 14/1.6 `--mut`.

### 1a — Workspace · Split (`WorkspaceSplit.dc.html`, 1440×900)
Header → 44px sub-bar (breadcrumb, title, mode/level/tag chips, `15 / 32`, interview timer) → grid `360px | 1fr | 330px`.
- Left: tabs Problem / Hints n/3 / Solution / Concepts.
- Centre: file tabs, Autocomplete + rust-analyzer switches (28×16 track), editor (12.5px mono, 21px lines, gutter 48px), 26px status bar.
- Right: Tests / Compiler / Output tabs; `4 / 6 passing`, 6-segment bar, expandable test rows (input / expected / got + nudge); Run tests + Submit (green).

### 1b — Workspace · Bench (`WorkspaceBench.dc.html`, 1440 wide, scrolling)
Hero (80px/800 title, copper second line, lead 18px, chips, 54px buttons) + example-graph topology panel → 4-column stat strip → **The bench** (editor card + test-tile grid with per-test mini node diagrams and a phase bar) → **Hints & solution** (4 cards; locked hints blurred with centred Reveal button) → **What this teaches** (3 concept cards) → big follow-up question.

### 1c — Workspace · Trace (`WorkspaceTrace.dc.html`, 1440×900)
56px icon rail (BRF/HNT/TST/SOL) toggling a 340px drawer → main: title bar with pill toolbar (autocomplete / RA / lanes, reset, Run) → editor with 280px borrow-lane column on the right (lanes at x=20/70/120; bars 6px wide, radius 3) → inline rustc lens (120px, `--bad` border + `--bad-bg`) under line 15 → status bar → run timeline + diff. Hint 3 → "Apply to line 15" switches to the fixed state (green line, no conflict, concept card "Split borrows" appears).

### 1d — Track · Graphs (`TrackGraphs.dc.html`, 1440 wide, scrolling)
Hero + clickable 7-node track topology → stat strip (Now on / Solved / Re-solve due / Graphs round %) → **The stages**: 3-col grid of 7 stage cards + a span-2 capstone card → selected-stage table with tag-filter chips (columns: status, #, problem, mode, level, tags, best) → **Rust readiness**: 7×2 tiles (name, big %, 10-seg bar, drills count; copper dot = trained by this track; colour: ≥70 green, 40–69 copper, <40 red) → marquee of algorithms/error codes (60s linear loop) → closing headline.

All 32 graph problems with modes/tags are listed in the `P` array in `TrackGraphs.dc.html` — use as seed data.

## Design tokens (oklch; dark default, light via `[data-theme=light]`)
| Token | Dark | Light | Use |
|---|---|---|---|
| --bg | 0.165 0.012 255 | 0.975 0.003 255 | page |
| --panel | 0.195 0.013 255 | 0.995 0.002 255 | cards |
| --raise | 0.235 0.014 255 | 0.95 0.005 255 | active tab, code blocks |
| --line / --line2 | 0.32 / 0.255 0.013 255 | 0.86 / 0.915 0.007 255 | borders |
| --grid | 0.205 0.012 255 | 0.94 0.006 255 | background grid |
| --fg / --mut / --dim | 0.95 / 0.80 / 0.63 | 0.20 / 0.40 / 0.52 | text |
| --acc (copper) | 0.76 0.11 55 | 0.58 0.13 50 | Write it, current, primary highlight |
| --vio | 0.72 0.13 290 | 0.52 0.17 290 | Fix this, concepts, hints |
| --grn | 0.77 0.13 165 | 0.54 0.12 165 | pass, Run/primary buttons, projects |
| --bad | 0.70 0.16 25 | 0.54 0.18 25 | errors, fails |
| --warn | 0.83 0.12 85 | 0.58 0.12 75 | rule violations |
| --on-acc | 0.17 0.02 255 | 0.99 0.002 255 | text on solid accent |
`*-bg` tints = accent at 10–14% alpha. Syntax: kw violet, types warm yellow (h70), fn blue (h235), strings green (h160), numbers copper (h45), macros teal (h200), comments `--com`. Exact values are in each file's `<style>` block.

**Type:** Plus Jakarta Sans (400–800) for UI/headlines; JetBrains Mono (400–600) for labels, code, nav, chips. Headlines 56–84px / 800 / −0.035 to −0.04em. Labels 10.5–12px mono, uppercase, letter-spacing .14–.26em. Body 14–18px / 1.6.
**Radius:** 3 (chips, bars), 4–5 (buttons, inputs), 6 (tiles), 8 (cards). **Spacing:** page gutter 64px, card gap 20px, section top 72–80px.

## Recommended architecture (suggestion — agent may adjust)
- **Frontend:** Next.js / React + TypeScript, CodeMirror 6 or Monaco. Theme via CSS variables above.
- **rust-analyzer:** server-side RA over LSP via WebSocket (per-session workspace), or rust-analyzer WASM for lighter setups. Toggle simply connects/disconnects the LSP client.
- **Runner:** Rust (axum) API that runs `cargo test` / `cargo clippy` in sandboxed containers (Firecracker / gVisor / nsjail), with CPU/mem/time limits and a warm crate cache. Return structured results (`cargo test -- -Z unstable-options --format json` or parse libtest output).
- **Borrow lanes:** derive from rustc diagnostics spans (primary + secondary labels) at minimum; optionally from MIR/Polonius facts for full per-line borrow ranges.
- **Rule checker:** `syn`-based AST pass per Fix-this problem (forbidden calls/types, max changed lines via diff).
- **Data:** Postgres. Tables: tracks, stages, problems, problem_tags, tests (visible/hidden), hints, attempts, runs, reviews (spaced repetition), concepts, readiness_snapshots, projects, project_stages, project_repos.
- **Content as files:** each problem a folder (`problem.toml`, `statement.md`, `starter/`, `tests/`, `solution/`, `hints.md`) so agents can author content in bulk.

## Build plan for agents (each phase has acceptance criteria)
1. **Shell & tokens** — header, theme toggle (persisted), grid background, fonts, tokens. ✔ matches screenshots in dark and light.
2. **Content model + seed** — schema + loader for problem folders; seed Graphs track (32 problems from `TrackGraphs`) and 10 borrow-checker drills. ✔ `GET /tracks/graphs` returns stages and problems.
3. **Runner service** — sandboxed `cargo test` + clippy, JSON results, hidden tests, timeouts. ✔ Network delay time returns 4/6 on the mock code, 6/6 on the reference.
4. **Workspace (1a layout first)** — editor, tabs, tests panel, Run/Submit, hints/solution gating, assisted flag. ✔ all interactions in `WorkspaceSplit`.
5. **rust-analyzer + autocomplete toggles** — LSP bridge, inlay hints, lenses, diagnostics; fallback word completion. ✔ toggles behave as in 1a.
6. **Fix-this mode (1c)** — rule checker, inline error lens, borrow lanes, run timeline + diffs. ✔ `WorkspaceTrace` flow incl. rule violation run.
7. **Track page (1d)** — topology, stage cards, filterable table, readiness tiles. ✔ stage click filters table; tag chips filter.
8. **Spaced repetition + readiness** — review scheduling, readiness % per area, "re-solve due". ✔ stat strip values computed from data.
9. **Projects** — multi-stage repo per user, stage tests, carry-forward of previous stage tests, stage snapshots/diffs. Design in the TrackGraphs language.
10. **Library, Mock interview, Readiness page** — reuse table, capstone and readiness components.
11. **Content expansion** — remaining DSA tracks (DP basics→advanced etc.) and all 14 concept areas.

## Open decisions
- Final workspace direction: 1a, 1b, 1c or a hybrid (e.g. 1a layout + 1c borrow lanes + run timeline).
- Hosting/sandbox tech and whether RA runs server-side or WASM.

## Files
- `designs/Anneal Mockups.dc.html` — overview canvas (open this)
- `designs/WorkspaceSplit.dc.html`, `WorkspaceBench.dc.html`, `WorkspaceTrace.dc.html`, `TrackGraphs.dc.html` — individual screens (each opens standalone)
- `designs/support.js` — runtime needed to open the HTML files
- `reference/*.png` — genuinebasil.dev screenshots (visual source)

# Course UX proposals: CLI, tables and the web (2026-10-09)

Status (2026-10-09): the CLI items 1, 2, 3 (`--watch`, `--filter`, `--only`), 5 (`status` progress and `--json`), 6 (the courses are compiled into the binary), 7 (a queue for runs that cannot be reported, `sync`), 8 (`doctor`) and 9 (`--version`, `completions`) are built; item 4 (a rendered `show`, `--hint`) and the table/web items are not. Written first as proposals (CLAUDE.md: propose extras with a recommendation, mock up UI changes first). Based on running the CLI as a
learner (`anneal course init`, `status`, `show`, `test`) and reading the web styles; the web pages were **not** rendered in a browser for this
review, so the UI items are from the CSS and need a screenshot pass before mockups. The CLI guidance follows the rust-skills CLI guide (stderr
for errors, TTY and `NO_COLOR` detection, non-zero exit codes, `indicatif` progress, `clap_complete`).

Done already from this request: **Fira Code** is the programming font (editor default, code blocks, diffs, compiler output; `--mono` stays the
JetBrains Mono label font; ligatures stay off, as decided in design.css). A saved editor setting of JetBrains Mono is kept until changed in the editor settings.

## CLI: what a learner sees today

| observation | effect |
|---|---|
| `anneal course test` exits **0** when tests fail | scripts, CI and the hook cannot tell pass from fail |
| a failing run prints every failing test with the raw panic line (`thread '...' (46799829) panicked at ...`), the `RUST_BACKTRACE` note and no count | a wall of text; no "3 of 9 passed"; the useful line (what was expected) is buried |
| no output while the crate compiles (up to a minute on a cold target dir) | looks hung |
| no colour or TTY detection; no `NO_COLOR` handling | plain text always, even when piped, never highlighted when interactive |
| `show` prints the raw markdown (callouts as `> [!TIP]`, tables as pipes) | harder to read than the web page; no link to it |
| `status` lists stages but has no overall progress | no sense of "42 of 163" |
| `init` needs a checkout of the anneal repo (`--courses courses`) | not something a learner can do from a clean machine |

## CLI proposals, in recommended order

1. **Exit codes.** `test` exits 1 on any failure (and 2 on a compile error), 0 only when the stage passes. Trivial and a real bug for scripting.
2. **A readable result.** One header line (`Stage 4a-03 · Committing and aborting`), a progress line while compiling (`indicatif` spinner on stderr, only on a TTY),
   then a summary (`6 of 9 passed`), and for each failure the test name plus the `left`/`right` or panic message **without** thread ids and backtrace
   notes; `--verbose` restores everything. Colour only on a TTY and not under `NO_COLOR`. Errors to stderr, results to stdout.
3. **Faster loop.** `test --watch` (re-run on save), `test <name-filter>`, and `test --only` (the current stage without the regression pass). Part of the
   speed is cargo: merging the ~40 test files into one test binary would cut link time (see the verifier numbers in BUSTUB_TASKS.md).
4. **Reading.** `show` renders markdown for the terminal (headings, code, tables, callouts) with a pager; `show --web` prints/opens the stage's page URL;
   `show --hint 1|2|3` reveals hints one at a time (the stage pages already order them deepest last).
5. **Progress.** `status` gets an overall bar (`42/163 · 26%`), per-module bars, "next up", and `--json`. After a pass, `test` prints what unlocked
   (the next stage or module) instead of only "complete".
6. **Download.** One command from a clean machine: `cargo install --git ... anneal` or a release binary plus `anneal course init bustub`, which fetches the
   template from the web app (it can serve a versioned tarball) instead of needing the repo checkout. `anneal course update` prints a changelog (new stages,
   changed given files).
7. **Upload and progress sync.** Say so when results are reported (`reported to anneal.genuinebasil.dev ✓` or `offline: 2 runs queued`); queue and retry offline;
   `login` with a device-code flow instead of pasting a token; `anneal course sync` to push queued runs and pull progress.
8. **`anneal course doctor`.** Checks `rustc` version, the git hook, the login, the template version against the server's, the target dir size.
9. **Shell completions** (`clap_complete` for bash, zsh and fish) and `--version`.

Recommendation: build 1 and 2 first (an hour of work, the biggest daily difference), then 3 and 5, then 6 and 7 together (they share the server side).

## Tables and the web (needs screenshots first)

From the stylesheets: course catalog tables are CSS grids with `min-width: 900px` inside a scroll box; the progress table is a plain `<table>`;
rendered stage and concept tables (including every "C/C++ way" comparison) use `.cx-tbl`.

| idea | where | why |
|---|---|---|
| tabular numbers (`font-variant-numeric: tabular-nums`) in every numeric column | `.num`, `.best`, `.ptable .num` | columns of digits line up |
| sticky header row and sticky first column in long tables | `.tbl`, `.ptable`, `.cx-tbl` | the problem list and test tables scroll off their headers |
| a card layout under ~700px instead of a 900px horizontal scroll | `.tbl` | the catalog is hard to use on a phone |
| sortable columns and a filter box on the big tables | problem list, tests tab, readiness | currently filters live in a separate panel; sorting is not available |
| keyboard navigation (`j`/`k` to move a row, Enter to open) | `a.tr`, `.ptable tr.go` | consistent with the pattern navigation keys already built |
| the C++/Rust comparison tables: highlight code in the cells, align the two columns' rows, a "copy" on each cell | `.cx-tbl.versus` | those tables are the course's main teaching device and today show plain `code` |
| tests tab: group by stage, collapse passing tests, show duration | `.tcase*` | long runs are one flat list |
| row-level status colours that do not rely on colour alone (icon + text) | `.st`, `.mode` | accessibility |
| a "run all tests / last run" strip pinned above the console on the stage page | workspace | the result of the last run is the thing you look at most |

Other web ideas: show the CLI command next to each stage (`anneal course test 4a-03`) with a copy button; a "where am I" strip on the course page
(the current module's progress ring, as the DSA workspace has); keep scroll position when switching between Instructions and Hints.

Recommendation: do the table basics (tabular numbers, sticky headers, phone cards) as one change after a screenshot review, then mock up
the tests-tab regrouping before building it.

Mockups: [course-run-tab.html](mockups/course-run-tab.html) (built: the Run tab) and
[web-tables-and-run-strip.html](mockups/web-tables-and-run-strip.html) (sort and filter, keys, status icons, comparison tables, pinned run strip, CLI command, where-am-I strip; awaiting approval).

Motion and component mockups (awaiting approval, nothing built): [course-motion.html](mockups/course-motion.html) (course page, stage page, component kit,
popups; `#static`, `#static-stage`, `#static-kit`, `#static-win` open a state without animation) and [section-page.html](mockups/section-page.html) (Rust/DSA section page).

## What was built (CLI)

- `anneal course test`: exit 1 when tests fail, 2 when nothing could run; failures grouped by message and cleaned of thread ids and
  backtrace notes (`-v` for everything); a spinner while cargo compiles (terminals only); colour on terminals and not under `NO_COLOR`;
  `--only` (skip the regression run), `--filter TEXT` (tests with that text in their name; a filtered run never records progress),
  `--watch` (re-run on every change under `src/` and `tests/` until the stage passes); a pipe closed early (`| head`) ends quietly.
- `anneal course status`: a bar for the whole course and one per module, `Next up`, and `--json`.
- Download: the learner-facing part of every course (stage definitions and the template, never the reference) is compiled into the binary
  (`crates/cli/build.rs`), so `cargo install --git <repo> anneal-cli` followed by `anneal course init bustub` needs no checkout.
  `ANNEAL_EMBEDDED_ONLY=1` makes the CLI ignore directories and use only the compiled-in copy (the smoke test checks that it builds the same repo).
- Upload: a run that cannot be reported (no network, a server error, an expired session) is queued in `.anneal/outbox.jsonl` and sent with
  the next report or `anneal course sync`; the message says what happened and how many are waiting.
- `anneal course doctor` (rust, cargo, git, curl, the hook, the queue, the size of `target/`, the login) and `anneal completions <shell>`.

Not built: a rendered `show` with a pager and `--hint`, the device-code login (the passphrase prompt is unchanged), a template download from
the web app (superseded by compiling the courses into the binary), and the table and web items above.

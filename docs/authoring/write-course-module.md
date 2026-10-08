> **First read [../COURSE_STANDARDS.md](../COURSE_STANDARDS.md)**: stage size (6-10 per module, self-contained), a concept per stage, at least 5 tests, a Performance section, BusTub-level hints. `anneal course lint` enforces it.

You are writing one module of anneal's "Build a DBMS: BusTub in Rust" course, in the repo at {REPO}.

READ FIRST: docs/BUSTUB.md (all of it: requirements log §0, the CodeCrafters model §1, mirroring rules §2, stage anatomy §3, authoring §5, testing §6),
docs/BUSTUB_TASKS.md (the board and the pick-up steps), and docs/PORTING.md §2 (the C++ → Rust notes for BusTub). Then study module 1a as the model:
`courses/bustub/modules/01-disk-manager/` (module.toml, every stage.toml and stage.md) and `courses/bustub/reference/` (src with `@begin` markers, tests).
The reference tree is not in git; if it is missing on this machine, stop and tell the owner.

YOUR MODULE: {MODULE} (code {CODE}, directory `modules/{NN}-{SLUG}`). BusTub component: {BUSTUB_FILES}. Boss: {BOSS_TESTS}.

WHAT TO PRODUCE
1. An outline first (post it in your report or the task board): 10–30 stages, easy → hard, each a CodeCrafters-sized step. Difficulty labels and times:
   very-easy < 5 min · easy 5–10 min · medium 30–60 min · hard > 1 h. Open with foundation stages that teach exactly the std surface the component needs
   (the owner: "go through basics with small problems; give me the syntax and methods; ask me to solve something with my brain; then the next builds on it").
   The last stage is the **boss**: BusTub's own test file ported test for test (same names in snake_case, the same assertions; change C++ idioms such as fixed file
   names and `DISABLED_`, keep the checks).
2. The reference code in `courses/bustub/reference/src/...` mirroring BusTub's file names, with each part a learner writes wrapped in
   `// @begin {CODE}-NN` … `//~ <stub lines>` … `// @end`. A stub must declare any variable the rest of the function uses (typed `todo!()`), so every
   prefix of the stages compiles. Given code (structs, helpers, anything that isn't the point of a stage) stays outside the markers. Idiomatic, safe Rust, std only
   unless a stage names a crate; comments in the BusTub style. New public items need their module wired in `mod.rs` (given code).
3. Tests: `reference/tests/stages_{CODE}.rs` with functions `s{CODE}_NN_description` (≥ 3 per stage, covering the main case, the edge, and each rule easy to
   misread; use `tests/common` for temp dirs: tests run in parallel and must not share files); and the ported BusTub test file(s) `tests/<bustub_name>_test.rs`.
   A stage's tests may only use code from that stage and earlier ones. Concurrency tests need a time limit's worth of work, not sleeps.
4. `stage.toml` (id `{CODE}-NN`, title, kind learn/build/boss, difficulty, `tests = ["stages_{CODE}::s{CODE}_NN", ...]`) and `stage.md` for every stage with the
   sections in BUSTUB.md §3: Where this fits · The task · Tests · Syntax and methods · Notes · In BusTub (quote the C++ with its path) · **The C/C++ way** (a table of
   the C/POSIX, C++ and Rust spellings, the pitfalls C/C++ has that Rust removes, and one "port rule") · Learn more. Statements in your own words.
5. `module.toml`: code, title, summary, `lectures = [..]` (ids from `courses/bustub/lectures.toml`), `bustub = [..]` (BusTub paths), and `[[resources]]` that are as
   comprehensive as you can make them: std/core/crate docs, the Rust Book/Rust by Example/Nomicon, man pages, papers, blogs, videos, other projects' code (SQLite,
   PostgreSQL, redb, Turso, tokio, ...). **Check every URL** (HTTP 200; YouTube via `https://www.youtube.com/oembed?format=json&url=...`). Never invent one.
6. Ranks matter: stages sort by directory name across modules (`NN-slug`). Don't renumber other modules' ids.

CHECKING (all must pass before you commit)
- `cargo build -p anneal-cli && ./target/debug/anneal course verify --course bustub`: every stage's tests fail before it and pass after it, earlier stages stay green, every
  state compiles. A boss that cannot fail before it needs `retest = true`. Fix the reference or the test, not the check.
- `tools/course-smoke.sh`: verify, the full solution's `cargo test` and release build, the learner flow with the pre-push hook, update.
- Read three of your stage pages with `anneal course show` after `anneal course init bustub /tmp/x`: would a competent Rust developer who has never seen BusTub know what to do, which
  std items to use, and where to read more?
- `cargo clippy -p anneal-cli -- -D warnings` if you touched the CLI. Don't run cargo fmt or prettier (match the surrounding style, 4-space indent, ~160 columns).

SHIPPING
- `./target/debug/anneal course template` regenerates `courses/bustub/template/`. Commit `courses/bustub/{modules,template,lectures.toml,course.toml}` plus docs/tools you changed.
  **Never commit `courses/*/reference`** (BUSTUB.md §8; it is gitignored). Tick the module on BUSTUB_TASKS.md.
- Commit message ends with the Co-Authored-By line for your model. Push to master (the owner practises on each shipped module).

REPORT: the stage list with difficulties, the test counts, what you changed from BusTub's behaviour on purpose (and the stage page where you said so), and the
verify and smoke output lines.


## Stage pages in the app: what the markdown can use

The web app renders each `stage.md` (`web/src/pages/courseMd.ts`), so plain markdown gets structure:

- **Code** is syntax-highlighted by fence language: ` ```rust `, ` ```cpp `, ` ```sh ` (a bare fence that has `$ ` lines is treated as a shell session), ` ```toml `. Rust blocks get a green label, C++ blocks an amber one, so the two are never confused.
- **C/C++ vs Rust tables** are colour-coded by their header: a column headed `C / C++`, `C++`, `C` or `BusTub` is amber, `Rust` or `here` is green. A table with an empty header row (`| | |`) shows its first column as the key.
- **Callouts**: `> [!TIP] Optional title`, `[!WARNING]`, `[!PORT]`, `[!WHY]`, `[!NOTE]`, `[!BUSTUB]`, then the body on the following `>` lines. Paragraphs that start with a bold `**Port rule:**`, `**Where this fits.**`, `**Pitfall…**`, `**The classic bug…**` or `**Why …**` become callouts by themselves.
- **Hints** go in a `## Hints` section, one `### title` per hint. Write them at BusTub's level (the design choice, then the trap, then the invariant to check), never as a restatement of the task.
- **Tips and tricks** are `> [!TIP]` callouts: the tool that shows the learner what the code actually did (`xxd`, `strace`, `--nocapture`, a `debug_assert!` checker).
- **Concepts** are short articles in `courses/<id>/concepts/<slug>.md`, referenced from a stage with `concepts = ["slug"]` in `stage.toml`. A `---` header gives `title`, `summary` and `minutes`; each `##` is a section. They teach one idea a stage needs at BusTub's depth (the C and C++ version next to the Rust one, the failure mode, the invariant), not a restatement of the task. `anneal course verify` does not read them, but the API refuses to load a stage that names a concept that does not exist.
- **Our answer** appears once the owner has run `anneal course login <url>` and `anneal course solutions`; until then the stage page shows a locked box saying so.
- **Diagrams and animations**: an ```svg fence holds inline SVG, with an optional first line `caption: ...`. Use the theme classes (`box live free hot blue violet never ln ln-g dash flow pulse`, text `dim sm big mid end t-g t-w t-a t-b t-v t-r`) instead of hard-coded colours. Put a `<style>` with uniquely named `@keyframes` inside the SVG for an animation; keep the final state as the base style so reduced-motion readers see the finished picture. See `courses/bustub/concepts/positional-io-and-short-reads.md` (an animated read loop) and `slot-allocation-and-invariants.md` (a state picture and a cost graph).

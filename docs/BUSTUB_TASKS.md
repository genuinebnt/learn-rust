# Build a DBMS (BusTub in Rust): task board

Design: [BUSTUB.md](BUSTUB.md). Agent prompt for a module: [authoring/write-course-module.md](authoring/write-course-module.md).
Updated 2026-10-08. **Convention:** an agent that starts a task puts its name and the date next to it; when done it ticks the box, adds the commit, and
updates BUSTUB.md §6 if a test level changed. Ship each finished module (commit and push `master`; CI deploys; never commit `courses/*/reference`).
The owner practises on shipped modules while the next ones are built, so **never push a module whose `anneal course verify` isn't green**.

## Infrastructure

- [x] **CLI** `anneal course init | status | show | test | next | hooks | hook | update | build | template | verify` (`crates/cli/src/course.rs`). 2026-10-08
- [x] **Stage markers and renderer** (`// @begin <stage>` … `//~ stub` … `// @end`), cumulative states that always compile.
- [x] **verify**: per stage the tests fail before and pass after, earlier stages stay green, every state compiles; a boss may `retest`.
- [x] **Smoke script** `tools/course-smoke.sh` (verify, whole solution, template, learner flow with the pre-push hook, update).
- [x] **Lecture catalogue** `courses/bustub/lectures.toml` (25 CMU 15-445 lectures: slides, notes, video; from the Fall 2026/2025 schedule pages).
- [x] **Module resources** in `module.toml` (`[[resources]]` kind = docs/book/man/paper/blog/video/code), printed by `show`.
- [ ] **COURSE-1 API + DB**: `POST /api/course/submissions`, `GET /api/course/<id>/progress`, migration `course_progress`; `ANNEAL_CLI_TOKEN` bearer auth; the CLI posts after a pass (needs an HTTP client; none in `crates/cli` yet).
- [ ] **COURSE-2 Course page** in the web app (modules, stages, difficulty, history, the current stage's markdown). **Mockup first, wait for approval** (CLAUDE.md).
- [ ] **COURSE-3 Progress/planner integration**: count a stage like a problem in Progress and the Rust-area readiness.
- [ ] **COURSE-4 Windows**: `cfg(windows)` shim for positional I/O (`seek_read`/`seek_write`) so the disk stages build there.
- [ ] **COURSE-5 `anneal course test` polish**: `--list`, JSON output, a per-test timeout, colours.
- [ ] **COURSE-6 Reference backup**: decide where `courses/bustub/reference` lives (private repo?). Until then it exists only on the owner's machine.
- [x] **COURSE-8 link checker** `tools/check_course_links.py` (re-run it now and then: std docs move pages between `struct.` and `type.`; dsf.berkeley.edu went away).
- [ ] **COURSE-7 CI**: a job that renders `template/` and builds it (no reference needed): proves the shipped template compiles; and `anneal course template` leaves no diff.
- [ ] **FRONT-1 SQL front end** (parser, binder, planner for BusTub's SQL subset) as given code in the template, plus a sqllogictest runner. Needed by module 3's bosses.
- [ ] **EXTRA-1 extra tests** (deferred, only where a port can differ from C++): property tests against `HashMap`/`BTreeMap` models, loom for the latches.

## Content: modules in BusTub order (each = a track of stages; counts are planned)

Lecture ids refer to `courses/bustub/lectures.toml`. "Boss" is BusTub's own test, ported.

| Module | Stages | Lectures | Boss | Status |
|---|---|---|---|---|
| **1a Disk manager** | 19 | storage1 | `disk_manager_test` ×4 | **done, verified, shipped** |
| **1b Disk scheduler** (`Channel`, one-shot promise/future, worker thread, `RwLatch`, sharded workers) | 15 | storage1, bufferpool | `disk_scheduler_test`, `rwlatch_test` | **done, verified, shipped** |
| **1c Simple replacers** (generational `IndexList`, LRU, CLOCK) | 11 | bufferpool | `lru_replacer_test`, `clock_replacer_test` | **done, verified, shipped** |
| **1d LRU-K replacer** | 9 | bufferpool | `lru_k_replacer_test` | **done, verified, shipped** |
| **1e ARC replacer** (four lists, ghosts, adaptive target) | 9 | bufferpool | `arc_replacer_test` ×3, `arc_replacer_performance_test` | **done, verified, shipped** |
| **1f Buffer pool manager** (textbook `fetch_page`/`unpin_page` interface) | 10 | bufferpool, storage1 | classic `BinaryDataTest`/`SampleTest` + a stress test | **done, verified, shipped** |
| 1g Page guards (`ReadPageGuard`/`WritePageGuard`, `Drop`, move, flush; the deadlock lesson) | ~10 | bufferpool, indexconcurrency | `buffer_pool_manager_test` ×7, `page_guard_test` ×2 | next |
| 2a Typed pages (ints at offsets, header views, fixed arrays in a page, keys and comparators, sorted-array ops) | ~14 | storage2, indexes1 | (own tests) | |
| 2b Extendible hash table (bucket, directory, header pages; insert/split, remove/merge/shrink; concurrency) | ~30 | hashtables | `extendible_htable_page_test`, `…_test`, `…_concurrent_test` | |
| 2c B+ tree (pages, search, insert/split, delete/borrow/merge, iterator, crabbing, tombstones) | ~48 | indexes1, indexes2, indexconcurrency | `b_plus_tree_*_test` ×5 | |
| 3a Types, tuples, table pages and heap, catalog | ~25 | storage2, storage3 | `type_test`, `tuple_test`, `tmp_tuple_page_test` | |
| 3b Executors (expressions, scan, insert/update/delete, agg, joins, sort/top-N, window, external sort) | ~45 | queryexecution1/2, sorting, joins | `p3.*.slt` | needs FRONT-1 |
| 3c Optimizer rules | ~14 | optimization1/2 | optimizer `.slt` | needs FRONT-1 |
| 4a Watermark, timestamps, MVCC versions, snapshot reads, GC | ~30 | multiversioning | `txn_*_test` | |
| 4b Lock manager, 2PL, deadlock detection | ~25 | concurrencycontrol, twophaselocking | lock manager / deadlock tests | |
| 5 Logging and recovery | ~15 | logging, recovery | `recovery_test` | |
| 0 Primer (optional): trie + store, skiplist, count-min sketch, HyperLogLog, ORSet, Robin Hood hash set | ~40 | (none) | `trie_test` … | last |

Each module's stage outline lives in its `modules/<NN>-<slug>/stages/` as it is written; plan the outline in the PR description or here first.

## Done log

- 2026-10-08: design (BUSTUB.md), CLI, module 1a (19 stages, ~100 stage tests + BusTub's 4), lecture catalogue, resource lists, C/C++ way blocks in every 1a stage. `tools/course-smoke.sh` green.
- 2026-10-08: modules 1b-1f (54 stages: scheduler, LRU/CLOCK, LRU-K, ARC, buffer pool) with BusTub's ported tests; nested stage regions and plain `todo!()` stubs (the learner's freedom); `anneal course update`; `tools/check_course_links.py` (293 URLs checked). 73 stages verified.

## How a new agent picks up a module

1. Read BUSTUB.md §2–§6 and `authoring/write-course-module.md`. Look at module 1a as the model: `courses/bustub/modules/01-disk-manager/`.
2. Read BusTub's source and test for the component (`git clone --depth 1 https://github.com/cmu-db/bustub`). The test file is the boss; read PORTING.md §2 for the C++ → Rust notes.
3. Write the outline (stages with difficulty), then the reference code with markers, the stage tests, the stage pages, `module.toml` with lectures and **checked** resources.
4. `cargo build -p anneal-cli && ./target/debug/anneal course verify --course bustub`, then `tools/course-smoke.sh`. Zero problems, or don't push.
5. `anneal course template`, commit `courses/bustub/{modules,template,lectures.toml,course.toml}` (and `tools/`/`docs/` changes), push.

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
- [x] **COURSE-1 API + DB** (migration `0013_courses.sql`, `crates/api/src/course.rs`): `GET /api/courses/{c}` (tree + progress), `GET …/stages/{id}`, `POST …/runs` (the CLI reports each `anneal course test`), `POST …/hints` and `…/solution` (open = assisted), `PUT …/solutions`. The CLI signs in with `anneal course login <url>` (session cookie in `~/.config/anneal`, HTTP through `curl`). 2026-10-08
- [x] **COURSE-2 Course pages** (`/courses`, `/courses/<course>/<stage>`; `web/src/pages/Course*.tsx`, `styles/course.css`; mockup `docs/design_handoff_anneal/designs/course-page.html`, approved). Only modules in `course.toml` `published_modules` are shown. 2026-10-08
- [ ] **COURSE-3 Progress/planner integration**: count a stage like a problem in Progress and the Rust-area readiness.
- [ ] **COURSE-4 Windows**: `cfg(windows)` shim for positional I/O (`seek_read`/`seek_write`) so the disk stages build there.
- [ ] **COURSE-5 `anneal course test` polish**: `--list`, JSON output, a per-test timeout, colours.
- [ ] **COURSE-6 Reference backup**: the app now keeps each stage's solution diff in its database (`anneal course solutions`, owner-only), but `courses/bustub/reference` itself still exists only on the owner's machine: back it up (private repo).
- [x] **COURSE-8 link checker** `tools/check_course_links.py` (re-run it now and then: std docs move pages between `struct.` and `type.`; dsf.berkeley.edu went away).
- [ ] **COURSE-7 CI**: a job that renders `template/` and builds it (no reference needed): proves the shipped template compiles; and `anneal course template` leaves no diff.
- [x] **FRONT-1 SQL front end** (2026-10-09, module 3d): a std-only lexer/parser (`src/sql/`), binder, planner, optimizer driver, `BusTubInstance::execute_sql`, a shell (`cargo run --bin bustub_shell`) and a sqllogictest runner (`tests/slt/mod.rs`), all given code. The `.slt` files of BusTub are copied into `tests/sql/` as modules reach them (listed in each module.toml's `files`).
- [ ] **EXTRA-1 extra tests** (deferred, only where a port can differ from C++): property tests against `HashMap`/`BTreeMap` models, loom for the latches.

## Content: modules in BusTub order (each = a track of stages; counts are planned)

**Stage standards (2026-10-08): see [COURSE_STANDARDS.md](COURSE_STANDARDS.md); `anneal course lint` enforces them and CI runs it for the published modules.** In short: a self-contained exercise (not tiny, not a chapter), 6 to 10 per module (not a hard limit), a concept article and "You'll learn" lines, at least 5 tests, a Performance section, BusTub-level hints. `tools/course_merge.py` + `tools/course_merge_plan.json` regrouped the first cut of 115 tiny stages into 49 (each old stage is now a *Part* of its new stage and keeps its tests).

**Published modules** (`published_modules` in `course.toml`) are all of 1a to 3h: every non-boss stage passes `anneal course lint` (learn lines, at least two concept articles, a Performance section, at least two hints, a short Tests summary) and every stage has at least 5 tests. 2b has 12 stages, above the 6 to 10 sweet spot (a note, not a failure). Concept articles live in `courses/bustub/concepts/` (69, shared between stages).

Lecture ids refer to `courses/bustub/lectures.toml`. "Boss" is BusTub's own test, ported.

| Module | Stages | Lectures | Boss | Status |
|---|---|---|---|---|
| **1a Disk manager** | 8 | storage1 | `disk_manager_test` ×4 | **done, verified, shipped** |
| **1b Disk scheduler** (`Channel`, one-shot promise/future, worker thread, `RwLatch`, sharded workers) | 5 | storage1, bufferpool | `disk_scheduler_test`, `rwlatch_test` | **done, verified, shipped** |
| **1c Simple replacers** (generational `IndexList`, LRU, CLOCK) | 6 | bufferpool | `lru_replacer_test`, `clock_replacer_test` | **done, verified, shipped** |
| **1d LRU-K replacer** | 5 | bufferpool | `lru_k_replacer_test` | **done, verified, shipped** |
| **1e ARC replacer** (four lists, ghosts, adaptive target) | 8 | bufferpool | `arc_replacer_test` ×3, `arc_replacer_performance_test` | **done, verified, shipped** |
| **1f Buffer pool manager** (textbook `fetch_page`/`unpin_page` interface) | 6 | bufferpool, storage1 | classic `BinaryDataTest`/`SampleTest` + a stress test | **done, verified, shipped** |
| **1g Page guards** (`ReadPageGuard`/`WritePageGuard`, `Drop`, move, flush; the deadlock lesson) | 3 | bufferpool, indexconcurrency | `buffer_pool_manager_test` ×7, `page_guard_test` ×2 | **done, verified, shipped — Project 1 complete** |
| **2a Typed pages** (ints at offsets, optional page ids, `Rid`, `FixedSize`, `GenericKey`, `PageArray` with insert/remove/search, `repr(C)` layouts) | 5 | storage2, indexes1 | (own tests; BusTub has none for these) | **done, verified, shipped** |
| **2b Extendible hash table** (MurmurHash3, header/directory/bucket pages, insert with split, remove with merge and shrink, concurrency) | 12 | hashtables | `extendible_htable_page_test`, `…_test`, `…_concurrent_test` | **done, verified, shipped** |
| **2c B+ tree** (header/internal/leaf pages, search, insert with leaf and internal splits, iterator, remove with borrow and merge, latch crabbing with an optimistic path) | 10 | indexes1, indexes2, indexconcurrency | `b_plus_tree_{insert,delete,sequential_scale,concurrent}_test` | **done, verified, shipped** |
| **2d B+ tree tombstones** (a `TOMBS` const generic: a tombstone buffer in each leaf, logical deletes, resurrecting inserts, scans that skip, splits/borrows/merges that carry them) | 4 | indexes2 | `b_plus_tree_tombstone_test` ×4, and the `Tombs` variants of the 2c insert/delete/concurrent tests | **done, verified, shipped** |
| **3a Values and types** (`TypeId`, `Value` with typed NULLs, casts, three-valued comparison, checked arithmetic, byte encoding) | 7 | storage1, queryexecution1 | `type_test` | **done, verified, shipped** |
| **3b Schemas, tuples and table pages** (columns, schema layout, `Tuple` with fixed and variable parts, slotted `TablePage`) | 7 | storage2, storage3 | own `table_page_test` (BusTub has none) | **done, verified, shipped** |
| **3c Table heap, iterator and catalog** (heap insert/get/update, the Halloween-safe iterator, `Index` over the B+ tree with a schema comparator, catalog tables and indexes) | 7 | storage2, storage3 | `tuple_test` (BusTub's `TableHeapTest` + a catalog/index round trip) | **done, verified; shipping** |
| **3d Expressions and the SQL front end** (constants, columns, comparison, arithmetic, AND/OR in 3-valued logic, lower/upper, the planner's function factory; the whole parse-bind-plan-optimize-execute pipeline is given) | 7 | queryexecution1, modernsql | `p0.01..03`, `baby_arithmetic`, `intro` .slt | **done, verified, shipped** |
| **3e Access-method executors** (seq scan, scan with predicate, insert, insert + indexes, delete, update as delete+insert, index scan in key order and by key) | 9 | queryexecution1, indexes1 | `p3.00..p3.04` .slt (`p3.05`/`p3.06` need module 3h's index rule) | **done, verified; shipping** |
| **3f Aggregation and joins** (group keys, combine, aggregation executor, nested loop join inner/left, hash join inner/left, nested index join) | 9 | queryexecution2, joins | `p3.07..p3.13` .slt (`p3.14`/`p3.15` need module 3h's hash join rule) | **done, verified, shipped** |
| **3g Sorting, limits and window functions** (sort keys, runs on pages, pass 0, k-way merge, external merge sort executor, limit, top-N heap, window partitions, ordered frames and rank) | 10 | sorting, queryexecution2 | `p3.16`, `p3.18`..`p3.20` .slt (`p3.17` and `p3.16`'s hash_join checks need module 3h) | **done, verified, shipped** |
| **3h Optimizer rules** (equi-join keys, NLJ to hash join, sort+limit to top-N, point lookups, seq scan to index scan) | 6 | optimization1/2 | `p3.05/06/14/15/16/17` .slt with `+ensure:` plan checks | **done, verified, shipped** (not ported: `p3.22` composite prefix scans, hash/stl indexes, TopNPerGroup leaderboard, column pruning) |
| 4a Watermark, timestamps, MVCC versions, snapshot reads, GC | ~30 | multiversioning | `txn_*_test` | |
| 4b Lock manager, 2PL, deadlock detection | ~25 | concurrencycontrol, twophaselocking | lock manager / deadlock tests | |
| 5 Logging and recovery | ~15 | logging, recovery | `recovery_test` | |
| 0 Primer (optional): trie + store, skiplist, count-min sketch, HyperLogLog, ORSet, Robin Hood hash set | ~40 | (none) | `trie_test` … | last |

Each module's stage outline lives in its `modules/<NN>-<slug>/stages/` as it is written; plan the outline in the PR description or here first.

## Done log

- 2026-10-08: **all of 1a to 2b published in the app**: hints at BusTub's level, 2+ concepts per stage (42 articles with diagrams), Performance sections, a tests-passed popup with Proceed, stages regrouped to 49 (every stage 5+ tests). `anneal course lint` clean.
- 2026-10-08: **stages merged** 115 → 36 → 58 → 49 (see the stage-size rule above); web Course pages and API built; module 1a (hints, concepts, learn lines) is the first one published in the app; regrouped again to 58 self-contained stages after the owner asked for CodeCrafters-style sections of stage rows.
- 2026-10-08: design (BUSTUB.md), CLI, module 1a (19 stages, ~100 stage tests + BusTub's 4), lecture catalogue, resource lists, C/C++ way blocks in every 1a stage. `tools/course-smoke.sh` green.
- 2026-10-08: module 2a (13 stages, the toolkit for Project 2's pages). 93 stages verified.
- 2026-10-08: module 2b (22 stages, extendible hash table; ports BusTub's three hash table tests). 115 stages verified.
- 2026-10-08: module 1g (7 stages): BusTub Project 1 is complete (80 stages, all BusTub P1 tests ported and green).
- 2026-10-08: modules 1b-1f (54 stages: scheduler, LRU/CLOCK, LRU-K, ARC, buffer pool) with BusTub's ported tests; nested stage regions and plain `todo!()` stubs (the learner's freedom); `anneal course update`; `tools/check_course_links.py` (293 URLs checked). 73 stages verified.
- 2026-10-09: **module 3b published** (schemas, tuples, table pages): layout as in BusTub (fixed part with 4-byte offsets for VARCHARs, then the strings; slot array 24 bytes per tuple, tuples from the back); the slot's byte order is this port's. 3 new concepts (structs and accessors, tuple layout, slotted pages). 77 stages.
- 2026-10-09: **module 3c published** (table heap, iterator, indexes, catalog): `TableHeap` with a locked last-page pointer, an iterator that stops at the end seen when it began (the Halloween fix), an `Index` trait with a schema-aware comparator over the 2c B+ tree, `Catalog` with `create_table`/`create_index` (populates from the heap). 4 new concepts (heap files, Halloween problem, the catalog, lifetimes in structs). 84 stages.
- 2026-10-09: **module 3d published** (expressions + the SQL front end, FRONT-1): the learner writes the expression nodes (constant, column, comparison, arithmetic, AND/OR, lower/upper) and the planner's function factory; everything else on the way from SQL text to rows is given code, ported from BusTub's `binder/`, `planner/`, `optimizer/` (driver and the given rules), `execution_engine`, mock tables and the sqllogictest tool. Deviation: the parser is hand-written (BusTub uses libpg_query), so there are no dependencies. 4 new concepts (expression trees, unicode and case mapping, the SQL pipeline, name resolution). 91 stages.
- 2026-10-09: **module 3e published** (access-method executors): `SeqScan` (+predicate), `Insert`, `Delete`, `Update` (delete + insert, indexes kept in step), `IndexScan` (ordered and `pred_keys` lookups). Executor skeleton files are listed in 3d's `files` so the factory compiles from 3d on. 4 new concepts (iterator model, predicate pushdown, maintaining indexes, access paths). 100 stages.
- 2026-10-09: **module 3f published** (aggregation and joins): `AggregateKey` Hash/Eq with SQL grouping equality, `combine_aggregate_values`, `AggregationExecutor`, `NestedLoopJoinExecutor` (inner/left, init check), `HashJoinExecutor` (inner/left, NULL keys), `NestedIndexJoinExecutor`; a given `TupleStream` hides child batches. 3 new concepts (hash aggregation, hashing values and keys, join algorithms). 109 stages.
- 2026-10-09: **module 3g published** (sorting, limits, windows): `TupleComparator`/`generate_sort_key` (NULL is the smallest value, as in BusTub's tests), `MergeSortRun`/`RunBuilder` on buffer-pool pages, pass 0 runs, k-way merge (earlier run wins ties: stable), `ExternalMergeSortExecutor<2>`, `LimitExecutor`, `TopNExecutor` with a bounded heap and the `+ensure:topn` check, `WindowFunctionExecutor` (partitions, default frame with peers, rank). 4 new concepts. Not ported: TopNPerGroup (leaderboard). 119 stages.
- 2026-10-09: **module 3h published** (optimizer rules): `extract_equi_join_keys`, NLJ→hash join, Limit(Sort)→TopN, `extract_point_lookup`, SeqScan→IndexScan (keeps the whole predicate as filter). Also fixed an api scheduling bug that broke CI on Fridays (a weekday restriction could land a review on a break day). 125 stages.
- 2026-10-09: **scope decision**: BusTub's current course (P0 primer, P1 buffer pool, P2 indexes, P3 queries, P4 MVCC) has *no* lock manager or recovery project (`test/concurrency/*.disabled`, `test/recovery/*.disabled`), so the old plan's 4b lock manager and 5 recovery are dropped. Remaining: 4a/4b (MVCC) and the optional primer.
- 2026-10-09: **module 3a published** (values and types): `Value` is an enum with typed NULLs; BusTub's reserved-number NULL encoding is kept (and explained); casts follow the C++ tables (with proper range checks where C++ truncates); arithmetic computes in i128 and range-checks the result type. Timestamps are carried as numbers and there is no VECTOR type. 6 new concept articles. 70 stages.
- 2026-10-09: **module 2d published** (tombstones): rules derived from the four BusTub tombstone tests (BusTub's spec text is not in its source tree): a full buffer really removes the oldest; an insert revives a tombstoned key; a short leaf purges its own tombstones, then borrows (a deleted pair keeps its tombstone) or merges (the oldest overflowing tombstones are removed). Two new concepts (`const-generics-for-page-layouts`, `tombstones-and-lazy-deletion`). `check_structure_t::<T>` checks the buffers. 63 stages in the course.
- 2026-10-08: **module 2c published**: the B+ tree (10 stages, 59 stages in the course). Reference: pages, tree, iterator, `TracedBufferPoolManager`; 73 stage tests plus BusTub's insert, delete, scale and concurrent tests ported (14); `tests/b_plus_tree_utils` has `IsTreeValid`, `TreeValuesMatch`, `IndexLeaves` and the course's own `check_structure`. Eight new concept articles with tested in-memory B+ tree insert and remove. Tombstones are 2d (not started).
- 2026-10-08: **concepts teach usable code**: all concept articles (42 for 1a to 2b; 8 more for 2c) end with a tested "In real code" section (API tour or full algorithm, worked traces, `### In the exercises`, `### Where it is used`); `tools/course_snippets.py` runs the ~147 examples and CI runs it; lint enforces the structure.

## How a new agent picks up a module

1. Read BUSTUB.md §2–§6 and `authoring/write-course-module.md`. Look at module 1a as the model: `courses/bustub/modules/01-disk-manager/`.
2. Read BusTub's source and test for the component (`git clone --depth 1 https://github.com/cmu-db/bustub`). The test file is the boss; read PORTING.md §2 for the C++ → Rust notes.
3. Write the outline (stages with difficulty), then the reference code with markers, the stage tests, the stage pages, `module.toml` with lectures and **checked** resources.
4. `cargo build -p anneal-cli && ./target/debug/anneal course verify --course bustub`, then `tools/course-smoke.sh`. Zero problems, or don't push.
5. `anneal course template`, commit `courses/bustub/{modules,template,lectures.toml,course.toml}` (and `tools/`/`docs/` changes), push.

# BusTub course restructure (2026-10-09)

Written at the owner's request after three instructions in one session:

1. *"i should have creative freedom to come up with my own solutions, the tests should be mostly property testing + bustub tests that are generic and tests the invariants or covariants but not implementation details. and the course page content + concepts should teach me tricks and tips to do certain things in rust that i may not know as i am not a systems programmer."*
2. *"i have limited rust knowledge."*
3. *"the parts are still clear, disk manager, disk scheduler, replacer algorithms, page guards, b+ tree, optimizer, sql parser, acid, recovery etc. that's given as per bustub but what's underneath it is what you should decide based on bustub curriculum and my suggestions."*

So the **component list stays BusTub's**; everything underneath it (stages, tasks, tests, scaffolding, pages) is redesigned. This document is the design; the pilot is module 1a ([§8](#8-status)). Standards that still apply: [COURSE_STANDARDS.md](COURSE_STANDARDS.md) (esp. §11) and the skills `curriculum-review` and `mentor-teaching`. The follow-on course for everything BusTub does not teach is in [ADVANCED_DB_COURSE.md](ADVANCED_DB_COURSE.md).

## 1. What was wrong with the old shape

Measured on 2026-10-09: 10 of 137 task sections left any design to the learner; 74 said something was "given"; the stages were function-sized ("implement `slot_offset`", "implement `file_size_for`"); tests called those helpers directly (so a different but correct design failed to compile); most tests checked examples, not properties; the Rust a beginner needs was explained only where a concept article happened to cover it.

Each of those is the same defect: **the course described one implementation and tested for it.** The new rule is that a stage describes a capability and tests for its properties.

## 2. Principles

1. **The contract is the public API plus the properties that must hold.** The learner designs everything private: structs, fields, helper types, algorithms, file layout, locking.
2. **A stage is a capability, not a function.** "Pages survive a write and a read", not "implement `write_slot`". A stage adds behaviour; its tests exercise only the public API; no stage names a private function.
3. **Tests check invariants, not implementations.** Four kinds, in this order of preference:
   - **Model-based property tests** (proptest): a random sequence of operations is run against the learner's code and against a trivially correct model (a `HashMap`, a `Vec`, a `BTreeMap`), and every observable result must agree. When it fails, proptest shrinks to the shortest failing sequence, which is the best bug report a learner can get.
   - **Invariants and covariants.** An *invariant* holds after every operation (file never grows past twice the peak number of live pages; occupancy of every B+ tree page is within bounds; the tree is balanced). A *covariant* (a metamorphic relation) relates two runs: inserting in any order gives the same set; running an optimised plan gives the same rows as the unoptimised one; merging replicas in any order gives the same state.
   - **BusTub's own tests, in generic form:** ported test for test, but only through the public API, with no reliance on internals.
   - **Stress and fault injection:** many threads with timeouts (a hang is a failure, not a stuck test run); a disk that fails or drops writes after a chosen point.
4. **Fail with the behaviour, not the assertion.** Every property has a name that says what must be true, and failures print the shrunk input and what was expected ([§5](#5-test-design)).
5. **Scaffolding is plumbing only.** The template gives you shared types (`PageId`, `PageData`, error types), the public signatures with `todo!()` bodies and doc comments stating the contract, and nothing private. No fields, no helper functions to fill in.
6. **Rust is taught where it is needed.** Every stage page has a **Rust toolbox** ([§4](#4-the-rust-on-ramp)). Guidance is heaviest in the first modules and fades as you gain fluency.
7. **After you pass, compare, and choose.** The solution section is "what we would do"; you continue with your own code or adopt ours ([§3b](#3b-pluggable-components-your-implementation-or-ours)). Every stage ends with "Other designs": two or three alternative designs with their trade-offs, so you see the road not taken and can say why you chose yours (the question a database interview asks).
8. **Mentor voice.** Prose that explains why, retrieval prompts, experiments, as in [CURRICULUM_REASSESSMENT.md](CURRICULUM_REASSESSMENT.md).

## 3. Anatomy of a stage

```
## The goal            what the system can now do, in two or three sentences, and why it matters
## The contract        public API added (signatures are in your repo, with docs) and the properties that must hold, as prose
## Your freedom        what is deliberately not specified: layout, data structure, locking, algorithm
## The Rust toolbox    3 to 6 tips, each: the problem, a 5 to 10 line example, when to reach for it, what the compiler will say if you misuse it
## If this is new      Rust track problems to do first (L1..S4), with the specific idioms they teach
## Check yourself      one open question to answer before you code (no multiple choice)
## Tests               which properties are tested, in words (the Last run tab shows each by name)
## Hints              a ladder: question, direction, mechanism; never a line of code
## Performance        cost model, what to measure, a budget the tests enforce where it matters
## Experiment         predict, change one thing, measure, explain
## Other designs      alternatives and trade-offs, shown after you pass
## In BusTub          the C++ it mirrors; the C/C++ to Rust table; the port rule
```

The task is a contract. Steps, when they help, sit in a collapsed aside. The solution page shows one design among several.

## 3b. Pluggable components: your implementation or ours

The owner's model of teaching (2026-10-09): *"define a trait and let me implement it myself. you can implement your version and as long as the trait is satisfied the test can run with either the implementation. … the implementation detail never affects how I can progress to the next topic, only the invariants and covariants do."* Concretely:

- **Every BusTub component has a trait.** `DiskIo` (pages), a scheduler trait, `Replacer` (LRU, CLOCK) and the LRU-K and ARC variants, a buffer-pool trait, an `Index<K, V>` trait that the hash table and the B+ tree both satisfy, `Executor` and `Expression` (BusTub already has these), an optimiser entry point, a transaction manager trait. The trait file is given, with docs stating the contract and the invariants.
- **One factory per component.** The template has a small function such as `pub fn new_lru_replacer(capacity: usize) -> Box<dyn Replacer>` whose body is `todo!()`. You return your type. Nothing else in your repo is prescribed.
- **Layers above depend on the trait, never on a concrete type.** The buffer pool takes a `Box<dyn Replacer>` and a `Box<dyn DiskIo>` (or generics). So your replacer works under our buffer pool and our replacer works under yours, and any mix.
- **Tests are generic.** `fn lru_matches_the_model<R: Replacer>(make: impl Fn(usize) -> R)`; the instantiation for your factory is what `anneal course test` runs. The course's own checks run the same functions on at least two different correct implementations (ours, and a second design kept for the "Other designs" section), which proves the tests are about behaviour. A property that only one design passes is a bug in the test.
- **"Our solution" is a section of "what we would do".** After your attempt (or any time, recorded as an assisted solve, as now) it shows our implementation, why we chose it, and the two or three designs we did not choose and what each would cost. Under it: **Use your own**, or **Adopt ours** (`anneal course adopt <stage>` copies our files into your repo, where you can read and change them). Either way the next stage's tests run, because they depend on the trait.
- **The suite stays the gate.** Passing means every property holds for your implementation. It never depends on how.

Where BusTub names a concrete class (the disk manager, the buffer pool manager), the trait is the same API under a trait name, and the concrete type is whatever you write. Component pairs that BusTub couples tightly (the buffer pool and its page table) get one trait for the pair.

## 4. The Rust on-ramp

The owner has limited Rust knowledge, and creative freedom means nothing if every design collides with the compiler. Four things work together.

**A Rust Toolbox in every stage.** Short, concrete, systems-flavoured tips a non-systems programmer would not know. Examples by where they first matter: positional file I/O with `FileExt::read_at` and `write_all_at` (no seek, takes `&self`); `?` and `io::Result`; `Option::take` and `std::mem::replace` to move a value out of `&mut self`; `Vec` as a stack and `swap_remove`; the entry API on `HashMap`; slices and `chunks_exact`, `u32::from_le_bytes`, `copy_from_slice`; `Arc<Mutex<T>>`, `Condvar`, `RwLock` and why `lock().unwrap()` is normal; guards and `Drop`; `Send` and `Sync` and what the compiler is telling you; `#[repr(C)]` and `size_of`; indices instead of references to avoid self-referential structs; `debug_assert!` invariant checkers; `proptest` basics; reading a borrow-checker error from the top.

**A map from each stage to the Rust tracks.** The platform already has L1 ownership, L2 borrowing, L3 lifetimes, L4 traits, L5 generics, S1 Option and Result, S2 strings, S3 Vec and slices, S4 maps and sets. Each stage lists the track problems to do first if its idioms are new ("If this is new").

**A short Rust-for-systems module before 1a** (R1 to R5), each exercise property-tested like the rest: R1 bytes, endianness and positional file I/O; R2 errors and `io::Result`; R3 ownership shapes for systems code (`take`, `replace`, handles and indices); R4 shared state (`Arc`, `Mutex`, `Condvar`, `RwLock`); R5 testing with models and properties (proptest). Optional if you are already fluent, strongly advised otherwise.

**Compiler errors explained.** Each module has a short "errors you will meet" page: the five or six messages that module's designs provoke (cannot borrow as mutable more than once; value moved; `Send` is not implemented; lifetime may not live long enough), what they mean in plain words, and the two usual fixes.

Guidance fades: modules 1a to 1c carry the full toolbox and step asides; later modules assume the earlier tips and add only what is new.

### 4b. Concepts are an optional Rust library

The owner's rule (2026-10-09): *"concepts teach me useful rust things that I can use if I want, or it's missing knowledge."* So concept articles change role:

- **Never required.** A stage lists its concepts under `concepts_optional`; the stage page works without them, there is no "Read first" banner unless a stage genuinely cannot be done without one (rare), and passing never depends on reading. The Concepts tab and the page panel say "Rust and systems notes: all optional".
- **A library, not a lecture.** Each article teaches one Rust or systems technique a non-systems programmer may not know, framed as "when you need this, here is the idiom": the problem, the idiom, tested examples, the pitfalls and the compiler errors it provokes, the C++ version for comparison, and where real systems use it. Written as connected prose ([CURRICULUM_REASSESSMENT.md](CURRICULUM_REASSESSMENT.md) §3, the `curriculum-review` prose rules).
- **Independent of the exercises.** No article describes how to solve a stage or names a private function. The "In the exercises" section says only which stages could use the idea.
- **Reachable from where you are stuck.** The Rust toolbox tip in a stage links its article; a compiler-error page for each module links the articles that explain the error; the Concepts tab searches by Rust feature.
- **Filling known gaps.** The audit of 2026-10-09 ([RUST_CONCEPTS_AUDIT.md](RUST_CONCEPTS_AUDIT.md)) lists what is missing. New articles, in the order they are first needed: reading a borrow-checker error; `Option` and `Result` combinators and `?` with your own error type; `mem::take` and `mem::replace`; `Box`, `Rc`, `Arc`; `Cell`, `RefCell`, `Mutex` and when each is right; `Send` and `Sync` in plain words; iterators and closures for systems code; bytes, endianness and slices (`chunks_exact`, `from_le_bytes`); newtypes, typestate and `PhantomData`; designing an error enum; `Drop` and RAII guards; `unsafe` and what it promises; allocation, `with_capacity` and cache-friendly layouts; `Cow`; `impl Trait` versus `dyn Trait`; modules and `pub(crate)`; pattern-matching tricks (`let else`, `matches!`, slice patterns); and common anti-patterns.
- **Existing articles** (117) are reframed one at a time as their module is migrated: lead with the technique, drop stage-specific instructions, add a short "when you reach for this" paragraph, and keep the tested examples.

## 5. Test design

- **One generator per component** (`tests/common/gen.rs`, shipped in the template): random operation sequences, page contents, keys, schemas, transaction schedules. Learners can read and reuse them.
- **Named properties.** A test is called `writing_then_reading_returns_what_was_written`, not `test_3`. The Last run tab shows the name and the shrunk counterexample.
- **Deterministic by default.** Fixed seeds in CI (`PROPTEST_CASES` and a stored seed), random seeds locally with the failing seed printed so it can be replayed.
- **Budgets, not just answers.** Where a cost model is the lesson (ARC `O(1)`, LRU-K `O(log n)`, hash directory growth), a test fails if the operation count or wall time exceeds a generous bound at a large size.
- **No private access.** If a property needs to observe more than the public API gives, the API gets a public *observer* with BusTub's name (`get_db_file_size`, `get_num_writes`, `get_pin_count`, `size`), never a back door into internals.
- **Hidden tests are fine; hidden requirements are not.** The Tests section names every property in words; the code is visible in the repo.

## 6. The component map (BusTub's parts, new internals)

Stage lists are capabilities. Each module still ends with BusTub's own tests ported generically. Counts are targets; the pilot decides the real sizes.

**R · Rust for systems (new, 5 stages).** R1 bytes and positional I/O; R2 errors; R3 ownership shapes; R4 shared state; R5 property testing. Prepares for everything.

**Project 1 · Buffer pool**
- **1a Disk manager (6).** Pages survive (write, read, unwritten reads zeros, files created, bad path is an error); delete and reuse (the file stays bounded by the peak live pages); counters and the log (append-only, windows read like a byte string); concurrent use (many threads, exact counters); the `DiskIo` seam with in-memory disks (differential test: all disks agree with the model); boss: BusTub's `disk_manager_test`.
- **1b Disk scheduler (5).** A blocking queue and a one-shot promise (FIFO, each item once, stop signal); the scheduler (per-page order preserved; results equal a direct run); shutdown and failure (drain on drop, a panicking disk is an error); the reader-writer latch (mutual exclusion under stress); sharding (optional, with a measured speed-up); boss.
- **1c LRU and CLOCK (4).** A recency structure of your own design (model: `VecDeque`); the LRU replacer; the CLOCK replacer (differential against a slow reference); boss.
- **1d LRU-K (4).** History and k-distance (model); eviction, `set_evictable`, `remove` (invariants: size equals evictable frames); scan resistance and a complexity budget; boss.
- **1e ARC (4).** Four lists and new pages; hits and eviction; ghosts and the adaptive target; the `O(1)` budget; boss.
- **1f Buffer pool manager (5).** New pages, fetch and pin (model: a map of pages; invariant: what you wrote is what you read, whatever was evicted); unpin, dirty flags, eviction; flush and delete; concurrency; boss.
- **1g Page guards (4).** Guards and RAII (pin counts return to zero); latches and flush without deadlock (timeouts); concurrent access; boss.

**Project 2 · Indexes**
- **2a Typed pages (4).** Fixed-size encodings (round trip at any offset); a sorted page array (model: `Vec`); binary search (equals `partition_point`); a page layout of your design; boss.
- **2b Extendible hash table (6).** MurmurHash3 against golden vectors; directory and bucket pages with an invariant checker (`verify_integrity`); insert and split (model: `HashMap`; invariant checked after every operation); remove, merge, shrink; concurrency; boss.
- **2c B+ tree (7).** Pages; search and insert with splits (model: `BTreeMap`; invariants: order, occupancy, balance, depth); the iterator (equals `BTreeMap::range`); delete with borrow and merge; latch crabbing and the optimistic path; concurrency; boss.
- **2d Tombstones (3).** The same model and invariants, plus: observable behaviour is identical to the plain tree.

**Project 3 · Query execution**
- **3a Values and types (5).** Arithmetic against an `i128` oracle; comparisons are a total order on non-NULL values; three-valued logic as a truth-table property; casts; byte round trip.
- **3b Tuples, schemas, table pages (4).** Round trip over random schemas; page capacity invariants; in-place update.
- **3c Table heap, indexes, catalog (4).** Heap equals `Vec` with stable rids; the iterator never visits rows added during a scan (the Halloween problem as a property); catalog invariants.
- **3d SQL front end (new, 5).** Expressions and evaluation; **a lexer and parser** you write (property: printing and parsing an AST round-trips); the binder; the planner; boss: BusTub's SLT files for expressions.
- **3e Access-method executors (4).** Scan, insert, update, delete, index scan: results equal a naive in-memory evaluation on random tables.
- **3f Aggregation and joins (5).** Aggregates and group by; nested loop, hash and nested index join: all three agree with each other (differential) and with the naive result; join commutativity as a multiset relation.
- **3g Sorting, top-N, windows (5).** External merge sort (equals `slice::sort_by`; stable), top-N (equals sort then take), window functions against an `O(n²)` oracle.
- **3h Optimizer (4).** Rules written one at a time; the key property is **equivalence**: for random tables and queries, the optimised plan returns the same rows as the unoptimised one. Plus BusTub's plan-shape tests.

**Project 4 · Concurrency control**
- **4a Timestamps and version chains (5).** Watermark (against a naive minimum); begin, commit, abort; reconstructing a tuple and collecting logs; scanning with versions (a reader sees exactly the committed prefix at its timestamp).
- **4b MVCC writes, GC, serialisable (6).** Inserts, updates, deletes inside a transaction; write-write conflicts (no lost updates); abort restores; garbage collection preserves every version some reader can see (differential: with and without GC); primary-key indexes; serialisable validation (an anomaly finder).
- **4c ACID, logging and recovery (new, 5).** The write-ahead log and log records; undo and redo; checkpoints; **crash recovery as a property**: run a random workload on a disk that drops writes after a random point, recover, and the state must equal the model of the transactions that committed. Isolation levels and anomalies (write skew, lost update) as a spot-the-anomaly exercise.

**Primer · 0a to 0d.** Persistent trie (property: old snapshots never change; equals `HashMap`); skip list (equals `BTreeSet`); Robin Hood hash set (equals `HashSet`; bound on probe distance); sketches (count-min never underestimates; HyperLogLog error bound; ORSet merge is commutative, associative and idempotent: the CRDT laws as properties).

## 7. Migration procedure, per module

1. Write the capability list and the properties on paper. Cut the old stage ids that disappear; keep ids stable where the capability survives.
2. In the reference source, put every private item inside `@begin/@end` regions, so the template exposes only public signatures. Replace public helpers that existed only for tests with nothing, or make them private.
3. Rewrite the module's tests as properties (model, invariants, covariants) plus generic BusTub tests; share generators; add `proptest` as a dev-dependency.
4. Rewrite each `stage.md` to the anatomy in [§3](#3-anatomy-of-a-stage): contract, freedom, Rust toolbox, if-this-is-new, check, tests, hints, performance, experiment, other designs.
5. Update `stage.toml` (tests, learn, concepts), the concept articles that named old stage ids, and the module summary.
6. Regenerate the template; run `anneal course lint`, `anneal course verify --stage …`, `tools/course_snippets.py`, link check.
7. Mutation sanity check: break the reference in three plausible ways (wrong order, off by one, forgotten lock) and confirm a test fails with a readable message.
8. Ship the module (commit, push, deploy) before starting the next.

## 8. Status

- **Design:** this document. The follow-on course for what BusTub does not teach is in [ADVANCED_DB_COURSE.md](ADVANCED_DB_COURSE.md).
- **Pilot, module 1a (done in the working tree 2026-10-09):** 8 function-sized stages became 5 capability stages: 1a-01 Pages that survive, 1a-02 Delete and reuse, 1a-03 Counters and the log, 1a-04 One interface, three disks, 1a-05 Boss (threads, shutdown, BusTub's tests).
  - The template exposes the public API only: `pub struct DiskManager {}` with no fields, every method `todo!()`, no private helpers, no `slot_of`, `slot_offset`, `file_size_for` or `allocate_slot`.
  - 33 tests, 14 of them properties (model-based with `proptest`, a file-size invariant, log windows against a byte string, counters against the operations performed, three disks against one model). Counterexamples print the shortest failing operation sequence.
  - **Mutation check passed:** removing slot reuse, forgetting to zero an unwritten page, and counting only first writes each fail with a readable message.
  - Stage pages follow the anatomy of §3: contract, freedom, Rust toolbox, if-this-is-new, check, tests, hints, performance, experiment, other designs.
  - Lessons from the pilot: (1) a stage's tests must not use a *later* stage's API (the first draft ran stages 1 to 3 through the stage-4 trait and failed in `verify`); (2) a stage whose tests already pass on the previous stage's solution cannot be a stage, so concurrency is tested in the boss (`retest`), not in a stage of its own; (3) "unspecified after delete" must be stated in the contract and left unchecked.
- **Migrated (2026-10-09), each verified stage by stage with `anneal course verify`:**
  - **1b Disk scheduler (7 stages):** A queue that waits; A promise to answer later; The scheduler; Shutdown and a failing disk; The reader-writer latch; Several workers, one page at a time; Boss. 36 tests; properties: FIFO against a `VecDeque`, every element delivered once to one of many consumers, scheduled requests behave like running them in order on a model whatever the batching, the disk sees requests in the order scheduled, any number of workers gives the same answers. Hangs are failures (every wait has a timeout).
  - **1c Simple replacers (4):** A list you can pull from the middle (`IndexList`, opaque `Handle`, model: a `Vec`, stale handles never resolve); The LRU replacer; The CLOCK replacer; Boss. LRU and CLOCK are compared with a model, run through a policy-independent contract, and a deliberately different (quadratic) LRU runs the same LRU properties to prove the tests are about behaviour. Found while writing the boss: with a pin then an unpin on every use, CLOCK chooses the same victims as LRU, which is now a tested property.
  - **1d LRU-K (4):** Frames, accesses and the count (the contract, victim unspecified); Backward k-distance (policy against a brute-force model, plus consequences: `k = 1` is LRU, scan resistance, first access order); Fast eviction (O(log n) budget); Boss.
  - **1e ARC (4):** Live frames and the contract; Recency and frequency; Ghosts and the adaptive target (an exact model of BusTub's rules on four `Vec`s); Boss (ARC beats LRU on a scan trace).
  - Public API only outside regions in every migrated file; the learner owns every private type and helper. All concepts are optional (`concepts_optional`). Mutation checks (removing a wake-up, a join, `catch_unwind`, a sharded routing rule, LRU's refresh rule, CLOCK's second chance and hand rule, list generations, LRU-K's infinite distance, ARC's reordering and adaptation) each fail a test with a readable message.
  - **1f Buffer pool (4):** Pages in memory; Eviction that loses nothing; Flush and delete; Boss. The pool takes any `FrameReplacer` (new trait; `ArcReplacer` and `LruKReplacer` implement it), so tests run on a plain FIFO replacer and a spy that checks the pool/replacer protocol. Model: a table of expected page contents and pin counts; `fetch_page` fails exactly when every frame is pinned; no unmodified page is ever written.
  - **1g Page guards (3):** Guards that release themselves (model: guards taken and dropped in any order); Flushing through a guard, and panics (deadlock tests with timeouts); Boss (BusTub's guard-era tests, guard model under ARC and LRU-K).
  - **2a Typed pages (5):** round-trip properties at random offsets, a `PageArray` against a `Vec`, `lower_bound` against `partition_point`, a sorted bucket page in the pool against a `BTreeMap`.
  - **2b Extendible hash table (5):** A hash that spreads (MurmurHash3 against the C++ values); Three levels, no splits yet; Splits and growth; Remove, merge and shrink; Boss. The header, directory and bucket pages are the learner's design; the table is tested through its behaviour: a `HashMap` model, a rule for when an insert may fail (keys that share the header slot and the low `directory_max_depth` hash bits fill a bucket), a `global_depth` observer for growth and shrinking, no leaked pins, threads.
  - **2c B+ tree (6) and 2d tombstones (3):** all page types are the learner's. The tree has read-only observers (`depth`, `leaf_sizes`, `leaf_keys`, `leaf_tombstones`) and the test utilities check the rules from outside: leaves hold the keys, leaf sizes are within `[L/2, L-1]`, the depth fits the leaf count for fan-outs between `ceil(M/2)` and `M`, and every lookup latches exactly `depth() + 1` pages (so every leaf is at one depth). BusTub's tests are ported to the observers. Optimistic latching is tested by counting write latches through the traced pool.
  - **3a Values and types (6), 3b Schemas, tuples and table pages (5), 3c Table heap, iterator, indexes and catalog (5):** the storage layer for Project 3. Property tests: casts and arithmetic against an `i128` oracle, comparisons against a three-valued model, values and tuples round-tripping through bytes, a table page against a `Vec`, a heap against a `Vec` of `(rid, meta, bytes)` (every rid unique, an overwrite changes only that tuple), snapshot versus eager iterators on random tables, an index against a `BTreeMap`, a catalog against `HashMap`s. `Column`, `Schema`, `TableHeap`, `TableIterator` and `Catalog` hide their fields. Mutation checks: ignoring the stop rid, indexing deleted rows, not linking a new page and not moving the last page each fail several tests. Lesson: a property over a collection that can be empty needs the spec's empty case spelled out (an iterator made on an empty table is at the end), or it fails one run in a hundred; stress with `PROPTEST_CASES=1000` before shipping.
  - **3d Expressions and the SQL front end (7), 3e Access-method executors (5):** 3d now has the **lexer** (`tokenize`) and the **expression parser** (`Parser::expr`) as learner work: the lexer is tested by printing random token lists and lexing them back, the parser by printing random expression trees with the fewest parentheses their precedences allow and parsing them back (one property that pins every precedence and associativity); the statement-level parser, binder and planner stay given. The boss runs random integer and boolean SQL expressions through the whole pipeline against a 64-bit and a three-valued oracle. 3e merged scan+filter, insert+indexes, delete+update and the two index-scan jobs, and tests whole random SQL sessions (inserts, deletes, updates of `b`, `c` and the key, selects, an index created at a random moment) against vectors, checking the index against the table after every statement (`tests/common/sql_model.rs` is the shared model, reused by 3f to 3h). Mutation checks: eight lexer and parser mutations and six executor mutations each fail tests. **A real bug found by flake sweeps (`/tmp/c2/gen/flake.sh`):** `BPlusTree::begin` held a read latch on the first leaf while the iterator read-latched it again; with a writer queued in between this deadlocks (one run in twenty). Fixed in the reference, documented in the reader-writer latches concept and the 2c-03 hints; run a flake sweep (12 runs of every concurrent test file) before shipping a concurrency module.
- **Not built yet:** `anneal course adopt <stage>` (copy our implementation into your repo) and the trait-and-factory form of §3b for modules whose components have several implementations (replacers, indexes, executors). 1a already has the trait seam (`DiskIo`) with three implementations.
- **Everything else:** unchanged until its migration. Modules can migrate one at a time because nothing outside `disk_manager.rs` and its tests uses 1a's internals.

## 9. Decisions this design makes for you (change any of them)

- Stage count falls from 163 to about 120 as function-sized stages merge into capabilities; difficulty per stage rises, but the contract is clearer and you choose the design.
- `proptest` becomes a dev-dependency of the learner's repo.
- Two modules are new (the SQL front end and ACID, logging and recovery), and one short on-ramp module (R) comes first.
- Everything BusTub does not cover (LSM trees, Raft, columnar and vectorised execution, cost-based optimisation, vector and time-series systems) goes to the follow-on course, not into this one.

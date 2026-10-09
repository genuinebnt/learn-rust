# Follow-on course: advanced database systems (planned)

Decided 2026-10-09. The owner's words: what BusTub does not cover *"we will cover in next course after bustub based on other cmu db lectures and materials. ideally from advanced databases lectures then to vector, time series, query optimization etc lectures from cmu youtube channel."*

**Status: design only; nothing is written.** It starts after BusTub (all four projects, with the new SQL front end and recovery modules from [BUSTUB_RESTRUCTURE.md](BUSTUB_RESTRUCTURE.md)). It follows the same rules: components fixed by the source lectures, stages are capabilities, tests are property tests and generic invariants, every page teaches Rust tricks, no multiple-choice questions ([COURSE_STANDARDS.md](COURSE_STANDARDS.md) §11).

## 1. Sources

**Verified (2026-10-09):** the schedule of CMU 15-721 Advanced Database Systems, Spring 2024, <https://15721.courses.cs.cmu.edu/spring2024/schedule.html>. It lists 22 numbered lectures with required papers (below). Lectures are on the CMU Database Group YouTube channel.

**To verify before building (I could not confirm these from the pages I fetched):**
- the lectures on **vector databases** (the recent 15-445 editions added vector indexes; check the Fall 2024 and Spring 2026 15-445 schedules and the channel's seminar series);
- the lectures or seminars on **time-series databases**;
- further **query optimisation** material beyond 15-721's lectures 13 to 16 (for example the Database Seminar Series talks);
- the 15-445 lectures on **logging and recovery** and **distributed databases**, which feed the recovery module and a distributed module.

Rule from the course standards: never invent a lecture, paper or URL; each is checked before it is linked ([BUSTUB.md](BUSTUB.md) §3).

## 2. Course shape

Four parts, in this order, because each needs the previous one's vocabulary. Each module is a BusTub-style build in Rust with a source lecture and papers, a model-based test suite, and a measured experiment. Lecture numbers are those of 15-721 Spring 2024.

**Part A · Analytical engines (15-721 lectures 1 to 12)**
1. **Columnar storage and encodings** (lectures 2, 3): a columnar file format of your own with dictionary, run-length, bit-packing and frame-of-reference encodings. Properties: decode ∘ encode = identity; scans over encoded data equal scans over raw data; compressed size is bounded by raw size for the right data. Papers: Zeng et al. VLDB 2023; FastLanes; BtrBlocks.
2. **Vectorised execution** (lectures 4, 5, 6): a batch-at-a-time executor with selection vectors and SIMD-friendly kernels (portable `std::simd` or auto-vectorisation). Properties: vectorised result equals the row-at-a-time result of BusTub's executors on random tables. Papers: MonetDB/X100; Velox; Lang et al.
3. **Query compilation** (lecture 7): compile expressions to closures, then to bytecode, then (stretch) to machine code. Property: all engines agree. Paper: Neumann, VLDB 2011.
4. **Parallel execution and scheduling** (lecture 8): morsel-driven parallelism. Property: results independent of thread count; measured scaling. Paper: Leis et al., SIGMOD 2014.
5. **Hash joins and multi-way joins** (lectures 9, 10): radix-partitioned hash join; worst-case optimal joins. Property: equal to BusTub's hash join. Papers: Schuh et al.; Freitag et al.
6. **Server-side logic and the wire protocol** (lectures 11, 12): a Postgres-wire-compatible front end so `psql` talks to your engine; UDF inlining as a stretch. Property: protocol round trips, framing fuzzed. Papers: Raasveldt and Mühleisen; Froid.

**Part B · Query optimisation (lectures 13 to 16, plus seminar material to verify)**
7. **A Cascades-style optimiser** (lectures 13, 14): memo, groups, transformation and implementation rules, a search driver. Property: the chosen plan's result equals the unoptimised plan's on random data; cost is not worse than the naive plan's. Papers: Graefe; Orca; Calcite; Neumann (unnesting).
8. **Join ordering** (lecture 14): dynamic programming over subsets, then a greedy fallback for large queries. Property: DP finds a plan no more expensive than any plan found by enumeration for small queries.
9. **Statistics and cost models** (lectures 15, 16): histograms, sketches (reusing the primer's), cardinality estimation, a cost model. Property: estimates stay within a bound on generated data; the q-error is reported. Papers: Leis et al. "How good are query optimizers, really?".

**Part C · Storage and transactions beyond BusTub**
10. **LSM trees:** memtable, SSTables, bloom filters, compaction, a benchmark against the B+ tree. Property: equals `BTreeMap` under random operations and after compaction at any point.
11. **Distributed basics:** a replicated log and Raft (election, replication, safety). Property: under random message loss and delay, committed entries are never lost or reordered. Source: the Raft paper and 15-445's distributed lectures (to verify).
12. **Cloud and disaggregated storage:** object-store layout, caching, Delta/Iceberg-style table formats (lecture 18 reading).

**Part D · Specialised systems (sources to verify)**
13. **Vector databases:** exact and approximate nearest neighbour, IVF, HNSW, product quantisation. Properties: recall against brute force at a given parameter; index results subset-consistent; recall/latency curves measured.
14. **Time-series databases:** delta-of-delta and XOR (Gorilla-style) compression, downsampling, retention, tag indexes. Properties: decode ∘ encode = identity; aggregates equal on raw and rolled-up data.

**System analyses (reading with write-ups, lectures 17 to 22):** Dremel/BigQuery, Databricks Photon, Snowflake, DuckDB, Yellowbrick, Redshift. Each ends with a one-page comparison against your own engine's design: what they chose, what you chose, why.

## 3. Capstone

One repository combining the BusTub engine with a columnar vectorised path, a cost-based optimiser and either the LSM or the vector index, with benchmarks and a design write-up. This is the evidence a hiring team sees ([CURRICULUM_REASSESSMENT.md](CURRICULUM_REASSESSMENT.md) §5).

## 4. Prerequisites and Rust

BusTub restructured (all of project 1 to 4, ACID and recovery) and the Rust-for-systems module. New Rust used here and taught in the toolbox of the first module that needs it: iterators and closures at scale, `std::simd` and auto-vectorisation, `unsafe` for raw buffers (with the safety argument written out), `async` for the wire protocol, `Cow`, arenas, `PhantomData` and typestate for plan types.

## 5. Order of work

Finish the BusTub restructure first (module by module), then Part B (it builds on 3h), then Part A, then C, then D. Verify the unverified lecture sources before starting Parts C and D.

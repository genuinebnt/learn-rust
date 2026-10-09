#!/usr/bin/env python3
"""The Rust prerequisites of the BusTub course, module by module, in one place.

Single source for three things:
  1. docs/RUST_PREREQUISITES.md  (what to practise from the Rust tracks before each module, and the order to write the tracks in)
  2. web/src/trackSlugs.ts       (the slug of every Rust track, written or planned, so a link to a planned track lands on a "planned" page)
  3. the "If this is new" section of each stage page: every track is linked as [CODE Name](/t/<slug>), planned or not, so the
     links never need redoing when a track is written. The track's directory under content/tracks must be named exactly its slug.

Usage:  tools/rust_prereqs.py            write the doc and the TypeScript file
        tools/rust_prereqs.py --pages    also rewrite the "If this is new" sections of the stage pages
        tools/rust_prereqs.py --check    fail if a stage page names a track that is not in the registry

When a module is migrated, add its rows to MODULES (stage ids make the rows reach the stage pages) and run with --pages.
"""
import glob, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (code, name, slug, status, tier).  status: "written" if content/tracks/<slug> exists, else "planned".
REGISTRY = [
    ("L1", "Ownership & moves", "l1-ownership-moves", "core"),
    ("L2", "Borrowing", "l2-borrowing", "core"),
    ("L3", "Lifetimes", "l3-lifetimes", "core"),
    ("L4", "Traits & dispatch", "l4-traits-dispatch", "core"),
    ("L5", "Generics & associated types", "l5-generics", "core"),
    ("L6", "Closures & functional Rust", "l6-closures", "core"),
    ("L7", "Enums & pattern matching", "l7-enums-patterns", "core"),
    ("L8", "Error design", "l8-error-design", "core"),
    ("L9", "Modules, crates & Cargo", "l9-modules-cargo", "light"),
    ("L10", "Macros", "l10-macros", "sde3"),
    ("S1", "Option & Result", "s1-option-result", "core"),
    ("S2", "Strings & text", "s2-strings-text", "core"),
    ("S3", "Vec & slices", "s3-vec-slices", "core"),
    ("S4", "Maps & sets", "s4-maps-sets", "core"),
    ("S5", "Queues & heaps", "s5-queues-heaps", "core"),
    ("S6", "Iterators", "s6-iterators", "core"),
    ("S7", "Smart pointers & interior mutability", "s7-smart-pointers", "core"),
    ("S8", "The core traits", "s8-core-traits", "core"),
    ("S9", "I/O & filesystem", "s9-io-filesystem", "core"),
    ("S10", "Time, env & processes", "s10-time-env-processes", "light"),
    ("S11", "mem, ptr & alloc", "s11-mem-ptr-alloc", "sde3"),
    ("C1", "Threads & shared state", "c1-threads-shared-state", "core"),
    ("C2", "Message passing", "c2-message-passing", "core"),
    ("C3", "Atomics & lock-free", "c3-atomics-lock-free", "sde3"),
    ("C4", "Async & Tokio", "c4-async-tokio", "core"),
    ("C5", "Async internals", "c5-async-internals", "sde3"),
    ("C6", "Data parallelism", "c6-data-parallelism", "light"),
    ("Y2", "Unsafe Rust", "y2-unsafe-rust", "sde3"),
    ("Y3", "FFI", "y3-ffi", "sde3"),
    ("Y5", "Testing & verification", "y5-testing-verification", "sde3"),
    ("F1", "Measure & read the machine", "f1-measure-machine", "sde3"),
    ("F2", "Data layout", "f2-data-layout", "sde3"),
    ("F3", "Memory & allocation", "f3-memory-allocation", "sde3"),
    ("F4", "Hashing & purpose-built structures", "f4-hashing-structures", "sde3"),
    ("F5", "CPU-level tricks", "f5-cpu-tricks", "sde3"),
    ("F6", "Concurrency performance", "f6-concurrency-performance", "sde3"),
    ("F7", "I/O & serialization", "f7-io-serialization", "sde3"),
    # the DSA tracks the course points at (arenas and trees)
    ("D4", "Binary search", "d4-binary-search", "core"),
    ("D5", "Linked lists", "d5-linked-lists", "core"),
    ("D6", "Trees & BSTs", "d6-trees-bsts", "core"),
    ("D13", "Matrix, bits & math", "d13-matrix-bits-math", "core"),
    ("P3", "Binary search practice", "p3-binary-search-practice", "core"),
]
BY_CODE = {c: (n, s, t) for c, n, s, t in REGISTRY}


def status(slug):
    return "written" if os.path.isdir(os.path.join(ROOT, "content", "tracks", slug)) else "planned"


# module code -> (title, [(track, which stage of the track, what to practise, stage ids it reaches or None)])
MODULES = [
    ("R", "Rust for systems (new, planned)", [
        ("L1", "Moves & Copy; Passing values", "what a move is, why a guard or a handle is moved, `Option::take`", None),
        ("L2", "Shared vs unique; Where borrows end", "reading a borrow error from the top; two borrows of one struct", None),
        ("S1", "Use it", "`?`, `Option` and `Result` combinators, `let else`", None),
        ("S3", "Use it", "slices, `copy_from_slice`, `chunks_exact`, `try_into` to an array", None),
        ("S9", "Use", "files, `BufReader`, positional reads, `io::Result`", None),
        ("L8", "Custom errors", "an error enum, `Display`, `?` through two layers", None),
        ("Y5", "Use it", "unit tests, `#[should_panic]`, a first proptest", None),
    ]),
    ("1a", "Disk manager", [
        ("S9", "Use; Understand (I/O errors)", "open and create files, positional reads and writes, `io::Result`, `sync_all`", ["1a-01", "1a-03", "1a-05"]),
        ("L8", "Custom errors", "turn an `io::Error` into your own error; `?` through two layers", ["1a-01"]),
        ("S1", "Use it", "`Option` for \"no such page\", `?`, `ok_or`", ["1a-01", "1a-02"]),
        ("S3", "Use it; Understand it", "slices as views, `copy_from_slice`, `fill`, array vs `Vec`", ["1a-01", "1a-03"]),
        ("S4", "Use it", "`HashMap` and its entry API (your test model uses it)", ["1a-02"]),
        ("L1", "Clones & drops", "`Drop` and RAII: a file closes when its owner goes away", ["1a-05"]),
        ("L4", "Define & implement; Static vs dynamic", "a trait, `impl Trait for Type`, `Box<dyn Trait>`", ["1a-04"]),
        ("Y5", "Understand it", "a fake behind an injected trait; a model test with proptest", ["1a-04", "1a-05"]),
        ("C1", "Use it; Understand it", "`thread::spawn`, `move`, `Arc<Mutex<T>>`, `join`, Send/Sync in plain words", ["1a-05"]),
        ("F1", "Measure", "`Instant`, `black_box`: how to time what the Performance sections ask for", ["1a-01"]),
    ]),
    ("1b", "Disk scheduler", [
        ("C1", "Understand it; Build it", "poisoning, `RwLock`, deadlock and lock order, a bounded blocking queue with `Condvar` (`while`, never `if`)", ["1b-01", "1b-05"]),
        ("C2", "Use it; Understand it", "a worker loop that stops when told, graceful shutdown with no lost jobs, a bounded channel from `Mutex` + `Condvar`", ["1b-01", "1b-04", "1b-06"]),
        ("S5", "Use", "`VecDeque` as a queue", ["1b-01"]),
        ("S7", "Use it; Understand it", "`Arc`, why `Rc` cannot cross threads, shared state with two owners", ["1b-02", "1b-03"]),
        ("L6", "Closure basics; Fn / FnMut / FnOnce", "`move` closures, a callback that mutates state", ["1b-01", "1b-03"]),
        ("L1", "Closures take ownership; Partial moves & mem", "`Option::take`, `mem::replace`, moving out of `&mut self`", ["1b-04"]),
        ("S1", "Use it", "`Option` as a stop signal, `while let`", ["1b-01"]),
        ("L4", "Static vs dynamic", "`Arc<dyn Trait>` shared with a thread", ["1b-03"]),
        ("L8", "Errors at scale", "unwind boundaries, `catch_unwind`, a panic is not an error", ["1b-04"]),
        ("Y5", "Understand it; Build it", "a test double that fails on purpose, timeouts so a hang is a failure, loom", ["1b-04", "1b-07"]),
    ]),
    ("1c", "Simple replacers: LRU and CLOCK", [
        ("S7", "Use it; Understand it", "`Box`, `Rc`, choosing the cheapest correct pointer; why linked structures fight the borrow checker", ["1c-01"]),
        ("D5", "Linked lists, the Rust way", "index arenas, cursors, `take()`", ["1c-01"]),
        ("F3", "Arenas and pools", "a typed-index arena with generations (stale handles)", ["1c-01"]),
        ("L5", "Generic code", "`IndexList<T>`: a generic container", ["1c-01"]),
        ("S6", "Use; Understand", "returning `impl Iterator`, `iter::from_fn`", ["1c-01"]),
        ("S5", "Use; Understand", "`VecDeque` rotation, lazy deletion", ["1c-02", "1c-03"]),
        ("S4", "Use it", "a map from frame to handle; the entry API", ["1c-02"]),
        ("S3", "Use it; Understand it", "`Vec::insert`/`remove`, indices that must survive removals", ["1c-03"]),
        ("L4", "Define & implement", "one trait, two policies", ["1c-02"]),
        ("Y5", "Understand it", "model-based tests: a four-line model of the policy", ["1c-02", "1c-03"]),
    ]),
    ("1d", "LRU-K replacer", [
        ("S4", "Understand it", "`BTreeMap`/`BTreeSet`: ordered, with `first()`", ["1d-03"]),
        ("S5", "Understand", "a priority queue you can delete from; lazy deletion", ["1d-03"]),
        ("S6", "Use; Understand", "`filter().min_by_key().map()` chains", ["1d-02"]),
        ("S8", "Implement by hand", "`Ord` on tuples, deriving the order you need", ["1d-02", "1d-03"]),
        ("S1", "Use it", "`let else`, `?` on `Option`, ignoring the unknown frame", ["1d-01"]),
        ("Y5", "Understand it", "a brute-force model; properties that follow from a rule (k = 1 is LRU)", ["1d-02"]),
    ]),
    ("1e", "ARC replacer", [
        ("S7", "Understand it", "handles instead of references between list nodes", ["1e-01", "1e-02"]),
        ("S4", "Use it", "two maps with two key types (frames and pages)", ["1e-01"]),
        ("S8", "Derive", "`Hash`, `Eq`, `Copy` on id newtypes", ["1e-01"]),
        ("L2", "Split borrows; Borrow-checker limits", "copy out what you need before calling `&mut self` methods", ["1e-02", "1e-03"]),
        ("Y5", "Understand it", "an exact model of a published algorithm", ["1e-03"]),
    ]),
    ("1f", "Buffer pool manager", [
        ("C1", "Understand it", "`Mutex<Inner>` plus a latch per frame; never wait for a latch while holding the lock; lock ordering", ["1f-01", "1f-02", "1f-04"]),
        ("S7", "Understand it", "`Box<dyn Trait>` in a field, `Arc`", ["1f-01"]),
        ("L4", "Static vs dynamic", "injecting a trait object", ["1f-01"]),
        ("L2", "Reborrows; Split borrows", "a borrow of one field while using another", ["1f-01", "1f-02"]),
        ("F3", "Allocate less", "reusing buffers, copying a page into a `Box` for a request", ["1f-02", "1f-03"]),
        ("S1", "Understand it", "`Option::take`, `?` on `Option` in a function that returns `Option`", ["1f-02"]),
        ("Y5", "Build it", "a spy test double; threads sharing a pool; running a test many times", ["1f-01", "1f-04"]),
    ]),
    ("1g", "Page guards", [
        ("L1", "Clones & drops", "RAII guards: `Drop`, drop order, `Option::take` for an idempotent release", ["1g-01"]),
        ("L3", "Structs holding refs; Two lifetimes", "a guard that borrows the pool; `'a` on a struct", ["1g-01"]),
        ("S8", "Implement by hand", "`Deref`/`DerefMut`, `Drop` order", ["1g-01"]),
        ("S7", "Understand it", "`Deref` coercions, `RwLockReadGuard`", ["1g-01"]),
        ("C1", "Understand it", "deadlock and lock ordering; a flush that cannot deadlock", ["1g-02"]),
        ("L2", "Reborrows", "scoped blocks that end a borrow early", ["1g-02"]),
        ("Y5", "Build it", "loom or a watchdog timeout for a lock bug", ["1g-02", "1g-03"]),
    ]),
    ("2a", "Typed pages", [
        ("S3", "Understand it", "`copy_within`, `split_at_mut`, ranges of bytes", ["2a-02", "2a-03"]),
        ("S8", "Implement by hand", "`TryFrom` (slice to array), `Ord` for a comparator", ["2a-01", "2a-02"]),
        ("L4", "Define & implement", "a trait with an associated const (`FixedSize::SIZE`)", ["2a-01"]),
        ("L5", "Compile-time Rust", "const generics, `const fn`", ["2a-02"]),
        ("F2", "Size it", "padding, `repr(C)`, why layouts are stated and checked", ["2a-01"]),
        ("S11", "Understand", "`size_of`, `align_of`", ["2a-01"]),
        ("F7", "Encodings", "byte order, fixed-width encodings, `bytemuck` as the safe cast", ["2a-01", "2a-02"]),
        ("P3", "Binary search practice", "`partition_point`, lower bound and upper bound", ["2a-04"]),
        ("D4", "Binary search", "the lower-bound loop and its invariant", ["2a-04"]),
        ("Y5", "Understand it", "round-trip properties and a `Vec` model", ["2a-01", "2a-03", "2a-05"]),
    ]),
    ("2b", "Extendible hash table", [
        ("S8", "Implement by hand", "`Eq` + `Hash` consistency", ["2b-02"]),
        ("F4", "Hashing", "SipHash vs Fx vs identity hashers, `BuildHasher`, why low bits matter", ["2b-01"]),
        ("D13", "Matrix, bits & math", "`wrapping_*`, rotations, masks", ["2b-01"]),
        ("F2", "Size it", "`repr(C)` pages and `offset_of!`", ["2b-02"]),
        ("C1", "Understand it", "latch crabbing: take the child, then let go of the parent; lock ordering", ["2b-02", "2b-04", "2b-05"]),
        ("L5", "Bounds & associated types", "`K: FixedSize + Clone`, a generic table over key and value", ["2b-02"]),
        ("Y5", "Understand it", "an invariant checker run after every operation; scoped threads for a stress test", ["2b-02", "2b-04", "2b-05"]),
    ]),
    ("2c", "B+ tree index", [
        ("L5", "Compile-time Rust; Generic code", "const generics (`TOMBS`), bounds on an `impl` block", ["2c-01"]),
        ("L7", "Enums & exhaustiveness", "a page-type tag as an enum, `TryFrom<u32>`, `match` that must cover every kind", ["2c-01"]),
        ("S7", "Understand it", "page ids instead of pointers; why a tree of references fights the borrow checker", ["2c-01"]),
        ("F2", "Locality", "a slotted page for a B-tree node: header, slot array, cell heap", ["2c-01"]),
        ("D6", "Trees & BSTs", "search trees: split, borrow, merge", ["2c-02", "2c-04"]),
        ("S3", "Understand it", "`split_off`, `partition_point`, `insert`, `remove`", ["2c-02", "2c-04"]),
        ("S1", "Understand it", "`pop()` returns an `Option`; `let Some(x) = .. else`", ["2c-02", "2c-04"]),
        ("S6", "Build", "implementing `Iterator`, an iterator without allocation", ["2c-03"]),
        ("L3", "Structs holding refs", "an iterator that holds the pool by reference", ["2c-03"]),
        ("C1", "Understand it", "latch crabbing, lock order, `RwLock` has no upgrade", ["2c-05"]),
        ("L6", "Fn / FnMut / FnOnce", "`impl Fn` parameters: one descent for insert and remove", ["2c-05"]),
        ("Y5", "Understand it; Build it", "a model and a shape checker; threaded tests under a timeout", ["2c-02", "2c-04", "2c-05"]),
    ]),
    ("2d", "B+ tree tombstones", [
        ("L5", "Compile-time Rust", "const generics and associated constants decide a page layout", ["2d-01"]),
        ("S8", "Implement by hand", "comparing keys through a comparator, not by bytes", ["2d-01"]),
        ("L7", "Enums as design", "a state (live or deleted) that is part of an entry", ["2d-01"]),
        ("S3", "Understand it", "`partition`, `drain`, `extend` to move tombstones with their pairs", ["2d-02"]),
        ("Y5", "Understand it", "an equivalence property over every buffer size", ["2d-02"]),
    ]),
    ("3a", "Values and types", [
        ("L7", "Enums as design", "a `Value` enum with data, `match` on pairs of values", ["3a-01", "3a-03"]),
        ("S8", "Implement by hand", "`PartialOrd`/`Ord` with `total_cmp`, `From`/`TryFrom`", ["3a-02", "3a-03"]),
        ("L8", "Custom errors", "overflow and cast errors as values", ["3a-02", "3a-04"]),
        ("S2", "Understand", "UTF-8, case mapping, comparing strings", ["3a-01", "3a-03"]),
        ("D13", "Matrix, bits & math", "`checked_*`, `wrapping_*`, overflow in debug and release", ["3a-04"]),
        ("F7", "Encodings", "a value as bytes", ["3a-05"]),
    ]),
    ("3b", "Schemas, tuples and table pages", [
        ("F2", "Locality", "the slotted page: header, slot array, cell heap", ["3b-03"]),
        ("F7", "Encodings", "fixed and variable parts of a row", ["3b-02"]),
        ("S3", "Understand it", "sub-slices, `split_at`", ["3b-03", "3b-04"]),
        ("L7", "Patterns in depth", "matching on column types", ["3b-01", "3b-02"]),
        ("S2", "Understand", "strings stored in a page", ["3b-02"]),
    ]),
    ("3c", "Table heap, iterator and catalog", [
        ("S6", "Understand", "an iterator that holds a position; `IntoIterator` for a borrowed collection", ["3c-02"]),
        ("L3", "Structs holding refs", "an iterator that borrows the heap", ["3c-01", "3c-02"]),
        ("S4", "Use it", "the catalog's maps", ["3c-04"]),
        ("C1", "Understand it", "a lock around the last page; threads inserting at once", ["3c-01"]),
        ("Y5", "Understand it", "a heap checked against a `Vec`; the Halloween problem as a property", ["3c-01", "3c-02", "3c-03", "3c-04"]),
        ("L4", "Static vs dynamic", "`Box<dyn Index>`, one trait over several key sizes", ["3c-03", "3c-04"]),
    ]),
    ("3d", "Expressions and the SQL front end", [
        ("L4", "Static vs dynamic", "`Arc<dyn Expression>`, a trait object tree", ["3d-01", "3d-06"]),
        ("S7", "Use it", "`Arc` for shared expressions, `Box<Expr>` for a recursive syntax tree", ["3d-01", "3d-05"]),
        ("L7", "Enums as design", "`match` on an operator, on a pair of truth values; an AST as enums, `let else`", ["3d-02", "3d-03", "3d-05"]),
        ("S8", "Implement by hand", "comparison results as values (`Ordering`, `CmpBool`)", ["3d-02"]),
        ("D13", "Matrix, bits & math", "`checked_*`, overflow as an error", ["3d-02"]),
        ("L8", "Custom errors", "overflow errors; parse errors with messages", ["3d-02", "3d-04", "3d-05"]),
        ("S2", "Understand", "case mapping on characters; scanning characters and bytes", ["3d-03", "3d-04"]),
        ("S6", "Understand", "`Peekable` for a lexer", ["3d-04"]),
        ("F3", "Arenas and pools", "an arena AST, a string interner (optional)", ["3d-05"]),
        ("Y5", "Build it", "a model for three-valued logic; print-then-parse round trips; fuzzing a lexer and a parser", ["3d-02", "3d-03", "3d-04", "3d-05", "3d-07"]),
    ]),
    ("3e", "Access-method executors", [
        ("L4", "Static vs dynamic", "`Box<dyn Executor>` children, `Box<dyn Index>` calls", ["3e-01", "3e-02", "3e-04"]),
        ("S6", "Understand", "the iterator model: pulling by hand from an iterator, in batches", ["3e-01", "3e-04"]),
        ("L3", "Structs holding refs", "an executor that borrows the catalog and the heap", ["3e-01"]),
        ("S1", "Understand it", "`Option<Iterator>`, `?` in a loop, `Result<Option<T>>`", ["3e-01", "3e-02", "3e-03"]),
        ("L6", "Fn / FnMut / FnOnce", "predicates and target expressions as callable trees", ["3e-03"]),
        ("L8", "Custom errors", "execution errors", ["3e-02", "3e-03"]),
        ("Y5", "Build it", "a model of SQL in plain vectors; random sessions of statements", ["3e-01", "3e-02", "3e-03", "3e-04", "3e-05"]),
    ]),
    ("3f", "Aggregation and joins", [
        ("S4", "Understand it", "entry API for group-by", None),
        ("S8", "Implement by hand", "`Hash`/`Eq` on `Value`", None),
        ("S6", "Understand", "iterator chains for joins", None),
        ("S5", "Understand", "heaps for merge-style work", None),
        ("F4", "Right structure for the job", "hash tables for joins", None),
    ]),
    ("3g", "Sorting, limits and window functions", [
        ("S5", "Understand", "`BinaryHeap` + `Reverse` for top-N", None),
        ("S3", "Understand it", "`sort_by`, stable sort, merging runs", None),
        ("S9", "Understand", "spilling to files: bounded-memory reading", None),
        ("S6", "Understand", "iterators over runs", None),
    ]),
    ("3h", "Optimizer rules", [
        ("L7", "Enums as design", "matching on plan-tree shapes, a visitor", None),
        ("S7", "Understand it", "owning trees: `Box`, rebuilding a node", None),
        ("L4", "Define & implement", "a rule as a trait", None),
        ("Y5", "Build it", "equivalence: optimised plan and unoptimised plan return the same rows", None),
    ]),
    ("4a", "Timestamps, transactions and version chains", [
        ("S7", "Understand it", "`Arc`, `Mutex`, shared state", None),
        ("C1", "Understand it", "`RwLock`, atomics-free sharing first", None),
        ("C3", "Understand it", "atomic counters for timestamps", None),
        ("S4", "Understand it", "`BTreeMap` for a watermark", None),
        ("L7", "Patterns in depth", "undo log entries as enums", None),
    ]),
    ("4b", "MVCC writes, abort, garbage collection and serializability", [
        ("C1", "Understand it", "lock ordering and deadlock", None),
        ("S4", "Understand it", "version chains in maps", None),
        ("L8", "Custom errors", "write-write conflicts as errors", None),
        ("Y5", "Build it", "an anomaly finder as a property", None),
    ]),
    ("4c", "ACID, logging and recovery (new, planned)", [
        ("S9", "Understand", "append-only files, `fsync`", None),
        ("F7", "Storage formats", "write-ahead-log records: length prefix, checksum, torn-write recovery", None),
        ("Y5", "Build it", "crash a disk at a random point, then recover", None),
        ("L8", "Errors at scale", "a recovery that never panics on a damaged log", None),
        ("S8", "Implement by hand", "`Drop` order for durability", None),
        ("C1", "Understand it", "group commit", None),
    ]),
    ("0a", "A persistent trie", [
        ("L1", "Clones & drops", "sharing structure instead of copying", None),
        ("S7", "Understand it", "`Rc`/`Arc` for path copying", None),
        ("L7", "Enums & exhaustiveness", "optional children", None),
        ("S4", "Use it", "the model: `HashMap`", None),
    ]),
    ("0b", "A skip list", [
        ("S7", "Understand it", "`Option<Box<Node>>`, interior links", None),
        ("S5", "Understand", "ordered structures", None),
        ("D5", "Linked lists, the Rust way", "index-linked nodes", None),
        ("F3", "Arenas and pools", "a node arena", None),
        ("Y2", "Use it", "optional: raw pointers and their safety comments", None),
    ]),
    ("0c", "Robin Hood hashing", [
        ("F4", "Hashing; Right structure for the job", "open addressing, probe distance", None),
        ("S3", "Understand it", "a table in a `Vec`", None),
        ("S8", "Implement by hand", "`Hash` and `Eq`", None),
        ("F5", "Branches", "bit tricks", None),
    ]),
    ("0d", "Sketches and replicated sets", [
        ("F4", "Hashing", "independent hash functions", None),
        ("F5", "Branches", "popcount and leading zeros", None),
        ("S4", "Use it", "`HashMap`/`BTreeSet` as the exact answer", None),
        ("S8", "Implement by hand", "`Eq`/`Ord` and the laws a merge must obey", None),
        ("Y5", "Understand it", "algebraic laws as properties", None),
    ]),
]


def slug_of(code):
    return BY_CODE[code][1]


def link(code):
    return f"[{code} {BY_CODE[code][0]}](/t/{slug_of(code)})"


def build_doc():
    out = []
    w = out.append
    w("# Rust prerequisites for the BusTub course\n")
    w("Generated by `tools/rust_prereqs.py`; edit the data there, not this file.\n")
    w("The owner has limited Rust knowledge, and the course gives creative freedom, so every module lists the practice from the **Rust tracks** "
      "worth doing first. Tracks that are written already are marked **written**; the rest are **planned** and are implemented *after* the course, "
      "in the order of [section 3](#3-the-order-to-write-the-tracks-in) (the order the course first needs them). Stage pages already link every track "
      "as `/t/<slug>`, planned or not, so nothing needs linking again when a track is written: **name the track's directory under `content/tracks/` exactly "
      "its slug**, and add its stages and problems. Until then a planned link lands on a \"planned\" page (`web/src/trackSlugs.ts`).\n")
    w("## 1. The tracks the course uses\n")
    w("| Track | Slug | Status | Tier | Modules that use it |")
    w("|---|---|---|---|---|")
    uses = {}
    for mod, _, rows in MODULES:
        for code, *_ in rows:
            uses.setdefault(code, [])
            if mod not in uses[code]:
                uses[code].append(mod)
    order = [m for m, _, _ in MODULES]
    for code, name, slug, tier in REGISTRY:
        if code not in uses:
            continue
        w(f"| {code} {name} | `{slug}` | {status(slug)} | {tier} | {', '.join(uses[code])} |")
    unused = [f"{c} {n}" for c, n, sl, t in REGISTRY if c not in uses]
    w("\nNot used by the course: " + ", ".join(unused) + ". (They matter for other goals, not for BusTub.)\n")
    w("## 2. Module by module\n")
    w("Do the rows top to bottom; a module's first rows are the ones its first stages need. \"Stage\" is the stage of the track to open (the band in brackets for planned tracks follows [CURRICULUM.md](CURRICULUM.md)).\n")
    for mod, title, rows in MODULES:
        w(f"### {mod.upper()} · {title}\n")
        w("| Track | Stage of the track | Practise | Needed by |")
        w("|---|---|---|---|")
        for code, stage, what, stages in rows:
            st = status(slug_of(code))
            tag = "" if st == "written" else " *(planned)*"
            w(f"| {link(code)}{tag} | {stage} | {what} | {', '.join(stages) if stages else 'the module'} |")
        w("")
    w("## 3. The order to write the tracks in\n")
    w("The planned tracks, sorted by the first module that needs them (then by how many modules use them). Written tracks are skipped. "
      "Write them in this order after the course, and a learner who reaches module N always finds the tracks it points at.\n")
    first = {}
    for i, (mod, _, rows) in enumerate(MODULES):
        for code, *_ in rows:
            first.setdefault(code, i)
    planned = [c for c, n, s, t in REGISTRY if c in uses and status(s) == "planned"]
    planned.sort(key=lambda c: (first[c], -len(uses[c])))
    w("| # | Track | First needed by | Used by |")
    w("|---|---|---|---|")
    for n, code in enumerate(planned, 1):
        w(f"| {n} | {link(code)} | {order[first[code]].upper()} | {len(uses[code])} modules |")
    w("\n## 4. Gaps the tracks do not cover yet\n")
    w("Things the course asks for that no planned track has a stage for; decide whether to add a stage to an existing track (recommended) or leave them to the optional concept articles:\n")
    w("- **Reading compiler errors** (borrow, move, `Send`): L2 and L1 teach the rules; a stage that is nothing but \"read this error and fix it\" would serve every module. Today the concept `reading-compiler-errors` covers it.")
    w("- **Byte-level work** (`from_le_bytes`, `copy_within`, `chunks_exact`, `try_into`): S3 covers slices and F7 encodings; a short stage \"bytes and endianness\" in S3 would make 2a smoother.")
    w("- **Drop and RAII guards**: spread across L1 (clones & drops), S8 (Drop order) and S7 (Deref); a guard-focused stage in S8 (\"RAII guards\") would serve 1a and 1g.")
    w("- **Property testing with a model**: Y5 lists proptest; the course uses it from 1a, so Y5's first stage needs a model-test problem that appears early.")
    w("- **Timeouts and hang-proof tests** (a `recv_timeout` helper): worth one Y5 problem; used from 1b.")
    return "\n".join(out) + "\n"


def build_ts():
    lines = ["// Generated by tools/rust_prereqs.py. The slug of every Rust track the BusTub course links to, written or planned.", "// A link to a track that is not written yet lands on a \"planned\" page.", "export const TRACK_SLUGS: Record<string, { code: string; name: string }> = {"]
    for code, name, slug, tier in REGISTRY:
        lines.append(f'    "{slug}": {{ code: "{code}", name: {name!r} }},'.replace("'", '"'))
    lines.append("};")
    return "\n".join(lines) + "\n"


NAME_RE = re.compile(r"\*\*([LSCYFDP]\d+)\b[^*]*\*\*")
SECTION_RE = re.compile(r"(^## If this is new\n)(.*?)(?=^## |\Z)", re.S | re.M)


def rewrite_stage(path, stage_id, rows):
    text = open(path).read()
    m = SECTION_RE.search(text)
    if not m:
        return False
    body = m.group(2)
    known = set()

    def fix(mm):
        code = mm.group(1)
        if code not in BY_CODE:
            return mm.group(0)
        known.add(code)
        return link(code)

    body = NAME_RE.sub(fix, body)
    body = re.sub(r"\[([LSCYFDP]\d+) [^\]]*\]\(/t/[^)]*\)", lambda mm: (known.add(mm.group(1)) or link(mm.group(1))), body)
    extra = []
    for code, stage, what, stages in rows:
        if stages and stage_id in stages and code not in known:
            extra.append(f"- {link(code)}: {stage.lower() if False else stage}: {what}.")
            known.add(code)
    body = body.rstrip("\n") + "\n" + ("\n".join(extra) + "\n" if extra else "") + "\n"
    new = text[: m.start(2)] + body + text[m.end(2):]
    if new != text:
        open(path, "w").write(new)
        return True
    return False


def main():
    args = sys.argv[1:]
    open(os.path.join(ROOT, "docs", "RUST_PREREQUISITES.md"), "w").write(build_doc())
    open(os.path.join(ROOT, "web", "src", "trackSlugs.ts"), "w").write(build_ts())
    mod_rows = {m: rows for m, _, rows in MODULES}
    bad = 0
    changed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "courses", "bustub", "modules", "*", "stages", "*", "stage.md"))):
        toml = open(os.path.join(os.path.dirname(path), "stage.toml")).read()
        stage_id = re.search(r'^id = "([^"]+)"', toml, re.M).group(1)
        module = stage_id.split("-")[0]
        text = open(path).read()
        for code in set(re.findall(r"\*\*([LSCYFDP]\d+)\b[^*]*\*\*", re.search(r"^## If this is new\n(.*?)(?=^## |\Z)", text, re.S | re.M).group(1))) if "## If this is new" in text else []:
            if code not in BY_CODE:
                print(f"{stage_id}: unknown track {code}")
                bad += 1
        if "--pages" in args and module in mod_rows:
            changed += rewrite_stage(path, stage_id, mod_rows[module])
    if "--pages" in args:
        print(f"{changed} stage pages rewritten")
    if "--check" in args and bad:
        sys.exit(1)


if __name__ == "__main__":
    main()

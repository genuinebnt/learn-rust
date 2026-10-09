# Rust concepts audit (2026-10-09)

Method: the three-layer view of [actionbook/rust-skills](https://github.com/actionbook/rust-skills) (language mechanics, design choices,
domain constraints; its topic skills m01 ownership, m02 smart pointers, m03 mutability, m04 zero-cost abstraction, m05 type-driven design,
m06 errors, m07 concurrency, m10 performance, m12 lifecycle, m14 mental models, m15 anti-patterns). Each was compared with the 96 concept
articles in `courses/bustub/concepts/` and with what the reference code in `courses/bustub/reference/src` actually uses.
Only the repo's skill names and its anti-pattern and type-driven tables were read; nothing was copied.

## Coverage

| rust-skills topic | Our articles | Verdict |
|---|---|---|
| m01 ownership, borrowing, moves | `lifetimes-in-structs`, `raii-guards-and-lifetimes`, `ownership-of-files-and-raii`, `moving-data-across-threads` | No article on moves and borrowing as such; taught only through their uses |
| m02 `Box`, `Rc`, `Arc`, `RefCell` | none | **Gap.** The code has 72 `Arc<` uses, 35 `dyn`, only 4 `Rc`/`RefCell` (so the course never needs `Rc`), and `Deref` on three guard types |
| m03 mutability, interior mutability | `mutex-owns-its-data`, `atomics-ordering-and-the-log` | **Gap.** No article on `Cell`/`RefCell` vs `Mutex`/atomics, or on `&self` methods that mutate (4a-4b and the sketches rely on it) |
| m04 zero-cost, static vs dynamic dispatch | `trait-objects-and-the-disk-seam`, `traits-with-associated-consts`, `const-generics-for-page-layouts` | Partial: `dyn` is covered, generics and monomorphisation are not |
| m05 type-driven design | `structs-and-accessors`, `enums-with-data-and-match` | **Gap.** Newtypes, `PhantomData` (31 uses), typestate, sealed traits. Note `TxnId`, `Timestamp` are plain `i64` aliases while `PageId` and `FrameId` are newtypes: a ready-made lesson |
| m06 / m13 errors | `errors-as-values-with-result`, `rust-io-errors`, `panics-unwinding-and-catch-unwind`, `overflow-and-checked-arithmetic` | Partial: no article on designing an error enum, `From` and `?` conversions (the code has 0 `impl From`) or when to panic |
| m07 concurrency | 11 articles (latches, condvars, deadlocks, channels, shutdown, atomics) | Covered. Missing: `Send` and `Sync` themselves |
| m10 performance | `performance-tests-and-measuring`, `shifts-masks-and-bit-tricks` | Partial: allocation, `with_capacity`, cache locality, avoiding `clone` in hot loops |
| m12 lifecycle / RAII | `raii-guards-and-lifetimes`, `clean-shutdown-drop-and-join`, `ownership-of-files-and-raii` | Covered |
| m14 mental models | stage "C/C++ way" tables and port rules | Covered for C++ programmers; no "what the borrow checker is asking" article |
| m15 anti-patterns | none | **Gap.** See below |
| iterators and closures (not a skill, but ubiquitous) | `the-iterator-model` is the SQL iterator model | **Gap.** Rust iterators and closures: `filter_map`, `zip`, `windows`, `sort_by`, `retain`, `fold` |
| `unsafe-checker` | `repr-c-layouts-and-const-asserts` | The reference has 0 `unsafe`; a short article on what unsafe promises would explain why |

## What the reference code shows

- **157 `.unwrap()` in `src/`**: 112 are `lock()`, `read()` or `write()` on a lock (a poisoned lock means another thread panicked), 45 are others.
  The course never says why unwrapping a lock is the accepted choice, or when to handle poisoning instead. Worth an article.
- **213 `.clone()`**: most are `Arc` clones, `Tuple`s and `Value`s copied into batches. An honest "which clones are free (a refcount bump) and
  which copy data" article would help learners read the code.
- **0 `unsafe`, 0 `transmute`, 0 `lazy_static`, 4 `Rc`/`RefCell`:** the anti-pattern list from m15 (`Rc` for a single owner, `unsafe` for
  convenience, `lazy_static!`, transmute, custom linked list) is mostly avoided already; the arena-based lists and skip list are the
  "no custom linked list with pointers" answer. That deserves saying out loud.
- `Deref` is used for the guard types only (page guards, `ValueGuard`), which is the legitimate smart-pointer use, not OOP inheritance.

## Proposed new concept articles

Each would follow the course rules: a tested `## In real code` (two or more `#[test]`s), `### In the exercises` naming the stages that use it,
`### Where it is used`, and links from the stages' `concepts` lists. In priority order:

1. **send-and-sync**: why `Arc<Mutex<T>>` is shared across threads and `Rc` is not; what the compiler checks. Stages: 1b, 2d, 4a, 4b, 0a to 0d.
2. **smart-pointers-box-rc-arc**: `Box`, `Arc`, `Rc`, `Deref` for guards, when each fits, why `Rc` never appears. Stages: 3d (expression trees), 4a, 0a.
3. **interior-mutability**: `Cell`, `RefCell`, `Mutex`, `RwLock`, atomics: mutation through `&self`. Stages: 1d, 4a, 0d.
4. **lock-poisoning-and-the-unwrap-policy**: what the 112 `lock().unwrap()` mean; when to recover with `into_inner`. Stages: 1b, 1f, 4a.
5. **newtypes-and-type-driven-design**: `PageId`, `TxnId`, `PhantomData`, typestate and the builder; the `i64` aliases as the counter-example. Stages: 1a, 2a, 4a.
6. **designing-error-types**: an error enum, `From`, `?` conversions, `Display`, panic versus `Result`. Stages: 1a, 3d, 4b.
7. **iterators-and-closures**: adapters and consumers, borrowing in closures, `sort_by`/`retain`/`windows`. Stages: 3e to 3g, 4b.
8. **option-and-result-combinators**: `?`, `let ... else`, `filter`, `zip`, `ok_or_else`, `map_or`. Stages: 4a, 4b, 0a.
9. **generics-and-static-dispatch**: monomorphisation, trait bounds, `impl Trait`, generics versus `dyn`. Stages: 2a, 2b, 3d.
10. **eq-hash-ord-contracts**: `derive` and the rules a `BTreeMap` or `HashMap` key must keep. Stages: 2b, 3f, 0a, 0c.
11. **rust-anti-patterns-in-practice**: the m15 list shown against this codebase (clone to silence the borrow checker, index loops, `unwrap`,
    giant `match`, `Rc<RefCell>` sprawl, many `pub` fields, locks held across calls). Stages: 1f, 3f, 4b.
12. **allocation-and-cache-friendly-code**: `with_capacity`, avoiding clones in loops, flat `Vec` versus pointers, measuring. Stages: 3g, 0c, 0d.
13. **unsafe-and-its-contracts**: what `unsafe` promises, why this course needs none, `repr(C)` revisited. Stage: 2a.
14. **modules-visibility-and-api-boundaries**: `pub`, `pub(crate)`, re-exports, what the hidden-module mechanism relies on.

Recommended first batch: 1 to 6 (they explain code the learner meets in nearly every module), then 7 and 8.
Not started: awaiting the owner's go-ahead (CLAUDE.md: propose extras, then wait).

## Status after the first batch (2026-10-09)

Fifteen articles were written from items 1 to 14 above, plus one on testing concurrent code: `send-and-sync`, `smart-pointers-box-rc-arc`,
`interior-mutability`, `lock-poisoning-and-the-unwrap-policy`, `newtypes-and-type-driven-design`, `designing-error-types`,
`iterators-and-closures`, `option-and-result-combinators`, `generics-and-static-dispatch`, `eq-hash-ord-contracts`,
`rust-anti-patterns-in-practice`, `allocation-and-cache-friendly-code`, `unsafe-and-its-contracts`,
`testing-concurrent-code-with-loom-and-miri`, `modules-visibility-and-api-boundaries`. Each has two or more tested examples and is linked
from the stages that use it.

## Systems programming: what recurs, and what is covered

Rust used for systems work (databases, storage engines, OS components, network services, embedded firmware) keeps returning to the same
dozen topics. Against this course:

| recurring concept | covered by | gap |
|---|---|---|
| ownership, RAII, `Drop`, guards (files, locks, handles) | `raii-guards-and-lifetimes`, `ownership-of-files-and-raii`, `clean-shutdown-drop-and-join` | `Drop` order and `Option::take` in `Drop` |
| bytes, endianness, layout, `repr(C)`, alignment | `bytes-endianness-and-views`, `repr-c-layouts-and-const-asserts`, `serialization-of-values` | alignment and padding as a topic (`size_of`, `align_of`, `repr(align)`) |
| `unsafe`, raw pointers, `MaybeUninit`, `NonNull` | `unsafe-and-its-contracts` | **FFI** (`extern "C"`, `CString`, callbacks) |
| threads, locks, condvars, channels, atomics and memory ordering | 14 articles | **lock-free** (CAS loops, ABA), **false sharing** and cache padding |
| file and device I/O: `Read`/`Write`/`Seek`, positional I/O | `positional-io-and-short-reads`, `rust-io-errors` | **durability**: `fsync`, write ordering, torn writes; **memory-mapped files** |
| allocation, arenas, custom layouts | `arenas-and-generational-handles`, `allocation-and-cache-friendly-code` | **custom allocators**, `no_std` and `alloc` |
| error handling with OS errors | `designing-error-types`, `rust-io-errors` | |
| async I/O and the reactor | `promises-and-futures` (a one-shot) | **async/await**, `epoll`/`io_uring`, when threads are better |
| processes and the OS: signals, `std::process`, environment, exit codes | none | **process and signal handling** |
| testing: concurrency, UB | `testing-concurrent-code-with-loom-and-miri`, `model-based-testing`, `testing-with-fakes` | **property-based testing and fuzzing** (`proptest`, `cargo-fuzz`) |
| profiling | `performance-tests-and-measuring` (perf, flamegraphs), `allocation-and-cache-friendly-code` | |
| embedded: `no_std`, interrupts, peripheral ownership, static buffers | none | out of scope for BusTub; a separate track if wanted |

Candidate next articles, in order of fit with a database course: **durability and fsync** (the write path every storage engine rests on),
**lock-free basics and false sharing**, **FFI**, **property-based testing and fuzzing**, **memory-mapped files**, **async versus threads**.
Not started.

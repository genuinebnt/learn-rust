**Where this fits.** The whole table, under BusTub's own tests, including eight threads' worth of concurrent ones.

## The task

Nothing new. Run the ported tests:

| BusTub | here |
|---|---|
| `ExtendibleHTableTest.InsertTest2`, `RemoveTest1` | `extendible_htable_test::{insert_test_2, remove_test_1}` (`InsertTest1` lives in the stage tests, adapted: see stage 18) |
| `ExtendibleHTableConcurrentTest.InsertTest1/2` | two threads insert the same keys / disjoint keys; every key is found exactly once |
| `.DeleteTest1/2` | two threads delete the same keys / disjoint keys |
| `.MixTest1/2` | inserts, deletes and lookups at once; keys that are never deleted must **always** be found |

## Tests

- `s2b_22_*`: the same scenarios as scoped threads in the stage tests, plus a heavy workload (4 threads, 1500 random operations each, every thread on its own keys) after which `verify_integrity` passes.
- The ported BusTub tests above.

## Syntax and methods

```rust
thread::scope(|scope| { for t in 0..2 { let ht = &ht; scope.spawn(move || { /* uses ht */ }); } });   // all joined at the end of the scope
```

## Notes

**If a concurrent test hangs or fails once in a hundred runs:** a latch is taken in a different order somewhere, or a guard outlives its use. List, for `get_value`, `insert` (new directory, existing bucket, split) and `remove` (plain, merge), the order in which they take header → directory → bucket → (new/sibling bucket). Every path must follow one order. The only multi-bucket operations are split (old bucket, then new bucket, which nobody else can know about yet) and merge (the bucket, then its sibling: both reached through the directory's write latch, so nobody else is in this directory).

**What this version does not do:** it holds the directory's write latch through the whole `insert`/`remove`, so operations on the same directory serialise. A faster version releases the directory as soon as it holds a bucket that is "safe" (not full on insert, not going to be empty on remove); that optimisation is on the board as an extension.

## In BusTub

The test file's helpers `InsertHelper`, `InsertHelperSplit`, `DeleteHelper`, `DeleteHelperSplit`, `LookupHelper`, and `LaunchParallelTest(num_threads, args...)` that starts `std::thread`s.

## The C/C++ way

| gtest / C++ | Rust |
|---|---|
| `std::thread(args..., thread_itr)` pushed into a vector, `join()` each | `thread::scope`, `scope.spawn` |
| `template <typename... Args> void LaunchParallelTest(uint64_t num_threads, Args &&...args)` | `fn launch_parallel_test(n: u64, f: impl Fn(u64) + Sync)` |
| `ASSERT_EQ` inside a thread: a failure there doesn't stop the test thread (gtest's assertions in non-main threads are not safe) | `assert!` in a spawned thread panics that thread; `scope` re-raises it on join |
| data races detected only by ThreadSanitizer | none possible in safe Rust; logic races (lost updates) are what the tests find |

## What you built

A three-level, page-backed, concurrent hash table, tested against BusTub's suite. Next: the **B+ tree**.

## Learn more
- BusTub's [concurrent tests](https://github.com/cmu-db/bustub/blob/master/test/container/disk/hash/extendible_htable_concurrent_test.cpp) · the [Project 2 page](https://15445.courses.cs.cmu.edu/fall2026/project2/) · [`thread::scope`](https://doc.rust-lang.org/std/thread/fn.scope.html)

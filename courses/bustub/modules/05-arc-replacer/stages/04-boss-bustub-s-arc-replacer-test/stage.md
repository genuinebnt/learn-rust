**Where this fits.** BusTub's own tests for the ARC replacer, plus its performance test.

## The task

Nothing new, unless the performance test fails: then something is slower than O(1).

| BusTub | here | checks |
|---|---|---|
| `ArcReplacerTest.SampleTest` | `arc_replacer_test::sample_test` | the target moves 0 → 1 → 3 → 2; side choice; a pinned frame is skipped |
| `ArcReplacerTest.SampleTest2` | `arc_replacer_test::sample_test2` | a small replacer: ghost trimming (cases 4A and 4B), target growth |
| `ArcReplacerTest.RemoveBehaviorTest` | `arc_replacer_test::remove_behavior_test` | nine scenarios for `remove` |
| `ArcReplacerPerformanceTest.RecordAccessPerformanceTest` | `arc_replacer_performance_test::record_access_performance_test` | 256K frames, 10 rounds of 256K hits in the middle of the list: **average under 3 seconds per round** |

## Tests

- `s1e_09_the_size_always_matches_a_recount`: 2,000 random operations on an 8-frame replacer (access, set-evictable, evict, remove): `size()` equals a recount of the evictable frames after every step, and `evict` only ever returns a frame that was evictable.
- The four BusTub tests above.

## Syntax and methods

```rust
let start = std::time::Instant::now();
...
assert!(start.elapsed() < Duration::from_secs(3));
```

## Notes

If the performance test is slow, profile before you guess: `cargo test --release --test arc_replacer_performance_test`, or sample with `perf`/Instruments. The usual cause is an `O(n)` operation inside `record_access` (a list search, or `Vec::remove`); the usual fix is the handle you already store. The test says "if this takes above 3s on average, you might get into trouble in later projects": it is a promise about the buffer pool built on top.

## In BusTub

The performance test prints "This test will see how your RecordAccess performs when the list is large" and asserts `avg < 3` (seconds).

## The C/C++ way

| gtest | Rust |
|---|---|
| `std::chrono::system_clock::now()` (not monotonic: can go backwards) | `std::time::Instant::now()` (monotonic) |
| `ASSERT_LT(avg, 3)` | `assert!(avg < 3.0)` |
| `std::cout << ...` | `println!` (captured unless the test fails or you pass `-- --nocapture`) |
| `256 << 10` | `256 << 10` (same shift; make sure the type is wide enough: `usize`) |

## Experiment

Optional. Predict first, then run it.

1. **Make it O(n).** Replace the handle-based removal in one of ARC's lists with a linear search. Measure `record_access` per round at 1 000, 16 000 and 256 000 frames and sketch time against size. Where does the 3-second bar of the performance test fall on your curve?
2. **Watch the target move.** Print `p` after every access in `sample_test`. Match each change to a ghost hit of the kind your code handles, and say which list the page came back from.

## What you built

The replacer layer of the buffer pool: LRU, CLOCK, LRU-K and ARC, with the same shape of API and the same BusTub tests. Next: the **buffer pool manager**, which uses one of them.

## Learn more
- BusTub's [arc_replacer.h](https://github.com/cmu-db/bustub/blob/master/src/include/buffer/arc_replacer.h) and [tests](https://github.com/cmu-db/bustub/blob/master/test/buffer/arc_replacer_test.cpp) · [`Instant`](https://doc.rust-lang.org/std/time/struct.Instant.html)

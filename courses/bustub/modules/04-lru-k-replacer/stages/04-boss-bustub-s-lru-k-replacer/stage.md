**Where this fits.** BusTub's own sample test for LRU-K.

## The task

Nothing new. Run the ported `tests/lru_k_replacer_test.rs`. It walks the replacer through 6 frames, accesses, evictions, a non-evictable frame becoming evictable, a re-inserted frame, a failed eviction that must not change the size, and operations on a nonexistent frame.

| BusTub | here |
|---|---|
| `LRUKReplacerTest.SampleTest` | `lru_k_replacer_test::sample_test` |
| `ASSERT_EQ(2, lru_replacer.Evict())` | `assert_eq!(Some(FrameId(2)), lru_replacer.evict())` |
| `frame = lru_replacer.Evict(); ASSERT_EQ(false, frame.has_value());` | `assert_eq!(None, lru_replacer.evict())` |

## Tests

- `s1d_09_scans_do_not_flush_the_hot_pages`: a 4-frame pool driven by your replacer. Two hot pages, each used three times, then a scan of 20 cold pages: after the scan both hot pages are still resident. (Plain LRU would have lost them. This is the reason LRU-K exists.)
- BusTub's sample test.

## Syntax and methods

```rust
assert_eq!(Some(f(2)), lru_replacer.evict());
```

## Notes

If the sample test fails halfway, print the replacer's state at that line (add a temporary `eprintln!`): the comments in the C++ test name the expected order of frames at each step (`[3, 1, 5, 4]`). The model test of stage 6 is the better debugging tool: it tells you the first operation where you and the obviously-correct version disagree.

## In BusTub

```cpp
LRUKReplacer lru_replacer(7, 2);
lru_replacer.RecordAccess(1);  ... lru_replacer.SetEvictable(6, false);
ASSERT_EQ(5, lru_replacer.Size());
```

## The C/C++ way

| gtest | Rust |
|---|---|
| `std::optional<frame_id_t> frame; ... frame.has_value()` | `Option<FrameId>`; `is_some()` / `== None` |
| comparing an `optional` with `ASSERT_EQ(2, opt)` (the comment in the C++ test explains how `nullopt` compares) | `assert_eq!(Some(f(2)), opt)` compares like with like |
| `DISABLED_SampleTest` | enabled |

## Experiment

Optional. Predict first, then run it.

1. **What `k` trades.** In the scan test of stage 9 (two hot pages used three times, then a scan of 20 cold pages in a 4-frame pool), change `k` from 2 to 1 and then to 3. Predict, for each, whether the hot pages survive. What does a bigger `k` cost, and what would a scan of 3 accesses per page do?
2. **The scan, measured.** Count the frames the scan evicts that were hot, for `k = 1, 2, 3`. Then make the hot pages 5 instead of 2 in a 4-frame pool: what should happen, and why is that not the replacer's fault?

## What you built

LRU-K with a bounded access history, an exact tie-break, `remove`, and an O(log n) eviction order. Next module: **ARC**, the adaptive replacement cache, which BusTub's current Project 1 uses instead of LRU-K.

## Learn more
- BusTub's [lru_k_replacer.h](https://github.com/cmu-db/bustub/blob/master/src/include/buffer/lru_k_replacer.h) and [test](https://github.com/cmu-db/bustub/blob/master/test/buffer/lru_k_replacer_test.cpp)

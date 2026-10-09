**Where this fits.** BusTub's own sample tests for the simple replacers.

## The task

Nothing new to write. Run the two ported tests (`tests/lru_replacer_test.rs`, `tests/clock_replacer_test.rs`). Both unpin frames 1..6 and 1 again (size 6), take victims 1, 2, 3, pin 3 (a no-op) and 4, unpin 4, and expect victims 5, 6, 4.

| BusTub | here |
|---|---|
| `LRUReplacerTest.SampleTest` | `lru_replacer_test::sample_test` |
| `ClockReplacerTest.SampleTest` | `clock_replacer_test::sample_test` |

(In the C++ tests `Victim(&value)` returns `bool` and fills `value`; the port asserts on `Option<FrameId>`.)

## Tests

- `s1c_11_*`: both replacers behave identically on the BusTub scenario, and through the common `Replacer` trait.
- The two BusTub tests above.

## Syntax and methods

```rust
fn run(r: &mut dyn Replacer) { /* any replacer, picked at run time */ }
assert_eq!(Some(FrameId(1)), lru_replacer.victim());
```

## Notes

Two different policies give the *same* answers on this scenario because every frame is touched once, in order. They disagree as soon as frames are re-accessed unevenly: that is the next module (LRU-K), which is about exactly that.

## In BusTub

```cpp
LRUReplacer lru_replacer(7);
lru_replacer.Unpin(1); ... lru_replacer.Unpin(6); lru_replacer.Unpin(1);
EXPECT_EQ(6, lru_replacer.Size());
int value;  lru_replacer.Victim(&value);  EXPECT_EQ(1, value);
```

## The C/C++ way

| gtest | Rust |
|---|---|
| `EXPECT_EQ(6, lru_replacer.Size());` | `assert_eq!(6, lru_replacer.size());` |
| `int value; Victim(&value); EXPECT_EQ(1, value);` | `assert_eq!(Some(FrameId(1)), lru_replacer.victim());` |
| `DISABLED_SampleTest` (students enable it) | enabled |

## Experiment

Optional. Predict first, then run it.

1. **Find the difference.** The notes say the two policies disagree once frames are re-accessed unevenly. Write a randomised test that feeds the same random `unpin` / `pin` / `victim` sequence to both and prints the first sequence where they disagree. Before you run it: does such a sequence exist for the rules you implemented? Explain the smallest one you find.
2. **What the reference bit buys.** Which of the two does more work per `unpin`, and which per `victim`? Count the steps in each (a counter in your code is enough) over 100 000 random operations.

## What you built

A generational index list, an O(1) LRU replacer, and a CLOCK replacer. Next: **LRU-K**, the policy BusTub's buffer pool actually used for years, which fixes LRU's weakness against sequential scans.

## Learn more
- BusTub's [lru_replacer_test.cpp](https://github.com/cmu-db/bustub/blob/master/test/buffer/lru_replacer_test.cpp) and [clock_replacer_test.cpp](https://github.com/cmu-db/bustub/blob/master/test/buffer/clock_replacer_test.cpp)

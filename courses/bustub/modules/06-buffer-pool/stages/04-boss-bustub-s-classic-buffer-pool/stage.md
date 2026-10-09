**Where this fits.** The pool as a whole.

## The task

Nothing new. Run BusTub's earlier buffer pool tests, adapted to this module's interface (`new_page` hands out an id; `fetch_page` pins), in `tests/buffer_pool_manager_classic_test.rs`, and the stress test.

| BusTub (`buffer_pool_manager_instance_test.cpp`) | here | checks |
|---|---|---|
| `BinaryDataTest` | `binary_data_test` | random bytes **with zeros in the middle and at the end** survive a round trip through eviction (a C string function would cut them short) |
| `SampleTest` | `sample_test` | fill the pool, refuse the next page, unpin five, bring in four more, page 0 still has "Hello" |

BusTub's *current* tests (`VeryBasicTest`, `PagePinEasyTest`, ...) use page guards; they are the boss of the next module.

## Tests

- `s1f_10_threads_share_a_small_pool_without_losing_updates`: 8 threads each do 300 increments on random pages out of 40, through a pool of 12 frames. An increment is fetch, change under the frame's write latch, `unpin(dirty)`. At the end every page holds exactly the number of increments applied to it: nothing lost to eviction, write-back, or a race.
- The two classic tests.

## Syntax and methods

```rust
let mut data = bpm.frame_data(frame).write().unwrap();      // the frame's write latch: one writer at a time
let n = u32::from_le_bytes(data[..4].try_into().unwrap()) + 1;   // &[u8] -> [u8; 4] with try_into
data[..4].copy_from_slice(&n.to_le_bytes());
```

## Notes

If the stress test loses an update, the usual suspects: an unpin that forgot the dirty flag; a victim whose write-back happened *after* its frame was handed to another page; a pin count changed outside the lock. Add `eprintln!`s of (page, frame, pin count) at fetch/unpin/evict and look at one page's life.

**What is still serialised.** Every fetch miss holds the pool lock for the whole disk read. With a 10 ms disk, 8 threads missing at once take 80 ms, not 10. Fixing that needs a per-frame "loading" state; it is the hard extension of this module (see the board).

## In BusTub

```cpp
// BinaryDataTest
char random_binary_data[BUSTUB_PAGE_SIZE];  /* fill with std::uniform_int_distribution<char> */
random_binary_data[BUSTUB_PAGE_SIZE / 2] = '\0';  random_binary_data[BUSTUB_PAGE_SIZE - 1] = '\0';
std::strncpy(page0->GetData(), random_binary_data, BUSTUB_PAGE_SIZE);   // the old test used strncpy: it stops at the first '\0'
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `strncpy` / `strcmp` stop at `'\0'`: binary data silently truncated | `copy_from_slice` / `==` on byte arrays: lengths and every byte matter |
| `std::uniform_int_distribution<char>` seeded from `std::random_device` | a small LCG with a fixed seed: reproducible failures |
| `EXPECT_NE(nullptr, bpm->NewPage(&id))` | `assert!(bpm.fetch_page(..).is_some())` |
| `delete bpm; delete disk_manager;` at the end | `Drop` |

## Experiment

Optional. Predict first, then run it.

1. **Count the disk.** In `sample_test`, read the disk manager's counters (`num_writes`, and a read counter if you add one) before and after. Predict how many writes the test causes, then check. Which pages are written, and why those?
2. **Swap the policy.** Run the same workload with your LRU replacer and with LRU-K (`k = 2`) behind the buffer pool. Which writes fewer pages? Build a workload that makes the other one win.

## What you built

A buffer pool: pin counts, a page table, free frames, eviction through a replacer you wrote, write-back of dirty pages, flush and delete. It is the layer every later module sits on. Next: **page guards**, which make pinning and latching impossible to forget.

## Learn more
- BusTub's [buffer_pool_manager.cpp](https://github.com/cmu-db/bustub/blob/master/src/buffer/buffer_pool_manager.cpp) and the [Project 1 page](https://15445.courses.cs.cmu.edu/fall2026/project1/) · [`TryInto`](https://doc.rust-lang.org/std/convert/trait.TryInto.html)

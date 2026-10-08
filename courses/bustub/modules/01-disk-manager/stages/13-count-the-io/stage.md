**Where this fits.** Later modules assert how many writes happened ("the buffer pool wrote the dirty page exactly once"). The disk manager keeps the count.

## The task

Three counters (`num_writes`, `num_deletes`, `num_flushes`) live outside the mutex as `AtomicUsize`. In `src/storage/disk/disk_manager.rs`:
- count a write in `write_page` (every call, rewrites included) and a delete in `delete_page` (only when the page existed);
- fill in the getters `get_num_writes`, `get_num_deletes`, `get_num_flushes`. (Flushes are counted by the log, stage 14.)

## Tests

- All three start at 0. Two writes to page 0 and one to page 1 make 3 writes. Reads don't count.
- Of three `delete_page` calls (one real, one repeat, one unknown) only one counts.
- Eight threads writing 50 pages each make exactly 400.

## Syntax and methods

```rust
use std::sync::atomic::{AtomicUsize, Ordering};

let n = AtomicUsize::new(0);          // not `mut`: atomics change through &self
n.fetch_add(1, Ordering::Relaxed);    // one indivisible increment; returns the old value
n.load(Ordering::Relaxed)             // the current value
```

## Notes

Why not put the counters in `DbIo`? So that anyone can read them without the file lock, and so incrementing from many threads can never race. `Ordering::Relaxed` means "this number must be right, but I don't need it to order any other memory": exactly right for a statistic. (`Acquire`/`Release` come later, in the lock-free structures.)

## In BusTub

```cpp
num_writes_ += 1;                                           // a plain int, bumped under db_io_latch_
auto DiskManager::GetNumWrites() const -> int { return num_writes_; }   // read with no lock: a data race
```

## The C/C++ way
| C / C++ | Rust |
|---|---|
| `int num_writes_; num_writes_ += 1;` from many threads: a **data race, undefined behaviour** | `AtomicUsize::fetch_add`, or increment under the mutex |
| `std::atomic<int> n; n.fetch_add(1);` defaults to `memory_order_seq_cst` (the strongest, slowest) | the ordering is always spelled out: `Ordering::Relaxed` for a statistic |
| C11 `<stdatomic.h>`: `atomic_fetch_add_explicit(&n, 1, memory_order_relaxed)` | same operation, same ordering names |
| `memory_order_relaxed / acquire / release / acq_rel / seq_cst` | `Ordering::Relaxed / Acquire / Release / AcqRel / SeqCst` (no `consume`) |
| a getter that reads a plain int without the lock (BusTub's `GetNumWrites`) | `load(Relaxed)`: a defined, race-free read |

**Port rule:** every shared counter that C++ wrote as a plain `int` and "protected by convention" is either `Atomic*` or inside the `Mutex`. Pick `Relaxed` only when the number does not order other memory.

## Learn more
- [`AtomicUsize`](https://doc.rust-lang.org/std/sync/atomic/struct.AtomicUsize.html) · [`Ordering`](https://doc.rust-lang.org/std/sync/atomic/enum.Ordering.html)

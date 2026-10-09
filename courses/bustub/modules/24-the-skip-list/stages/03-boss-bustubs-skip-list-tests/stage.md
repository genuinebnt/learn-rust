BusTub's skip list tests, ported: insert/contains/clear, and the four concurrent tests: ten threads inserting disjoint ranges, ten erasing, a mix of both, and eight readers walking a list of 80 000 keys at once.

## The task

Make the stage's tests pass: `cargo test --test stages_0b s0b_03`.

## Tests

- `s0b_03_insert_contains_clear`.
- `s0b_03_concurrent_insert`, `s0b_03_concurrent_erase`, `s0b_03_concurrent_insert_and_erase`: exact counts of successful operations and the final contents.
- `s0b_03_readers_share_the_list`: eight readers over 80 000 keys.
- `s0b_03_a_big_list_is_dropped_without_overflowing_the_stack`.

## Notes

**Readers must share.** `contains` takes the **read** lock; if it took the write lock, eight readers would take turns and BusTub's test would time out ("`You will see a timeout if your reads cannot share access to the skip list`").

**What a race looks like here.** A lost insert (fewer successes than threads × keys), a key present after its erase, or a panic from an out-of-range link: all mean two threads were inside a write at once, or a read overlapped a write. With one `RwLock` around everything that cannot happen unless a method forgets its lock.

**Memory.** The big-list drop test builds 200 000 nodes; in C++ this is the case the iterative `Drop` exists for. An arena is dropped without recursion.

## In BusTub

`test/primer/skiplist_test.cpp`: `InsertContainsTest1`, `ConcurrentInsertTest`, `ConcurrentEraseTest`, `ConcurrentInsertAndEraseTest`, `ConcurrentReadTest`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::atomic<int> successful_insertions` | `Arc<AtomicUsize>` |
| `std::thread` with a lambda capturing by reference | `thread::spawn(move || ...)` with a cloned `Arc` |

**Port rule:** threads cannot borrow locals in Rust (without scoped threads), so shared state is an `Arc`.

## Learn more
- [`std::thread::scope`](https://doc.rust-lang.org/std/thread/fn.scope.html) · [`AtomicUsize`](https://doc.rust-lang.org/std/sync/atomic/index.html)

## Performance

Reads scale with the number of cores (shared lock); writes serialise. A list that is mostly read can use a single `RwLock`; a write-heavy one needs finer locking (per-node, or lock-free like LevelDB's memtable), which is beyond this exercise.

**Measure it.** Time the eight-reader test with the read lock and with a `Mutex` instead: the mutex version takes several times longer.

## Hints

### Take the lock inside each public method

`insert`, `erase`, `contains`, `size`, `clear` each take their own guard; do not call one public method from another while holding a guard (a read guard then write lock on the same thread deadlocks).

### A failing concurrent test: shrink it

Two threads and ten keys reproduce most races with a readable failure.

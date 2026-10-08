**Where this fits.** A new page needs a place to live. The allocator decides which slot.

## The task

`DbIo` (given, in `src/storage/disk/disk_manager.rs`) is everything the db file's lock protects: the file, the page table, the free list and two counters. The disk manager keeps it in a `Mutex<DbIo>`, so one thread at a time touches any of it.

Implement the first part of `DbIo::allocate_slot`: always take a fresh slot at the end. `num_slots` counts how many have been handed out, so the next fresh slot **is** `num_slots`; hand it out and move the counter on. (Stages 11 and 12 add growing the file and reusing freed slots to this same function; the stub marks the places.) `DiskManager::allocate_slot` is given: it takes the lock and calls yours.

## Tests

- The first slot is `0`; slots then count up with no gaps and no repeats.
- Four threads allocating 25 slots each get exactly `0..100` between them.

## Syntax and methods

```rust
let mut io = self.db_io.lock().unwrap();   // MutexGuard<DbIo>: derefs to DbIo; the lock is released when `io` is dropped
self.num_slots += 1;                       // inside `impl DbIo`, `self` is &mut DbIo
```

## Notes

`lock()` returns a `Result`: if a thread panicked while holding the lock it is *poisoned*, and `unwrap()` passes that panic on. The threads test only passes because the counter lives **inside** the mutex.

## In BusTub

```cpp
return pages_.size() * BUSTUB_PAGE_SIZE;   // derived from the page table's size; here it's an explicit counter
```

## The C/C++ way
| C / C++ | Rust |
|---|---|
| `pthread_mutex_t m; pthread_mutex_lock(&m); ... pthread_mutex_unlock(&m);` | `let g = m.lock().unwrap();` unlocks when `g` goes out of scope |
| `std::mutex m; std::scoped_lock l(m);` / `std::lock_guard` | `Mutex<T>` + `MutexGuard<T>` |
| the mutex and the data it protects are separate members; "protects" is a comment | `Mutex<DbIo>` **owns** the data: no lock, no access |
| forget to unlock on an early `return` / exception (C), or lock the wrong mutex (C++) | not expressible: the guard unlocks in `Drop`; there is only one mutex to lock |
| `std::atomic<size_t> next{0}; next.fetch_add(1)` for a counter | an `AtomicUsize`, or a plain field inside the `Mutex` (this stage) |

**Port rule:** a C++ class with `mutex_` + several fields it guards becomes `Mutex<Inner>` with those fields in `Inner`. In BusTub this is `db_io_latch_` + `pages_` + `free_slots_` → `Mutex<DbIo>`.

## Learn more
- [`Mutex`](https://doc.rust-lang.org/std/sync/struct.Mutex.html) · The Rust Book: [shared-state concurrency](https://doc.rust-lang.org/book/ch16-03-shared-state.html)

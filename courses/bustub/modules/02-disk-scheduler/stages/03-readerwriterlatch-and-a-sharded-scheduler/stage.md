This stage has 2 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · ReaderWriterLatch: many readers or one writer

**Where this fits.** The buffer pool and every index page will be protected by reader-writer latches. BusTub wraps `std::shared_mutex` in a tiny class; here is the Rust version.

### The task

In `src/common/rwlatch.rs`, `ReaderWriterLatch<T>` (a wrapper around `std::sync::RwLock<T>`): implement `read()` and `write()`. Each returns the guard; the latch is released when the guard is dropped. A **poisoned** lock (a thread panicked while holding it) must still hand out its guard.

### Tests

- `write()` changes the value, `read()` sees it.
- Four readers hold read latches at the same time (they wait for each other on a `Barrier`: only possible if reads overlap).
- Eight writers each add 1000 times: the total is exactly 8000. A writer waits while a reader holds the latch.
- After a thread panics holding the write latch, other threads can still read and write.

### Syntax and methods

```rust
self.inner.read().unwrap_or_else(PoisonError::into_inner)    // LockResult -> guard, poisoned or not
self.inner.write().unwrap_or_else(PoisonError::into_inner)
*latch.write() += 1;                                          // the guard derefs to T; the latch is released at the end of the statement
```

### Notes

**Poisoning.** std locks remember when a holder panicked and make later `lock()` calls return `Err(PoisonError)`: a warning that the protected data may be half-updated. BusTub's C++ latches have no such concept, and its tests expect plain locking, so this latch ignores the warning (`into_inner` gives the guard back). That is a *choice* with a price: if an update can leave the data inconsistent, don't ignore poison. Rust's other answer is `parking_lot`, whose locks never poison.

### In BusTub

```cpp
class ReaderWriterLatch {
 public:
  void WLock()   { mutex_.lock(); }
  void WUnlock() { mutex_.unlock(); }
  void RLock()   { mutex_.lock_shared(); }
  void RUnlock() { mutex_.unlock_shared(); }
 private:
  std::shared_mutex mutex_;
};
```

### The C/C++ way

| C (POSIX) | C++ | Rust |
|---|---|---|
| `pthread_rwlock_rdlock(&l)` / `_wrlock` / `_unlock` | `lock_shared()` / `lock()` / `unlock_shared()` / `unlock()` called by hand | `read()` / `write()` return a guard; `Drop` unlocks |
| unlock on every exit path by hand | `std::shared_lock<std::shared_mutex>` / `std::unique_lock` / `lock_guard` (RAII) | the guard is the only way: no unlock call exists |
| the lock and the data are separate; "which lock protects this?" is a comment | same | `RwLock<T>` **contains** the `T` |
| unlock twice, or unlock a lock you don't hold: undefined behaviour | same | not expressible |

**Port rule:** a C++ class with manual `Lock()/Unlock()` pairs becomes a type that returns guards. If callers *must* lock in one function and unlock in another (BusTub's page latches in the B+ tree crabbing code), the guard is stored in a struct and moved (stages in module 1e and 2c).

### Learn more
- [`RwLock`](https://doc.rust-lang.org/std/sync/struct.RwLock.html) · [poisoning](https://doc.rust-lang.org/std/sync/struct.RwLock.html#poisoning) · [`Barrier`](https://doc.rust-lang.org/std/sync/struct.Barrier.html) · [`parking_lot`](https://docs.rs/parking_lot)
- C++ [`std::shared_mutex`](https://en.cppreference.com/w/cpp/thread/shared_mutex) · [pthread_rwlock_rdlock(3p)](https://man7.org/linux/man-pages/man3/pthread_rwlock_rdlock.3p.html)
- *Rust Atomics and Locks*, [Building our own locks](https://marabos.nl/atomics/building-locks.html)

## Part 2 · ShardedDiskScheduler: several workers, per-page order

**Where this fits.** One worker runs one request at a time. A real disk (an SSD) can serve many requests at once. More workers help, but they can't be allowed to reorder two requests for the *same page*.

### The task

In `src/storage/disk/disk_scheduler.rs`, `ShardedDiskScheduler` (a second scheduler, same request type, same `execute`):
- `new(disk, workers)`: one queue and one worker thread per worker (`workers` ≥ 1: panic with a message containing "at least one worker" for 0);
- `schedule(requests)`: send each request to the queue of its page's shard, `page_id mod workers`;
- `Drop`: stop and join every worker, after they finish what is queued.

### Tests

- 10 write/read pairs on one page, interleaved with other work: each read sees the write before it.
- 30 pages, each written and read back, on 3 workers.
- Eight 40 ms writes on four different pages take well under the 320 ms one worker needs (the workers overlap).
- Dropping with 40 queued writes: all 40 happen; every worker has ended. One worker works like `DiskScheduler`.

### Syntax and methods

```rust
request.page_id.0.rem_euclid(n as i32) as usize     // always 0..n, even for negative ids (% would give a negative remainder)
self.queues[shard].put(Some(request));
for worker in self.workers.drain(..) { let _ = worker.join(); }   // drain(..) moves every handle out of the Vec in place
```

### Notes

The invariant is *per-page FIFO*. Requests for the same page always take the same queue, so they run in the order scheduled; requests for different pages may run in any order and in parallel. This is how real systems keep a file system's or database's ordering guarantees while still using the device's parallelism. The buffer pool never has two requests for the same page in flight in conflicting ways except through this ordering, so it needs nothing more.

### In BusTub

BusTub's scheduler has exactly one worker. The leaderboard (extra credit) asks students to make disk access parallel; this stage is one way to do it.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `page_id % n` with a negative `page_id` is negative in C/C++ (truncating division): an out-of-bounds index | `rem_euclid` (always non-negative); or use unsigned ids |
| `std::vector<std::thread>`; `for (auto &t : workers) t.join();` | `Vec<JoinHandle<()>>`; `for w in workers.drain(..) { w.join() }` |
| `std::vector<Channel<...>>` needs `Channel` to be movable (it holds a mutex: it isn't), so people use `unique_ptr<Channel>` | `Vec<Arc<Channel<..>>>`: the `Arc` is shared with the worker anyway |
| thread-per-shard routing by hash (`std::hash<page_id_t>`) | same idea; `hash % n` or `% n` of the id |

**Port rule:** `%` on signed integers is a remainder with the dividend's sign in C/C++ *and* in Rust; Rust's `rem_euclid` is what you wanted. Checked at the type level it'd be `u32` ids.

### Learn more
- [`i32::rem_euclid`](https://doc.rust-lang.org/std/primitive.i32.html#method.rem_euclid) · [`Vec::drain`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.drain)
- [I/O scheduling](https://en.wikipedia.org/wiki/I/O_scheduling) · [`threadpool`](https://docs.rs/threadpool) and [`rayon`](https://docs.rs/rayon): what ready-made pools look like

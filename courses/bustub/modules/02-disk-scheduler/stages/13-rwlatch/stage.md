**Where this fits.** The buffer pool and every index page will be protected by reader-writer latches. BusTub wraps `std::shared_mutex` in a tiny class; here is the Rust version.

## The task

In `src/common/rwlatch.rs`, `ReaderWriterLatch<T>` (a wrapper around `std::sync::RwLock<T>`): implement `read()` and `write()`. Each returns the guard; the latch is released when the guard is dropped. A **poisoned** lock (a thread panicked while holding it) must still hand out its guard.

## Tests

- `write()` changes the value, `read()` sees it.
- Four readers hold read latches at the same time (they wait for each other on a `Barrier`: only possible if reads overlap).
- Eight writers each add 1000 times: the total is exactly 8000. A writer waits while a reader holds the latch.
- After a thread panics holding the write latch, other threads can still read and write.

## Syntax and methods

```rust
self.inner.read().unwrap_or_else(PoisonError::into_inner)    // LockResult -> guard, poisoned or not
self.inner.write().unwrap_or_else(PoisonError::into_inner)
*latch.write() += 1;                                          // the guard derefs to T; the latch is released at the end of the statement
```

## Notes

**Poisoning.** std locks remember when a holder panicked and make later `lock()` calls return `Err(PoisonError)`: a warning that the protected data may be half-updated. BusTub's C++ latches have no such concept, and its tests expect plain locking, so this latch ignores the warning (`into_inner` gives the guard back). That is a *choice* with a price: if an update can leave the data inconsistent, don't ignore poison. Rust's other answer is `parking_lot`, whose locks never poison.

## In BusTub

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

## The C/C++ way

| C (POSIX) | C++ | Rust |
|---|---|---|
| `pthread_rwlock_rdlock(&l)` / `_wrlock` / `_unlock` | `lock_shared()` / `lock()` / `unlock_shared()` / `unlock()` called by hand | `read()` / `write()` return a guard; `Drop` unlocks |
| unlock on every exit path by hand | `std::shared_lock<std::shared_mutex>` / `std::unique_lock` / `lock_guard` (RAII) | the guard is the only way: no unlock call exists |
| the lock and the data are separate; "which lock protects this?" is a comment | same | `RwLock<T>` **contains** the `T` |
| unlock twice, or unlock a lock you don't hold: undefined behaviour | same | not expressible |

**Port rule:** a C++ class with manual `Lock()/Unlock()` pairs becomes a type that returns guards. If callers *must* lock in one function and unlock in another (BusTub's page latches in the B+ tree crabbing code), the guard is stored in a struct and moved (stages in module 1e and 2c).

## Learn more
- [`RwLock`](https://doc.rust-lang.org/std/sync/struct.RwLock.html) · [poisoning](https://doc.rust-lang.org/std/sync/struct.RwLock.html#poisoning) · [`Barrier`](https://doc.rust-lang.org/std/sync/struct.Barrier.html) · [`parking_lot`](https://docs.rs/parking_lot)
- C++ [`std::shared_mutex`](https://en.cppreference.com/w/cpp/thread/shared_mutex) · [pthread_rwlock_rdlock(3p)](https://man7.org/linux/man-pages/man3/pthread_rwlock_rdlock.3p.html)
- *Rust Atomics and Locks*, [Building our own locks](https://marabos.nl/atomics/building-locks.html)

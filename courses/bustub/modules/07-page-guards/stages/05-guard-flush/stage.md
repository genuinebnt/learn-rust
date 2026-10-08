**Where this fits.** A guard that holds a page often wants it on disk *now* (a checkpoint, the end of a build step) without letting go.

## The task

- In `src/buffer/buffer_pool_manager.rs`: `write_page_data(page_id, data)`: copy the bytes into a `Box`, schedule a write on the disk scheduler, wait for it. No pool lock, no frame latch.
- In `src/storage/page/page_guard.rs`: `flush()` on both guards: write the bytes **the guard already holds** with `write_page_data`; for the write guard, the page is now clean (`is_dirty()` false). The guard keeps its pin and its latch.

## Tests

- A write guard flushes: the disk has the bytes, `is_dirty()` is false, the pin count stays 1. A clean guard flushes too. A read guard can flush.
- Flushing while holding the latch does not hang (a thread with a timeout checks).

## Syntax and methods

```rust
let data: PageData = *self.get_data();        // copy the 8 KiB out of the latch you hold (arrays of Copy types are Copy)
self.bpm.write_page_data(self.page_id, &data);
```

## Notes

**Why not just call `flush_page`?** `flush_page` takes the frame's *read* latch to copy the bytes. A write guard already holds the *write* latch of the same lock: `RwLock` isn't reentrant, so the same thread waiting for it **deadlocks with itself**. (A read guard re-taking a read latch can also hang when a writer is queued in between: std's `RwLock` may block new readers behind a waiting writer.) So the guard uses the bytes it already has. General rule: **a function that locks must not be called by code that already holds the lock**; give it a variant that takes the data (`write_page_data`).

## In BusTub

```cpp
void WritePageGuard::Flush() {
  // writes frame_->GetData() through disk_scheduler_ and clears frame_->is_dirty_
}
```

(C++ `std::shared_mutex` has the same self-deadlock rules; BusTub's guard flushes through its own `disk_scheduler_` pointer, which is why the guard keeps a `shared_ptr<DiskScheduler>`.)

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::shared_ptr<DiskScheduler>` in every guard to flush | the guard borrows the pool; the pool owns the scheduler |
| `std::memcpy(buf, frame->GetData(), BUSTUB_PAGE_SIZE)` | `*self.get_data()` copies an array by value |
| re-locking a non-recursive `std::mutex`/`shared_mutex` on the same thread: undefined behaviour in C++ | deadlock or panic in Rust's std locks (documented as unspecified): never rely on either |

## Learn more
- [`RwLock`: "this function might panic or deadlock if the current thread already holds the lock"](https://doc.rust-lang.org/std/sync/struct.RwLock.html#method.read) · [Self-deadlock](https://en.wikipedia.org/wiki/Deadlock)

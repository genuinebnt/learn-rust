This stage has 3 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · read_page and write_page: panic when there is no room

**Where this fits.** Most callers (an index, a table heap) have already made sure there is room: running out of frames is a bug for them, not a case to handle.

### The task

In `src/buffer/buffer_pool_manager.rs`: `read_page(page_id)` and `write_page(page_id)` do what `checked_read_page` / `checked_write_page` do, but return the guard itself and **panic** (message containing "every frame is pinned") if the page can't be brought in.

### Tests

- With room, both return a guard (two guards on the same page give pin count 2).
- In a one-frame pool with the frame pinned, both panic with the message.

### Syntax and methods

```rust
self.checked_read_page(page_id).expect("every frame is pinned: no room to bring the page into memory")
```

### Notes

**Two APIs, one meaning.** `Option` for "the caller can recover" and a panic for "the caller can't": BusTub has both (`CheckedReadPage`/`ReadPage`) because C++ code often wraps the former in a throwing check. In Rust, the convention is `try_*`/`checked_*` returning `Option`/`Result` and the plain name panicking (compare `Vec::get` and indexing, `checked_add` and `+`).

### In BusTub

```cpp
auto BufferPoolManager::ReadPage(page_id_t page_id, AccessType access_type) -> ReadPageGuard {
  auto guard_opt = CheckedReadPage(page_id, access_type);
  if (!guard_opt.has_value()) { fmt::println(stderr, "\n`CheckedReadPage` failed to bring in page {}\n", page_id); std::abort(); }
  return std::move(guard_opt).value();
}
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::abort()` after printing to stderr | `panic!` / `expect`: unwinds (running destructors, poisoning locks) instead of killing the process |
| `std::move(guard_opt).value()` | `.expect(..)` / `.unwrap()` moves the guard out |
| `fmt::println(stderr, ...)` | the panic message |

**Port rule:** `abort()` on an impossible condition is `panic!`/`unwrap`/`expect`; use `process::abort()` only when unwinding itself would be unsafe.

### Learn more
- The Rust Book: [`unwrap` and `expect`](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#shortcuts-for-panic-on-error-unwrap-and-expect) · [`Option::expect`](https://doc.rust-lang.org/std/option/enum.Option.html#method.expect)

## Part 2 · flush() through a guard

**Where this fits.** A guard that holds a page often wants it on disk *now* (a checkpoint, the end of a build step) without letting go.

### The task

- In `src/buffer/buffer_pool_manager.rs`: `write_page_data(page_id, data)`: copy the bytes into a `Box`, schedule a write on the disk scheduler, wait for it. No pool lock, no frame latch.
- In `src/storage/page/page_guard.rs`: `flush()` on both guards: write the bytes **the guard already holds** with `write_page_data`; for the write guard, the page is now clean (`is_dirty()` false). The guard keeps its pin and its latch.

### Tests

- A write guard flushes: the disk has the bytes, `is_dirty()` is false, the pin count stays 1. A clean guard flushes too. A read guard can flush.
- Flushing while holding the latch does not hang (a thread with a timeout checks).

### Syntax and methods

```rust
let data: PageData = *self.get_data();        // copy the 8 KiB out of the latch you hold (arrays of Copy types are Copy)
self.bpm.write_page_data(self.page_id, &data);
```

### Notes

**Why not just call `flush_page`?** `flush_page` takes the frame's *read* latch to copy the bytes. A write guard already holds the *write* latch of the same lock: `RwLock` isn't reentrant, so the same thread waiting for it **deadlocks with itself**. (A read guard re-taking a read latch can also hang when a writer is queued in between: std's `RwLock` may block new readers behind a waiting writer.) So the guard uses the bytes it already has. General rule: **a function that locks must not be called by code that already holds the lock**; give it a variant that takes the data (`write_page_data`).

### In BusTub

```cpp
void WritePageGuard::Flush() {
  // writes frame_->GetData() through disk_scheduler_ and clears frame_->is_dirty_
}
```

(C++ `std::shared_mutex` has the same self-deadlock rules; BusTub's guard flushes through its own `disk_scheduler_` pointer, which is why the guard keeps a `shared_ptr<DiskScheduler>`.)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::shared_ptr<DiskScheduler>` in every guard to flush | the guard borrows the pool; the pool owns the scheduler |
| `std::memcpy(buf, frame->GetData(), BUSTUB_PAGE_SIZE)` | `*self.get_data()` copies an array by value |
| re-locking a non-recursive `std::mutex`/`shared_mutex` on the same thread: undefined behaviour in C++ | deadlock or panic in Rust's std locks (documented as unspecified): never rely on either |

### Learn more
- [`RwLock`: "this function might panic or deadlock if the current thread already holds the lock"](https://doc.rust-lang.org/std/sync/struct.RwLock.html#method.read) · [Self-deadlock](https://en.wikipedia.org/wiki/Deadlock)

## Part 3 · A flush must not wait for a latch while holding the pool's lock

**Where this fits.** The lesson of BusTub's `DeadlockTest`, in the place where it's easiest to get wrong: your own `flush_page` from module 1f.

### The scenario

Thread W holds the **write guard** on page P. Thread F calls `flush_page(P)`. Your 1f version takes the pool's lock, then asks for P's frame latch to copy the bytes. W holds that latch, so F waits **holding the pool lock**. Now W calls `write_page(Q)`, which needs the pool lock. W waits for F; F waits for W. **Deadlock.** (This is exactly what the C++ test's comment says: "Think about what might happen if you hold a certain 'all-encompassing' latch for too long...")

### The task

Rewrite `flush_page` in `src/buffer/buffer_pool_manager.rs` so that it never waits for a frame latch while holding the pool lock:
1. under the lock: find the frame (return `false` if the page isn't resident), **pin** it (so it can't be evicted meanwhile), mark it not evictable, clear its dirty flag; **release the lock**;
2. take the frame's **read latch** (this may wait, and that's fine now), copy the bytes, release the latch;
3. write the copy with `write_page_data`;
4. `unpin_page(page_id, false)`; return `true`.

### Tests

- The deadlock scenario above, with a 10-second watchdog: W holds P, F flushes P, W takes Q, W releases P, F completes and returns `true`.
- `flush_page` still writes the latest bytes and leaves the pin count where it found it; a flushed page can be evicted afterwards.

### Syntax and methods

```rust
let frame = {
    let mut inner = self.inner.lock().unwrap();     // lock in an inner block: the guard is dropped at the closing brace
    let Some(&frame) = inner.page_table.get(&page_id) else { return false };
    inner.meta[frame.0].pin_count += 1;
    inner.replacer.set_evictable(frame, false);
    frame
};
```

### Notes

**The rule: never block while holding the lock that everyone else needs.** Waiting on another lock, on the disk, on a channel, on a condition variable that someone needs this lock to signal. Do the cheap bookkeeping under the lock, record what you need (a pin), let go, then wait. The pin is what makes this safe: it is your reservation on the frame while you aren't holding the lock.

Look for the same shape in `delete_page` (it waits for nothing: the page is unpinned, so no latch holder can exist) and `fetch_page`'s miss path (it holds the pool lock across the disk read: slow, but no cycle, because the disk doesn't need the pool lock; making it fast is the hard extension on the board).

**Lock ordering** is the general cure: if every thread takes locks in one global order (here: the pool lock is *always* taken without any frame latch held by the same thread, and frame latches are taken without the pool lock), cycles can't form.

### In BusTub

```cpp
// DeadlockTest: main holds WritePage(pid0); a child blocks on WritePage(pid0); main then takes WritePage(pid1) -- which needs bpm_latch_.
// "If your latching mechanism is incorrect, the next line of code will deadlock."
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::scoped_lock` for the whole function body, "just to be safe" | a small block `{ let guard = lock(); ...; value }` so the guard dies early |
| `std::unique_lock::unlock()` / `lock()` to release and retake in the middle | drop the guard (`drop(guard)`), later lock again |
| `std::lock(m1, m2)` / `std::scoped_lock(m1, m2)` (deadlock-avoiding multi-lock) | no std equivalent; fix an order, or use `parking_lot`'s `deadlock_detection` feature in debug builds |
| ThreadSanitizer, `helgrind`: detect lock-order inversions at run time | Rust prevents data races, not deadlocks; `loom` explores interleavings, `parking_lot::deadlock` finds cycles |

**Port rule:** C++ code that does I/O, waits, or calls unknown callbacks inside a `scoped_lock` is a deadlock waiting to happen: restructure to do that outside the critical section.

### Learn more
- *Rust Atomics and Locks*, [locks and deadlock](https://marabos.nl/atomics/building-locks.html) · [`loom`](https://github.com/tokio-rs/loom) (exhaustive interleaving tests) · [`parking_lot::deadlock`](https://docs.rs/parking_lot/latest/parking_lot/deadlock/index.html)
- Coffman conditions: [Deadlock](https://en.wikipedia.org/wiki/Deadlock#Necessary_conditions) · CMU 15-445 "Index Concurrency Control" (latch crabbing: the same discipline, applied to trees)

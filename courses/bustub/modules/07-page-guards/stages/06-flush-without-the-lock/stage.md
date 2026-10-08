**Where this fits.** The lesson of BusTub's `DeadlockTest`, in the place where it's easiest to get wrong: your own `flush_page` from module 1f.

## The scenario

Thread W holds the **write guard** on page P. Thread F calls `flush_page(P)`. Your 1f version takes the pool's lock, then asks for P's frame latch to copy the bytes. W holds that latch, so F waits **holding the pool lock**. Now W calls `write_page(Q)`, which needs the pool lock. W waits for F; F waits for W. **Deadlock.** (This is exactly what the C++ test's comment says: "Think about what might happen if you hold a certain 'all-encompassing' latch for too long...")

## The task

Rewrite `flush_page` in `src/buffer/buffer_pool_manager.rs` so that it never waits for a frame latch while holding the pool lock:
1. under the lock: find the frame (return `false` if the page isn't resident), **pin** it (so it can't be evicted meanwhile), mark it not evictable, clear its dirty flag; **release the lock**;
2. take the frame's **read latch** (this may wait, and that's fine now), copy the bytes, release the latch;
3. write the copy with `write_page_data`;
4. `unpin_page(page_id, false)`; return `true`.

## Tests

- The deadlock scenario above, with a 10-second watchdog: W holds P, F flushes P, W takes Q, W releases P, F completes and returns `true`.
- `flush_page` still writes the latest bytes and leaves the pin count where it found it; a flushed page can be evicted afterwards.

## Syntax and methods

```rust
let frame = {
    let mut inner = self.inner.lock().unwrap();     // lock in an inner block: the guard is dropped at the closing brace
    let Some(&frame) = inner.page_table.get(&page_id) else { return false };
    inner.meta[frame.0].pin_count += 1;
    inner.replacer.set_evictable(frame, false);
    frame
};
```

## Notes

**The rule: never block while holding the lock that everyone else needs.** Waiting on another lock, on the disk, on a channel, on a condition variable that someone needs this lock to signal. Do the cheap bookkeeping under the lock, record what you need (a pin), let go, then wait. The pin is what makes this safe: it is your reservation on the frame while you aren't holding the lock.

Look for the same shape in `delete_page` (it waits for nothing: the page is unpinned, so no latch holder can exist) and `fetch_page`'s miss path (it holds the pool lock across the disk read: slow, but no cycle, because the disk doesn't need the pool lock; making it fast is the hard extension on the board).

**Lock ordering** is the general cure: if every thread takes locks in one global order (here: the pool lock is *always* taken without any frame latch held by the same thread, and frame latches are taken without the pool lock), cycles can't form.

## In BusTub

```cpp
// DeadlockTest: main holds WritePage(pid0); a child blocks on WritePage(pid0); main then takes WritePage(pid1) -- which needs bpm_latch_.
// "If your latching mechanism is incorrect, the next line of code will deadlock."
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::scoped_lock` for the whole function body, "just to be safe" | a small block `{ let guard = lock(); ...; value }` so the guard dies early |
| `std::unique_lock::unlock()` / `lock()` to release and retake in the middle | drop the guard (`drop(guard)`), later lock again |
| `std::lock(m1, m2)` / `std::scoped_lock(m1, m2)` (deadlock-avoiding multi-lock) | no std equivalent; fix an order, or use `parking_lot`'s `deadlock_detection` feature in debug builds |
| ThreadSanitizer, `helgrind`: detect lock-order inversions at run time | Rust prevents data races, not deadlocks; `loom` explores interleavings, `parking_lot::deadlock` finds cycles |

**Port rule:** C++ code that does I/O, waits, or calls unknown callbacks inside a `scoped_lock` is a deadlock waiting to happen: restructure to do that outside the critical section.

## Learn more
- *Rust Atomics and Locks*, [locks and deadlock](https://marabos.nl/atomics/building-locks.html) · [`loom`](https://github.com/tokio-rs/loom) (exhaustive interleaving tests) · [`parking_lot::deadlock`](https://docs.rs/parking_lot/latest/parking_lot/deadlock/index.html)
- Coffman conditions: [Deadlock](https://en.wikipedia.org/wiki/Deadlock#Necessary_conditions) · CMU 15-445 "Index Concurrency Control" (latch crabbing: the same discipline, applied to trees)

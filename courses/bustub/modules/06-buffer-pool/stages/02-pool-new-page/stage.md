**Where this fits.** Pages need names before they exist.

## The task

Implement `new_page()` in `src/buffer/buffer_pool_manager.rs`: return a fresh `PageId`: 0, then 1, 2, ... No two callers, even concurrent ones, may get the same id. It touches neither memory nor disk: the page comes into existence when it is first fetched (and reads as zeros, because the disk has never seen it).

## Tests

- Ids count up from 0; `new_page` does no disk I/O; 4 threads × 50 calls get 200 distinct ids `0..200`.

## Syntax and methods

```rust
let mut inner = self.inner.lock().unwrap();
let id = PageId(inner.next_page_id);
inner.next_page_id += 1;
```

(An `AtomicI32::fetch_add(1, Relaxed)` would also do, without taking the pool's lock: BusTub's `std::atomic<page_id_t> next_page_id_`.)

## Notes

Where a counter lives decides how it is protected: inside the `Mutex<Inner>` it is protected for free; as an `AtomicI32` it is lock-free. Both are correct; the atomic avoids contention on the pool lock, the mutex keeps *all* state under one lock (simpler to reason about). Pick one and keep it. Page ids are never reused here, even after `delete_page`; real systems recycle them.

## In BusTub

```cpp
auto BufferPoolManager::NewPage() -> page_id_t { /* TODO(P1): Add implementation */ }   // allocates the next id; the page is brought in lazily
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::atomic<page_id_t> next_page_id_; next_page_id_++` (`fetch_add` with `seq_cst`) | `AtomicI32::fetch_add(1, Ordering::Relaxed)` |
| `page_id_t` = `int32_t`, overflows after 2^31 pages (16 TiB at 8 KiB) with undefined behaviour for signed overflow | `i32` overflow panics in debug, wraps in release; use `i64`/`u64` for a real system |
| returning the id through an out-parameter (`NewPage(&page_id)`) in older BusTub | returning it |

## Learn more
- [`AtomicI32`](https://doc.rust-lang.org/std/sync/atomic/type.AtomicI32.html) · *Rust Atomics and Locks*, [chapter 2: atomics](https://marabos.nl/atomics/atomics.html)

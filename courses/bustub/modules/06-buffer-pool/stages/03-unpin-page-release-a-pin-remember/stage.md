This stage has 2 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · Hits, and get_pin_count

**Where this fits.** Most fetches hit: the page is already in memory.

### The task

In `src/buffer/buffer_pool_manager.rs`:
- in `fetch_page`, when the page is **already resident**: add one pin, tell the replacer about the access, keep it non-evictable, return its frame. **No disk read.**
- `get_pin_count(page_id) -> Option<usize>`: the page's pin count, or `None` if it isn't in memory.

### Tests

- A page not in memory has no pin count; a fetched page has 1; fetched twice, 2 and the same frame, with only one disk read.
- Pin counts are per page. An unsaved change to a resident page is still there after another fetch.

### Syntax and methods

```rust
if let Some(&frame) = inner.page_table.get(&page_id) { /* copy the FrameId out of the reference */ }
inner.meta[frame.0].pin_count += 1;
let frame = inner.page_table.get(&page_id)?;     // in get_pin_count: `?` returns None when absent
```

### Notes

A pin count is a **reference count with a different job**: it doesn't free anything when it reaches zero; it makes the frame *eligible* for eviction. When you see `Arc::strong_count` and a pin count side by side you are looking at the same idea, one managed by the compiler and one by you.

### In BusTub

```cpp
auto BufferPoolManager::GetPinCount(page_id_t page_id) -> std::optional<size_t>   // nullopt if the page is not in the pool
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::optional<size_t>` | `Option<usize>` |
| `std::atomic<size_t> pin_count_` in `FrameHeader` (read without the pool latch by guards) | a plain `usize` inside `Mutex<Inner>`: guards go through the lock |
| `if (page_table_.find(id) != page_table_.end())` then `page_table_[id]` (two lookups) | `if let Some(&frame) = page_table.get(&id)` (one) |

### Learn more
- [`Option::?`](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#a-shortcut-for-propagating-errors-the--operator) · *The Internals of PostgreSQL*, [buffer descriptors and refcount](https://www.interdb.jp/pg/pgsql08.html)

## Part 2 · unpin_page: release a pin, remember the dirt

**Where this fits.** The counterpart of `fetch_page`.

### The task

Implement `unpin_page(page_id, is_dirty) -> bool` in `src/buffer/buffer_pool_manager.rs`: if the page is in memory with a pin count above zero, subtract one, **OR** `is_dirty` into the frame's dirty flag (a flag, once set, stays set until the page is written), and if the count reached zero tell the replacer the frame is **evictable**; return `true`. Otherwise (not in memory, or pin count already 0) return `false` and change nothing.

### Tests

- Two pins, two unpins: counts 1 then 0, the page stays in memory. Unpinning an unknown page or a page at 0 returns `false` (and the count doesn't go negative).
- A page can be fetched again after being unpinned, with no new disk read.

### Syntax and methods

```rust
meta.pin_count -= 1;
meta.dirty |= is_dirty;                          // bool |= bool
if meta.pin_count == 0 { inner.replacer.set_evictable(frame, true); }
```

### Notes

The borrow checker's first complaint here: `let meta = &mut inner.meta[frame.0];` borrows `inner.meta`, then `inner.replacer.set_evictable(..)` borrows `inner.replacer`. Because `inner` is a `MutexGuard`, `inner.meta` and `inner.replacer` both go through `DerefMut` on the *whole* guard, so the compiler sees two `&mut` of `inner` and refuses. The fix is either to finish with `meta` before touching `replacer` (copy the count out), or to take `let inner = &mut *guard;` once, which lets Rust split the borrow across fields. Remember this one: it comes up whenever you lock a struct and use two of its fields.

### In BusTub

The destructor of `ReadPageGuard`/`WritePageGuard` does this: lock the pool, `pin_count_--`, `is_dirty_ |= ...`, and `if (pin_count_ == 0) replacer_->SetEvictable(frame_id_, true)`.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `frame->is_dirty_ \|= is_dirty;` (`bool \|=` is legal C++ but promotes through `int`) | `meta.dirty \|= is_dirty;` |
| `pin_count_--` on a `size_t` at 0 wraps to 2^64 - 1 | `-= 1` on `usize` panics in debug; the explicit check returns `false` first |
| two locks: `bpm_latch_` and the frame's `rwlatch_` | two locks, taken in a fixed order (pool first, then never frame while waiting; see the next module) |

### Learn more
- Rust Nomicon, [splitting borrows](https://doc.rust-lang.org/nomicon/borrow-splitting.html) · [`MutexGuard` deref](https://doc.rust-lang.org/std/sync/struct.MutexGuard.html)

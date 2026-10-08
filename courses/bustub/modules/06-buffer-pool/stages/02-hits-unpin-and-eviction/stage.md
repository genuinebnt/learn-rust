Pinning and eviction. A resident page that is fetched again is a **hit**: the pin count goes up and no I/O happens. `unpin_page` takes a pin away and records whether the caller dirtied the page; at zero the frame becomes evictable. And when `fetch_page` needs a frame and none is free, it asks the replacer (ARC from module 1e) for a victim.

This stage is where the invariants of the pool appear: *a frame is evictable iff its pin count is zero*, *a page is in the page table iff it is resident*, and *dirtiness only accumulates*.

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

## Part 3 · Evict an unpinned page when no frame is free

**Where this fits.** The reason the pool exists: more pages than frames.

### The task

In `fetch_page` (`src/buffer/buffer_pool_manager.rs`), when the page is not in memory and there is **no free frame**, ask the replacer for a victim. If there is none (every frame is pinned), return `None`. Otherwise forget the victim page (remove it from the page table, clear the frame's metadata) and reuse its frame for the new page exactly as in stage 3.

### Tests

- A full pool of pinned pages refuses another (`None`, and the page is not resident). Unpin one and the fetch succeeds; the unpinned page is gone, the pinned ones stay.
- Pinned pages are never the victim. The replacer decides: **least recently accessed first** (not least recently unpinned), and a page accessed twice outlives one accessed once (ARC). Clean victims cost no disk writes.

### Syntax and methods

```rust
let frame = inner.replacer.evict()?;                                  // None if nothing is evictable: the fetch fails
let old_page = inner.meta[frame.0].page_id.take().expect("an evicted frame holds a page");
inner.page_table.remove(&old_page);
```

### Notes

**Who is in charge of what.** The replacer says *which*; the pool does the *bookkeeping* around it (page table, metadata). Keep the replacer ignorant of pins and disks: its entire interface is "access / evictable / evict / remove". Everything the pool must remember to undo when it takes a frame back is the list above, and the next stage adds one more item (write the page if it is dirty). When code has a to-do list like this, put it in **one function**.

### In BusTub

```cpp
frame_id_t fid;
if (!free_frames_.empty()) { fid = free_frames_.front(); free_frames_.pop_front(); }
else { auto victim = replacer_->Evict();  if (!victim.has_value()) { return std::nullopt; }  fid = *victim;  /* flush if dirty; erase from page_table_ */ }
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto victim = replacer_->Evict(); if (!victim.has_value()) return std::nullopt; fid = *victim;` | `let frame = inner.replacer.evict()?;` |
| `page_table_.erase(page_id)` | `page_table.remove(&page_id)` |
| `*victim` on an empty optional: undefined behaviour | `?` / `expect` / `match` |
| "the page that was in the frame": looked up by scanning `page_table_` for `fid` (O(n)) | stored in `FrameMeta.page_id` (O(1)), as BusTub's own comment suggests |

### Learn more
- [`Option::take`](https://doc.rust-lang.org/std/option/enum.Option.html#method.take) · CMU 15-445 "Memory Management": eviction, pinning, dirty pages · *PostgreSQL buffer manager*, [README](https://github.com/postgres/postgres/blob/master/src/backend/storage/buffer/README)

## Performance

A hit is O(1) and touches no disk. `unpin_page` is O(1) plus one `set_evictable` call when the count reaches zero. An eviction is whatever the replacer costs (O(1) for ARC with few pinned frames) plus the write-back (next stage).

The thing to watch is the **hit ratio**, not the instruction count: with 100 frames and a uniform random workload over 1 000 pages the hit ratio is about 10% whatever the policy; with a skewed workload (80% of accesses to 20% of pages) a good policy keeps it above 80%. A pool that leaks pins shrinks its effective size without any error.

**Measure it.** Count hits and misses with `get_pin_count` and a counting disk over a Zipf trace at pool sizes of 10, 50 and 100 frames and plot hit ratio against size; then deliberately leak one pin per 10 operations and watch the pool run out of frames.

## Hints

### Pin counts and the replacer must tell the same story

The replacer's evictable set should be exactly the frames with `pin_count == 0`. Two events change it: a fetch makes a frame non-evictable (every fetch, hit or miss), and the unpin that brings the count to 0 makes it evictable. Keep both calls next to the pin-count update, never in a different method, and add a `check()` asserting `meta.pin_count == 0` iff the replacer says evictable.

### `dirty |= is_dirty`

Two threads use the same page: one writes and unpins with `true`, the other only reads and unpins with `false`. If the second unpin *assigns*, it erases the first's change, and the page is evicted without being written. The flag only goes from false to true by unpin and from true to false when the page is written to disk. Test it explicitly: unpin `true`, then `false`, and confirm the page is still dirty.

### What does unpin of an unpinned page mean?

`unpin_page` returns `false` for a page that is not resident *or* has pin count 0: the caller released more pins than it took, which is a bug the pool can report instead of corrupting a counter (a `usize` decrement below zero panics in debug and wraps in release). Return `false` before touching any state, and keep the count from ever going negative.

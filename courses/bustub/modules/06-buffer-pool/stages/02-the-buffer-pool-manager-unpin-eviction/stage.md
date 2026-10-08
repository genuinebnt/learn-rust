This stage has 5 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · unpin_page: release a pin, remember the dirt

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

## Part 2 · Evict an unpinned page when no frame is free

**Where this fits.** The reason the pool exists: more pages than frames.

### The task

In `fetch_page` (`src/buffer/buffer_pool_manager.rs`), when the page is not in memory and there is **no free frame**, ask the replacer for a victim. If there is none (every frame is pinned), return `None`. Otherwise forget the victim page (remove it from the page table, clear the frame's metadata) and reuse its frame for the new page exactly as in stage 3.

### Tests

- A full pool of pinned pages refuses another (`None`, and the page is not resident).
- Unpin one and the fetch succeeds; the unpinned page is gone, the pinned ones stay.
- Pinned pages are never the victim. The replacer decides: **least recently accessed first** (not least recently unpinned), and a page accessed twice outlives one accessed once (ARC).
- Clean victims cost no disk writes.

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

## Part 3 · Write dirty victims back before reusing their frame

**Where this fits.** Without this a database loses data every time memory fills up.

### The task

In `src/buffer/buffer_pool_manager.rs`:
- `store(page_id, frame)` (a suggested helper): copy the frame's bytes into a `Box`, schedule a **write** request, wait for the future, `expect` that the write succeeded;
- in the eviction path of `fetch_page`: if the victim is **dirty**, `store` it *before* the frame is reused, then mark it clean.

### Tests

- A page modified and unpinned dirty survives eviction: its bytes come back from disk (1 write). Pages written through a pool of 3 frames, 20 pages, all read back.
- Unpinned **clean**, a modification is lost and nothing is written: the dirty flag is the caller's word.
- Dirt accumulates across pins: one dirty unpin among two still means "write it". After a write-back the page is clean again, so evicting it a second time writes nothing.

### Syntax and methods

```rust
let mut copy = Box::new([0u8; BUSTUB_PAGE_SIZE]);
copy.copy_from_slice(&**self.frames[frame.0].read().unwrap());   // read latch, then deref the guard and the Box
let (request, future) = DiskRequest::write(page_id, copy);
```

### Notes

**Why copy into a `Box`?** The request owns its buffer (module 1b), and the bytes must be a *snapshot*: the frame is about to be reused for another page. A zero-copy design would let the disk read the frame directly and hold the frame back until the I/O completes, which is faster and needs a state ("being written") in the frame metadata. This one is the simple, obviously-correct version.

**Write-ahead rule (preview).** With a write-ahead log (the Recovery module), the log record for a change must reach disk *before* the page does. That rule will go right here, before `store`.

### In BusTub

```cpp
if (frame->is_dirty_) {
  auto promise = disk_scheduler_->CreatePromise();  auto future = promise.get_future();
  disk_scheduler_->Schedule({{true, frame->GetDataMut(), old_page_id, std::move(promise)}});
  future.get();                       // wait until the page is on disk before reusing the frame
  frame->is_dirty_ = false;
}
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| the write request points at the frame's own memory (`char *`) | the request owns a copy (8 KiB `memcpy`) |
| `future.get()` rethrows an exception from the worker | `future.get()` returns `Result`; `expect` turns an error into a panic with context |
| `msync`/`write` straight from a `mmap`ed frame (what a zero-copy design does) | not here; see the mmap paper in the resources for why DBMSs avoid mmap |

**Port rule:** C++ code that hands a raw pointer to a worker and waits on a future/promise becomes ownership transfer plus a future, as in module 1b; if you need to keep using the memory while the I/O runs, copy first.

### Learn more
- Crotty, Leis, Pavlo, [*Are You Sure You Want to Use MMAP in Your DBMS?*](https://db.cs.cmu.edu/mmap-cidr2022/) · [Write policies](https://en.wikipedia.org/wiki/Cache_(computing)#Writing_policies) (write-back vs write-through)

## Part 4 · flush_page and flush_all_pages

**Where this fits.** Sometimes a page must reach the disk *now* (a checkpoint, a test, a shutdown).

### The task

In `src/buffer/buffer_pool_manager.rs`:
- `flush_page(page_id) -> bool`: if the page is in memory, write it to disk **whether or not it is dirty**, mark it clean, return `true`; if not, return `false` and write nothing. A pinned page may be flushed (the pin stays);
- `flush_all_pages()`: flush every page that is in memory.

### Tests

- A dirty page flushed is on disk (the disk's copy has the bytes); a clean page is written too; an unknown page returns `false` with no write.
- After a flush, evicting the page writes nothing more. A pinned page can be flushed and stays pinned.
- `flush_all_pages` writes every resident page, and again on a second call.

### Syntax and methods

```rust
let pages: Vec<PageId> = self.inner.lock().unwrap().page_table.keys().copied().collect();   // snapshot the keys, release the lock
for page in pages { self.flush_page(page); }                                                // flush_page locks again, one page at a time
```

### Notes

**Never call a locking method while holding the lock.** `std::sync::Mutex` is not reentrant: locking it twice on one thread **deadlocks** (or panics). `flush_all_pages` collects the page ids, drops its guard, and then calls `flush_page`, which takes the lock itself. The C++ solutions use `std::scoped_lock` in both and need a private unlocked helper (`FlushPageUnsafe` in BusTub's header) for exactly this reason.

### In BusTub

```cpp
auto FlushPageUnsafe(page_id_t page_id) -> bool;   // flushes without taking the latch: the caller holds it
auto FlushPage(page_id_t page_id) -> bool;         // takes the latch, then does the same
void FlushAllPagesUnsafe();  void FlushAllPages();
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `Foo` / `FooUnsafe` pairs: one locks, one assumes the lock is held | a private function that takes `&mut Inner` (the lock's contents), and a public one that locks and calls it |
| `std::recursive_mutex` to allow re-locking | no recursive mutex in std; restructure instead |
| `fsync` after writing, for durability | the disk manager decides (`sync_all` in `shut_down`); a flush here means "handed to the disk layer" |

**Port rule:** when C++ has `Method` and `MethodUnsafe`/`MethodLocked`, Rust usually has a function taking the guard (or `&mut Inner`) as an argument: you can't call it without proof that you hold the lock.

### Learn more
- [Deadlock](https://en.wikipedia.org/wiki/Deadlock) · [`Mutex` docs: "locking twice on the same thread"](https://doc.rust-lang.org/std/sync/struct.Mutex.html#method.lock)

## Part 5 · delete_page

**Where this fits.** A page that is deleted (a table dropped, an index node merged away) must disappear from the pool and its disk space must be freed.

### The task

Implement `delete_page(page_id) -> bool` in `src/buffer/buffer_pool_manager.rs`: if the page is in memory and **pinned**, return `false` and change nothing. If it is in memory with pin count 0: remove it from the page table, remove its frame from the replacer, reset the frame's metadata, zero its bytes, put the frame back on the free list. In every case that returns `true` (including a page that wasn't in memory), tell the disk to free the page (`deallocate_page` on the scheduler). A deleted dirty page is **not** written back.

### Tests

- A pinned page can't be deleted. An unpinned one is deleted, its pin count is `None`, the disk is told, and the freed frame takes another page with no eviction.
- Deleting a page that isn't in memory succeeds and still tells the disk; deleting twice is fine.
- A deleted dirty page is never written. The replacer forgets the frame: afterwards, with the other frames pinned, nothing is evictable.

### Syntax and methods

```rust
inner.replacer.remove(frame);                     // evictable frames only: pin count 0 implies evictable
inner.free_frames.push(frame);
self.frames[frame.0].write().unwrap().fill(0);
self.disk_scheduler.deallocate_page(page_id);
```

### Notes

**`remove` vs `evict` (module 1e).** The replacer's `remove` leaves no ghost: the page is gone for good, not "recently evicted". Calling `evict`-like code here would make ARC think the page might come back. The ordering matters too: remove from the replacer *before* putting the frame on the free list, otherwise a concurrent fetch could take the frame while the replacer still lists it. (Under one mutex that can't happen; in the lock-split designs it can.)

### In BusTub

"Delete a page from the buffer pool. If page_id is not in the buffer pool, do nothing and return true. If the page is pinned and cannot be deleted, return false immediately. After deleting the page from the page table, stop tracking the frame in the replacer and add the frame back to the free list. Also, reset the page's memory and metadata. Finally, you should call DeallocatePage() to imitate freeing the page on the disk."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::fill(frame->data_.begin(), frame->data_.end(), 0)` / `memset` | `frame_data.fill(0)` |
| `free_frames_.push_back(fid)` | `free_frames.push(frame)` |
| `return true` for "nothing to do" | same; `bool` return values here mean "did it work", not "did anything happen" |

### Learn more
- BusTub's [buffer_pool_manager.h](https://github.com/cmu-db/bustub/blob/master/src/include/buffer/buffer_pool_manager.h) (the doc comments are the spec) · [`slice::fill`](https://doc.rust-lang.org/std/primitive.slice.html#method.fill)

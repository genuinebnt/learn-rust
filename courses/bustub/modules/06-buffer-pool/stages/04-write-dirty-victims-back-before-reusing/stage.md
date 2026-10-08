This stage has 2 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · Evict an unpinned page when no frame is free

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

## Part 2 · Write dirty victims back before reusing their frame

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

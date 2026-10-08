**Where this fits.** Without this a database loses data every time memory fills up.

## The task

In `src/buffer/buffer_pool_manager.rs`:
- `store(page_id, frame)` (a suggested helper): copy the frame's bytes into a `Box`, schedule a **write** request, wait for the future, `expect` that the write succeeded;
- in the eviction path of `fetch_page`: if the victim is **dirty**, `store` it *before* the frame is reused, then mark it clean.

## Tests

- A page modified and unpinned dirty survives eviction: its bytes come back from disk (1 write). Pages written through a pool of 3 frames, 20 pages, all read back.
- Unpinned **clean**, a modification is lost and nothing is written: the dirty flag is the caller's word.
- Dirt accumulates across pins: one dirty unpin among two still means "write it". After a write-back the page is clean again, so evicting it a second time writes nothing.

## Syntax and methods

```rust
let mut copy = Box::new([0u8; BUSTUB_PAGE_SIZE]);
copy.copy_from_slice(&**self.frames[frame.0].read().unwrap());   // read latch, then deref the guard and the Box
let (request, future) = DiskRequest::write(page_id, copy);
```

## Notes

**Why copy into a `Box`?** The request owns its buffer (module 1b), and the bytes must be a *snapshot*: the frame is about to be reused for another page. A zero-copy design would let the disk read the frame directly and hold the frame back until the I/O completes, which is faster and needs a state ("being written") in the frame metadata. This one is the simple, obviously-correct version.

**Write-ahead rule (preview).** With a write-ahead log (the Recovery module), the log record for a change must reach disk *before* the page does. That rule will go right here, before `store`.

## In BusTub

```cpp
if (frame->is_dirty_) {
  auto promise = disk_scheduler_->CreatePromise();  auto future = promise.get_future();
  disk_scheduler_->Schedule({{true, frame->GetDataMut(), old_page_id, std::move(promise)}});
  future.get();                       // wait until the page is on disk before reusing the frame
  frame->is_dirty_ = false;
}
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| the write request points at the frame's own memory (`char *`) | the request owns a copy (8 KiB `memcpy`) |
| `future.get()` rethrows an exception from the worker | `future.get()` returns `Result`; `expect` turns an error into a panic with context |
| `msync`/`write` straight from a `mmap`ed frame (what a zero-copy design does) | not here; see the mmap paper in the resources for why DBMSs avoid mmap |

**Port rule:** C++ code that hands a raw pointer to a worker and waits on a future/promise becomes ownership transfer plus a future, as in module 1b; if you need to keep using the memory while the I/O runs, copy first.

## Learn more
- Crotty, Leis, Pavlo, [*Are You Sure You Want to Use MMAP in Your DBMS?*](https://db.cs.cmu.edu/mmap-cidr2022/) · [Write policies](https://en.wikipedia.org/wiki/Cache_(computing)#Writing_policies) (write-back vs write-through)

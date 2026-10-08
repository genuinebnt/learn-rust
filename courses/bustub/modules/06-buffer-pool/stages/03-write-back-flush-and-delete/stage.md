Getting data **out**. Before a dirty victim's frame is reused, its bytes are written back to disk; `flush_page` and `flush_all_pages` write on demand; `delete_page` forgets a page and releases its disk space. These are the operations that decide whether anything is ever durable.

The ordering matters more here than anywhere so far: write back *before* the frame is overwritten, with the page id the frame *used to* hold, and release a page's disk space only when nobody has it pinned. The stage ends with a stress test that mixes all operations from several threads.

## Part 1 · Write dirty victims back before reusing their frame

**Where this fits.** Without this a database loses data every time memory fills up.

### The task

In `src/buffer/buffer_pool_manager.rs`:
- `store(page_id, frame)` (a suggested helper): copy the frame's bytes into a `Box`, schedule a **write** request, wait for the future, `expect` that the write succeeded;
- in the eviction path of `fetch_page`: if the victim is **dirty**, `store` it *before* the frame is reused, then mark it clean.

### Tests

- A page modified and unpinned dirty survives eviction: its bytes come back from disk (1 write). Pages written through a pool of 3 frames, 20 pages, all read back. Unpinned **clean**, a modification is lost and nothing is written: the dirty flag is the caller's word.
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

## Part 2 · flush_page and flush_all_pages

**Where this fits.** Sometimes a page must reach the disk *now* (a checkpoint, a test, a shutdown).

### The task

In `src/buffer/buffer_pool_manager.rs`:
- `flush_page(page_id) -> bool`: if the page is in memory, write it to disk **whether or not it is dirty**, mark it clean, return `true`; if not, return `false` and write nothing. A pinned page may be flushed (the pin stays);
- `flush_all_pages()`: flush every page that is in memory.

### Tests

- A dirty page flushed is on disk (the disk's copy has the bytes); a clean page is written too; an unknown page returns `false` with no write. After a flush, evicting the page writes nothing more. A pinned page can be flushed and stays pinned.
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

## Part 3 · delete_page

**Where this fits.** A page that is deleted (a table dropped, an index node merged away) must disappear from the pool and its disk space must be freed.

### The task

Implement `delete_page(page_id) -> bool` in `src/buffer/buffer_pool_manager.rs`: if the page is in memory and **pinned**, return `false` and change nothing. If it is in memory with pin count 0: remove it from the page table, remove its frame from the replacer, reset the frame's metadata, zero its bytes, put the frame back on the free list. In every case that returns `true` (including a page that wasn't in memory), tell the disk to free the page (`deallocate_page` on the scheduler). A deleted dirty page is **not** written back.

### Tests

- A pinned page can't be deleted. An unpinned one is deleted, its pin count is `None`, the disk is told, and the freed frame takes another page with no eviction. Deleting a page that isn't in memory succeeds and still tells the disk; deleting twice is fine.
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

## Performance

A **clean** eviction costs no I/O; a **dirty** one costs one disk write *before* the read that follows it, so a miss on a dirty victim is roughly **two I/Os in series** while holding the pool latch. That is why real pools write dirty pages in the background (a *page cleaner*) so that evictions find clean frames. `flush_page` is one copy of 8 KiB and one write; `flush_all_pages` is O(resident pages) writes. `delete_page` is O(1) and does no I/O to the data: it tells the disk layer to free a slot.

The extra copy in `flush_page` (the page is copied out of the frame, then written) is deliberate: it lets the write happen **without holding the frame's latch**, so a slow disk does not block readers of that page.

**Measure it.** Compare the time of N misses with all-clean victims against all-dirty victims (use the disk's write counter to confirm one write per eviction in the second case), and the time of `flush_all_pages` over 100, 1 000 and 10 000 resident pages.

## Hints

### The page id you write with is the *old* one

By the time you are about to overwrite the frame, the pool is already in the middle of turning it into a frame for the *new* page. Take the old page id out of the metadata **first** (`page_id.take()`), write the frame's bytes to disk under that id if the frame is dirty, clear the dirty flag, remove the old page-table entry, and only then read the new page into the frame. A test with a counting disk checks that exactly one write happens, with the old id, and none for a clean victim.

### `delete_page` and pins

A pinned page cannot be deleted (return `false`): someone is using the bytes. For an unpinned resident page you must undo **everything** that fetching it did: remove it from the page table, tell the replacer to forget the frame (a frame still marked evictable would be chosen later and double-freed), reset its metadata, push the frame back on the free list, and tell the disk layer to free the page. Check that deleting a page that is not resident still succeeds and still frees the disk space.

### Flush must not wait for a latch while holding the pool's lock

`flush_page` needs to read a frame's bytes, which means taking that frame's latch, which a writer may be holding for a long time. If you hold the pool latch while you wait, every other thread waits behind that writer, and if the writer needs the pool latch to finish you have a deadlock (module 1g makes this exact). A first version may hold the lock; make a note of why that is wrong and what pinning the page first would let you do.

This stage has 2 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · flush_page and flush_all_pages

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

## Part 2 · delete_page

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

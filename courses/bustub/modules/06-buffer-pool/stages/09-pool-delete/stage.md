**Where this fits.** A page that is deleted (a table dropped, an index node merged away) must disappear from the pool and its disk space must be freed.

## The task

Implement `delete_page(page_id) -> bool` in `src/buffer/buffer_pool_manager.rs`: if the page is in memory and **pinned**, return `false` and change nothing. If it is in memory with pin count 0: remove it from the page table, remove its frame from the replacer, reset the frame's metadata, zero its bytes, put the frame back on the free list. In every case that returns `true` (including a page that wasn't in memory), tell the disk to free the page (`deallocate_page` on the scheduler). A deleted dirty page is **not** written back.

## Tests

- A pinned page can't be deleted. An unpinned one is deleted, its pin count is `None`, the disk is told, and the freed frame takes another page with no eviction.
- Deleting a page that isn't in memory succeeds and still tells the disk; deleting twice is fine.
- A deleted dirty page is never written. The replacer forgets the frame: afterwards, with the other frames pinned, nothing is evictable.

## Syntax and methods

```rust
inner.replacer.remove(frame);                     // evictable frames only: pin count 0 implies evictable
inner.free_frames.push(frame);
self.frames[frame.0].write().unwrap().fill(0);
self.disk_scheduler.deallocate_page(page_id);
```

## Notes

**`remove` vs `evict` (module 1e).** The replacer's `remove` leaves no ghost: the page is gone for good, not "recently evicted". Calling `evict`-like code here would make ARC think the page might come back. The ordering matters too: remove from the replacer *before* putting the frame on the free list, otherwise a concurrent fetch could take the frame while the replacer still lists it. (Under one mutex that can't happen; in the lock-split designs it can.)

## In BusTub

"Delete a page from the buffer pool. If page_id is not in the buffer pool, do nothing and return true. If the page is pinned and cannot be deleted, return false immediately. After deleting the page from the page table, stop tracking the frame in the replacer and add the frame back to the free list. Also, reset the page's memory and metadata. Finally, you should call DeallocatePage() to imitate freeing the page on the disk."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::fill(frame->data_.begin(), frame->data_.end(), 0)` / `memset` | `frame_data.fill(0)` |
| `free_frames_.push_back(fid)` | `free_frames.push(frame)` |
| `return true` for "nothing to do" | same; `bool` return values here mean "did it work", not "did anything happen" |

## Learn more
- BusTub's [buffer_pool_manager.h](https://github.com/cmu-db/bustub/blob/master/src/include/buffer/buffer_pool_manager.h) (the doc comments are the spec) · [`slice::fill`](https://doc.rust-lang.org/std/primitive.slice.html#method.fill)

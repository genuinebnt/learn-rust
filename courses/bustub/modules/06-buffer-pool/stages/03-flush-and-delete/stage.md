Two more operations finish the textbook interface. A **flush** makes the disk copy of a page match memory now, not whenever the page happens to be evicted: this is how a database makes work durable at checkpoints, and later how the write-ahead log will force pages out in order. A **delete** removes a page from the database altogether: its frame goes back to the free list, the replacer forgets it, and the disk is told it can reuse the space. Both operations are small; the difficulty is leaving every table (page table, free list, metadata, replacer) consistent after them.

> [!CHECK] A page is pinned and a thread calls `delete_page` on it. Should it succeed? Describe one thing that would break if it did, in terms of the thread that holds the pin.
> ||No: it must return `false`. The thread holding the pin believes the frame contains that page; if the pool freed the frame and gave it to another page, the thread would read and write another page's data through a pointer it was told was safe. Pins are a promise that the page stays put, and a delete is a promise-breaker, so it must wait for the last unpin.||
>
> - What does a pin promise?
> - What does `delete_page` of a page that is not in memory do?
> - Does a deleted page that is dirty need to be written?

## The task

- `flush_page(page)`: writes the page's bytes to the disk **whether or not it is dirty**, and marks it clean. `false` if the page is not in memory. A pinned page can be flushed and stays pinned (the pin count does not change).
- `flush_all_pages()`: flushes every page that is in memory.
- `delete_page(page)`: `false` if the page is pinned. Otherwise: if it is in memory it leaves the page table and the replacer, its frame returns to the free list (zeroed), and a dirty page is **not** written (it is being deleted); in every case the disk is told to deallocate the page; `true`. Deleting a page that is not in memory succeeds; deleting twice is fine.
- A frame freed by a delete is usable at once: with a pool of one frame, deleting the page frees room for another.

The model test now includes flush and delete operations in the random sequences. A flushed page's bytes are on the disk; `delete_page` succeeds exactly when nobody has the page pinned; the invariants from 1f-02 still hold. A page may now legitimately be written even though it was never reported dirty (a flush writes regardless), and the model knows that.

## Your freedom

How you copy and write the bytes of a flush, how you mark a page clean, and in what order the delete steps happen, as long as no step leaves a table pointing at a frame that is free.

## The Rust toolbox

**Hold the lock only as long as you need it.** A flush needs the pool's lock to find the frame and to change the metadata, and the frame's read latch to copy the bytes. A scoped block `{ let mut inner = self.inner.lock().unwrap(); ... }` releases the lock at the closing brace; the stage 1g-02 experiment shows why not to wait for a latch while holding it.

**Pin while you work without the lock.** If you let go of the pool's lock in the middle of a flush, the page could be evicted. Pinning it (and telling the replacer) for the duration prevents that, and `unpin_page` at the end undoes it. The same trick appears in every layer above.

**Collect keys, then iterate.** `let pages: Vec<PageId> = inner.page_table.keys().copied().collect();` then loop over `pages` and call `flush_page` for each: iterating a `HashMap` while mutating it is a borrow error, and a flush takes the lock itself.

**`Vec::push` / `pop` as a free list.** The free list is a stack of `FrameId`s. A delete pushes the frame back.

**Zero a buffer.** `frame.fill(0)` sets every byte; a reused frame must not leak the old page's contents into a new page that is never written (a page that reads as zeros must really be zeros).

## If this is new

- **S3 Vec & slices**: `fill`, `copy_from_slice`.
- **S4 Maps & sets**: `keys`, `remove`, why you cannot mutate while iterating.
- **L2 Borrowing**: the scoped-block pattern to end a borrow early.

## Tests

- `flush_page` writes a clean page; fails for a page not in memory; leaves the page clean (the next eviction writes nothing); works on a pinned page without unpinning it.
- `flush_all_pages` writes every page in memory.
- A pinned page cannot be deleted; an unpinned one can, and its frame is free again; the disk is told.
- Deleting a page that is not in memory succeeds; a deleted dirty page is not written; deleting twice is fine.
- For random sequences with flush and delete, the pool matches the model.

## Hints

### List the tables a delete touches

Page table, free list, metadata, replacer, frame bytes, disk. For each, say what a delete does. Then check your order: which step would leave a stale entry if it failed halfway?

### A flush must not lose a concurrent write

Suppose a writer is changing the page while you flush. What bytes does the flush write: the ones from before or after? What do you mark clean, and what if the writer unpins dirty after your flush?

### The replacer and delete

The replacer forgets a frame with `remove`, which panics if the frame is not evictable. What must be true of the frame at that moment, and what does that say about the order of your checks?

## Performance

A flush is a write: tens of microseconds. `flush_all_pages` is proportional to the number of pages in memory, and a database does it at checkpoints, not on every commit; commits flush the log instead (module 4c). A delete is cheap: a few table updates and a message to the disk.

**Measure it.** Fill a pool of 1 000 frames with dirty pages and time `flush_all_pages` against a disk that takes 50 microseconds per write. Does it match 1 000 × 50 µs? What would issuing the writes together (module 1b's batch `schedule`) change?

## Experiment

Optional. Predict first, then run.

1. **Flush without cleaning.** Do not clear the dirty flag in `flush_page`. Which test notices, and what is the cost in a real system?
2. **Delete while pinned.** Remove the pin check. Which test fails, and what does the failure message tell a reader who did not write the test?

## Other designs

- **Flush copies under the latch, writes outside (ours).** The disk request owns a copy; the frame is free for readers meanwhile.
- **Flush holds the frame latch for the whole write.** Simpler, but a slow disk blocks readers.
- **Delete as a tombstone.** Mark the page deleted and reclaim later in the background.

## In BusTub

`FlushPage`, `FlushAllPages` and `DeletePage` have the same contract in BusTub's header. Its guards' `Flush()` (module 1g) is flush by another route.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::scoped_lock lock(*bpm_latch_);` | `let mut inner = self.inner.lock().unwrap();` (the guard is the lock) |
| `page_table_.erase(page_id)` | `inner.page_table.remove(&page_id)` |
| `free_frames_.push_back(frame_id)` | `inner.free_frames.push(frame)` |
| `disk_scheduler_->DeallocatePage(page_id)` | the scheduler you built in module 1b |

**Port rule:** `erase(key)` is `remove(&key)` and returns the old value if you want it.

## Learn more

- [`HashMap::remove`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.remove) · [`slice::fill`](https://doc.rust-lang.org/std/primitive.slice.html#method.fill)

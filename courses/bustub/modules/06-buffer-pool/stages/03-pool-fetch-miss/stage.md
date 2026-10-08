**Where this fits.** The first real work of the pool.

## The task

Implement the first case of `fetch_page(page_id) -> Option<FrameId>` in `src/buffer/buffer_pool_manager.rs` (`load` is a suggested helper): the page is not in memory and there is a **free frame**. Take the frame, **read the page from disk into it** (schedule a read request on the disk scheduler and wait for its future), record it in the page table, set the frame's metadata (this page, **pin count 1**, clean), tell the replacer about the access, and mark the frame **not evictable** (it is pinned). Return the frame.

## Tests

- A new page arrives zeroed. A page already on disk arrives with its bytes (and costs exactly one disk read).
- Different pages get different frames; five misses cost five reads.

## Syntax and methods

```rust
let (request, future) = DiskRequest::read(page_id);
self.disk_scheduler.schedule(vec![request]);
let data = future.get().expect("the scheduler is running").expect("reading from disk");   // Result<Result<Box<PageData>>>
self.frames[frame.0].write().unwrap().copy_from_slice(&*data);
inner.replacer.record_access(frame, page_id);
inner.replacer.set_evictable(frame, false);
```

## Notes

A frame is **referred to by index** (`FrameId`), never by a reference into `self.frames`: the metadata, the replacer and the page table all name the frame, and an index can live in all of them without borrowing. This is what an arena buys you (module 1c); the C++ `FrameHeader*`/`shared_ptr` versions need the pool to outlive every pointer.

The I/O happens **while holding the pool's lock**: simple and correct, slow when many threads miss at once. Making it concurrent is the "hard" extension at the end of the module.

## In BusTub

```cpp
// CheckedReadPage / CheckedWritePage, simplified:
frame_id_t fid = free_frames_.front();  free_frames_.pop_front();
auto promise = disk_scheduler_->CreatePromise();  auto future = promise.get_future();
disk_scheduler_->Schedule({{/*is_write=*/false, frame->GetDataMut(), page_id, std::move(promise)}});
future.get();   // wait for the read
page_table_[page_id] = fid;  replacer_->RecordAccess(fid, page_id);  replacer_->SetEvictable(fid, false);
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a `char *` into the frame handed to the scheduler, valid "until the future completes" | the request owns a `Box`; you copy the bytes into the frame when the future gives them back |
| `std::unique_lock<std::mutex> lock(*bpm_latch_);` | `let mut inner = self.inner.lock().unwrap();` (unlocks at the end of scope) |
| `page_table_[page_id] = fid;` | `inner.page_table.insert(page_id, frame);` |
| early `return nullptr`/`std::nullopt` | `return None` / `?` on an `Option` |
| `free_frames_.front(); free_frames_.pop_front();` | `free_frames.pop()` returns `Option<FrameId>` in one step |

## Learn more
- [`Vec::pop`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.pop) · [`copy_from_slice`](https://doc.rust-lang.org/std/primitive.slice.html#method.copy_from_slice) · BusTub [buffer_pool_manager.h](https://github.com/cmu-db/bustub/blob/master/src/include/buffer/buffer_pool_manager.h)

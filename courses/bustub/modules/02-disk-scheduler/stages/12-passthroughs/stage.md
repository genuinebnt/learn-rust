**Where this fits.** Two small methods the buffer pool will call.

## The task

In `src/storage/disk/disk_scheduler.rs`:
- `create_promise()` returns a fresh promise/future pair for a request's callback;
- `deallocate_page(page_id)` asks the disk to delete the page.

## Tests

- `create_promise` gives a working pair; a request built by hand with that promise can be scheduled and completed.
- `deallocate_page(6)` then `(2)` reach the disk in that order.

## Syntax and methods

```rust
promise()                      // from src/common/promise.rs: (Promise<T>, Future<T>)
self.disk.delete_page(page_id) // the scheduler keeps the Arc<dyn DiskIo> it was created with
```

## Notes

`deallocate_page` runs on the **caller's** thread, not the worker's: it skips the queue. That is how BusTub does it too (and why the buffer pool's `delete_page` warns you about ordering with pending writes).

## In BusTub

```cpp
auto CreatePromise() -> DiskSchedulerPromise { return {}; };
void DeallocatePage(page_id_t page_id) { disk_manager_->DeletePage(page_id); }
```

## The C/C++ way

| C++ | Rust |
|---|---|
| `using DiskSchedulerPromise = std::promise<bool>;` (an alias so tests can swap their own promise) | `type DiskResult = io::Result<Box<PageData>>;` + a function returning the pair |
| `DiskManager *disk_manager_ __attribute__((__unused__))` (a raw pointer that must outlive the scheduler) | `Arc<dyn DiskIo>`: shared ownership, the disk lives as long as anyone uses it |
| `inline` one-line member functions in the header | ordinary methods; the compiler inlines as it likes |

**Port rule:** a raw pointer field `T *p` "owned by someone else" becomes `Arc<T>` (shared) or a `&'a T` with a lifetime parameter (borrowed). `Arc` is the right default when the pointee is used from other threads.

## Learn more
- [`Arc`](https://doc.rust-lang.org/std/sync/struct.Arc.html) · The Rust Book: [`Arc<T>`](https://doc.rust-lang.org/book/ch16-03-shared-state.html#atomic-reference-counting-with-arct)

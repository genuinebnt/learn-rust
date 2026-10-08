**Where this fits.** A request names a page, says read or write, carries the buffer, and carries the promise to complete.

## The task

In `src/storage/disk/disk_scheduler.rs`, implement the two constructors that make a request together with the future for its result:
- `DiskRequest::read(page_id)`: `is_write` false, a zeroed buffer to fill;
- `DiskRequest::write(page_id, data)`: `is_write` true, carrying `data`.

Each also creates the promise/future pair: the promise goes in the request as `callback`, the future is returned.

## Tests

- A read request has a zeroed 8192-byte buffer, the page id, and a future that isn't ready.
- A write request carries the data it was given. The future is connected to the request's callback. Dropping a request breaks its future.

## Syntax and methods

```rust
pub struct DiskRequest { pub is_write: bool, pub data: Box<PageData>, pub page_id: PageId, pub callback: Promise<DiskResult> }
let (callback, future) = promise();                     // the type is inferred from `callback`'s field
Box::new([0; BUSTUB_PAGE_SIZE])                          // a heap-allocated 8 KiB array
(request, future)                                        // return a tuple
```

## Notes

**The design decision of this module.** BusTub's `DiskRequest` holds a raw `char *data_`: the worker thread reads or writes memory the caller also holds, and the caller promises not to touch it until the callback fires. The compiler can't check that promise. In Rust the request **owns** its buffer (`Box<PageData>`): moved to the worker, and *returned through the future*. No sharing, no `unsafe`, no use-after-free. The cost is that the buffer pool will copy a frame into a box before a write (8 KiB `memcpy`), which is also what makes the write safe from concurrent modification: the page written is the snapshot taken when the request was made.

## In BusTub

```cpp
DiskRequest r1{/*is_write=*/true, data, /*page_id=*/0, std::move(promise1)};   // data is a char[BUSTUB_PAGE_SIZE] on the caller's stack
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `char *data` shared between threads, valid "until the callback" by convention | `Box<PageData>` moved into the request and handed back in the result |
| out-parameter `char *buf` for a read | the result carries the buffer: `Result<Box<PageData>>` |
| a dangling `data_` if the caller returns early: use-after-free | impossible: the request owns the memory |
| `std::move(promise1)` into the struct | assigning `callback: promise` moves it |
| aggregate initialisation `DiskRequest{a, b, c, d}` | struct literal `DiskRequest { is_write, data, page_id, callback }` |

**Port rule:** when C/C++ passes `T *buf` to another thread "to fill in", port it as *ownership transfer in, ownership transfer back out* (`Box<T>` or `Vec<u8>` through a channel/future), not as `Arc<Mutex<..>>` unless the buffer really must stay shared.

## Learn more
- The Rust Book: [`Box<T>`](https://doc.rust-lang.org/book/ch15-01-box.html) · [Rust API guidelines](https://rust-lang.github.io/api-guidelines/) on ownership in APIs
- BusTub's [disk_scheduler.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/disk/disk_scheduler.h)

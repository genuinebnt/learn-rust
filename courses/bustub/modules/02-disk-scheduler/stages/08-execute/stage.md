**Where this fits.** The worker's job for one request, with no threads yet, so it can be tested directly.

## The task

In `src/storage/disk/disk_scheduler.rs`:
- `run(disk, is_write, page_id, data)`: call `disk.write_page` for a write, `disk.read_page` (into `data`) for a read, and return its `io::Result<()>`;
- in `execute(disk, request)`: complete the request's `callback` with the buffer if the I/O succeeded (`Ok(data)`), or with the error.

## Tests

- A write then a read of the same page through `execute` round-trips; a write hands its buffer back; an unwritten page reads as zeros.
- A disk that returns `Err` (read-only disk) makes the future's result an `Err` with the same `ErrorKind`.

## Syntax and methods

```rust
let DiskRequest { is_write, mut data, page_id, callback } = request;   // destructuring a struct: moves each field out
disk.read_page(page_id, &mut data)                                      // &mut Box<[u8; N]> derefs to &mut [u8; N]
result.map(|()| data)                                                   // Result<(), E> -> Result<Box<PageData>, E>
callback.set(value)
```

## Notes

`run` is separate from `execute` on purpose: stage 11 will wrap just the call to `run` in a panic guard. A function that does one thing is a function you can wrap.

## In BusTub

```cpp
// the student's StartWorkerThread() loop body:
if (r.is_write_) { disk_manager_->WritePage(r.page_id_, r.data_); }
else             { disk_manager_->ReadPage(r.page_id_, r.data_); }
r.callback_.set_value(true);
```

BusTub's callback carries a `bool`; here it carries the whole `io::Result` and the buffer.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `if (r.is_write_) {...} else {...}` as a statement | `if`/`else` as an expression returning a value |
| `callback_.set_value(true)`: success only, errors lost or logged | `Result<Box<PageData>>`: success carries the buffer, failure carries the `io::Error` |
| `disk_manager_->ReadPage(id, buf)` through a `DiskManager *` | through a `&dyn DiskIo` |
| a request is a struct passed by `std::move` | passed by value; destructure to take it apart |

## Learn more
- The Rust Book: [`Result`](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) · [destructuring structs](https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#destructuring-structs)
- [`Result::map`](https://doc.rust-lang.org/std/result/enum.Result.html#method.map)

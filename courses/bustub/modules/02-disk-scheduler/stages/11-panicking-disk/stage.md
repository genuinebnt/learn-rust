**Where this fits.** `DiskManagerMemory` panics when a page is out of range; a bug in any disk could panic. If the worker thread dies, every later request waits forever.

## The task

In `execute` (`src/storage/disk/disk_scheduler.rs`), catch a panic from the disk call and report it to the caller as an `io::Error` (any message containing the word "panicked"). The line that calls `run` is the one to wrap: the stub has the plain call and a TODO.

## Tests

- A read of page 13 on a disk that panics for page 13 gives an `Err` whose text contains "panicked".
- On a scheduler: a panicking request and a good request scheduled after it: the first reports an error, **the second still runs**. Five panics in a row are all caught.
- Requests that don't panic behave as before.

## Syntax and methods

```rust
use std::panic::{catch_unwind, AssertUnwindSafe};
let result = catch_unwind(AssertUnwindSafe(|| run(disk, is_write, page_id, &mut data)))   // Result<io::Result<()>, Box<dyn Any + Send>>
    .unwrap_or_else(|_panic| Err(io::Error::other("the disk panicked")));                 // flatten: a panic becomes an io::Error
```

## Notes

`catch_unwind` needs the closure to be `UnwindSafe`: "if this panics halfway, nobody sees broken state." We hold `&mut data` and a `&dyn DiskIo`, so the compiler can't promise that; `AssertUnwindSafe` is *you* promising. It's fair here: after a panic we discard `data`'s contents anyway and only report the error. Panics are for bugs, not for control flow; catching them belongs at a boundary like this one (a worker, a request handler), never inside the logic.

## In BusTub

C++ has the same problem with exceptions: an exception escaping the lambda passed to `std::thread` calls `std::terminate` and kills the whole process. The BusTub tests never throw from the disk; production code would wrap the call in `try { ... } catch (...) { callback.set_value(false); }`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `try { disk->ReadPage(..); } catch (const std::exception &e) { ... }` | `catch_unwind(..)` for panics; `Result` for expected failures |
| an uncaught exception in a `std::thread` → `std::terminate` (whole process) | an uncaught panic ends *that thread*; `join()` returns `Err` |
| exceptions for I/O errors, bad arguments, programming errors alike | `Result` for errors you expect; panic for bugs |
| `-fno-exceptions` builds (kernels, some databases) | `panic = "abort"` makes `catch_unwind` useless: unwinding is optional |
| `noexcept` | (no equivalent; a panic can occur anywhere) |

**Port rule:** C++ `catch (...)` at a thread or request boundary → `catch_unwind` + `AssertUnwindSafe`, and only there.

## Learn more
- [`catch_unwind`](https://doc.rust-lang.org/std/panic/fn.catch_unwind.html) · [`io::Error::other`](https://doc.rust-lang.org/std/io/struct.Error.html#method.other) · [Unwinding](https://doc.rust-lang.org/nomicon/unwinding.html) · The Rust Book: [to panic or not to panic](https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html)

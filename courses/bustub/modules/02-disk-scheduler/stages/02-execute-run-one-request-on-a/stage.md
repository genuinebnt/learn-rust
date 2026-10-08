This stage has 3 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · A dropped promise must not hang the future

**Where this fits.** What if the worker dies, or a request is thrown away, before anyone completes its promise? The future would wait forever. A promise that is dropped without a value must tell its future.

### The task

In `src/common/promise.rs`:
- implement `Drop for Promise<T>`: if the state is still `Pending`, set it to `Broken` and wake the future;
- fill the `Broken` arm in `Future::get`: return `Err(BrokenPromise)`.

(`set` consumes the promise, so `Drop` also runs right after a successful `set`: it must leave `Ready` alone.)

### Tests

- `drop(promise)` makes `get` return `Err(BrokenPromise)` and `is_ready()` true; a getter that was already waiting is woken.
- `set` then drop is *not* a break. A thread that panics while holding the promise breaks it. A promise dropped inside a dropped channel breaks.

### Syntax and methods

```rust
impl<T> Drop for Promise<T> {
    fn drop(&mut self) { /* runs when the value goes out of scope, on every path: return, `?`, panic unwinding */ }
}
let mut state = self.shared.state.lock().unwrap_or_else(PoisonError::into_inner);   // lock even if poisoned: never panic inside drop
matches!(*state, State::Pending)
```

### Notes

`Drop` is Rust's destructor: it is how a `MutexGuard` unlocks and a `File` closes. It runs during **unwinding** when a thread panics, which is exactly when promises must break; and a panic *inside* `drop` during unwinding aborts the process, hence `into_inner` instead of `unwrap` on the possibly-poisoned lock.

### In BusTub

C++ does this for free: destroying a `std::promise` that has a shared state but no value stores a `broken_promise` error in it, and `future::get()` throws it. If `DiskScheduler`'s worker thread died, every pending `future.get()` would throw instead of hanging.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| C: no destructors; every exit path must unlock/close/free by hand (`goto cleanup`) | `Drop` runs on every path |
| C++ destructor `~T()`; RAII; exceptions unwind and run destructors | `impl Drop`; panics unwind and run `Drop` (unless `panic = "abort"`) |
| an exception escaping a destructor → `std::terminate` | a panic in `drop` while unwinding → abort |
| `std::future_error(broken_promise)` | `Err(BrokenPromise)` |
| rule of three/five (copy/move constructors and assignment, destructor) | move by default, copy only with `Clone`; only `Drop` to write |

**Port rule:** RAII classes become types with `Drop`. If the C++ destructor does cleanup that can fail, decide what to do with the error (log it, `let _ =`), since `drop` can't return one.

### Learn more
- [`Drop`](https://doc.rust-lang.org/std/ops/trait.Drop.html) · The Rust Book: [`Drop`](https://doc.rust-lang.org/book/ch15-03-drop.html) · [Unwinding (Nomicon)](https://doc.rust-lang.org/nomicon/unwinding.html) · [Mutex poisoning](https://doc.rust-lang.org/std/sync/struct.Mutex.html#poisoning)
- C++ [`std::promise`](https://en.cppreference.com/w/cpp/thread/promise) (see "broken_promise")

## Part 2 · DiskRequest: who owns the buffer?

**Where this fits.** A request names a page, says read or write, carries the buffer, and carries the promise to complete.

### The task

In `src/storage/disk/disk_scheduler.rs`, implement the two constructors that make a request together with the future for its result:
- `DiskRequest::read(page_id)`: `is_write` false, a zeroed buffer to fill;
- `DiskRequest::write(page_id, data)`: `is_write` true, carrying `data`.

Each also creates the promise/future pair: the promise goes in the request as `callback`, the future is returned.

### Tests

- A read request has a zeroed 8192-byte buffer, the page id, and a future that isn't ready.
- A write request carries the data it was given. The future is connected to the request's callback. Dropping a request breaks its future.

### Syntax and methods

```rust
pub struct DiskRequest { pub is_write: bool, pub data: Box<PageData>, pub page_id: PageId, pub callback: Promise<DiskResult> }
let (callback, future) = promise();                     // the type is inferred from `callback`'s field
Box::new([0; BUSTUB_PAGE_SIZE])                          // a heap-allocated 8 KiB array
(request, future)                                        // return a tuple
```

### Notes

**The design decision of this module.** BusTub's `DiskRequest` holds a raw `char *data_`: the worker thread reads or writes memory the caller also holds, and the caller promises not to touch it until the callback fires. The compiler can't check that promise. In Rust the request **owns** its buffer (`Box<PageData>`): moved to the worker, and *returned through the future*. No sharing, no `unsafe`, no use-after-free. The cost is that the buffer pool will copy a frame into a box before a write (8 KiB `memcpy`), which is also what makes the write safe from concurrent modification: the page written is the snapshot taken when the request was made.

### In BusTub

```cpp
DiskRequest r1{/*is_write=*/true, data, /*page_id=*/0, std::move(promise1)};   // data is a char[BUSTUB_PAGE_SIZE] on the caller's stack
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `char *data` shared between threads, valid "until the callback" by convention | `Box<PageData>` moved into the request and handed back in the result |
| out-parameter `char *buf` for a read | the result carries the buffer: `Result<Box<PageData>>` |
| a dangling `data_` if the caller returns early: use-after-free | impossible: the request owns the memory |
| `std::move(promise1)` into the struct | assigning `callback: promise` moves it |
| aggregate initialisation `DiskRequest{a, b, c, d}` | struct literal `DiskRequest { is_write, data, page_id, callback }` |

**Port rule:** when C/C++ passes `T *buf` to another thread "to fill in", port it as *ownership transfer in, ownership transfer back out* (`Box<T>` or `Vec<u8>` through a channel/future), not as `Arc<Mutex<..>>` unless the buffer really must stay shared.

### Learn more
- The Rust Book: [`Box<T>`](https://doc.rust-lang.org/book/ch15-01-box.html) · [Rust API guidelines](https://rust-lang.github.io/api-guidelines/) on ownership in APIs
- BusTub's [disk_scheduler.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/disk/disk_scheduler.h)

## Part 3 · execute: run one request on a disk

**Where this fits.** The worker's job for one request, with no threads yet, so it can be tested directly.

### The task

In `src/storage/disk/disk_scheduler.rs`:
- `run(disk, is_write, page_id, data)`: call `disk.write_page` for a write, `disk.read_page` (into `data`) for a read, and return its `io::Result<()>`;
- in `execute(disk, request)`: complete the request's `callback` with the buffer if the I/O succeeded (`Ok(data)`), or with the error.

### Tests

- A write then a read of the same page through `execute` round-trips; a write hands its buffer back; an unwritten page reads as zeros.
- A disk that returns `Err` (read-only disk) makes the future's result an `Err` with the same `ErrorKind`.

### Syntax and methods

```rust
let DiskRequest { is_write, mut data, page_id, callback } = request;   // destructuring a struct: moves each field out
disk.read_page(page_id, &mut data)                                      // &mut Box<[u8; N]> derefs to &mut [u8; N]
result.map(|()| data)                                                   // Result<(), E> -> Result<Box<PageData>, E>
callback.set(value)
```

### Notes

`run` is separate from `execute` on purpose: stage 11 will wrap just the call to `run` in a panic guard. A function that does one thing is a function you can wrap.

### In BusTub

```cpp
// the student's StartWorkerThread() loop body:
if (r.is_write_) { disk_manager_->WritePage(r.page_id_, r.data_); }
else             { disk_manager_->ReadPage(r.page_id_, r.data_); }
r.callback_.set_value(true);
```

BusTub's callback carries a `bool`; here it carries the whole `io::Result` and the buffer.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `if (r.is_write_) {...} else {...}` as a statement | `if`/`else` as an expression returning a value |
| `callback_.set_value(true)`: success only, errors lost or logged | `Result<Box<PageData>>`: success carries the buffer, failure carries the `io::Error` |
| `disk_manager_->ReadPage(id, buf)` through a `DiskManager *` | through a `&dyn DiskIo` |
| a request is a struct passed by `std::move` | passed by value; destructure to take it apart |

### Learn more
- The Rust Book: [`Result`](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html) · [destructuring structs](https://doc.rust-lang.org/book/ch19-03-pattern-syntax.html#destructuring-structs)
- [`Result::map`](https://doc.rust-lang.org/std/result/enum.Result.html#method.map)

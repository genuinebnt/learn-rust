This stage has 6 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · DiskRequest: who owns the buffer?

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

## Part 2 · execute: run one request on a disk

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

## Part 3 · DiskScheduler: start the worker and schedule requests

**Where this fits.** All the pieces exist. Now the scheduler itself: a thread that executes requests while the callers carry on.

### The task

In `src/storage/disk/disk_scheduler.rs`:
- `DiskScheduler::new(disk)`: spawn the background thread. It runs `consume` on the request queue, and `execute`s each request on the disk. The thread handle goes in `background_thread`.
- `schedule(requests)`: put each request on the queue **in order**, wrapped in `Some`. Return immediately.

### Tests

- A write and then a read of page 0, scheduled one after the other, see each other: the read returns what was written.
- A batch `[W5, W3, W9, W1, R3]` runs in exactly that order (a recording disk logs it).
- `schedule` returns before a 100 ms read finishes. Four threads each schedule 25 write/read pairs. An empty batch is fine.

### Syntax and methods

```rust
use std::thread;
let handle: thread::JoinHandle<()> = thread::spawn(move || { /* runs on the new thread */ });   // `move`: the closure takes ownership of what it uses
let worker_queue = Arc::clone(&request_queue);        // each owner of an Arc gets its own clone (one atomic increment)
let worker_disk = Arc::clone(&disk);
execute(&*worker_disk, request)                       // &*Arc<dyn DiskIo> -> &dyn DiskIo
```

### Notes

`thread::spawn` needs the closure to be `'static` and `Send`: it can't borrow `self`, so the worker gets *clones of the `Arc`s* it needs. One worker and one FIFO queue make the order of execution equal to the order of scheduling, which is the guarantee callers rely on (a read scheduled after a write of the same page sees it). Stage 14 takes it further.

### In BusTub

```cpp
DiskScheduler::DiskScheduler(DiskManager *disk_manager) : disk_manager_(disk_manager) {
  background_thread_.emplace([&] { StartWorkerThread(); });    // [&] captures `this` by reference: the thread must be joined before `this` dies
}
void DiskScheduler::Schedule(std::vector<DiskRequest> &requests) { /* TODO */ }
```

### The C/C++ way

| C (pthreads) | C++ | Rust |
|---|---|---|
| `pthread_create(&tid, NULL, fn, arg)`; `arg` is a `void *` you cast back | `std::thread t([&] { ... });` captures by reference or value | `thread::spawn(move \|\| { ... })` |
| `pthread_join(tid, NULL)` | `t.join()`; a joinable `std::thread` destroyed without `join` calls `std::terminate` | `handle.join()` → `Result` (an `Err` if the thread panicked); a dropped handle *detaches* |
| `[&]` capture of `this`: **dangling** if the thread outlives the object | same | borrowed captures can't cross `spawn` (`'static`), so you clone `Arc`s: the compiler found the bug for you |
| `std::shared_ptr<T>` copy = refcount (atomic) | | `Arc::clone` |
| `std::vector<DiskRequest> &requests` (a mutable reference, then moved from) | | `Vec<DiskRequest>` by value: the scheduler takes them |

**Port rule:** a C++ lambda thread capturing `[&]` or `[this]` becomes `move` with explicit `Arc` clones of exactly the shared state the thread needs (here: the queue and the disk), not of `self`.

### Learn more
- [`thread::spawn`](https://doc.rust-lang.org/std/thread/fn.spawn.html) · [`JoinHandle`](https://doc.rust-lang.org/std/thread/struct.JoinHandle.html) · The Rust Book: [using threads](https://doc.rust-lang.org/book/ch16-01-threads.html)
- [I/O scheduling](https://en.wikipedia.org/wiki/I/O_scheduling) (what real disk schedulers reorder, and why BusTub's doesn't) · C++ [`std::thread`](https://en.cppreference.com/w/cpp/thread/thread/join)

## Part 4 · Drop: finish the work, stop the worker, join it

**Where this fits.** A scheduler that is dropped must not leave a thread running, or throw away requests.

### The task

Implement `Drop for DiskScheduler` in `src/storage/disk/disk_scheduler.rs`: put the **stop signal** (`None`) on the queue, then **join** the worker thread. Because the queue is FIFO, everything scheduled before the drop runs first.

### Tests

- 20 slow writes scheduled, then `drop(scheduler)`: right after the drop, the disk has performed all 20 and every future is ready.
- After the drop, the worker has ended and let go of its `Arc` to the disk (`Arc::strong_count` goes from 3 back to 1).
- An unused scheduler drops cleanly; twenty schedulers in a row on one disk leave nothing behind.

### Syntax and methods

```rust
impl Drop for DiskScheduler {
    fn drop(&mut self) {
        self.request_queue.put(None);
        if let Some(thread) = self.background_thread.take() {   // Option::take: move the handle out of &mut self
            let _ = thread.join();                               // join(self): needs ownership, hence the Option; ignore a panic result
        }
    }
}
```

### Notes

`join` takes the `JoinHandle` **by value**, but `drop` only has `&mut self`. That is why the field is an `Option<JoinHandle>`: `take()` leaves `None` behind. This `Option::take` dance is the standard way to move a field out in `Drop`.

### In BusTub

```cpp
DiskScheduler::~DiskScheduler() {
  request_queue_.Put(std::nullopt);               // signal the worker to exit
  if (background_thread_.has_value()) { background_thread_->join(); }
}
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| destructor `~DiskScheduler()` | `impl Drop for DiskScheduler` |
| `std::optional<std::thread>` so the destructor can `join` | `Option<JoinHandle<()>>` + `.take()` |
| forgetting `join`: `std::terminate` (C++) or a zombie/detached thread using freed memory (C) | a dropped `JoinHandle` detaches the thread silently; here you join explicitly |
| `delete scheduler;` / `unique_ptr` going out of scope | the value going out of scope, or `drop(x)` |
| order of member destruction is reverse of declaration | fields drop in declaration order, *after* your `drop` body |

**Port rule:** a C++ destructor that stops and joins a thread becomes `Drop` with `Option::take`. Always make shutdown wait for the work already queued, or document that it doesn't.

### Learn more
- [`Option::take`](https://doc.rust-lang.org/std/option/enum.Option.html#method.take) · [`JoinHandle::join`](https://doc.rust-lang.org/std/thread/struct.JoinHandle.html#method.join) · [`Arc::strong_count`](https://doc.rust-lang.org/std/sync/struct.Arc.html#method.strong_count)
- [Drop order](https://doc.rust-lang.org/reference/destructors.html)

## Part 5 · A panicking disk must not kill the worker

**Where this fits.** `DiskManagerMemory` panics when a page is out of range; a bug in any disk could panic. If the worker thread dies, every later request waits forever.

### The task

In `execute` (`src/storage/disk/disk_scheduler.rs`), catch a panic from the disk call and report it to the caller as an `io::Error` (any message containing the word "panicked"). The line that calls `run` is the one to wrap: the stub has the plain call and a TODO.

### Tests

- A read of page 13 on a disk that panics for page 13 gives an `Err` whose text contains "panicked".
- On a scheduler: a panicking request and a good request scheduled after it: the first reports an error, **the second still runs**. Five panics in a row are all caught.
- Requests that don't panic behave as before.

### Syntax and methods

```rust
use std::panic::{catch_unwind, AssertUnwindSafe};
let result = catch_unwind(AssertUnwindSafe(|| run(disk, is_write, page_id, &mut data)))   // Result<io::Result<()>, Box<dyn Any + Send>>
    .unwrap_or_else(|_panic| Err(io::Error::other("the disk panicked")));                 // flatten: a panic becomes an io::Error
```

### Notes

`catch_unwind` needs the closure to be `UnwindSafe`: "if this panics halfway, nobody sees broken state." We hold `&mut data` and a `&dyn DiskIo`, so the compiler can't promise that; `AssertUnwindSafe` is *you* promising. It's fair here: after a panic we discard `data`'s contents anyway and only report the error. Panics are for bugs, not for control flow; catching them belongs at a boundary like this one (a worker, a request handler), never inside the logic.

### In BusTub

C++ has the same problem with exceptions: an exception escaping the lambda passed to `std::thread` calls `std::terminate` and kills the whole process. The BusTub tests never throw from the disk; production code would wrap the call in `try { ... } catch (...) { callback.set_value(false); }`.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `try { disk->ReadPage(..); } catch (const std::exception &e) { ... }` | `catch_unwind(..)` for panics; `Result` for expected failures |
| an uncaught exception in a `std::thread` → `std::terminate` (whole process) | an uncaught panic ends *that thread*; `join()` returns `Err` |
| exceptions for I/O errors, bad arguments, programming errors alike | `Result` for errors you expect; panic for bugs |
| `-fno-exceptions` builds (kernels, some databases) | `panic = "abort"` makes `catch_unwind` useless: unwinding is optional |
| `noexcept` | (no equivalent; a panic can occur anywhere) |

**Port rule:** C++ `catch (...)` at a thread or request boundary → `catch_unwind` + `AssertUnwindSafe`, and only there.

### Learn more
- [`catch_unwind`](https://doc.rust-lang.org/std/panic/fn.catch_unwind.html) · [`io::Error::other`](https://doc.rust-lang.org/std/io/struct.Error.html#method.other) · [Unwinding](https://doc.rust-lang.org/nomicon/unwinding.html) · The Rust Book: [to panic or not to panic](https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html)

## Part 6 · create_promise and deallocate_page

**Where this fits.** Two small methods the buffer pool will call.

### The task

In `src/storage/disk/disk_scheduler.rs`:
- `create_promise()` returns a fresh promise/future pair for a request's callback;
- `deallocate_page(page_id)` asks the disk to delete the page.

### Tests

- `create_promise` gives a working pair; a request built by hand with that promise can be scheduled and completed.
- `deallocate_page(6)` then `(2)` reach the disk in that order.

### Syntax and methods

```rust
promise()                      // from src/common/promise.rs: (Promise<T>, Future<T>)
self.disk.delete_page(page_id) // the scheduler keeps the Arc<dyn DiskIo> it was created with
```

### Notes

`deallocate_page` runs on the **caller's** thread, not the worker's: it skips the queue. That is how BusTub does it too (and why the buffer pool's `delete_page` warns you about ordering with pending writes).

### In BusTub

```cpp
auto CreatePromise() -> DiskSchedulerPromise { return {}; };
void DeallocatePage(page_id_t page_id) { disk_manager_->DeletePage(page_id); }
```

### The C/C++ way

| C++ | Rust |
|---|---|
| `using DiskSchedulerPromise = std::promise<bool>;` (an alias so tests can swap their own promise) | `type DiskResult = io::Result<Box<PageData>>;` + a function returning the pair |
| `DiskManager *disk_manager_ __attribute__((__unused__))` (a raw pointer that must outlive the scheduler) | `Arc<dyn DiskIo>`: shared ownership, the disk lives as long as anyone uses it |
| `inline` one-line member functions in the header | ordinary methods; the compiler inlines as it likes |

**Port rule:** a raw pointer field `T *p` "owned by someone else" becomes `Arc<T>` (shared) or a `&'a T` with a lifetime parameter (borrowed). `Arc` is the right default when the pointee is used from other threads.

### Learn more
- [`Arc`](https://doc.rust-lang.org/std/sync/struct.Arc.html) · The Rust Book: [`Arc<T>`](https://doc.rust-lang.org/book/ch16-03-shared-state.html#atomic-reference-counting-with-arct)

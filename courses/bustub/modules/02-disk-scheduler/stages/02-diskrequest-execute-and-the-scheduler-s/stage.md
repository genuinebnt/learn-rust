A request to the disk needs three things the worker can act on: *what* to do (read or write a page), *which* page, and *where the answer goes*. This stage defines `DiskRequest`, the function that executes one, and the scheduler that owns a worker thread and feeds it.

The design question that matters is **who owns the 8 KiB buffer** while the request is in flight. BusTub passes a raw pointer and relies on the caller not touching it; here the request owns the buffer and returns it through the promise, so there is no moment when two threads may touch it. Getting that hand-off right is the point of the exercise; the thread plumbing around it is short.

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

- A write and then a read of page 0, scheduled one after the other, see each other: the read returns what was written. A batch `[W5, W3, W9, W1, R3]` runs in exactly that order (a recording disk logs it).
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

## Performance

Each request allocates one 8 KiB `Box<PageData>` (a read) or moves one in (a write), plus a promise cell; the worker does one `read_page`/`write_page` and one `set`. So a request costs one heap allocation of 8 KiB, one queue push/pop with a possible wake-up (a few microseconds), and the I/O itself: against a real file the I/O dominates by orders of magnitude, against `DiskManagerUnlimitedMemory` the allocation and the wake-up are the whole cost.

One worker runs requests **one at a time**, so throughput is at most `1 / (latency of one I/O)`: with a 100 µs SSD read that is 10 000 requests per second however many callers there are. That ceiling is what the sharded scheduler in the next stage lifts.

**Measure it.** Schedule 100 000 writes to distinct pages on an in-memory disk and time `schedule` plus waiting for the last future; then count allocations (a counting global allocator, or `dhat`) and confirm it is about two per request. Compare with doing the same writes directly on the disk in a loop to see what the thread hand-off costs.

## Hints

### Does the buffer move with the request, or does the request borrow it?

A `&mut PageData` cannot go into a request that another thread will run: the borrow would have to outlive the caller's stack frame, which the compiler rejects (`'static` bound on `thread::spawn`). Moving a `Box<PageData>` in and out is the way to satisfy both the compiler and the data-race rule. Work out what the *read* request carries (an empty buffer to fill) and what a *write* carries (the page), and what comes back through the promise in each case.

### What does the worker do with an I/O error?

`DiskIo::read_page` returns `io::Result`. The worker has no caller to return it to, so it goes **through the promise**: `DiskResult = io::Result<Box<PageData>>`. The failure then reaches the thread that asked, who can decide to retry or to give up. Check that a failing disk completes the future with `Err` rather than leaving it pending, and that the worker carries on to the next request.

### Why two clones of an Arc and a `move` closure?

The worker thread needs the queue and the disk for its whole life, and `thread::spawn` requires the closure to be `'static`. So the scheduler keeps one `Arc` of each and the worker's closure takes its own clone with `move`. If you capture `self` instead it will not compile: the thread could outlive the scheduler. The same shape (a clone per owner) returns whenever a background thread needs shared state.

**Where this fits.** All the pieces exist. Now the scheduler itself: a thread that executes requests while the callers carry on.

## The task

In `src/storage/disk/disk_scheduler.rs`:
- `DiskScheduler::new(disk)`: spawn the background thread. It runs `consume` on the request queue, and `execute`s each request on the disk. The thread handle goes in `background_thread`.
- `schedule(requests)`: put each request on the queue **in order**, wrapped in `Some`. Return immediately.

## Tests

- A write and then a read of page 0, scheduled one after the other, see each other: the read returns what was written.
- A batch `[W5, W3, W9, W1, R3]` runs in exactly that order (a recording disk logs it).
- `schedule` returns before a 100 ms read finishes. Four threads each schedule 25 write/read pairs. An empty batch is fine.

## Syntax and methods

```rust
use std::thread;
let handle: thread::JoinHandle<()> = thread::spawn(move || { /* runs on the new thread */ });   // `move`: the closure takes ownership of what it uses
let worker_queue = Arc::clone(&request_queue);        // each owner of an Arc gets its own clone (one atomic increment)
let worker_disk = Arc::clone(&disk);
execute(&*worker_disk, request)                       // &*Arc<dyn DiskIo> -> &dyn DiskIo
```

## Notes

`thread::spawn` needs the closure to be `'static` and `Send`: it can't borrow `self`, so the worker gets *clones of the `Arc`s* it needs. One worker and one FIFO queue make the order of execution equal to the order of scheduling, which is the guarantee callers rely on (a read scheduled after a write of the same page sees it). Stage 14 takes it further.

## In BusTub

```cpp
DiskScheduler::DiskScheduler(DiskManager *disk_manager) : disk_manager_(disk_manager) {
  background_thread_.emplace([&] { StartWorkerThread(); });    // [&] captures `this` by reference: the thread must be joined before `this` dies
}
void DiskScheduler::Schedule(std::vector<DiskRequest> &requests) { /* TODO */ }
```

## The C/C++ way

| C (pthreads) | C++ | Rust |
|---|---|---|
| `pthread_create(&tid, NULL, fn, arg)`; `arg` is a `void *` you cast back | `std::thread t([&] { ... });` captures by reference or value | `thread::spawn(move \|\| { ... })` |
| `pthread_join(tid, NULL)` | `t.join()`; a joinable `std::thread` destroyed without `join` calls `std::terminate` | `handle.join()` → `Result` (an `Err` if the thread panicked); a dropped handle *detaches* |
| `[&]` capture of `this`: **dangling** if the thread outlives the object | same | borrowed captures can't cross `spawn` (`'static`), so you clone `Arc`s: the compiler found the bug for you |
| `std::shared_ptr<T>` copy = refcount (atomic) | | `Arc::clone` |
| `std::vector<DiskRequest> &requests` (a mutable reference, then moved from) | | `Vec<DiskRequest>` by value: the scheduler takes them |

**Port rule:** a C++ lambda thread capturing `[&]` or `[this]` becomes `move` with explicit `Arc` clones of exactly the shared state the thread needs (here: the queue and the disk), not of `self`.

## Learn more
- [`thread::spawn`](https://doc.rust-lang.org/std/thread/fn.spawn.html) · [`JoinHandle`](https://doc.rust-lang.org/std/thread/struct.JoinHandle.html) · The Rust Book: [using threads](https://doc.rust-lang.org/book/ch16-01-threads.html)
- [I/O scheduling](https://en.wikipedia.org/wiki/I/O_scheduling) (what real disk schedulers reorder, and why BusTub's doesn't) · C++ [`std::thread`](https://en.cppreference.com/w/cpp/thread/thread/join)

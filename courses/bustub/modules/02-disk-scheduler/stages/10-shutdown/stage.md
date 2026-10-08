**Where this fits.** A scheduler that is dropped must not leave a thread running, or throw away requests.

## The task

Implement `Drop for DiskScheduler` in `src/storage/disk/disk_scheduler.rs`: put the **stop signal** (`None`) on the queue, then **join** the worker thread. Because the queue is FIFO, everything scheduled before the drop runs first.

## Tests

- 20 slow writes scheduled, then `drop(scheduler)`: right after the drop, the disk has performed all 20 and every future is ready.
- After the drop, the worker has ended and let go of its `Arc` to the disk (`Arc::strong_count` goes from 3 back to 1).
- An unused scheduler drops cleanly; twenty schedulers in a row on one disk leave nothing behind.

## Syntax and methods

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

## Notes

`join` takes the `JoinHandle` **by value**, but `drop` only has `&mut self`. That is why the field is an `Option<JoinHandle>`: `take()` leaves `None` behind. This `Option::take` dance is the standard way to move a field out in `Drop`.

## In BusTub

```cpp
DiskScheduler::~DiskScheduler() {
  request_queue_.Put(std::nullopt);               // signal the worker to exit
  if (background_thread_.has_value()) { background_thread_->join(); }
}
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| destructor `~DiskScheduler()` | `impl Drop for DiskScheduler` |
| `std::optional<std::thread>` so the destructor can `join` | `Option<JoinHandle<()>>` + `.take()` |
| forgetting `join`: `std::terminate` (C++) or a zombie/detached thread using freed memory (C) | a dropped `JoinHandle` detaches the thread silently; here you join explicitly |
| `delete scheduler;` / `unique_ptr` going out of scope | the value going out of scope, or `drop(x)` |
| order of member destruction is reverse of declaration | fields drop in declaration order, *after* your `drop` body |

**Port rule:** a C++ destructor that stops and joins a thread becomes `Drop` with `Option::take`. Always make shutdown wait for the work already queued, or document that it doesn't.

## Learn more
- [`Option::take`](https://doc.rust-lang.org/std/option/enum.Option.html#method.take) · [`JoinHandle::join`](https://doc.rust-lang.org/std/thread/struct.JoinHandle.html#method.join) · [`Arc::strong_count`](https://doc.rust-lang.org/std/sync/struct.Arc.html#method.strong_count)
- [Drop order](https://doc.rust-lang.org/reference/destructors.html)

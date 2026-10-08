**Where this fits.** How does a worker blocked in `get` ever stop? BusTub's answer: put a special "stop" element in the queue.

## The task

The channel's elements are `Option<T>`: `Some(request)` is work, `None` is the stop signal (C++'s `std::nullopt`). Implement `consume(channel, f)` in `src/common/channel.rs`: call `f` on each `Some` element as it arrives, in order, and **return when it receives a `None`** (that `None` is consumed).

## Tests

- `Some(1), Some(2), Some(3), None` calls `f` with 1, 2, 3, then `consume` returns.
- Elements after the `None` stay in the channel; a lone `None` ends it at once.
- Run in a worker thread: it sums 1..=10 and ends when stopped. `f` may be a closure that keeps state (`FnMut`).

## Syntax and methods

```rust
while let Some(item) = channel.get() {   // `get()` returns Option<T> here, because the channel holds Options
    f(item);
}
pub fn consume<T>(channel: &Channel<Option<T>>, mut f: impl FnMut(T))   // `impl Trait` in argument position; FnMut can mutate what it captured
```

## Notes

This is the whole protocol of a thread pool: a queue, workers that loop on it, and a sentinel per worker to shut it down. A sentinel is simpler than the alternatives (a shared "stop" flag the workers must poll while asleep, or killing the thread), because it wakes the sleeping worker *through the same door* work comes in.

## In BusTub

```cpp
DiskScheduler::~DiskScheduler() {
  request_queue_.Put(std::nullopt);       // the stop signal
  if (background_thread_.has_value()) { background_thread_->join(); }
}
void DiskScheduler::StartWorkerThread() { /* TODO: loop on request_queue_.Get() until you see std::nullopt */ }
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::optional<T>` (`std::nullopt`, `has_value()`, `*opt`) | `Option<T>` (`None`, `if let Some(x)`, `match`) |
| `while (true) { auto r = q.Get(); if (!r) break; f(*r); }` | `while let Some(item) = channel.get() { f(item) }` |
| `*opt` on an empty optional is **undefined behaviour** | pattern matching forces the `None` case |
| function pointer `void (*f)(T)` + `void *ctx` (C), `std::function<void(T)>` (C++) | `impl FnMut(T)` (static dispatch) or `Box<dyn FnMut(T)>` (dynamic) |
| C worker threads stop with a flag + `pthread_cond_broadcast`, or `pthread_cancel` | a `None` message per worker |

**Port rule:** a `std::function` parameter becomes a generic `impl Fn…` unless it must be stored or chosen at run time; pick `Fn`/`FnMut`/`FnOnce` by whether the callee calls it many times, mutates captures, or consumes them.

## Learn more
- The Rust Book: [closures](https://doc.rust-lang.org/book/ch13-01-closures.html) and [`while let`](https://doc.rust-lang.org/book/ch19-01-all-the-places-for-patterns.html)
- [`std::sync::mpmc` source](https://github.com/rust-lang/rust/blob/master/library/std/src/sync/mpmc/mod.rs) and [crossbeam-channel](https://github.com/crossbeam-rs/crossbeam/tree/master/crossbeam-channel): what a production channel does instead

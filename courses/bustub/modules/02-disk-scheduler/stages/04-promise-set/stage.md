**Where this fits.** When the caller schedules a disk request it wants to wait for *that request* to finish, not for the whole queue. A one-shot promise/future pair is a mailbox for exactly one value.

## The task

`promise::<T>()` (given, in `src/common/promise.rs`) returns a connected `(Promise<T>, Future<T>)` sharing a `Mutex<State<T>>` and a `Condvar`. Implement `Promise::set(self, value)`: store the value as `State::Ready(value)` and wake whoever waits.

## Tests

- `is_ready()` is false before `set`, true after; works with non-`Clone` values and from another thread; two pairs are independent.

## Syntax and methods

```rust
*self.shared.state.lock().unwrap() = State::Ready(value);   // assign through the guard with `*`
self.shared.changed.notify_all();
pub fn set(self, value: T)                                  // `self` by value: the promise is used up, so it can be set only once
```

## Notes

`set(self, ..)` **consumes** the promise. C++'s `std::promise::set_value` can be called twice (the second throws `promise_already_satisfied`); here "set twice" simply doesn't compile. This is the idiom: *encode "at most once" as ownership*.

## In BusTub

```cpp
struct DiskRequest {
  bool is_write_;  char *data_;  page_id_t page_id_;
  std::promise<bool> callback_;     // the worker calls callback_.set_value(true) when the I/O is done
};
```

## The C/C++ way

| C++ | Rust (this module) | Rust (elsewhere) |
|---|---|---|
| `std::promise<T> p; std::future<T> f = p.get_future();` | `let (p, f) = promise::<T>();` | `std::sync::mpsc::sync_channel(1)`, or `tokio::sync::oneshot::channel()` |
| `p.set_value(v);` (UB-ish error if called twice) | `p.set(v)` (consumes `p`) | `tx.send(v)` |
| `std::promise<void>` | `Promise<()>` | |
| C: a struct with `mutex`, `cond`, `done`, `result` and a `pthread_cond_wait` loop | `Shared<T>` with `Mutex<State<T>>` + `Condvar` | |

**Port rule:** a `promise`/`future` pair used once is a one-shot channel. In real Rust code reach for `mpsc::sync_channel(1)` or `oneshot` first; this stage builds one so you know what's inside.

## Learn more
- [Futures and promises](https://en.wikipedia.org/wiki/Futures_and_promises) · C++ [`std::promise`](https://en.cppreference.com/w/cpp/thread/promise) · [tokio's `oneshot`](https://github.com/tokio-rs/tokio/blob/master/tokio/src/sync/oneshot.rs)
- [`mpsc::sync_channel`](https://doc.rust-lang.org/std/sync/mpsc/fn.sync_channel.html)

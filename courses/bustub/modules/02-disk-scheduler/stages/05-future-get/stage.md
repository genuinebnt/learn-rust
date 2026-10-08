**Where this fits.** The other end of the mailbox: the caller waiting for its disk request.

## The task

Implement `Future::get(self) -> Result<T, BrokenPromise>` in `src/common/promise.rs`: **wait while the state is `Pending`**, then take the state out of the mutex (leave `State::Taken` behind) and return the value. (The `Broken` case is the next stage; for now it can be `unreachable!()` or a `todo!()`.)

## Tests

- `get` returns the value that was set (the very value: a `String` is moved, not cloned).
- `get` blocks until another thread calls `set`.
- 100 promises travel through a `Channel` to a worker that answers them; all 100 futures get their answers.

## Syntax and methods

```rust
let mut state = self.shared.changed
    .wait_while(self.shared.state.lock().unwrap(), |s| matches!(s, State::Pending))
    .unwrap();
let taken = std::mem::replace(&mut *state, State::Taken);   // swap a new value in, get the old one out
matches!(expr, Pattern)                                      // expands to a match that returns bool
```

## Notes

You cannot move a value out of a `&mut` (the mutex guard derefs to one): the compiler would be left with a hole. `std::mem::replace` (and `mem::take` for `Default` types) is the way: put a placeholder in, get the original out.

## In BusTub

```cpp
ASSERT_TRUE(future1.get());      // blocks until the worker has called set_value
```

## The C/C++ way

| C++ | Rust |
|---|---|
| `T v = f.get();` blocks; throws `std::future_error` if the promise was broken | `f.get()` returns `Result<T, BrokenPromise>` |
| `f.wait()`, `f.wait_for(duration)`, `f.valid()` | `get` only; `is_ready()` for polling; a timeout version is an exercise |
| `std::move(value)` out of shared state | `mem::replace` / `Option::take` out of the guard |
| a future can be `get()`-ed once; the second call throws | `get(self)` consumes the future |
| `std::shared_future<T>` (many readers) | `Arc<Mutex<..>>`/`OnceLock<T>` (not needed here) |

## Learn more
- [`mem::replace`](https://doc.rust-lang.org/std/mem/fn.replace.html) · [`matches!`](https://doc.rust-lang.org/std/macro.matches.html) · C++ [`std::future`](https://en.cppreference.com/w/cpp/thread/future)
- [`OnceLock`](https://doc.rust-lang.org/std/sync/struct.OnceLock.html): the std type for "set once, read many"

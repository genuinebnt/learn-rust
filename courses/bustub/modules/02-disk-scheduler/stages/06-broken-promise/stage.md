**Where this fits.** What if the worker dies, or a request is thrown away, before anyone completes its promise? The future would wait forever. A promise that is dropped without a value must tell its future.

## The task

In `src/common/promise.rs`:
- implement `Drop for Promise<T>`: if the state is still `Pending`, set it to `Broken` and wake the future;
- fill the `Broken` arm in `Future::get`: return `Err(BrokenPromise)`.

(`set` consumes the promise, so `Drop` also runs right after a successful `set`: it must leave `Ready` alone.)

## Tests

- `drop(promise)` makes `get` return `Err(BrokenPromise)` and `is_ready()` true; a getter that was already waiting is woken.
- `set` then drop is *not* a break. A thread that panics while holding the promise breaks it. A promise dropped inside a dropped channel breaks.

## Syntax and methods

```rust
impl<T> Drop for Promise<T> {
    fn drop(&mut self) { /* runs when the value goes out of scope, on every path: return, `?`, panic unwinding */ }
}
let mut state = self.shared.state.lock().unwrap_or_else(PoisonError::into_inner);   // lock even if poisoned: never panic inside drop
matches!(*state, State::Pending)
```

## Notes

`Drop` is Rust's destructor: it is how a `MutexGuard` unlocks and a `File` closes. It runs during **unwinding** when a thread panics, which is exactly when promises must break; and a panic *inside* `drop` during unwinding aborts the process, hence `into_inner` instead of `unwrap` on the possibly-poisoned lock.

## In BusTub

C++ does this for free: destroying a `std::promise` that has a shared state but no value stores a `broken_promise` error in it, and `future::get()` throws it. If `DiskScheduler`'s worker thread died, every pending `future.get()` would throw instead of hanging.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| C: no destructors; every exit path must unlock/close/free by hand (`goto cleanup`) | `Drop` runs on every path |
| C++ destructor `~T()`; RAII; exceptions unwind and run destructors | `impl Drop`; panics unwind and run `Drop` (unless `panic = "abort"`) |
| an exception escaping a destructor → `std::terminate` | a panic in `drop` while unwinding → abort |
| `std::future_error(broken_promise)` | `Err(BrokenPromise)` |
| rule of three/five (copy/move constructors and assignment, destructor) | move by default, copy only with `Clone`; only `Drop` to write |

**Port rule:** RAII classes become types with `Drop`. If the C++ destructor does cleanup that can fail, decide what to do with the error (log it, `let _ =`), since `drop` can't return one.

## Learn more
- [`Drop`](https://doc.rust-lang.org/std/ops/trait.Drop.html) · The Rust Book: [`Drop`](https://doc.rust-lang.org/book/ch15-03-drop.html) · [Unwinding (Nomicon)](https://doc.rust-lang.org/nomicon/unwinding.html) · [Mutex poisoning](https://doc.rust-lang.org/std/sync/struct.Mutex.html#poisoning)
- C++ [`std::promise`](https://en.cppreference.com/w/cpp/thread/promise) (see "broken_promise")

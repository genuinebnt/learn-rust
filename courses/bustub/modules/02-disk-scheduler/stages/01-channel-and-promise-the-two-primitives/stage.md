This stage has 6 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · Channel::put: add an element and wake a getter

**Where this fits.** The disk scheduler lives on a queue: callers put requests in, a worker takes them out. BusTub's `Channel<T>` is that queue. This module builds it by hand, then a one-shot promise/future, then the scheduler on top.

### The task

`Channel<T>` (given, in `src/common/channel.rs`) is a `Mutex<VecDeque<T>>` plus a `Condvar`. Implement `put(&self, element)`: push the element at the **back** of the queue and wake **one** thread that may be waiting for an element. It never blocks.

### Tests

- A new channel is empty; three `put`s make `len()` 3.
- It accepts values that can't be cloned (`Box`), and is safe to call from four threads at once (100 puts, 100 elements).

### Syntax and methods

```rust
self.queue.lock().unwrap().push_back(element);   // lock() -> LockResult<MutexGuard<VecDeque<T>>>; the guard is dropped at the `;`
self.ready.notify_one();                          // wake one thread waiting on the Condvar (notify_all wakes all)
```

### Notes

A `Condvar` is a place for threads to sleep until *some condition on shared data* might have become true. It never holds the data itself; the data lives in the `Mutex`. Notifying when nobody waits is harmless (the notification is simply lost, which is why getters must *check the queue*, not just wait: next stage).

### In BusTub

```cpp
void Put(T element) {
  std::unique_lock<std::mutex> lk(m_);
  q_.push(std::move(element));
  lk.unlock();                 // unlock first, then notify, so the woken thread doesn't wake only to block on the mutex
  cv_.notify_all();
}
```

### The C/C++ way

| C (pthreads) | C++ | Rust |
|---|---|---|
| `pthread_mutex_lock(&m); push(..); pthread_mutex_unlock(&m); pthread_cond_signal(&c);` | `std::unique_lock<std::mutex> lk(m_); q_.push(std::move(x)); lk.unlock(); cv_.notify_one();` | `self.queue.lock().unwrap().push_back(x); self.ready.notify_one();` |
| `pthread_cond_signal` (one) / `pthread_cond_broadcast` (all) | `notify_one` / `notify_all` | `notify_one` / `notify_all` |
| the mutex and the queue are separate variables | same | `Mutex<VecDeque<T>>` owns the queue |
| `std::move(element)` | | passing `element` by value *is* a move |

**Port rule:** `std::queue<T>` + `std::mutex` + `std::condition_variable` as three members becomes `Mutex<VecDeque<T>>` + `Condvar`. `std::queue` is a container *adaptor* over `deque`; `VecDeque` is the Rust deque.

### Learn more
- [`Condvar`](https://doc.rust-lang.org/std/sync/struct.Condvar.html) · [`VecDeque`](https://doc.rust-lang.org/std/collections/struct.VecDeque.html) · The Rust Book: [shared-state concurrency](https://doc.rust-lang.org/book/ch16-03-shared-state.html)
- *Rust Atomics and Locks*, [Building our own channel](https://marabos.nl/atomics/building-channels.html)

## Part 2 · Channel::get: wait for an element

**Where this fits.** The other half of the queue: the worker sleeping until a request arrives.

### The task

Implement `get(&self) -> T` in `src/common/channel.rs`: if the queue is empty, **sleep until an element is put**; then remove and return the element at the **front**. Several threads may call `get` at once; each element goes to exactly one of them.

### Tests

- Elements come out in the order they went in; each producer's elements stay in order.
- `get` on an empty channel doesn't return until someone puts (checked with a second thread).
- Four getters sharing 100 elements get each exactly once; four producers and one consumer lose nothing (sum of 4 × 1..=1000).

### Syntax and methods

```rust
let mut queue = self.ready
    .wait_while(self.queue.lock().unwrap(), |q| q.is_empty())   // sleeps while the closure is true; returns the re-locked guard
    .unwrap();                                                    // LockResult: poisoned if a thread panicked holding the lock
queue.pop_front()                                                 // Option<T>: Some once the wait is over
```

### Notes

`wait_while` takes the **guard** (it releases the lock while sleeping and reacquires it before returning) and loops on your condition, so it handles two classic traps: **spurious wakeups** (a waiting thread may wake with nothing put) and **stolen wakeups** (two getters woken for one element: the loser must go back to sleep). Never write `if queue.is_empty() { wait }`; always a loop on the condition.

### In BusTub

```cpp
auto Get() -> T {
  std::unique_lock<std::mutex> lk(m_);
  cv_.wait(lk, [&]() { return !q_.empty(); });   // the predicate form of wait is the same loop
  T element = std::move(q_.front());
  q_.pop();
  return element;
}
```

### The C/C++ way

| C (pthreads) | C++ | Rust |
|---|---|---|
| `while (queue_empty(q)) pthread_cond_wait(&c, &m);` (you write the loop) | `cv_.wait(lk, pred)` (the loop is inside) | `condvar.wait_while(guard, pred)` (the loop is inside); `condvar.wait(guard)` is the bare one |
| forget the loop: bug on spurious wakeup (allowed by POSIX) | same | not possible with `wait_while` |
| `q.front(); q.pop();` (two calls; `front()` of an empty queue is **undefined behaviour**) | same | `pop_front()` returns `Option<T>`: emptiness can't be ignored |
| `T element = std::move(q_.front());` | | `pop_front` moves the element out |

**Port rule:** C/C++ `cond_wait` in a `while` loop, or `wait(lk, pred)`, becomes `wait_while(guard, |data| !condition)`. Note the Rust closure says when to *keep waiting*; the C++ predicate says when to *stop*.

### Learn more
- [`Condvar::wait_while`](https://doc.rust-lang.org/std/sync/struct.Condvar.html#method.wait_while) · [Spurious wakeup](https://en.wikipedia.org/wiki/Spurious_wakeup) · [pthread_cond_wait(3p)](https://man7.org/linux/man-pages/man3/pthread_cond_wait.3p.html)
- [Monitors](https://en.wikipedia.org/wiki/Monitor_(synchronization)) (the idea behind mutex + condvar) · [`Crust of Rust: Channels`](https://www.youtube.com/watch?v=b4mS5UPHh20)

## Part 3 · consume: the worker loop and the stop signal

**Where this fits.** How does a worker blocked in `get` ever stop? BusTub's answer: put a special "stop" element in the queue.

### The task

The channel's elements are `Option<T>`: `Some(request)` is work, `None` is the stop signal (C++'s `std::nullopt`). Implement `consume(channel, f)` in `src/common/channel.rs`: call `f` on each `Some` element as it arrives, in order, and **return when it receives a `None`** (that `None` is consumed).

### Tests

- `Some(1), Some(2), Some(3), None` calls `f` with 1, 2, 3, then `consume` returns.
- Elements after the `None` stay in the channel; a lone `None` ends it at once.
- Run in a worker thread: it sums 1..=10 and ends when stopped. `f` may be a closure that keeps state (`FnMut`).

### Syntax and methods

```rust
while let Some(item) = channel.get() {   // `get()` returns Option<T> here, because the channel holds Options
    f(item);
}
pub fn consume<T>(channel: &Channel<Option<T>>, mut f: impl FnMut(T))   // `impl Trait` in argument position; FnMut can mutate what it captured
```

### Notes

This is the whole protocol of a thread pool: a queue, workers that loop on it, and a sentinel per worker to shut it down. A sentinel is simpler than the alternatives (a shared "stop" flag the workers must poll while asleep, or killing the thread), because it wakes the sleeping worker *through the same door* work comes in.

### In BusTub

```cpp
DiskScheduler::~DiskScheduler() {
  request_queue_.Put(std::nullopt);       // the stop signal
  if (background_thread_.has_value()) { background_thread_->join(); }
}
void DiskScheduler::StartWorkerThread() { /* TODO: loop on request_queue_.Get() until you see std::nullopt */ }
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::optional<T>` (`std::nullopt`, `has_value()`, `*opt`) | `Option<T>` (`None`, `if let Some(x)`, `match`) |
| `while (true) { auto r = q.Get(); if (!r) break; f(*r); }` | `while let Some(item) = channel.get() { f(item) }` |
| `*opt` on an empty optional is **undefined behaviour** | pattern matching forces the `None` case |
| function pointer `void (*f)(T)` + `void *ctx` (C), `std::function<void(T)>` (C++) | `impl FnMut(T)` (static dispatch) or `Box<dyn FnMut(T)>` (dynamic) |
| C worker threads stop with a flag + `pthread_cond_broadcast`, or `pthread_cancel` | a `None` message per worker |

**Port rule:** a `std::function` parameter becomes a generic `impl Fn…` unless it must be stored or chosen at run time; pick `Fn`/`FnMut`/`FnOnce` by whether the callee calls it many times, mutates captures, or consumes them.

### Learn more
- The Rust Book: [closures](https://doc.rust-lang.org/book/ch13-01-closures.html) and [`while let`](https://doc.rust-lang.org/book/ch19-01-all-the-places-for-patterns.html)
- [`std::sync::mpmc` source](https://github.com/rust-lang/rust/blob/master/library/std/src/sync/mpmc/mod.rs) and [crossbeam-channel](https://github.com/crossbeam-rs/crossbeam/tree/master/crossbeam-channel): what a production channel does instead

## Part 4 · Promise::set: complete a one-shot

**Where this fits.** When the caller schedules a disk request it wants to wait for *that request* to finish, not for the whole queue. A one-shot promise/future pair is a mailbox for exactly one value.

### The task

`promise::<T>()` (given, in `src/common/promise.rs`) returns a connected `(Promise<T>, Future<T>)` sharing a `Mutex<State<T>>` and a `Condvar`. Implement `Promise::set(self, value)`: store the value as `State::Ready(value)` and wake whoever waits.

### Tests

- `is_ready()` is false before `set`, true after; works with non-`Clone` values and from another thread; two pairs are independent.

### Syntax and methods

```rust
*self.shared.state.lock().unwrap() = State::Ready(value);   // assign through the guard with `*`
self.shared.changed.notify_all();
pub fn set(self, value: T)                                  // `self` by value: the promise is used up, so it can be set only once
```

### Notes

`set(self, ..)` **consumes** the promise. C++'s `std::promise::set_value` can be called twice (the second throws `promise_already_satisfied`); here "set twice" simply doesn't compile. This is the idiom: *encode "at most once" as ownership*.

### In BusTub

```cpp
struct DiskRequest {
  bool is_write_;  char *data_;  page_id_t page_id_;
  std::promise<bool> callback_;     // the worker calls callback_.set_value(true) when the I/O is done
};
```

### The C/C++ way

| C++ | Rust (this module) | Rust (elsewhere) |
|---|---|---|
| `std::promise<T> p; std::future<T> f = p.get_future();` | `let (p, f) = promise::<T>();` | `std::sync::mpsc::sync_channel(1)`, or `tokio::sync::oneshot::channel()` |
| `p.set_value(v);` (UB-ish error if called twice) | `p.set(v)` (consumes `p`) | `tx.send(v)` |
| `std::promise<void>` | `Promise<()>` | |
| C: a struct with `mutex`, `cond`, `done`, `result` and a `pthread_cond_wait` loop | `Shared<T>` with `Mutex<State<T>>` + `Condvar` | |

**Port rule:** a `promise`/`future` pair used once is a one-shot channel. In real Rust code reach for `mpsc::sync_channel(1)` or `oneshot` first; this stage builds one so you know what's inside.

### Learn more
- [Futures and promises](https://en.wikipedia.org/wiki/Futures_and_promises) · C++ [`std::promise`](https://en.cppreference.com/w/cpp/thread/promise) · [tokio's `oneshot`](https://github.com/tokio-rs/tokio/blob/master/tokio/src/sync/oneshot.rs)
- [`mpsc::sync_channel`](https://doc.rust-lang.org/std/sync/mpsc/fn.sync_channel.html)

## Part 5 · Future::get: wait for the value

**Where this fits.** The other end of the mailbox: the caller waiting for its disk request.

### The task

Implement `Future::get(self) -> Result<T, BrokenPromise>` in `src/common/promise.rs`: **wait while the state is `Pending`**, then take the state out of the mutex (leave `State::Taken` behind) and return the value. (The `Broken` case is the next stage; for now it can be `unreachable!()` or a `todo!()`.)

### Tests

- `get` returns the value that was set (the very value: a `String` is moved, not cloned).
- `get` blocks until another thread calls `set`.
- 100 promises travel through a `Channel` to a worker that answers them; all 100 futures get their answers.

### Syntax and methods

```rust
let mut state = self.shared.changed
    .wait_while(self.shared.state.lock().unwrap(), |s| matches!(s, State::Pending))
    .unwrap();
let taken = std::mem::replace(&mut *state, State::Taken);   // swap a new value in, get the old one out
matches!(expr, Pattern)                                      // expands to a match that returns bool
```

### Notes

You cannot move a value out of a `&mut` (the mutex guard derefs to one): the compiler would be left with a hole. `std::mem::replace` (and `mem::take` for `Default` types) is the way: put a placeholder in, get the original out.

### In BusTub

```cpp
ASSERT_TRUE(future1.get());      // blocks until the worker has called set_value
```

### The C/C++ way

| C++ | Rust |
|---|---|
| `T v = f.get();` blocks; throws `std::future_error` if the promise was broken | `f.get()` returns `Result<T, BrokenPromise>` |
| `f.wait()`, `f.wait_for(duration)`, `f.valid()` | `get` only; `is_ready()` for polling; a timeout version is an exercise |
| `std::move(value)` out of shared state | `mem::replace` / `Option::take` out of the guard |
| a future can be `get()`-ed once; the second call throws | `get(self)` consumes the future |
| `std::shared_future<T>` (many readers) | `Arc<Mutex<..>>`/`OnceLock<T>` (not needed here) |

### Learn more
- [`mem::replace`](https://doc.rust-lang.org/std/mem/fn.replace.html) · [`matches!`](https://doc.rust-lang.org/std/macro.matches.html) · C++ [`std::future`](https://en.cppreference.com/w/cpp/thread/future)
- [`OnceLock`](https://doc.rust-lang.org/std/sync/struct.OnceLock.html): the std type for "set once, read many"

## Part 6 · A dropped promise must not hang the future

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

**Where this fits.** The other half of the queue: the worker sleeping until a request arrives.

## The task

Implement `get(&self) -> T` in `src/common/channel.rs`: if the queue is empty, **sleep until an element is put**; then remove and return the element at the **front**. Several threads may call `get` at once; each element goes to exactly one of them.

## Tests

- Elements come out in the order they went in; each producer's elements stay in order.
- `get` on an empty channel doesn't return until someone puts (checked with a second thread).
- Four getters sharing 100 elements get each exactly once; four producers and one consumer lose nothing (sum of 4 × 1..=1000).

## Syntax and methods

```rust
let mut queue = self.ready
    .wait_while(self.queue.lock().unwrap(), |q| q.is_empty())   // sleeps while the closure is true; returns the re-locked guard
    .unwrap();                                                    // LockResult: poisoned if a thread panicked holding the lock
queue.pop_front()                                                 // Option<T>: Some once the wait is over
```

## Notes

`wait_while` takes the **guard** (it releases the lock while sleeping and reacquires it before returning) and loops on your condition, so it handles two classic traps: **spurious wakeups** (a waiting thread may wake with nothing put) and **stolen wakeups** (two getters woken for one element: the loser must go back to sleep). Never write `if queue.is_empty() { wait }`; always a loop on the condition.

## In BusTub

```cpp
auto Get() -> T {
  std::unique_lock<std::mutex> lk(m_);
  cv_.wait(lk, [&]() { return !q_.empty(); });   // the predicate form of wait is the same loop
  T element = std::move(q_.front());
  q_.pop();
  return element;
}
```

## The C/C++ way

| C (pthreads) | C++ | Rust |
|---|---|---|
| `while (queue_empty(q)) pthread_cond_wait(&c, &m);` (you write the loop) | `cv_.wait(lk, pred)` (the loop is inside) | `condvar.wait_while(guard, pred)` (the loop is inside); `condvar.wait(guard)` is the bare one |
| forget the loop: bug on spurious wakeup (allowed by POSIX) | same | not possible with `wait_while` |
| `q.front(); q.pop();` (two calls; `front()` of an empty queue is **undefined behaviour**) | same | `pop_front()` returns `Option<T>`: emptiness can't be ignored |
| `T element = std::move(q_.front());` | | `pop_front` moves the element out |

**Port rule:** C/C++ `cond_wait` in a `while` loop, or `wait(lk, pred)`, becomes `wait_while(guard, |data| !condition)`. Note the Rust closure says when to *keep waiting*; the C++ predicate says when to *stop*.

## Learn more
- [`Condvar::wait_while`](https://doc.rust-lang.org/std/sync/struct.Condvar.html#method.wait_while) · [Spurious wakeup](https://en.wikipedia.org/wiki/Spurious_wakeup) · [pthread_cond_wait(3p)](https://man7.org/linux/man-pages/man3/pthread_cond_wait.3p.html)
- [Monitors](https://en.wikipedia.org/wiki/Monitor_(synchronization)) (the idea behind mutex + condvar) · [`Crust of Rust: Channels`](https://www.youtube.com/watch?v=b4mS5UPHh20)

**Where this fits.** The disk scheduler lives on a queue: callers put requests in, a worker takes them out. BusTub's `Channel<T>` is that queue. This module builds it by hand, then a one-shot promise/future, then the scheduler on top.

## The task

`Channel<T>` (given, in `src/common/channel.rs`) is a `Mutex<VecDeque<T>>` plus a `Condvar`. Implement `put(&self, element)`: push the element at the **back** of the queue and wake **one** thread that may be waiting for an element. It never blocks.

## Tests

- A new channel is empty; three `put`s make `len()` 3.
- It accepts values that can't be cloned (`Box`), and is safe to call from four threads at once (100 puts, 100 elements).

## Syntax and methods

```rust
self.queue.lock().unwrap().push_back(element);   // lock() -> LockResult<MutexGuard<VecDeque<T>>>; the guard is dropped at the `;`
self.ready.notify_one();                          // wake one thread waiting on the Condvar (notify_all wakes all)
```

## Notes

A `Condvar` is a place for threads to sleep until *some condition on shared data* might have become true. It never holds the data itself; the data lives in the `Mutex`. Notifying when nobody waits is harmless (the notification is simply lost, which is why getters must *check the queue*, not just wait: next stage).

## In BusTub

```cpp
void Put(T element) {
  std::unique_lock<std::mutex> lk(m_);
  q_.push(std::move(element));
  lk.unlock();                 // unlock first, then notify, so the woken thread doesn't wake only to block on the mutex
  cv_.notify_all();
}
```

## The C/C++ way

| C (pthreads) | C++ | Rust |
|---|---|---|
| `pthread_mutex_lock(&m); push(..); pthread_mutex_unlock(&m); pthread_cond_signal(&c);` | `std::unique_lock<std::mutex> lk(m_); q_.push(std::move(x)); lk.unlock(); cv_.notify_one();` | `self.queue.lock().unwrap().push_back(x); self.ready.notify_one();` |
| `pthread_cond_signal` (one) / `pthread_cond_broadcast` (all) | `notify_one` / `notify_all` | `notify_one` / `notify_all` |
| the mutex and the queue are separate variables | same | `Mutex<VecDeque<T>>` owns the queue |
| `std::move(element)` | | passing `element` by value *is* a move |

**Port rule:** `std::queue<T>` + `std::mutex` + `std::condition_variable` as three members becomes `Mutex<VecDeque<T>>` + `Condvar`. `std::queue` is a container *adaptor* over `deque`; `VecDeque` is the Rust deque.

## Learn more
- [`Condvar`](https://doc.rust-lang.org/std/sync/struct.Condvar.html) · [`VecDeque`](https://doc.rust-lang.org/std/collections/struct.VecDeque.html) · The Rust Book: [shared-state concurrency](https://doc.rust-lang.org/book/ch16-03-shared-state.html)
- *Rust Atomics and Locks*, [Building our own channel](https://marabos.nl/atomics/building-channels.html)

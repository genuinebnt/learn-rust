---
title: Async versus threads: when each one is the right tool
summary: What an `async fn` really is (a state machine polled by an executor), what `.await` does and does not do, the one rule (never block the executor), and a decision table for choosing between threads, a thread pool and async tasks.
minutes: 9
---
Threads and async solve different problems. A **thread** is a unit of *scheduling by the operating system*: it can run on its own core and it can block. An **async task** is a unit of *scheduling by your program*: many tasks share a few threads, and a task gives up its thread only at an `.await`.

## What an `async fn` is

`async fn f() -> T` returns a **future**: a value (a state machine the compiler writes) with one method, `poll`, which runs the code until the next `.await` that cannot finish yet and then returns `Pending`. Three consequences:

- **Futures are lazy.** Calling `f()` runs nothing; the body starts at the first `poll`.
- **`.await` is a yield point, not a thread switch.** It polls the inner future; if that is `Pending`, this task returns `Pending` too and the executor runs another task on the same thread.
- **Rust ships no executor.** The standard library defines `Future`, `Waker` and `async`; a runtime (`tokio`, `smol`, `async-std`) provides the executor, the timers and the non-blocking I/O (on `epoll`, `kqueue` or `io_uring`).

## The one rule: never block the executor

If an async task calls something that blocks the thread (`std::fs::read`, `std::thread::sleep`, a `Mutex::lock` held for long, a CPU loop), every other task on that thread waits. Use the runtime's async version, or move the work off the executor (`tokio::task::spawn_blocking`, a thread pool). A `std::sync::MutexGuard` held across an `.await` is worse: the task may be resumed on another thread and the guard is not `Send`, so the compiler rejects it.

## Choosing

| the work is | use | because |
|---|---|---|
| CPU-bound (sorting, hashing, a query operator) | threads or a pool (`rayon`, `std::thread::scope`) | async adds nothing: the task never waits, so it never yields |
| a few blocking calls, a few concurrent jobs | threads | simplest; a thread costs about 8 MiB of *address space* but only touched memory |
| tens of thousands of mostly idle connections | async tasks | a task is a few hundred bytes; a thread each would exhaust memory and scheduler time |
| blocking disk I/O (`fsync`, `read`) | a thread pool, or a runtime that uses `io_uring` | regular files have no readiness notification on Linux; `epoll` does not help |
| a mix | an async front end with `spawn_blocking` for the blocking parts | keeps the executor responsive |

A database engine is mostly CPU and disk, so its core uses **threads** (this course's disk scheduler is a worker thread with a channel); the *network layer* in front of it is where async often sits.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::thread`, `std::async` (a thread, not a state machine) | `std::thread::spawn` |
| C++20 coroutines (`co_await`) with a library such as Boost.Asio or libunifex | `async` / `.await` with `tokio` |
| `std::future` (blocking `get()`) | a Rust `Future` you `.await`; `block_on` is the blocking `get()` |
| thread pool (`std::jthread` plus a queue) | `rayon`, `threadpool`, `tokio`'s blocking pool |

**Port rule:** C++ `std::future` is a *handle to a result on another thread*; a Rust `Future` is *the computation itself*, started only by polling.

## In real code

### Using it: a tiny executor, to see that futures are lazy and `.await` yields

This is the whole machinery in about thirty lines; a real runtime adds a reactor and a work-stealing queue.

```rust test
use std::future::Future;
use std::pin::{pin, Pin};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::task::{Context, Poll, Wake, Waker};

struct NoopWake;
impl Wake for NoopWake {
    fn wake(self: Arc<Self>) {}
}

/// Polls one future to completion on this thread (a busy loop is enough for a demo).
fn block_on<F: Future>(f: F) -> F::Output {
    let waker = Waker::from(Arc::new(NoopWake));
    let mut cx = Context::from_waker(&waker);
    let mut f = pin!(f);
    loop {
        if let Poll::Ready(v) = f.as_mut().poll(&mut cx) {
            return v;
        }
    }
}

/// Returns `Pending` once, then `Ready`: what an `.await` on slow I/O looks like to the executor.
struct YieldNow(bool);
impl Future for YieldNow {
    type Output = ();
    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        if self.0 {
            Poll::Ready(())
        } else {
            self.0 = true;
            cx.waker().wake_by_ref();
            Poll::Pending
        }
    }
}

#[test]
fn an_async_fn_does_nothing_until_it_is_polled() {
    let ran = Arc::new(AtomicUsize::new(0));
    let r = ran.clone();
    let fut = async move {
        r.fetch_add(1, Ordering::SeqCst);
        7
    };
    assert_eq!(ran.load(Ordering::SeqCst), 0, "creating the future ran no code");
    assert_eq!(block_on(fut), 7);
    assert_eq!(ran.load(Ordering::SeqCst), 1);
}

#[test]
fn two_tasks_on_one_thread_interleave_at_their_awaits() {
    let log = Arc::new(Mutex::new(Vec::new()));
    let task = |name: &'static str, log: Arc<Mutex<Vec<String>>>| async move {
        for step in 1..=2 {
            log.lock().unwrap().push(format!("{name}{step}"));
            YieldNow(false).await; // give the thread to the other task
        }
    };
    let mut tasks: Vec<Pin<Box<dyn Future<Output = ()>>>> =
        vec![Box::pin(task("a", log.clone())), Box::pin(task("b", log.clone()))];
    // a round-robin executor: poll each unfinished task once per round
    let waker = Waker::from(Arc::new(NoopWake));
    let mut cx = Context::from_waker(&waker);
    while !tasks.is_empty() {
        tasks.retain_mut(|t| t.as_mut().poll(&mut cx).is_pending());
    }
    assert_eq!(*log.lock().unwrap(), ["a1", "b1", "a2", "b2"], "one thread, two tasks, switching only at .await");
}
```

### Using it: the same fan-out with threads

```rust test
#[test]
fn cpu_bound_work_belongs_on_threads() {
    let chunks: Vec<Vec<u64>> = (0..4).map(|c| (c * 1000..(c + 1) * 1000).collect()).collect();
    let total: u64 = std::thread::scope(|s| {
        let handles: Vec<_> = chunks.iter().map(|ch| s.spawn(move || ch.iter().sum::<u64>())).collect();
        handles.into_iter().map(|h| h.join().unwrap()).sum()
    });
    assert_eq!(total, (0..4000u64).sum::<u64>());
}
```

### In the exercises

- **1b-02:** the disk scheduler's `Promise` and `Future` are a *one-shot channel* you block on, not Rust's `async` futures; the *promises and futures* article draws the line.
- **1g-02:** a read of a page waits on a lock, which is the blocking style this course uses throughout; nothing here is `async`.

### Where it is used

- **tokio** (the common runtime), **smol**, and **monoio / glommio** (thread-per-core, `io_uring`) are the executors; **hyper**, **axum** and **sqlx** are async libraries built on them (this project's own API is axum).
- **PostgreSQL** uses a process per connection and **MySQL** a thread per connection; **ScyllaDB** and **Redis** (I/O threads) use event loops; each is a trade-off from the table above.

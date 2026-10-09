---
title: Promises and futures: a result that arrives later
summary: The one-shot promise/future pair that tells a caller its request is done, its four states, why set and get consume their owner, and what a dropped promise means.
minutes: 8
---
When the buffer pool asks the disk scheduler to read a page, it does not wait: it gets back a **future** and carries on. The worker thread holds the matching **promise** and fills it in when the I/O is done. This pair is how a value crosses from one thread to another exactly once.

## Two halves of one channel

```rust
let (promise, future) = promise::<DiskResult>();     // connected, nothing in them yet
// ... the promise goes to the worker inside the request ...
promise.set(Ok(buffer));                             // worker side: fill it in, wake the waiter
let result = future.get();                           // caller side: wait for it
```

Both halves share one heap cell, an `Arc<Shared>` holding a `Mutex<State>` and a `Condvar`: the same ingredients as the blocking queue, specialised to a single value.

```svg
caption: A promise is in exactly one of four states. set and get each happen once because they consume their half; dropping the promise before set breaks it, so a waiting get returns an error instead of hanging.
<svg viewBox="0 0 760 210" role="img" aria-label="State machine: Pending to Ready on set, Ready to Taken on get, Pending to Broken on drop">
<defs><marker id="pf-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="hot" x="40" y="70" width="130" height="50" rx="6"/><text class="mid t-a" x="105" y="100">Pending</text>
<rect class="live" x="330" y="30" width="130" height="50" rx="6"/><text class="mid t-g" x="395" y="60">Ready(v)</text>
<rect class="box" x="600" y="30" width="130" height="50" rx="6"/><text class="mid dim" x="665" y="60">Taken</text>
<rect class="bad" x="330" y="130" width="130" height="50" rx="6"/><text class="mid t-r" x="395" y="160">Broken</text>
<path class="ln-g" d="M170 85 C240 85 260 55 328 55" marker-end="url(#pf-a)"/><text class="t-g sm" x="210" y="50">promise.set(v)</text>
<path class="ln" d="M460 55 H598" marker-end="url(#pf-a)"/><text class="dim sm" x="488" y="48">future.get()</text>
<path class="ln-w" d="M170 108 C240 108 260 155 328 155" marker-end="url(#pf-a)"/><text class="t-w sm" x="196" y="170">promise dropped first</text>
<text class="t-r sm" x="470" y="160">get() &#8594; Err(BrokenPromise)</text>
</svg>
```

## Four states

| state | meaning | next |
|---|---|---|
| `Pending` | nobody has set a value yet | `set` makes it `Ready`; dropping the promise makes it `Broken` |
| `Ready(v)` | the value is waiting | `get` takes it and leaves `Taken` |
| `Broken` | the promise was dropped without setting a value | `get` returns `Err(BrokenPromise)` |
| `Taken` | the future has already taken the value | (terminal) |

`get` waits (on the condvar) while the state is `Pending`, then `mem::replace`s the state with `Taken` and returns what was there.

## Consuming `self`: use-once, enforced by the type

`Promise::set(self, value)` and `Future::get(self)` take `self` **by value**. After `promise.set(x)`, the name `promise` is moved-from and cannot be used again: *the compiler guarantees a promise is fulfilled at most once.* The same holds for `get`. C++ has to check at run time: `std::promise::set_value` twice throws `promise_already_satisfied`; `std::future::get` twice is undefined or throws.

## A promise that is dropped

If the worker panics or exits without calling `set`, the future would wait forever. The promise's `Drop` therefore flips `Pending` to `Broken` and wakes the waiters, so `get` returns `Err(BrokenPromise)`. C++'s `std::promise` does the same, storing a `broken_promise` error.

> [!WARNING] A hang is the worst failure
> A waiting thread that nobody will ever wake is a deadlock, and a deadlock gives no error message. `Drop` for the promise exists to turn that silent hang into an `Err`. Whenever you write code that hands a "wake me" token to another thread, ask what happens to the waiter if the other thread dies.

## Not Rust's `async` futures

Rust also has `std::future::Future`, a different thing: a *poll-based* state machine driven by an executor, which does nothing until polled. The `Future` in this module is the C++ meaning (`std::future`): a handle to a result being computed on another thread, which a thread blocks on. The names are the same by accident of history; the stages here use blocking futures because BusTub's disk scheduler does.

| | C++ | Rust (this course) |
|---|---|---|
| create | `std::promise<T> p; auto f = p.get_future();` | `let (p, f) = promise::<T>();` |
| fulfil | `p.set_value(v);` (throws if called twice) | `p.set(v)` (consumes `p`: cannot be called twice) |
| wait | `f.get()` (rethrows a stored exception) | `f.get()` returns `Result<T, BrokenPromise>` |
| a dropped promise | stores a `broken_promise` error | `Drop` marks the state `Broken` |
| the value is taken | `f.get()` once, then `valid() == false` | `get(self)` consumes the future |

## In real code

### The API (this course's own)

| call | what it does |
|---|---|
| `let (p, f) = promise::<T>();` | a connected pair, nothing set yet |
| `p.set(value)` | completes the future; consumes `p`, so it can happen once |
| `f.get()` | blocks until completed: `Ok(value)` or `Err(BrokenPromise)`; consumes `f` |
| `f.is_ready()` | true if `get` would not block |
| drop `p` without `set` | the future's `get` returns `Err(BrokenPromise)` instead of hanging |

The standard library has no blocking promise, but `std::sync::mpsc` gives you the same hand-off with a channel of one element, which is the quickest way to see the pattern in real code:

```rust test
use std::sync::mpsc;
use std::thread;

fn spawn_read(page: u32) -> mpsc::Receiver<Result<Vec<u8>, String>> {
    let (tx, rx) = mpsc::channel();                           // tx plays the promise, rx the future
    thread::spawn(move || {
        let data = if page == 13 { Err("bad page".to_string()) } else { Ok(vec![page as u8; 4]) };
        let _ = tx.send(data);                                // set
    });
    rx
}

#[test]
fn a_one_shot_result_through_a_channel() {
    let f1 = spawn_read(7);
    let f2 = spawn_read(13);
    // both reads are running at once; we wait only when we need the answer
    assert_eq!(f1.recv().unwrap().unwrap(), vec![7, 7, 7, 7]);
    assert_eq!(f2.recv().unwrap(), Err("bad page".to_string()));
}

#[test]
fn a_dropped_sender_ends_the_wait() {
    let (tx, rx) = mpsc::channel::<u32>();
    drop(tx);                                                 // the "promise" died without setting a value
    assert!(rx.recv().is_err());                              // recv returns an error instead of hanging: BrokenPromise
}
```

A hand-written promise is a `Mutex<State>` plus a `Condvar`, exactly the structure in the previous concept; this is its use:

```rust test
use std::sync::{Arc, Condvar, Mutex};
use std::thread;

enum State<T> { Pending, Ready(T), Taken }

struct Shared<T> { state: Mutex<State<T>>, changed: Condvar }

fn promise<T>() -> (impl FnOnce(T), impl FnOnce() -> T) {
    let shared = Arc::new(Shared { state: Mutex::new(State::Pending), changed: Condvar::new() });
    let s2 = Arc::clone(&shared);
    let set = move |v: T| {
        *s2.state.lock().unwrap() = State::Ready(v);
        s2.changed.notify_all();
    };
    let get = move || {
        let mut st = shared.changed.wait_while(shared.state.lock().unwrap(), |s| matches!(s, State::Pending)).unwrap();
        match std::mem::replace(&mut *st, State::Taken) {
            State::Ready(v) => v,
            _ => unreachable!("the wait ended, and a future is read once"),
        }
    };
    (set, get)
}

#[test]
fn set_on_one_thread_get_on_another() {
    let (set, get) = promise::<&'static str>();
    let worker = thread::spawn(move || set("done"));
    assert_eq!(get(), "done");
    worker.join().unwrap();
}
```

### In the exercises

- **1b-02:** `Promise::set(self, v)`, `Future::get(self)` and `Drop for Promise` are the third example plus the `Broken` state (the first example's second test shows the behaviour you must reproduce).
- **1b-03:** a `DiskRequest` carries a `Promise<DiskResult>`; the worker calls `callback.set(result)`.
- **1f-01, 1f-02:** the pool hands the disk scheduler a request and waits on its future for the page (or for the write to finish).

### Where it is used

- **Async I/O in databases**: BusTub's disk scheduler returns a future per request so the buffer pool can start several reads and wait for each when it needs the page.
- **Request/response across threads**: an actor or worker pool answers a caller through a one-shot channel (Tokio's `oneshot` is the async version; `crossbeam`'s `bounded(1)` the blocking one).
- **Parallel fan-out**: spawn N tasks, keep N futures, collect the results in order.
- **Group commit**: each committing transaction holds a future that the log flusher completes when its record is durable.

---
title: Worker threads, move closures and the stop signal
summary: How a background thread is started and owned, what the 'static and Send bounds are protecting you from, and why a queue is stopped by putting a sentinel in it.
minutes: 8
---
The disk scheduler is a classic *producer/consumer* arrangement: any number of threads put requests on a queue, and one **worker thread** takes them off and does the slow part. Three things have to be got right: starting the worker, handing it what it needs, and stopping it.

## Starting a thread

```rust
let queue = Arc::new(Channel::new());
let worker_queue = Arc::clone(&queue);          // a second owner, for the worker
let worker_disk = Arc::clone(&disk);
let handle: JoinHandle<()> = std::thread::spawn(move || {
    consume(&worker_queue, |request| execute(&*worker_disk, request));
});
```

`thread::spawn` takes a closure and returns a `JoinHandle`. Two rules in its signature do most of the safety work:

- **`F: 'static`**: the closure may not borrow anything from the spawning function's stack, because the new thread may outlive it. That is why the worker gets *clones* of the `Arc`s, not references to `self`'s fields. `move` makes the closure take ownership of what it uses.
- **`F: Send`** (and the captured values `Send`): everything handed to the thread must be safe to move to another thread. An `Rc` is not (its counter is not atomic), an `Arc<Mutex<_>>` is.

C++ has neither check: `std::thread t([this] { ... });` captures `this` by pointer, and if the scheduler is destroyed first the thread runs on a dangling pointer. Rust refuses to compile the equivalent.

```svg
caption: Requests go into the FIFO queue in order and the stop signal goes in last, so the worker finishes everything scheduled before it. The scheduler then joins the worker.
<svg viewBox="0 0 760 190" role="img" aria-label="A queue with three requests and a stop sentinel, consumed by a worker thread, joined by the owner">
<defs><marker id="wt-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<text class="dim sm" x="20" y="30">schedule()</text>
<rect class="box" x="120" y="44" width="70" height="44" rx="4"/><text class="mid fg sm" x="155" y="70">req 3</text>
<rect class="box" x="196" y="44" width="70" height="44" rx="4"/><text class="mid fg sm" x="231" y="70">req 2</text>
<rect class="box" x="272" y="44" width="70" height="44" rx="4"/><text class="mid fg sm" x="307" y="70">req 1</text>
<rect class="bad" x="64" y="44" width="50" height="44" rx="4"/><text class="mid t-r sm" x="89" y="70">None</text>
<path class="ln" d="M20 66 H60" marker-end="url(#wt-a)"/>
<text class="dim sm" x="64" y="110">queue (FIFO)</text>
<path class="ln" d="M342 66 H420" marker-end="url(#wt-a)"/>
<rect class="blue" x="424" y="36" width="200" height="60" rx="4"/><text class="mid t-b" x="524" y="62">worker thread</text><text class="mid dim sm" x="524" y="80">get &#8594; execute &#8594; get &#8594; ...</text>
<path class="ln-w dash" d="M624 66 H690"/><text class="t-w sm" x="634" y="58">None: return</text>
<rect class="hot" x="424" y="130" width="200" height="38" rx="4"/><text class="mid t-a sm" x="524" y="154">owner: handle.join()</text>
<path class="ln-w" d="M524 98 V128" marker-end="url(#wt-a)"/>
</svg>
```

## Stopping it: the sentinel

A worker blocked in `get` on an empty queue cannot be told to stop by a flag it never checks. BusTub's answer, and this course's, is to put a **sentinel** in the queue itself: the queue holds `Option<DiskRequest>`, and `None` means "stop".

```rust
pub fn consume<T>(channel: &Channel<Option<T>>, mut f: impl FnMut(T)) {
    while let Some(item) = channel.get() {
        f(item);
    }
}                                  // a None ended the loop: the worker returns
```

Because the queue is first-in-first-out, **everything scheduled before the `None` is processed first**. Shutdown therefore does not drop work: `put(None)` means "finish what is queued, then stop".

| way to stop a worker | works when | trade-off |
|---|---|---|
| a sentinel in the queue (`None`) | the worker blocks on the queue | in-order, drains first; one sentinel per worker |
| an `AtomicBool` "stop" flag | the worker polls it | the worker must wake up to look: needs a timeout on every wait |
| closing the channel (`mpsc`: drop the `Sender`) | you use `std::sync::mpsc` | the receiver sees `Err` when all senders are gone; no custom sentinel |
| cancelling the thread | never | there is no safe thread cancellation; `pthread_cancel` is a footgun |

## Joining

`handle.join()` waits for the thread to finish and returns `Result<T, Box<dyn Any + Send>>`: the `Err` is the panic payload if the worker panicked. Dropping a `JoinHandle` without joining **detaches** the thread: it keeps running, and the process may exit under it. The disk scheduler joins in `Drop` (see the concept on clean shutdown), so a finished test has no worker left running.

> [!PORT] `std::thread` versus `JoinHandle`
> In C++, destroying a joinable `std::thread` calls `std::terminate`, so every owner needs a destructor that joins (or you use C++20's `std::jthread`, which joins for you). In Rust a dropped handle detaches silently, so the burden is the other way: if you need the work finished, you must `join`.

## In real code

### The API you will use

| call | what it does | when |
|---|---|---|
| `thread::spawn(f)` → `JoinHandle<T>` | start a thread; `f: FnOnce() -> T + Send + 'static` | background workers |
| `handle.join()` | wait; `Err(payload)` if the thread panicked | shutdown, collecting results |
| `thread::Builder::new().name("disk-worker".into()).spawn(f)` | a named thread (shows in panics and profilers) | production code |
| `thread::current().id()` / `.name()` | which thread am I | logging |
| `Option<JoinHandle<()>>` + `.take()` | store a handle you must consume in `Drop` | the standard idiom |

```rust test
use std::collections::VecDeque;
use std::sync::{Arc, Condvar, Mutex};
use std::thread::{self, JoinHandle};

struct Pool {
    queue: Arc<(Mutex<VecDeque<Option<u32>>>, Condvar)>,      // None = stop
    worker: Option<JoinHandle<Vec<u32>>>,
}

impl Pool {
    fn new() -> Pool {
        let queue = Arc::new((Mutex::new(VecDeque::new()), Condvar::new()));
        let q = Arc::clone(&queue);
        let worker = thread::Builder::new().name("worker".into()).spawn(move || {
            let mut done = Vec::new();
            loop {
                let item = {
                    let (m, cv) = &*q;
                    let mut g = cv.wait_while(m.lock().unwrap(), |g| g.is_empty()).unwrap();
                    g.pop_front().unwrap()
                };
                match item {
                    Some(x) => done.push(x * 2),
                    None => return done,                          // the sentinel: stop after everything queued before it
                }
            }
        });
        Pool { queue, worker: Some(worker.unwrap()) }
    }
    fn submit(&self, x: u32) {
        self.queue.0.lock().unwrap().push_back(Some(x));
        self.queue.1.notify_one();
    }
    fn finish(mut self) -> Vec<u32> {
        self.queue.0.lock().unwrap().push_back(None);
        self.queue.1.notify_one();
        self.worker.take().unwrap().join().unwrap()
    }
}

#[test]
fn work_queued_before_the_stop_signal_runs() {
    let pool = Pool::new();
    for x in 1..=3 {
        pool.submit(x);
    }
    assert_eq!(pool.finish(), vec![2, 4, 6]);
}
```

```rust test
use std::thread;

#[test]
fn join_reports_a_panic() {
    let h = thread::spawn(|| -> u32 { panic!("worker bug") });
    let err = h.join().unwrap_err();                              // the panic payload
    assert_eq!(err.downcast_ref::<&str>(), Some(&"worker bug"));

    let ok = thread::spawn(|| 7).join().unwrap();
    assert_eq!(ok, 7);
}
```

### In the exercises

- **1b-03 (`DiskScheduler::new`):** spawn the worker with `move`, giving it clones of the queue `Arc` and the disk `Arc`; store `Some(handle)` in the scheduler. The first example is the same structure in miniature.
- **1b-01 (`consume`):** the loop `while let Some(item) = channel.get() { f(item) }` is the worker body: `None` ends it.
- **1b-04 (`Drop`):** `put(None)`, then `self.background_thread.take()` and `join()`: the `finish` method above, written as `Drop`.
- **1b-06:** one such worker *per shard*, each with its own queue and its own sentinel.

### Where it is used

- **Thread pools** (Rayon, Tokio's blocking pool, a web server's workers) are N of these with a shared queue.
- **Background services in databases**: the log flusher, the checkpointer, the page cleaner and the deadlock detector are each one worker thread with a stop signal.
- **Graceful shutdown of any service**: stop accepting new work, put the sentinel behind what is queued, wait for the join.

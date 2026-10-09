---
title: Clean shutdown: Drop, join and ordering
summary: How the scheduler stops its worker without losing queued requests, why the order of put(None) and join matters, and the deadlocks that a Drop impl can create.
minutes: 7
---
Starting a thread is one line; stopping it correctly is the part with bugs. The disk scheduler's `Drop` is the whole story in six lines, and each line is there for a reason.

```rust
impl Drop for DiskScheduler {
    fn drop(&mut self) {
        self.request_queue.put(None);                          // 1. tell the worker: after the queued requests, stop
        if let Some(thread) = self.background_thread.take() {  // 2. take the handle out of the Option
            let _ = thread.join();                             // 3. wait until the worker has really finished
        }
    }
}
```

## Why each step

1. **`put(None)` first.** The worker is parked in `get()` on an empty queue; nothing wakes it except an element. The `None` is that element, and since the queue is FIFO, every request scheduled earlier runs first: a caller who dropped the scheduler right after `schedule(..)` still gets its writes done.
2. **`take()` on an `Option<JoinHandle>`.** `join(self)` consumes the handle, but `drop` only has `&mut self`, and you cannot move a field out of a borrowed struct. Holding the handle in an `Option` lets you `take()` it, leaving `None` behind. This is the standard idiom for "a field I must consume in `Drop`".
3. **`join()` last.** Without it the worker may still be running when the scheduler's other fields are dropped, and a test may finish while a thread writes to a file the next test reopens. `join` makes "dropped" mean "nothing of mine is still running".

The result of `join()` is ignored with `let _ =`: if the worker panicked there is nothing useful `drop` can do, and panicking inside `drop` while another panic unwinds aborts the process.

```svg
caption: Shutdown, in order. The owner puts the stop signal behind whatever is queued, the worker finishes those requests and sees the signal, returns, and only then does join return in the owner's Drop.
<svg viewBox="0 0 760 210" role="img" aria-label="Sequence of the owner dropping the scheduler and the worker draining its queue before stopping">
<defs><marker id="cs-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<text class="big" x="20" y="64">owner (Drop)</text><text class="big" x="20" y="150">worker</text>
<line class="grid" x1="130" y1="58" x2="740" y2="58"/><line class="grid" x1="130" y1="144" x2="740" y2="144"/>
<rect class="hot" x="140" y="42" width="130" height="32" rx="4"/><text class="mid t-a sm" x="205" y="62">put(None)</text>
<rect class="hot" x="280" y="42" width="330" height="32" rx="4" style="fill:none;stroke-dasharray:4 4"/><text class="mid dim sm" x="445" y="62">join(): blocked, waiting</text>
<rect class="live" x="610" y="42" width="130" height="32" rx="4"/><text class="mid t-g sm" x="675" y="62">join returns</text>
<rect class="blue" x="140" y="128" width="150" height="32" rx="4"/><text class="mid t-b sm" x="215" y="148">execute req 1</text>
<rect class="blue" x="296" y="128" width="150" height="32" rx="4"/><text class="mid t-b sm" x="371" y="148">execute req 2</text>
<rect class="bad" x="452" y="128" width="150" height="32" rx="4"/><text class="mid t-r sm" x="527" y="148">get() &#8594; None: return</text>
<path class="ln-g dash" d="M606 128 V76" marker-end="url(#cs-a)"/>
<text class="dim sm" x="140" y="196">time &#8594;     requests queued before the None are still served</text>
</svg>
```

## Things that go wrong

| bug | what happens | the fix |
|---|---|---|
| forgetting `put(None)` | `join` waits forever for a worker that waits forever for a request | always signal before joining |
| joining before signalling | the same deadlock, with the lines swapped | signal first |
| dropping the scheduler **from the worker thread** (a request that owns an `Arc<DiskScheduler>`) | a thread cannot join itself: it deadlocks or fails, depending on the platform | never give the worker a way to own its owner |
| `thread::spawn` without keeping the handle | the thread is detached; you cannot wait for it | store the `JoinHandle` |
| a panicking worker | `join()` returns `Err`; queued requests never complete; their promises were dropped (futures return `BrokenPromise`) | catch panics per request (previous concept) |

> [!PORT] C++
> `~DiskScheduler() { request_queue_.Put(std::nullopt); if (background_thread_.has_value()) { background_thread_->join(); } }`. The same three steps, with `std::optional<std::thread>` where Rust has `Option<JoinHandle>`. Forget the `join()` in C++ and `~thread()` calls `std::terminate` on a joinable thread; forget it in Rust and the thread is silently detached. C++20's `std::jthread` joins in its destructor.

## Scoped threads: no handle to manage

When the threads do not need to outlive a function, `std::thread::scope` makes shutdown automatic: all threads spawned in the scope are joined before it returns, and they may *borrow* local variables (no `'static` and no `Arc` needed). The tests use it so that a test cannot end with a thread still running. A long-lived worker like the scheduler's cannot be scoped, which is why it needs `Drop`.

## In real code

### The API you will use

| tool | what it does | when |
|---|---|---|
| `impl Drop for T { fn drop(&mut self) }` | runs when the value goes out of scope | stopping what the type started |
| `Option<T>::take()` | move a value out of `&mut self`, leaving `None` | consuming a handle in `drop` |
| `handle.join()` | wait for a thread to finish | the last step of shutdown |
| `drop(x)` | drop early, on purpose | releasing a guard or a scheduler before the end of scope |
| `std::mem::ManuallyDrop` | suppress the automatic drop | rare: FFI and unsafe code |

```rust test
use std::sync::mpsc::{channel, Sender};
use std::sync::{Arc, Mutex};
use std::thread::{self, JoinHandle};

struct Scheduler {
    tx: Option<Sender<u32>>,
    worker: Option<JoinHandle<()>>,
}

impl Scheduler {
    fn new(log: Arc<Mutex<Vec<u32>>>) -> Scheduler {
        let (tx, rx) = channel::<u32>();
        let worker = thread::spawn(move || {
            for x in rx {                                         // ends when every Sender is dropped
                thread::sleep(std::time::Duration::from_millis(2));
                log.lock().unwrap().push(x);
            }
        });
        Scheduler { tx: Some(tx), worker: Some(worker) }
    }
    fn schedule(&self, x: u32) {
        self.tx.as_ref().unwrap().send(x).unwrap();
    }
}

impl Drop for Scheduler {
    fn drop(&mut self) {
        drop(self.tx.take());                                     // 1. close the queue: the worker will see the end after the queued work
        if let Some(w) = self.worker.take() {
            let _ = w.join();                                     // 2. wait for it
        }
    }
}

#[test]
fn dropping_the_scheduler_finishes_the_queue() {
    let log = Arc::new(Mutex::new(Vec::new()));
    {
        let s = Scheduler::new(Arc::clone(&log));
        for x in 1..=5 {
            s.schedule(x);
        }
    }                                                             // drop runs here, and does not return before the work is done
    assert_eq!(*log.lock().unwrap(), vec![1, 2, 3, 4, 5]);
}
```

```rust test
use std::sync::Mutex;

struct Guard<'a>(&'a Mutex<Vec<&'static str>>, &'static str);
impl Drop for Guard<'_> {
    fn drop(&mut self) { self.0.lock().unwrap().push(self.1); }
}

#[test]
fn fields_drop_in_declaration_order() {
    let log = Mutex::new(Vec::new());
    struct Pair<'a> { first: Guard<'a>, second: Guard<'a> }
    {
        let _p = Pair { first: Guard(&log, "first"), second: Guard(&log, "second") };
    }
    assert_eq!(*log.lock().unwrap(), vec!["first", "second"]);   // declaration order (C++ destroys members in the reverse order)
}
```

### In the exercises

- **1b-04:** `impl Drop for DiskScheduler` is the first example, with the course's `Channel<Option<_>>` and a `None` sentinel where the example closes a channel. Check with a test that schedules work, drops the scheduler, and asserts the work ran.
- **1b-06:** the sharded scheduler's `Drop` repeats this for every queue and every worker: signal all, then join all.
- **1g-01 (guards):** the same `Drop` shape releases a latch and a pin; the field order decides what is released first (second example).

### Where it is used

- **Every owner of a background thread or a connection**: HTTP servers, database connection pools, log writers: `Drop` (or an explicit `shutdown()`) signals and joins.
- **Flush-on-close**: `BufWriter` flushes in `drop`; a database flushes dirty pages in its shutdown path.
- **Tests**: a test that spawns workers should drop its subject before asserting, so no thread is still running when the next test starts.

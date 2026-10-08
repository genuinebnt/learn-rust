---
title: Condition variables and blocking queues
summary: How a thread waits for "something to be true" without spinning, why the wait always sits in a loop on a predicate, and how the disk scheduler's Channel is built from a Mutex and a Condvar.
minutes: 9
---
A **blocking queue** is a queue where `get` on an empty queue puts the caller to sleep until someone `put`s. It is the glue between the threads of every database: the disk scheduler's request queue, a thread pool's task queue, the log writer's buffer. You build one from a lock and a **condition variable**.

## The problem a condition variable solves

A mutex answers "who may touch the data right now". It cannot answer "wake me when the data is *worth* touching". The naive answer is to spin:

```rust
loop {
    let mut q = queue.lock().unwrap();
    if let Some(x) = q.pop_front() { return x; }
    // nothing yet: unlock and try again... burning a core
}
```

A condition variable lets a thread **atomically release the mutex and go to sleep**, and be woken later with the mutex held again. The two operations that must be atomic are "unlock" and "start waiting": if they were separate, a `put` could slip in between and its wake-up would be lost.

## The shape of every correct wait

```rust
pub struct Channel<T> {
    queue: Mutex<VecDeque<T>>,
    ready: Condvar,
}

pub fn get(&self) -> T {
    let mut queue = self.ready.wait_while(self.queue.lock().unwrap(), |q| q.is_empty()).unwrap();
    queue.pop_front().expect("the wait only ends with an element in the queue")
}

pub fn put(&self, element: T) {
    self.queue.lock().unwrap().push_back(element);
    self.ready.notify_one();
}
```

`wait_while(guard, pred)` is shorthand for: *while `pred` is true, wait.* The condition ("the queue is empty") is **state stored under the mutex**, and the wait is always inside a loop that re-checks it.

```svg
caption: A consumer calls get on an empty queue and sleeps (the mutex is released while it waits). The producer's put takes the mutex, pushes, and notifies; the consumer wakes holding the mutex again, re-checks the predicate, and pops.
<svg viewBox="0 0 760 250" role="img" aria-label="Timeline of a consumer waiting on a condvar and a producer notifying it">
<text class="big" x="20" y="62">consumer</text><text class="big" x="20" y="182">producer</text>
<line class="grid" x1="110" y1="56" x2="740" y2="56"/><line class="grid" x1="110" y1="176" x2="740" y2="176"/>
<rect class="live" x="120" y="40" width="110" height="32" rx="4"/><text class="mid t-g sm" x="175" y="60">lock, empty?</text>
<rect class="never" x="230" y="40" width="200" height="32" rx="4"/><text class="mid dim sm" x="330" y="60">asleep in wait (mutex free)</text>
<rect class="live" x="430" y="40" width="130" height="32" rx="4"/><text class="mid t-g sm" x="495" y="60">woken: lock held</text>
<rect class="hot" x="560" y="40" width="150" height="32" rx="4"/><text class="mid t-a sm" x="635" y="60">empty? no: pop_front</text>
<rect class="live" x="300" y="160" width="130" height="32" rx="4"/><text class="mid t-g sm" x="365" y="180">lock, push_back</text>
<rect class="blue" x="430" y="160" width="120" height="32" rx="4"/><text class="mid t-b sm" x="490" y="180">notify_one()</text>
<path class="ln-b" d="M490 158 V74" marker-end="url(#cv-a)"/>
<defs><marker id="cv-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--fn)"/></marker></defs>
<text class="dim sm" x="120" y="230">time &#8594;</text>
<text class="t-w sm" x="120" y="108">1. get() on an empty queue</text><text class="t-w sm" x="120" y="124">2. wait releases the mutex and sleeps</text>
<text class="t-w sm" x="560" y="108">3. the predicate is checked again</text>
</svg>
```

## Why a loop, never an `if`

1. **Spurious wakeups.** The standard allows `wait` to return when nobody notified. Checking the predicate again makes them harmless.
2. **Stolen wakeups.** With two consumers, one `put` wakes one of them, but a third thread may take the element first; the woken thread finds the queue empty again and must go back to sleep.
3. **Lost notifications.** `notify_one` does nothing if nobody is waiting yet. A thread that arrives *after* the notify must find the state already true. That is why the state lives in the queue, not in the notification: the condvar says "look again", the queue says what you will find.

> [!WARNING] The classic bug
> `if queue.is_empty() { queue = condvar.wait(queue).unwrap(); }` followed by `queue.pop_front().unwrap()` works in a demo and panics under load, because of (1) and (2). In C++ the same bug is `if (q.empty()) cv.wait(lock);`. The fix is the same in both languages: `while`, or the predicate overload.

## `notify_one` or `notify_all`

`put` adds one element, so waking one consumer is enough: `notify_one`. Waking all of them (`notify_all`) is correct but wasteful: every waiter wakes, one wins, the rest go back to sleep (a *thundering herd*). Use `notify_all` when the change might satisfy *several* different waiters, or when waiters wait on different conditions on one condvar. The one-shot `Promise::set` uses `notify_all` for that reason: there may be a thread waiting in `get` and another in `is_ready`.

| | C++ | Rust |
|---|---|---|
| the pair | `std::mutex m; std::condition_variable cv;` | `Mutex<T>` + `Condvar` (the data is inside the mutex) |
| wait on a predicate | `cv.wait(lock, [&]{ return !q.empty(); });` | `cv.wait_while(guard, \|q\| q.is_empty())` |
| wait without one (a loop is on you) | `cv.wait(lock);` | `cv.wait(guard)` |
| with a timeout | `cv.wait_for(lock, 100ms, pred)` | `cv.wait_timeout_while(guard, dur, pred)` |
| wake one / all | `notify_one()` / `notify_all()` | `notify_one()` / `notify_all()` |
| you hold | a `unique_lock` you pass in | the `MutexGuard`, which `wait` takes and gives back |

Note the last row: in Rust the guard is **moved into** `wait` and returned, so you cannot forget that the lock is released while you sleep, and you cannot touch the data without the lock afterwards.

## In real code

### The API you will use

| call | what it does | when |
|---|---|---|
| `Condvar::new()` | creates the wake-up half; always paired with a `Mutex` that holds the state | construction |
| `cv.wait(guard)` | releases the lock, sleeps, re-acquires on wake; returns the guard | the raw primitive: put it in a `while` loop |
| `cv.wait_while(guard, \|s\| cond)` | the loop for you: sleeps while `cond` is true | **prefer this** |
| `cv.wait_timeout_while(guard, dur, \|s\| cond)` | same with a deadline; tells you if it timed out | never wait forever |
| `cv.notify_one()` / `notify_all()` | wake one / every waiter | after changing the state under the lock |
| `std::sync::mpsc::channel()` | std's ready-made multi-producer, single-consumer queue | when one consumer is enough |

```rust test
use std::collections::VecDeque;
use std::sync::{Arc, Condvar, Mutex};
use std::thread;

struct Channel<T> {
    queue: Mutex<VecDeque<T>>,
    ready: Condvar,
}

impl<T> Channel<T> {
    fn new() -> Self {
        Channel { queue: Mutex::new(VecDeque::new()), ready: Condvar::new() }
    }
    fn put(&self, x: T) {
        self.queue.lock().unwrap().push_back(x);
        self.ready.notify_one();
    }
    fn get(&self) -> T {
        let mut q = self.ready.wait_while(self.queue.lock().unwrap(), |q| q.is_empty()).unwrap();
        q.pop_front().unwrap()
    }
}

#[test]
fn a_getter_waits_for_the_putter() {
    let ch = Arc::new(Channel::new());
    let consumer = {
        let ch = Arc::clone(&ch);
        thread::spawn(move || (ch.get(), ch.get()))          // starts first, finds the queue empty, sleeps
    };
    thread::sleep(std::time::Duration::from_millis(20));
    ch.put("a");
    ch.put("b");
    assert_eq!(consumer.join().unwrap(), ("a", "b"));
}
```

```rust test
use std::sync::{Arc, Condvar, Mutex};
use std::thread;
use std::time::Duration;

#[test]
fn wait_with_a_deadline() {
    let state = Arc::new((Mutex::new(false), Condvar::new()));       // the (flag, condvar) pair is the classic shape
    let (lock, cv) = &*state;
    let (guard, timeout) = cv.wait_timeout_while(lock.lock().unwrap(), Duration::from_millis(30), |done| !*done).unwrap();
    assert!(timeout.timed_out());                                      // nobody set the flag
    assert!(!*guard);

    drop(guard);
    let s2 = Arc::clone(&state);
    thread::spawn(move || {
        *s2.0.lock().unwrap() = true;
        s2.1.notify_all();
    });
    let done = cv.wait_while(lock.lock().unwrap(), |done| !*done).unwrap();
    assert!(*done);
}
```

```rust test
use std::sync::mpsc;
use std::thread;

#[test]
fn std_channel_when_you_do_not_need_your_own() {
    let (tx, rx) = mpsc::channel::<u32>();
    let producers: Vec<_> = (0..3).map(|i| { let tx = tx.clone(); thread::spawn(move || tx.send(i).unwrap()) }).collect();
    drop(tx);                                             // when every sender is gone, recv() returns Err: the stop signal
    for p in producers { p.join().unwrap(); }
    let mut got: Vec<u32> = rx.iter().collect();
    got.sort();
    assert_eq!(got, vec![0, 1, 2]);
}
```

### In the exercises

- **1b-01 Part 1 and 2 (`Channel::put` / `get`):** the first example is the whole exercise in miniature. `put` pushes under the lock and `notify_one`s; `get` uses `wait_while(..., |q| q.is_empty())` so a getter that arrives early sleeps and one that is woken too late goes back to sleep.
- **1b-01 Part 3 (`consume`):** a loop of `channel.get()` that stops when it receives `None`: the `Option` is the stop signal (see the worker-threads concept).
- **Part 5 (`Future::get`):** the same pair with a state enum instead of a queue; you need `wait_while(.., |s| matches!(s, State::Pending))` and `notify_all`.
- **Tests you can write yourself:** start the consumer thread first and sleep before putting, as the first example does; it fails if `get` spins or loses a wake-up.

### Where it is used

- **Every thread pool and task queue**: Tokio's blocking pool, Rayon's job queue, a database's connection pool all park idle workers on a condvar or a futex.
- **The log writer in a database**: transactions append to a buffer and wait on a condvar until the flusher thread has made their record durable (*group commit*).
- **Lock managers**: a transaction that cannot get a row lock sleeps on a condvar tied to that lock's queue (module 4).
- **Backpressure**: a bounded queue makes `put` wait on a second condvar while full: producers slow to the consumer's pace.

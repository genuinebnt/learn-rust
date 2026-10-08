---
title: Panics, unwinding and keeping a worker alive
summary: What a panic does to a thread, why a poisoned Mutex is a feature, and when (rarely) to catch one with catch_unwind: the disk worker's boundary.
minutes: 8
---
A **panic** is Rust's response to a bug: an index out of range, an `unwrap()` on `None`, a failed `assert!`. It is not an exception you handle in the normal flow; it is the program saying an invariant broke. But threads make it matter: *what should happen to the rest of the system when one worker thread panics?*

## What a panic does

1. The panic message is printed (`thread '<name>' panicked at src/x.rs:12:5:`).
2. The thread **unwinds**: it walks back up its call stack, running every `Drop` on the way (guards unlock, files close, promises are broken).
3. If nothing catches it, the *thread* ends. The *process* continues, unless it was the main thread or the build uses `panic = "abort"`, in which case it stops at once without unwinding.

C++ has the same shape with exceptions: unwinding runs destructors, but an exception that escapes a `std::thread`'s function calls `std::terminate` and kills the whole process. A Rust panic in a worker ends only that worker.

| | C++ | Rust |
|---|---|---|
| a bug | `assert` / `BUSTUB_ASSERT` aborts the process | `assert!` panics; unwinds; the thread dies |
| recoverable failure | an exception, or an error code | `Result<T, E>` |
| escaping a thread | `std::terminate()`: the process dies | the thread ends; `join()` returns `Err(payload)` |
| cleanup on the way out | destructors run | `Drop` runs |

## The consequences for a worker

If the disk scheduler's worker panics inside `disk.write_page(..)`, three things happen. The worker thread ends, so **no later request will ever be served**. The request being run had a `Promise` in its callback; unwinding dropped it, so that caller's future returns `Err(BrokenPromise)` instead of hanging. And any `MutexGuard` the worker held (inside the disk, say) is dropped *during a panic*, so that mutex is now **poisoned**: every other thread's `lock()` returns `Err`.

Poisoning is the type system's way of saying "the data behind this lock may be half-updated". It turns one thread's bug into a loud failure everywhere instead of silent corruption: a feature, until you want a single bad request not to take the whole disk down.

```svg
caption: A panic inside the disk call unwinds the worker's frames. Without a catch the thread ends and later requests are never served; with catch_unwind at the request boundary, only that request fails and the worker returns to its queue.
<svg viewBox="0 0 760 230" role="img" aria-label="Two call stacks; one unwinds through the worker loop and ends the thread, the other is caught at the request boundary">
<defs><marker id="pu-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--bad)"/></marker></defs>
<text class="big" x="20" y="24">no catch</text><text class="big" x="400" y="24">catch_unwind in execute</text>
<rect class="box" x="20" y="40" width="300" height="34" rx="3"/><text class="fg sm" x="32" y="62">consume (worker loop)</text>
<rect class="box" x="20" y="78" width="300" height="34" rx="3"/><text class="fg sm" x="32" y="100">execute(request)</text>
<rect class="bad" x="20" y="116" width="300" height="34" rx="3"/><text class="t-r sm" x="32" y="138">disk.write_page: panic!</text>
<path class="ln-w" d="M335 130 V56" marker-end="url(#pu-a)"/><text class="t-r sm" x="348" y="96">unwinds</text>
<text class="t-r sm" x="20" y="176">thread ends; promise dropped &#8594; BrokenPromise;</text><text class="t-r sm" x="20" y="192">every later request waits forever</text>
<rect class="box" x="400" y="40" width="340" height="34" rx="3"/><text class="fg sm" x="412" y="62">consume (worker loop)</text>
<rect class="live" x="400" y="78" width="340" height="34" rx="3"/><text class="t-g sm" x="412" y="100">execute: catch_unwind boundary</text>
<rect class="bad" x="400" y="116" width="340" height="34" rx="3"/><text class="t-r sm" x="412" y="138">disk.write_page: panic!</text>
<path class="ln-w" d="M728 130 V104" marker-end="url(#pu-a)"/>
<text class="t-g sm" x="400" y="176">this request gets Err("the disk panicked");</text><text class="t-g sm" x="400" y="192">the worker goes back to get()</text>
</svg>
```

## `catch_unwind` at a boundary

You can stop an unwind at a chosen frame with `std::panic::catch_unwind`, which runs a closure and returns `Err(payload)` if it panicked:

```rust
let result = catch_unwind(AssertUnwindSafe(|| run(disk, is_write, page_id, &mut data)))
    .unwrap_or_else(|_| Err(io::Error::other("the disk panicked")));
callback.set(result.map(|()| data));          // the caller learns about it; the worker lives on
```

The worker now turns a panicking disk into an `Err` for *that one request* and goes back to its queue.

Rules for using it well:

- **Catch at a boundary you own** (a worker loop, a request handler, an FFI edge), not around arbitrary code, and never as a way to do control flow. Errors you expect are `Result`s.
- **`AssertUnwindSafe` is a promise**: the closure captures `&mut data`, which may be half-written when the panic hits. You assert that nothing observes it in that state; here `data` is only handed back inside an `Err`, so the buffer is not returned.
- **It does not catch aborts** (`panic = "abort"`, a stack overflow, a segfault). Tests run with unwinding on.
- It will not fix a poisoned mutex inside the disk: that is why the in-memory test disks have no lock held across the panicking call.

> [!WHY] Is catching a panic honest?
> It trades a crash for a degraded service. That is right for a database worker thread (a bad request should fail, not stop all I/O) and wrong for code that has lost its invariants (a corrupted page table). Decide which one your worker is, and write the decision in a comment above the `catch_unwind`.

## In real code

### The API you will use

| call | what it does | when |
|---|---|---|
| `panic!("msg {x}")` / `assert!` / `unwrap()` / `expect("why")` | start a panic | a bug, a violated assumption |
| `std::panic::catch_unwind(AssertUnwindSafe(\|\| f()))` | run `f`, return `Err(payload)` if it panicked | a boundary you own: a worker's request loop |
| `std::panic::resume_unwind(payload)` | continue a caught panic | re-raise after cleanup |
| `handle.join()` | `Err(payload)` when a thread panicked | collecting a worker's outcome |
| `err.downcast_ref::<&str>()` / `::<String>()` | read the panic message | reporting |
| `std::panic::set_hook(..)` | change what is printed | tests, services |
| `#[should_panic(expected = "text")]` | a test that must panic with that text | pinning a contract |

```rust test
use std::panic::{catch_unwind, AssertUnwindSafe};

fn risky(x: u32) -> u32 {
    if x == 0 { panic!("zero is not allowed") }
    100 / x
}

#[test]
fn a_boundary_turns_a_panic_into_an_error() {
    let ok = catch_unwind(|| risky(4));
    assert_eq!(ok.unwrap(), 25);

    let bad = catch_unwind(|| risky(0));
    let payload = bad.unwrap_err();
    assert_eq!(payload.downcast_ref::<&str>(), Some(&"zero is not allowed"));
}

#[test]
fn worker_loop_survives_one_bad_request() {
    let mut results = Vec::new();
    for x in [4, 0, 5] {
        let mut acc = 0u32;                                       // state the closure mutates: AssertUnwindSafe says "I accept that"
        let r = catch_unwind(AssertUnwindSafe(|| { acc = risky(x); acc }));
        results.push(r.map_err(|_| "failed".to_string()));
    }
    assert_eq!(results, vec![Ok(25), Err("failed".to_string()), Ok(20)]);   // the loop went on after the panic
}
```

```rust test
use std::sync::{Arc, Mutex};
use std::thread;

#[test]
fn a_panic_with_a_guard_poisons_the_mutex() {
    let m = Arc::new(Mutex::new(1));
    let m2 = Arc::clone(&m);
    let _ = thread::spawn(move || {
        let _g = m2.lock().unwrap();
        panic!("died holding the lock");
    })
    .join();
    assert!(m.is_poisoned());
    let value = *m.lock().unwrap_or_else(|e| e.into_inner());     // recover the data if you can prove it is consistent
    assert_eq!(value, 1);
}

#[test]
#[should_panic(expected = "ran out of disk space")]
fn a_contract_pinned_by_should_panic() {
    let capacity = 4;
    let page = 9;
    assert!(page < capacity, "page {page} on a disk of {capacity}: ran out of disk space");
}
```

### In the exercises

- **1b-03 Part 2:** wrap the disk call in `catch_unwind(AssertUnwindSafe(..))`, map a panic to `Err(io::Error::other("the disk panicked"))` and `set` it on the request's promise (the second test above is the loop you need).
- **1a-07:** `DiskManagerMemory` panics with "ran out of disk space"; the stage tests use `#[should_panic(expected = ...)]` as in the last example, so your message must contain that text.
- **Every stage with a `remove` or an out-of-range id:** decide panic versus `None` as in the contract above and make the message name the offender.

### Where it is used

- **Servers**: a request handler runs inside a catch boundary so one bad request returns a 500 instead of killing the process (web frameworks do this for you).
- **Thread pools**: a panicking task must not kill the pool thread; Rayon and Tokio catch it and surface it through the join handle.
- **Tests**: the harness itself catches each test's panic and reports a failure; `should_panic` is `catch_unwind` with an assertion.
- **FFI boundaries**: a panic must not unwind into C code; a catch at the boundary turns it into an error code.

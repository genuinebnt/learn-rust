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

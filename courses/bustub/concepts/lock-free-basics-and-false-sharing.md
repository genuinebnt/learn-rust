---
title: Lock-free basics and false sharing
summary: Compare-and-swap loops as the building block of lock-free code, why the ABA problem exists, and how two threads incrementing different counters can still slow each other down when the counters share a cache line.
minutes: 8
---
Locks are simple and usually right (see *coarse and fine-grained locking*). When a lock is the bottleneck, or a thread must never block, **lock-free** code builds on one primitive: **compare-and-swap (CAS)**. `compare_exchange(current, new)` atomically sets a value to `new` only if it still equals `current`, and tells you whether it did. A **CAS loop** reads, computes, and retries if somebody changed the value meanwhile:

```text
loop {
    let seen = x.load();
    let wanted = f(seen);
    if x.compare_exchange(seen, wanted).is_ok() { break; }   // else: someone else won; try again
}
```

`fetch_add`, `fetch_max` and friends are CAS loops done by the hardware or the library. `fetch_update(f)` runs the loop for you.

## Why lock-free is hard

- **ABA.** A value goes A to B and back to A between your read and your CAS; the CAS succeeds although the world changed (a stack node popped and pushed back, a recycled pointer). Fixes: a version counter next to the value (a *tagged pointer*), or hazard pointers or epoch reclamation so a node cannot be reused while anyone may still hold it.
- **Memory ordering.** Every atomic call takes an `Ordering` (see *atomics ordering*). A CAS that publishes data needs `Release` on success and `Acquire` on the reads that consume it. Loom (see *testing concurrent code*) is the tool for checking this.
- **Progress.** *Lock-free* means some thread always makes progress; *wait-free* means every thread does. A CAS loop under heavy contention can starve one thread.

For most application code, an atomic counter or a `Mutex` is the right answer. Lock-free structures belong in libraries (`crossbeam`, `tokio`) that have been model-checked.

## False sharing

A CPU reads memory in **cache lines** (64 bytes on x86-64 and most ARM; 128 on Apple M-series). If two threads write *different* variables that sit on the **same line**, each write invalidates the other core's copy: the line ping-pongs between cores, and both threads slow down although they share nothing logically. That is **false sharing**.

The fix is padding: align each hot variable to its own cache line (`#[repr(align(64))]`, or `crossbeam_utils::CachePadded`). This course's count-min sketch keeps one flat array of counters (good for memory, and each item touches `depth` different lines); a very hot per-thread counter array is where padding would pay.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::atomic<T>::compare_exchange_weak` in a loop | `AtomicX::compare_exchange_weak` or `fetch_update` |
| `alignas(std::hardware_destructive_interference_size)` | `#[repr(align(64))]` (or the line size you measured) |
| `std::memory_order_*` | `Ordering::{Relaxed, Acquire, Release, AcqRel, SeqCst}` |
| ABA solved with tagged pointers or hazard pointers | the same; `crossbeam-epoch` provides epochs |

**Port rule:** a C++ CAS loop is `fetch_update` or `compare_exchange_weak` in a `loop`; padding for false sharing is an aligned wrapper struct.

## In real code

### Using it: a CAS loop and fetch_update

```rust test
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::thread;

/// A maximum register updated lock-free: only ever raises the value.
fn raise(max: &AtomicU64, v: u64) {
    let mut seen = max.load(Ordering::Relaxed);
    while v > seen {
        match max.compare_exchange_weak(seen, v, Ordering::AcqRel, Ordering::Relaxed) {
            Ok(_) => return,
            Err(now) => seen = now, // somebody else changed it: look again
        }
    }
}

#[test]
fn many_threads_raising_one_register_leave_the_maximum() {
    let max = Arc::new(AtomicU64::new(0));
    let hs: Vec<_> = (0..8u64)
        .map(|t| {
            let max = max.clone();
            thread::spawn(move || (0..1000u64).for_each(|i| raise(&max, t * 1000 + i)))
        })
        .collect();
    hs.into_iter().for_each(|h| h.join().unwrap());
    assert_eq!(max.load(Ordering::SeqCst), 7999);
}

#[test]
fn fetch_update_is_the_loop_written_for_you() {
    let a = AtomicU64::new(10);
    assert_eq!(a.fetch_update(Ordering::SeqCst, Ordering::SeqCst, |x| (x < 100).then_some(x * 2)), Ok(10));
    assert_eq!(a.load(Ordering::SeqCst), 20);
    let b = AtomicU64::new(200);
    assert_eq!(b.fetch_update(Ordering::SeqCst, Ordering::SeqCst, |x| (x < 100).then_some(x * 2)), Err(200), "the closure refused: nothing changed");
}
```

### Using it: padding to a cache line

```rust test
use std::sync::atomic::{AtomicU64, Ordering};

#[repr(align(64))]
struct Padded(AtomicU64);

#[test]
fn a_padded_counter_fills_a_whole_cache_line() {
    assert_eq!(std::mem::align_of::<Padded>(), 64);
    assert_eq!(std::mem::size_of::<Padded>(), 64);
    assert_eq!(std::mem::size_of::<AtomicU64>(), 8, "eight unpadded counters would share one line");
}

#[test]
fn separate_padded_counters_count_independently() {
    let counters: Vec<Padded> = (0..4).map(|_| Padded(AtomicU64::new(0))).collect();
    std::thread::scope(|s| {
        for (i, c) in counters.iter().enumerate() {
            s.spawn(move || (0..10_000).for_each(|_| { c.0.fetch_add(i as u64 + 1, Ordering::Relaxed); }));
        }
    });
    let totals: Vec<u64> = counters.iter().map(|c| c.0.load(Ordering::Relaxed)).collect();
    assert_eq!(totals, vec![10_000, 20_000, 30_000, 40_000]);
}
```

### In the exercises

- **0d-01:** the sketch's atomic counters (`fetch_add`), and where padding would matter.
- **0d-02:** the register "keep the maximum" update that the lock-free `raise` above implements without a lock.
- **4a-02:** `last_commit_ts` is an atomic read under the watermark lock.

### Where it is used

- **crossbeam** (epoch-based reclamation, `CachePadded`), **tokio**'s task queues, the Linux kernel's RCU, and database latch-free indexes (the Bw-tree).
- The Rust Atomics and Locks book (Mara Bos) covers CAS loops, ordering and ABA in depth.

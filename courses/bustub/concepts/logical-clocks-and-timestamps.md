---
title: Logical clocks: counting events instead of reading the time
summary: Why a replacer, a lock manager and a transaction system all number events with a counter rather than the wall clock, and the clocks Rust gives you when you do need real time.
minutes: 6
---
LRU-K needs to say "this access happened before that one". The obvious tool is the system clock. It is the wrong one.

## Three reasons not to use wall-clock time for ordering

1. **Ties.** Two accesses a few nanoseconds apart can read the same clock value on a coarse clock, and then "which was first?" has no answer.
2. **It can go backwards.** `SystemTime` follows the real-time clock, which an NTP correction or an administrator can step back. `Instant` is monotonic (it never goes back) but its resolution and origin are unspecified.
3. **Tests become non-deterministic.** A test that asserts which frame is evicted must not depend on how fast the machine ran.

## A logical clock

A **logical clock** is a counter you advance yourself, one tick per event that matters:

```rust
pub struct LruKReplacer {
    current_timestamp: usize,       // advances by one on every recorded access
    /* ... */
}

pub fn record_access(&mut self, frame: FrameId) {
    let now = self.current_timestamp;
    self.current_timestamp += 1;
    /* node.record(now) */
}
```

Properties: **total order** (no two events share a value), **deterministic** (replaying the same calls gives the same stamps), **free** (an increment), and **meaningless as a duration** (timestamp 100 is not "100 ms"). For eviction order that is exactly what you want: only the *order* matters.

Leslie Lamport's 1978 paper generalised this to distributed systems (each process keeps a counter and takes the maximum of its own and any received one), and **transaction timestamps** in module 4's MVCC are the same idea: a monotonically increasing number that says who is older.

## When you do need real time

| need | use | notes |
|---|---|---|
| measure how long something took | `std::time::Instant::now()` and `.elapsed()` | monotonic; the tests' timing assertions use it |
| a timestamp to store or show | `std::time::SystemTime` | can jump; convert with `duration_since(UNIX_EPOCH)` |
| sleep or timeout | `thread::sleep`, `Condvar::wait_timeout`, `recv_timeout` | |
| a counter shared by threads | `AtomicU64::fetch_add(1, Relaxed)` | a logical clock for concurrent code; `Relaxed` is enough when only uniqueness matters |

> [!PORT] C++
> `std::chrono::steady_clock` is Rust's `Instant`; `system_clock` is `SystemTime`. Using `system_clock::now()` to order events is a classic bug in ported code: use a counter.

## A caveat

A counter in a `usize` wraps after 2<sup>64</sup> increments on a 64-bit machine, which at one billion events per second takes about 585 years. On a 32-bit `usize` it takes about 4 seconds at that rate: the reference replacer's counter is a `usize` because the tests never get near, and a production system would use a `u64`.

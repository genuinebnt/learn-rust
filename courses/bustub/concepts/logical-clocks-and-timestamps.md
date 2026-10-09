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

## In real code

### Using it: three clocks you will write or meet

```rust test
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;

/// A logical clock shared by threads: unique, increasing, no relation to real time.
struct LogicalClock(AtomicU64);
impl LogicalClock {
    fn tick(&self) -> u64 { self.0.fetch_add(1, Ordering::Relaxed) }     // Relaxed is enough: only uniqueness matters, not ordering with other memory
}

#[test]
fn every_thread_gets_unique_increasing_stamps() {
    let clock = Arc::new(LogicalClock(AtomicU64::new(0)));
    let handles: Vec<_> = (0..8).map(|_| {
        let c = Arc::clone(&clock);
        std::thread::spawn(move || (0..1000).map(|_| c.tick()).collect::<Vec<_>>())
    }).collect();
    let per_thread: Vec<Vec<u64>> = handles.into_iter().map(|h| h.join().unwrap()).collect();
    for stamps in &per_thread { assert!(stamps.windows(2).all(|w| w[0] < w[1]), "each thread sees its own stamps increase"); }
    let mut all: Vec<u64> = per_thread.into_iter().flatten().collect();
    all.sort();
    assert_eq!(all, (0..8000).collect::<Vec<_>>(), "no ties and no gaps across threads");
}

#[test]
fn a_single_threaded_counter_is_deterministic() {
    // The replacer's clock: replaying the same calls gives the same stamps, so a test can assert which frame is evicted.
    fn run() -> Vec<usize> { let mut now = 0; (0..5).map(|_| { let t = now; now += 1; t }).collect() }
    assert_eq!(run(), run());
}
```

```rust test
/// Lamport clocks: each process counts its own events and, on receiving a message,
/// jumps past the sender's stamp. If A happened before B then stamp(A) < stamp(B).
#[derive(Default)]
struct Lamport { t: u64 }
impl Lamport {
    fn event(&mut self) -> u64 { self.t += 1; self.t }
    fn send(&mut self) -> u64 { self.event() }                           // the stamp travels with the message
    fn receive(&mut self, msg: u64) -> u64 { self.t = self.t.max(msg) + 1; self.t }
}

#[test]
fn receiving_a_message_orders_the_events_across_processes() {
    let (mut a, mut b) = (Lamport::default(), Lamport::default());
    for _ in 0..5 { b.event(); }                                         // B is "ahead" locally
    let sent = a.send();                                                 // A's first event: stamp 1
    let received = b.receive(sent);
    assert!(received > sent, "the receive happens after the send");
    assert_eq!(received, 6);                                             // max(5, 1) + 1
    let local_a = a.event();
    assert!(local_a < received, "A's later local event is NOT ordered after B's receive: stamps only give happens-before one way");
}

#[test]
fn what_the_real_clocks_promise() {
    use std::time::{Instant, SystemTime, UNIX_EPOCH};
    let t0 = Instant::now();
    let t1 = Instant::now();
    assert!(t1 >= t0, "Instant is monotonic: it never goes backwards (but ties are possible)");
    let secs = SystemTime::now().duration_since(UNIX_EPOCH).unwrap().as_secs();
    assert!(secs > 1_700_000_000, "SystemTime is wall-clock time since 1970; it can be stepped by NTP, so never use it for ordering");
    // A coarse clock ties; a (coarse, counter) pair does not.
    let coarse = |t_ns: u64| t_ns / 1_000_000;                           // 1 ms resolution
    assert_eq!(coarse(1_000_100), coarse(1_900_000), "two events 0.8 ms apart read the same time");
}
```

### In the exercises

- **1d-01, 1d-02:** the replacer's `current_timestamp`: read, then increment, exactly as in `tick` above. Distinct timestamps are what make every comparison in the LRU-K rule unambiguous.

### Where it is used

- **Id and sequence generators**: `AtomicU64::fetch_add` behind task ids, span ids (`tracing`), connection ids and `Arc`-shared counters in nearly every async runtime.
- **Databases**: PostgreSQL transaction ids (`xid`) and MVCC snapshots, log sequence numbers (LSNs) in every write-ahead log, and the timestamps module 4's MVCC uses are all logical clocks.
- **Distributed systems**: Lamport timestamps and vector clocks (Dynamo-style stores) track causality; Google Spanner uses *real* time with a stated uncertainty (TrueTime) because logical clocks cannot order events between machines that never communicate.
- **Hybrid logical clocks** (CockroachDB, YugabyteDB) pair a wall-clock reading with a counter so timestamps are both close to real time and tie-free: the `(coarse, counter)` idea in the last test.

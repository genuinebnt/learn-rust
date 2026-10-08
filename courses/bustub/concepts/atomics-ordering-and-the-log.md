---
title: Atomic counters, memory ordering and the append-only log
summary: What Relaxed, Acquire/Release and SeqCst actually promise, why statistics only need Relaxed, and why a write-ahead log is a file you only append to.
minutes: 8
---
The disk manager keeps counters (`get_num_writes`, `get_num_flushes`, `get_num_deletes`) and a log. Both look trivial and both hide a decision that you will need again in every concurrent module of the course.

## What an atomic gives you, and what it does not

An atomic integer gives you exactly one guarantee for free: **the operation itself is indivisible**. Two threads doing `fetch_add(1)` cannot lose an update, which a plain `+= 1` on shared memory can (it is a read, an add and a write, and two threads can interleave them).

What it does *not* give you for free is **ordering with respect to other memory**. A modern CPU and compiler may reorder independent loads and stores, and another thread is allowed to observe them in a different order than you wrote them. The `Ordering` argument is how you say how much ordering you want:

| Rust `Ordering` | C++ `memory_order` | promises | typical use |
|---|---|---|---|
| `Relaxed` | `memory_order_relaxed` | this one operation is atomic; nothing about other memory | counters, statistics, ids |
| `Release` (store) | `memory_order_release` | everything I wrote before this store is visible to whoever *acquires* it | publishing data: "the buffer is ready" |
| `Acquire` (load) | `memory_order_acquire` | if I see the value a release stored, I also see everything written before it | consuming that data |
| `AcqRel` | `memory_order_acq_rel` | both, for read-modify-write operations | locks, reference counts |
| `SeqCst` | `memory_order_seq_cst` | one global order of all `SeqCst` operations, on top of the rest | when you cannot prove a weaker one is enough |

C++'s `std::atomic<T>::fetch_add(1)` with no argument is `memory_order_seq_cst`: the strongest and slowest choice, chosen as the default so that naive code is correct. Rust has no default; you must write the ordering, which is deliberate.

## Why a statistics counter is `Relaxed`

`num_writes` is only ever *read* to be displayed or compared in a test. No other data is published through it: nobody reads `num_writes` and then assumes some other memory is in a particular state. Atomicity is all that is needed, so `Relaxed` is correct, and on x86 it compiles to the same instruction as the others (`lock xadd`); on ARM it avoids the acquire/release forms of the load and store instructions.

**When `Relaxed` is wrong** is when the atomic is a *flag* for other data:

```rust
// Thread A
data.store(42, Ordering::Relaxed);
ready.store(true, Ordering::Relaxed);

// Thread B
while !ready.load(Ordering::Relaxed) {}
assert_eq!(data.load(Ordering::Relaxed), 42);   // may fail!
```

Nothing orders the `data` store before the `ready` store as seen by B. The fix is `Release` on the `ready` store and `Acquire` on the load: that pair creates a *happens-before* edge. You will meet the pattern again in the buffer pool's pin counts and in latches.

```svg
caption: A release store and an acquire load that reads its value create a happens-before edge: everything thread A wrote before the release is visible to thread B after the acquire. With Relaxed on both there is no edge, and B may still see data == 0.
<svg viewBox="0 0 760 270" role="img" aria-label="Two thread timelines joined by a synchronizes-with arrow from a release store to an acquire load">
<defs><marker id="hb-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--fn)"/></marker>
<marker id="hb-b" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<text class="big" x="20" y="18">thread A</text><text class="big" x="20" y="262">thread B</text>
<rect class="box" x="60" y="40" width="230" height="40" rx="4"/><text class="mid fg" x="175" y="65">data.store(42, Relaxed)</text>
<rect class="blue" x="400" y="40" width="270" height="40" rx="4"/><text class="mid t-b" x="535" y="65">ready.store(true, Release)</text>
<rect class="blue" x="400" y="190" width="270" height="40" rx="4"/><text class="mid t-b" x="535" y="215">ready.load(Acquire) &#8594; true</text>
<rect class="live" x="60" y="190" width="230" height="40" rx="4"/><text class="mid t-g" x="175" y="215">data.load(Relaxed) &#8594; 42</text>
<path class="ln" d="M290 60 H398" marker-end="url(#hb-b)"/>
<text class="dim sm" x="296" y="52">program order</text>
<path class="ln" d="M398 210 H292" marker-end="url(#hb-b)"/>
<text class="dim sm" x="296" y="238">program order</text>
<path class="ln-b" d="M535 82 V188" marker-end="url(#hb-a)"/>
<text class="t-b sm" x="547" y="140">synchronizes-with</text>
<path class="ln-g dash" d="M175 82 V188" marker-end="url(#hb-b)"/>
<text class="t-g sm" x="187" y="140">so B must see 42</text>
</svg>
```

> [!TIP] Counting after success
> Increment *after* the operation succeeded: `write_all_at(…)?; num_writes.fetch_add(1, Relaxed)`. A failing write must not inflate the count, and an early return with `?` skips the increment for free. Counting before is the more natural-looking code and the one that makes a failure test report the wrong number.

## The log: a file you only append to

The log file exists for the recovery manager in module 5: before a change reaches the database file, a record describing it is appended to the log, so that after a crash the log can redo or undo it. This is the **write-ahead logging** rule, and it makes three demands that explain the shape of the API:

- **Append-only**, so a writer never has to find where the end is: open with append, and the kernel (`O_APPEND`) positions every write at the current end *atomically*. Two threads appending records cannot overwrite each other.
- **Read from an offset**, so a reader (the recovery loop) walks forward through the records without sharing a cursor with the writers: `read_at(buf, offset)`.
- **A clean end-of-log signal**, because recovery loops "read the next record until there is none": `read_log` returns `false` at or past the end of the log, and `true` with a zero-padded tail when the log ends in the middle of the buffer.

That last case is the interesting one. A crash can leave the log ending **halfway through a record**. The reader gets `true`, a buffer that is part data and part zeros, and must decide from the *record's own length field* whether it has a whole record. This is why the API does not promise `buf.len()` valid bytes, and why every log format starts each record with its length and a checksum.

```sh
$ strace -f -e trace=write,pwrite64,pread64 ./test 2>&1 | head
pwrite64(3, "..."..., 8192, 24576) = 8192      # a page: explicit offset
write(4, "..."..., 32) = 32                    # the log: no offset, O_APPEND chooses it
```

A **flush** here means "one `write_log` call that wrote bytes": an empty write is not counted, because it did nothing. Note that it is *not* an `fsync`: the log is in the page cache after `write_log` returns. Making it durable (and deciding when to) is the subject of module 5.

## In real code

### The API you will use

| call | what it does | when |
|---|---|---|
| `AtomicUsize::new(0)` | an atomic integer (also `AtomicU64`, `AtomicBool`, `AtomicI32`, ...) | counters, flags, ids |
| `a.load(ord)` / `a.store(v, ord)` | read / write | flags, reading a counter |
| `a.fetch_add(n, ord)` | add and return the **old** value | counters, unique ids |
| `a.swap(v, ord)` | store and return the old value | taking a flag |
| `a.compare_exchange(old, new, succ, fail)` | store `new` only if the value is still `old` | lock-free updates, claiming something once |
| `a.fetch_update(s, f, \|x\| Some(..))` | a compare-exchange loop for you | "update by a function" |
| `Ordering::Relaxed` | atomic and nothing else | statistics |
| `Ordering::{Acquire, Release}` | publish data with a flag | a "ready" flag |

```rust test
use std::sync::atomic::{AtomicUsize, Ordering};
use std::thread;

#[test]
fn counters_need_only_relaxed() {
    let writes = AtomicUsize::new(0);
    thread::scope(|s| {
        for _ in 0..8 {
            s.spawn(|| {
                for _ in 0..1000 {
                    writes.fetch_add(1, Ordering::Relaxed);
                }
            });
        }
    });
    assert_eq!(writes.load(Ordering::Relaxed), 8000);       // atomicity is all a statistic needs
}
```

```rust test
use std::sync::atomic::{AtomicBool, AtomicU32, Ordering};
use std::sync::Arc;
use std::thread;

#[test]
fn release_acquire_publishes_data() {
    let data = Arc::new(AtomicU32::new(0));
    let ready = Arc::new(AtomicBool::new(false));
    let (d, r) = (Arc::clone(&data), Arc::clone(&ready));
    let writer = thread::spawn(move || {
        d.store(42, Ordering::Relaxed);
        r.store(true, Ordering::Release);                    // everything above becomes visible to whoever acquires `ready`
    });
    while !ready.load(Ordering::Acquire) {}                  // spin: fine in a test
    assert_eq!(data.load(Ordering::Relaxed), 42);            // guaranteed by the release/acquire pair
    writer.join().unwrap();
}
```

```rust test
use std::sync::atomic::{AtomicU64, Ordering};

#[test]
fn compare_exchange_claims_once() {
    let owner = AtomicU64::new(0);                           // 0 = nobody
    assert!(owner.compare_exchange(0, 7, Ordering::AcqRel, Ordering::Acquire).is_ok());      // thread 7 wins
    assert_eq!(owner.compare_exchange(0, 9, Ordering::AcqRel, Ordering::Acquire), Err(7));   // thread 9 loses and learns who won
    let old = owner.fetch_update(Ordering::AcqRel, Ordering::Acquire, |x| Some(x + 1)).unwrap();
    assert_eq!((old, owner.load(Ordering::Relaxed)), (7, 8));
}
```

### In the exercises

- **1a-05 Part 1:** `num_writes`, `num_flushes` and `num_deletes` are `AtomicUsize` fields read by `get_*`. Use `fetch_add(1, Relaxed)` *after* the operation succeeded and `load(Relaxed)` in the getters (the first example). The stage tests run eight threads at once and expect exactly 400.
- **1a-05 Part 2 and 3:** `write_log` appends and counts one flush; `read_log` reads at an offset. The log's own `Mutex<File>` is what keeps two appends from interleaving.
- **Later, 1d-01:** the replacer's logical clock is a plain `usize` because the replacer takes `&mut self`; a concurrent clock would be `AtomicU64::fetch_add(1, Relaxed)`.

### Where it is used

- **Statistics everywhere**: PostgreSQL's `pg_stat_*` counters, RocksDB's tickers, a web server's request count. Relaxed increments, summed on read.
- **Reference counts**: `Arc` itself is an atomic count (`fetch_add` on clone, `fetch_sub` on drop, with an acquire fence on the last drop).
- **Lock-free queues and ID generators**: a global `fetch_add` hands out transaction ids and log sequence numbers.
- **Stop flags**: an `AtomicBool` a worker polls (with `Acquire`) so a shutdown request is seen promptly.
- **Spinlocks and `Once`**: built from `compare_exchange` and `swap`.

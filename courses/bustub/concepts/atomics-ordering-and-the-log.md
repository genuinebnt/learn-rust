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
// Thread A                                // Thread B
data.store(42, Ordering::Relaxed);         while !ready.load(Ordering::Relaxed) {}
ready.store(true, Ordering::Relaxed);      assert_eq!(data.load(Ordering::Relaxed), 42);   // may fail!
```

Nothing orders the `data` store before the `ready` store as seen by B. The fix is `Release` on the `ready` store and `Acquire` on the load: that pair creates a *happens-before* edge. You will meet the pattern again in the buffer pool's pin counts and in latches.

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

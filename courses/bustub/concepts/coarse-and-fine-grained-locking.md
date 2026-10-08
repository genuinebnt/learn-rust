---
title: Coarse and fine-grained locking: one latch or many
summary: What the pool's single latch protects, why each frame also has its own reader-writer latch, how long a lock is held (and what is held across I/O), and the order rules that keep it deadlock-free.
minutes: 9
---
Locking is a trade: **one lock is simple and slow, many locks are fast and hard**. The buffer pool uses both at once, on purpose, and this page is why.

## Coarse: one latch for the metadata

All of the pool's *bookkeeping* (the page table, the free list, pin counts and dirty flags, the replacer, `next_page_id`) sits behind **one** `Mutex<Inner>`. Every operation that touches it takes the latch, reads and updates, and releases. That makes each public method **atomic** with respect to the others: there is no interleaving to reason about, and the invariants (a frame is in the page table iff it has a page; pin count zero iff evictable) hold at every instant a lock is not held.

Cost: every `fetch_page`, `unpin_page` and `flush_page` from every thread serialises on it, and in this course the disk I/O of a miss is done under it too. For a teaching pool that is the right default: **start with the coarse lock, measure, and split only what the measurements say.**

## Fine: one latch per frame, for the bytes

The page *contents* are different. A thread reading page 4 should not block a thread writing page 9, and many threads may read page 4 at once. So each frame's 8 KiB lives behind its own `RwLock`:

```rust
frames: Vec<RwLock<Box<PageData>>>,       // one latch per frame: the page's bytes
inner: Mutex<Inner>,                       // one latch for everything else: the metadata
```

| | pool latch (`inner`) | frame latch (`frames[i]`) |
|---|---|---|
| protects | page table, free list, pin counts, dirty bits, replacer | the 8 KiB of one page |
| held for | microseconds (a few hash and list operations; a disk I/O on a miss) | as long as the caller uses the page (a guard's lifetime) |
| contention | every thread, on every call | only threads using that page |
| mode | exclusive | shared (readers) or exclusive (one writer) |

The two are used together by the page guards: `checked_read_page` takes the pool latch just long enough to **pin** the page, *releases it*, and then takes the frame's read latch.

```svg
caption: A page access takes the pool latch only to pin, then works under the frame's own latch. Threads on different pages meet only at the short pool-latch step; threads reading the same page share its read latch.
<svg viewBox="0 0 760 240" role="img" aria-label="Three threads using two pages: short pool latch sections, then separate frame latches">
<text class="big" x="20" y="48">thread 1</text><text class="big" x="20" y="100">thread 2</text><text class="big" x="20" y="152">thread 3</text>
<rect class="hot" x="120" y="30" width="40" height="26" rx="3"/><rect class="live" x="160" y="30" width="400" height="26" rx="3"/><text class="mid t-g sm" x="360" y="48">frame 4: read latch (page 4)</text>
<rect class="never" x="120" y="82" width="40" height="26" rx="3"/><rect class="hot" x="160" y="82" width="40" height="26" rx="3"/><rect class="live" x="200" y="82" width="300" height="26" rx="3"/><text class="mid t-g sm" x="350" y="100">frame 4: read latch (shared with thread 1)</text>
<rect class="hot" x="120" y="134" width="40" height="26" rx="3"/><rect class="bad" x="160" y="134" width="320" height="26" rx="3"/><text class="mid t-r sm" x="320" y="152">frame 9: write latch (page 9)</text>
<text class="t-a sm" x="120" y="196">&#9632; pool latch (pin only): one thread at a time, microseconds</text>
<text class="dim sm" x="120" y="214">thread 2 waited briefly for the pool latch; everything after it runs in parallel</text>
</svg>
```

## The hold-time rule

> **Never wait for a latch you may not get while holding one that others need.**

Waiting on a page latch (which a user may hold for a long time) *while holding the pool latch* stalls every thread in the system until that user finishes, and can deadlock outright: the page's holder may need the pool latch to unpin its page. So the order is fixed by construction:

1. take the pool latch, **pin** the page, release the pool latch;
2. then wait for the page latch (the pin keeps the frame from being reused meanwhile);
3. on release: drop the page latch, *then* take the pool latch to unpin.

The pin is what makes it safe to let go of the pool latch early: it is a promise the frame will stay put, standing in for the lock.

## Ordering and deadlock

Two locks used together must always be taken in the **same order** by every thread. Here the order is *pool latch before frame latch* when both are needed at once (a thread holding a frame latch must not then block on the pool latch while another thread holds the pool latch waiting for that frame latch). The next module's flush bug is exactly a violation of this, and its fix is the hold-time rule above.

| style | what it protects well | when it hurts |
|---|---|---|
| one global latch | everything, trivially | many threads, long critical sections, I/O inside |
| per-object latches | independent objects in parallel | needs an ordering discipline; more state to get wrong |
| lock-free / atomics | counters and flags | hard to prove; only for the simplest state |

> [!NOTE] Real systems
> Production buffer pools shard the page table and free list into many partitions (a latch per partition) and use per-frame state words updated with atomics, so that a hit takes no global lock at all. The structure here is the first rung of that ladder.

## In real code

### Using it: one pool latch for metadata, one `RwLock` per frame

The hold-time rule in code: pin under the pool latch, *release it*, then take the frame latch. The tests check that the data is right and that the pins balance, and one test would deadlock if the frame latch were exclusive.

```rust test
use std::collections::HashMap;
use std::sync::{Barrier, Mutex, RwLock};
use std::sync::Arc;

struct Inner { table: HashMap<u32, usize>, pin: Vec<usize> }

struct Pool { inner: Mutex<Inner>, frames: Vec<RwLock<[u8; 8]>> }

impl Pool {
    fn new(pages: u32) -> Self {
        Pool {
            inner: Mutex::new(Inner { table: (0..pages).map(|p| (p, p as usize)).collect(), pin: vec![0; pages as usize] }),
            frames: (0..pages).map(|_| RwLock::new([0; 8])).collect(),
        }
    }

    fn pin(&self, page: u32) -> usize {
        let mut inner = self.inner.lock().unwrap();               // coarse latch: microseconds
        let frame = inner.table[&page];
        inner.pin[frame] += 1;                                     // the pin keeps the frame from being reused...
        frame
    }                                                              // ...so the latch can be released here

    fn unpin(&self, frame: usize) { self.inner.lock().unwrap().pin[frame] -= 1; }

    fn with_write<R>(&self, page: u32, f: impl FnOnce(&mut [u8; 8]) -> R) -> R {
        let frame = self.pin(page);
        let r = { let mut guard = self.frames[frame].write().unwrap(); f(&mut guard) };   // fine latch: held while the caller works
        self.unpin(frame);                                        // drop the page latch, THEN take the pool latch
        r
    }

    fn with_read<R>(&self, page: u32, f: impl FnOnce(&[u8; 8]) -> R) -> R {
        let frame = self.pin(page);
        let r = { let guard = self.frames[frame].read().unwrap(); f(&guard) };
        self.unpin(frame);
        r
    }
}

#[test]
fn writers_to_one_page_are_exclusive_and_pins_balance() {
    let pool = Arc::new(Pool::new(4));
    let handles: Vec<_> = (0..4).map(|_| {
        let pool = Arc::clone(&pool);
        std::thread::spawn(move || for _ in 0..250 { pool.with_write(0, |b| b[0] = b[0].wrapping_add(1)); })
    }).collect();
    for h in handles { h.join().unwrap(); }
    assert_eq!(pool.with_read(0, |b| b[0]), (1000u32 % 256) as u8);              // 1000 increments, none lost
    assert!(pool.inner.lock().unwrap().pin.iter().all(|&p| p == 0));
}

#[test]
fn readers_share_a_frame_latch() {
    let pool = Arc::new(Pool::new(1));
    let barrier = Arc::new(Barrier::new(2));
    let handles: Vec<_> = (0..2).map(|_| {
        let (pool, barrier) = (Arc::clone(&pool), Arc::clone(&barrier));
        std::thread::spawn(move || pool.with_read(0, |_| { barrier.wait(); }))     // both hold the read latch at the same moment
    }).collect();
    for h in handles { h.join().unwrap(); }                                         // with an exclusive latch this would deadlock
}

#[test]
fn different_pages_do_not_block_each_other() {
    let pool = Arc::new(Pool::new(2));
    let barrier = Arc::new(Barrier::new(2));
    let handles: Vec<_> = (0..2u32).map(|page| {
        let (pool, barrier) = (Arc::clone(&pool), Arc::clone(&barrier));
        std::thread::spawn(move || pool.with_write(page, |b| { barrier.wait(); b[0] = page as u8 + 1; }))   // both hold WRITE latches at once
    }).collect();
    for h in handles { h.join().unwrap(); }
    assert_eq!((pool.with_read(0, |b| b[0]), pool.with_read(1, |b| b[0])), (1, 2));
}
```

### In the exercises

- **1f-01, 1f-03:** the pool's `Mutex<Inner>` is the coarse latch; every `BufferPoolManager` method takes it first.
- **1g-02 Part 3 (a flush must not wait for a latch while holding the pool's lock):** the fix is exactly `pin`, release the pool latch, then take the frame latch, as in `with_write` above.
- **1g-01:** guards hold the frame latch for as long as the user holds the guard, and take the pool latch only briefly in `Drop` to unpin.

### Where it is used

- **Sharded maps**: `dashmap` and Java's `ConcurrentHashMap` split one big lock into many partitions (the coarse-to-fine step).
- **Databases**: PostgreSQL protects the buffer mapping hash table with partitioned LWLocks and each buffer with a content lock plus a header spinlock; InnoDB has a latch per block and a mutex per buffer pool instance.
- **Filesystems and kernels**: Linux's per-inode locks over a global dcache lock, and the rule "take the table lock, take a reference, drop the table lock, then block on the object".
- **Application code with a shared registry**: look up under the registry mutex, clone an `Arc` to the entry, release the mutex, then lock the entry: the same pin-then-release pattern.

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

---
title: Evicting a page: the order of steps and what a failure leaves behind
summary: The sequence for bringing a page into a full pool (choose, write back, unmap, read, map), why each step precedes the next, and the cost of doing disk I/O while holding the pool's lock.
minutes: 9
---
`fetch_page` for a page that is not resident, in a pool with no free frame, is the most delicate operation in the buffer pool: it evicts one page and loads another into the same frame, and a mistake in the order loses data or serves the wrong page.

## The sequence

1. **Choose a victim.** Ask the replacer for an evictable frame. If there is none, every frame is pinned: return `None` (the caller gets an error, and no state has changed).
2. **Write the victim back if it is dirty.** The frame still holds the old page; write its bytes to disk as the *old* page id, and mark it clean.
3. **Unmap the old page.** Remove the old page id from the page table.
4. **Read the new page** into the frame, from disk as the *new* page id.
5. **Map and pin.** Record `new page id → frame` in the page table, set the pin count to 1, tell the replacer about the access and that the frame is not evictable.

```rust
let frame = match inner.free_frames.pop() {
    Some(frame) => frame,                                     // a free frame needs none of steps 1-3
    None => {
        let frame = inner.replacer.evict()?;                  // 1
        let old = inner.meta[frame.0].page_id.take().expect("an evicted frame holds a page");
        if inner.meta[frame.0].dirty { self.store(old, frame); inner.meta[frame.0].dirty = false; }   // 2
        inner.page_table.remove(&old);                        // 3
        frame
    }
};
self.load(page_id, frame);                                    // 4
inner.page_table.insert(page_id, frame);                      // 5
```

```svg
caption: Bringing page 9 into a full pool. The victim's dirty bytes are written under the old id before the frame is reused, and the new mapping is published last. The red cross marks the one order that loses data: reading before writing back.
<svg viewBox="0 0 760 250" role="img" aria-label="Five steps of eviction: choose, write back, unmap, read, map">
<defs><marker id="ev-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="blue" x="20" y="30" width="130" height="64" rx="5"/><text class="t-b" x="32" y="52">1. choose</text><text class="dim sm" x="32" y="72">replacer.evict()</text><text class="dim sm" x="32" y="86">victim: frame 1</text>
<rect class="free" x="164" y="30" width="130" height="64" rx="5"/><text class="t-w" x="176" y="52">2. write back</text><text class="dim sm" x="176" y="72">if dirty: page 7</text><text class="dim sm" x="176" y="86">to disk, then clean</text>
<rect class="box" x="308" y="30" width="130" height="64" rx="5"/><text class="fg" x="320" y="52">3. unmap</text><text class="dim sm" x="320" y="72">page table:</text><text class="dim sm" x="320" y="86">remove page 7</text>
<rect class="live" x="452" y="30" width="130" height="64" rx="5"/><text class="t-g" x="464" y="52">4. read</text><text class="dim sm" x="464" y="72">page 9 from disk</text><text class="dim sm" x="464" y="86">into frame 1</text>
<rect class="hot" x="596" y="30" width="144" height="64" rx="5"/><text class="t-a" x="608" y="52">5. map and pin</text><text class="dim sm" x="608" y="72">page 9 &#8594; frame 1</text><text class="dim sm" x="608" y="86">pin = 1, not evictable</text>
<path class="ln" d="M150 62 H162" marker-end="url(#ev-a)"/><path class="ln" d="M294 62 H306" marker-end="url(#ev-a)"/><path class="ln" d="M438 62 H450" marker-end="url(#ev-a)"/><path class="ln" d="M582 62 H594" marker-end="url(#ev-a)"/>
<rect class="bad" x="164" y="140" width="418" height="44" rx="5"/><text class="t-r" x="176" y="160">&#215;  4 before 2: the read overwrites the only copy of page 7's changes</text><text class="dim sm" x="176" y="176">the dirty bytes are gone and nothing failed: the worst kind of bug</text>
<text class="dim sm" x="20" y="222">all five run under the pool latch in this course; steps 2 and 4 are the disk I/O</text>
</svg>
```

## Why this order

- **Write back before you read.** The read overwrites the frame's bytes. Reading first would destroy the dirty page that was the only copy of those changes.
- **Write with the old id.** After step 3 the pool no longer knows what the frame held; the page id is taken *before* it is forgotten (`page_id.take()`), then used in `store(old, frame)`.
- **Unmap before reuse.** If the old page stayed in the page table while its frame holds a different page, a concurrent `fetch_page(old)` would "hit" and return the wrong bytes.
- **Map only after the bytes are valid.** Publish the new mapping last, so no one can find a half-loaded frame.

## What if a step fails?

The disk can fail at step 2 or 4. The reference code `expect`s success (an I/O error is fatal in this teaching pool), but the question is worth asking, because a production pool must answer it. If the write at step 2 fails, the frame is still dirty and still mapped: nothing was lost, and the fetch can return an error. If the read at step 4 fails *after* step 3, the old page is unmapped and the frame holds stale bytes: the frame must go back on the free list, not stay mapped to anything. The rule is the one from the slot allocator: **order the steps so that a failure leaves a state you can describe**, and do the irreversible one last.

## The cost: I/O under the lock

In this pool, steps 2 and 4 run while holding the pool latch (`inner`), so every other thread waits for the disk. A write plus a read is two disk latencies of blocking for the entire pool. That is correct and simple, and it is the *first* thing a faster design removes. The two-latch alternatives and the hazards of each are in the concept on lock granularity; the short version is that releasing the pool latch during I/O means another thread can request the page you are loading, so the page table needs a "loading" state that the second thread waits on.

| design | during the disk I/O | hazard |
|---|---|---|
| pool latch held (this course) | everything waits | none; slow under load |
| latch released, frame marked `loading` | other pages proceed | a second fetch of the same page must wait for the first; more states |
| asynchronous: issue the I/O, return a future | the caller continues | the pool needs completion handling; this is what BusTub's scheduler is for |

> [!TIP] Count the I/O
> `DiskManagerUnlimitedMemory::get_num_writes()` lets a test assert that evicting a *clean* page writes nothing and a *dirty* one writes exactly once. That one assertion catches both "forgot the dirty flag" and "wrote every page".

## In real code

### Using it: the five steps on a one-frame pool, with injected failures

A pool with one frame needs a miss for every other page, which makes the ordering visible. The disk can be told to fail its next read, and a `buggy_fetch` shows the wrong order.

```rust test
use std::collections::HashMap;

struct OneFrame {
    frame: [u8; 4],
    page: Option<u64>,
    dirty: bool,
    disk: HashMap<u64, [u8; 4]>,
    writes: usize,
    fail_next_read: bool,
}

impl OneFrame {
    fn new() -> Self { OneFrame { frame: [0; 4], page: None, dirty: false, disk: HashMap::new(), writes: 0, fail_next_read: false } }

    fn store(&mut self, id: u64) { self.disk.insert(id, self.frame); self.writes += 1; }

    fn load(&mut self, id: u64) -> Result<(), String> {
        if std::mem::take(&mut self.fail_next_read) { return Err("read failed".into()); }
        self.frame = self.disk.get(&id).copied().unwrap_or([0; 4]);
        Ok(())
    }

    /// 1. choose (the only frame)  2. write back if dirty  3. unmap  4. read  5. map
    fn fetch(&mut self, id: u64) -> Result<(), String> {
        if self.page == Some(id) { return Ok(()); }
        if let Some(old) = self.page {
            if self.dirty { self.store(old); self.dirty = false; }       // 2: with the OLD id, before the frame is touched
            self.page = None;                                            // 3: nothing maps to this frame any more
        }
        self.load(id)?;                                                  // 4: if this fails the frame is simply empty
        self.page = Some(id);                                            // 5: publish the mapping last
        Ok(())
    }

    /// The wrong order: read first, then write back whatever is in the frame.
    fn buggy_fetch(&mut self, id: u64) {
        let old = self.page;
        self.frame = self.disk.get(&id).copied().unwrap_or([0; 4]);     // the read destroys the dirty bytes...
        if let (Some(old), true) = (old, self.dirty) { self.store(old); } // ...so this "writes back" the NEW page's bytes under the old id
        self.page = Some(id);
        self.dirty = false;
    }
}

#[test]
fn write_back_then_read_keeps_the_data() {
    let mut p = OneFrame::new();
    p.fetch(1).unwrap();
    p.frame[0] = 99; p.dirty = true;
    p.fetch(2).unwrap();                                                 // evicts 1
    assert_eq!(p.disk[&1][0], 99);
    p.fetch(1).unwrap();
    assert_eq!(p.frame[0], 99);
}

#[test]
fn the_wrong_order_loses_the_change() {
    let mut p = OneFrame::new();
    p.fetch(1).unwrap();
    p.frame[0] = 99; p.dirty = true;
    p.buggy_fetch(2);
    assert_ne!(p.disk.get(&1).map(|d| d[0]), Some(99), "page 1's change was overwritten by the read before it was saved");
}

#[test]
fn a_failed_read_leaves_a_state_you_can_describe() {
    let mut p = OneFrame::new();
    p.fetch(1).unwrap();
    p.frame[0] = 7; p.dirty = true;
    p.fail_next_read = true;
    assert!(p.fetch(2).is_err());
    assert_eq!(p.page, None, "page 1 was written back and unmapped; nothing claims the frame");
    assert_eq!(p.disk[&1][0], 7, "and its change is safe on disk");
    p.fetch(2).unwrap();                                                 // the retry works from that state
    assert_eq!(p.page, Some(2));
}

#[test]
fn count_the_writes() {
    let mut p = OneFrame::new();
    p.fetch(1).unwrap();
    p.fetch(2).unwrap();                                                 // page 1 was clean
    assert_eq!(p.writes, 0, "evicting a clean page writes nothing");
    p.frame[0] = 1; p.dirty = true;
    p.fetch(3).unwrap();
    assert_eq!(p.writes, 1, "a dirty page is written exactly once");
}
```

### In the exercises

- **1f-02 Part 3 (evict an unpinned page when no frame is free):** the miss path of `fetch_page`; "every frame pinned returns `None` and changes nothing" is the check before step 2.
- **1f-03 Part 1 (write dirty victims back):** step 2, with the *old* page id, before the frame is reused; the tests count writes like `count_the_writes`.

### Where it is used

- **Databases and kernels** all have this sequence: Linux's page reclaim writes back a dirty page before reusing its frame; PostgreSQL's `BufferAlloc` flushes the victim buffer (after making sure its WAL is flushed) before the buffer is re-tagged.
- **Write-back caches in storage stacks** (SSD controllers, ZFS's ARC with the ZIL) rely on the same rule: persist, then forget.
- **Rust code that swaps state**: `mem::replace`/`mem::take` followed by a fallible step, with the invariant that the structure is valid between the steps.

---
title: Pin counts, dirty pages and the write-back policy
summary: What a pin promises, how a leaked pin starves the pool, how the dirty flag accumulates, and why a database can write dirty pages late (and why that makes recovery necessary).
minutes: 9
---
Two small fields on every frame carry most of the buffer pool's correctness: the **pin count** and the **dirty flag**.

## Pinning: "I am using this page, do not take it"

A thread that is reading or writing a page's bytes must be sure the frame will not be reused for another page meanwhile. **Pinning** is that promise: `fetch_page` increments the page's pin count and tells the replacer the frame is *not evictable*. `unpin_page` decrements it; at zero the frame becomes evictable.

```rust
pub fn unpin_page(&self, page_id: PageId, is_dirty: bool) -> bool {
    let mut inner = self.inner.lock().unwrap();
    let Some(&frame) = inner.page_table.get(&page_id) else { return false };   // not resident
    let meta = &mut inner.meta[frame.0];
    if meta.pin_count == 0 { return false; }                                    // already unpinned: a bug in the caller
    meta.pin_count -= 1;
    meta.dirty |= is_dirty;                                                     // sticky: see below
    if meta.pin_count == 0 { inner.replacer.set_evictable(frame, true); }
    true
}
```

Pins **count**, because several threads can use one page at once: three `fetch_page`s need three `unpin_page`s before the page can be evicted. Only the last one makes it evictable.

## The leak

An `unpin` that never happens is a **pin leak**, and it is the classic buffer-pool bug. Each leaked pin takes one frame out of circulation for good; after enough of them `fetch_page` finds no free frame and no evictable one and returns `None`. The symptom is far from the cause (a query fails with "out of memory" minutes after the leaking code ran). Two defences: the tests check `get_pin_count` returns to zero, and module 1g's RAII guards make the unpin automatic.

| C++ (BusTub 2022 and earlier) | Rust here |
|---|---|
| `Page *p = bpm->FetchPage(id); ...; bpm->UnpinPage(id, dirty);` | `let f = bpm.fetch_page(id)?; ...; bpm.unpin_page(id, dirty);` |
| forget the unpin on an early `return` | the same bug (this module); impossible with guards (next module) |

## The dirty flag

A page is **dirty** when its in-memory bytes differ from what is on disk. The pool must know, because it must write a dirty page back *before* reusing its frame, and should not write a clean one.

The caller tells it at unpin time: `unpin_page(id, is_dirty)`. The pool combines that with what it already knows by **OR**, never by assignment:

```rust
meta.dirty |= is_dirty;      // NOT meta.dirty = is_dirty
```

Why: user A modifies the page and unpins with `dirty = true`; user B, who only read it, unpins with `dirty = false`. Assignment would let B *erase* A's modification and the change would be silently lost on eviction. The flag is cleared only when the page is written to disk (a flush or a write-back).

```svg
caption: Three threads pin the same page; only when the third unpin brings the count to zero does the frame become evictable. The dirty flag only goes up (OR) until the page is written, so a later clean unpin cannot erase an earlier change.
<svg viewBox="0 0 760 230" role="img" aria-label="A pin count rising to three and falling to zero over a timeline, and a dirty flag that stays set">
<line class="grid" x1="60" y1="160" x2="740" y2="160"/>
<text class="dim sm" x="20" y="30">pin count</text><text class="dim sm" x="20" y="200">dirty</text>
<polyline class="ln-b" fill="none" points="60,160 120,160 120,130 200,130 200,100 280,100 280,70 380,70 380,100 460,100 460,130 540,130 540,160 740,160"/>
<text class="t-b sm" x="124" y="124">1</text><text class="t-b sm" x="204" y="94">2</text><text class="t-b sm" x="284" y="64">3</text><text class="t-b sm" x="384" y="94">2</text><text class="t-b sm" x="464" y="124">1</text><text class="t-b sm" x="544" y="154">0</text>
<text class="dim sm" x="96" y="182">fetch</text><text class="dim sm" x="176" y="182">fetch</text><text class="dim sm" x="256" y="182">fetch</text>
<text class="dim sm" x="356" y="182">unpin</text><text class="dim sm" x="436" y="182">unpin</text><text class="dim sm" x="516" y="182">unpin</text>
<rect class="live" x="544" y="40" width="190" height="26" rx="3"/><text class="mid t-g sm" x="639" y="58">evictable from here</text>
<rect class="never" x="60" y="206" width="320" height="18" rx="3"/><text class="mid dim sm" x="220" y="219">clean</text>
<rect class="free" x="380" y="206" width="360" height="18" rx="3"/><text class="mid t-w sm" x="560" y="219">dirty (a writer unpinned with true; later clean unpins keep it)</text>
</svg>
```

## When may a dirty page reach the disk?

A buffer pool has a free choice, and the choice shapes the whole recovery design:

| policy | meaning | consequence |
|---|---|---|
| **steal** | the pool may write a dirty page of an *uncommitted* transaction to disk (to free the frame) | the disk can hold changes that must be **undone** after a crash |
| **no-steal** | uncommitted changes never reach disk | needs enough memory for every in-flight transaction |
| **force** | all of a transaction's dirty pages are written at commit | commits are slow (random writes) |
| **no-force** | commit need not write the data pages | the disk can lack committed changes that must be **redone** |

Nearly every real system is **steal / no-force**: it is the fastest, and it makes crashes survivable only because of the **write-ahead log** (module 5): before a dirty page may be written, the log record describing its change must already be on disk, so recovery can redo and undo. The buffer pool in this module is "steal / no-force without the log", which is why it is correct for the tests and unsafe for a real crash.

> [!WHY] Why `flush_page` ignores the dirty flag
> It is for **durability points**: the caller (a checkpoint, a test) wants the bytes on disk now, whatever the flag says; and it then clears the flag, because the disk is up to date.

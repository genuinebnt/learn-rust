---
title: Anatomy of a buffer pool: frames, page table, pins and the replacer
summary: The five pieces of state in a buffer pool, the life of a page through them, and the questions each BufferPoolManager method answers.
minutes: 10
---
A database is bigger than memory, so it keeps a **buffer pool**: a fixed set of memory slots (**frames**) that hold copies of disk pages. Every other component (the heap, the indexes, the executors) asks the pool for a page by id and never touches the disk directly. If you understand the five pieces of state below, every method of the pool is a few lines.

## The pieces

| state | what it is | BusTub name | in this repo |
|---|---|---|---|
| **frames** | the memory: `num_frames` buffers of 8 KiB | `pages_` array | `Vec<RwLock<Box<PageData>>>`: each behind its own latch |
| **page table** | which frame holds which page | `page_table_` | `HashMap<PageId, FrameId>` |
| **free list** | frames that hold nothing | `free_frames_` | `Vec<FrameId>` |
| **frame metadata** | for each frame: page id, **pin count**, **dirty** flag | fields of `Page` | `FrameMeta { page_id, pin_count, dirty }` |
| **replacer** | which unpinned frame to evict next | `replacer_` | `ArcReplacer` (module 1e) |

Plus one counter: `next_page_id`, from which `new_page` hands out ids, and the disk scheduler from module 1b, which performs the I/O.

```svg
caption: The buffer pool's state. The page table maps resident pages to frames; the free list holds empty frames; the replacer knows which frames are evictable (pin count 0). Page 9 is on disk only: fetching it needs a frame from the free list or an eviction.
<svg viewBox="0 0 760 290" role="img" aria-label="Frames with pin counts and dirty flags, a page table, a free list and a replacer">
<defs><marker id="bp-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<text class="dim sm" x="20" y="22">page table</text>
<rect class="box" x="20" y="30" width="150" height="26" rx="3"/><text class="fg sm" x="30" y="48">page 4  &#8594;  frame 0</text>
<rect class="box" x="20" y="60" width="150" height="26" rx="3"/><text class="fg sm" x="30" y="78">page 7  &#8594;  frame 1</text>
<rect class="box" x="20" y="90" width="150" height="26" rx="3"/><text class="fg sm" x="30" y="108">page 2  &#8594;  frame 3</text>
<text class="dim sm" x="230" y="22">frames (each behind its own latch)</text>
<rect class="blue" x="230" y="30" width="130" height="90" rx="4"/><text class="t-b" x="242" y="52">frame 0</text><text class="fg sm" x="242" y="72">page 4</text><text class="fg sm" x="242" y="88">pin count 2</text><text class="dim sm" x="242" y="104">clean</text>
<rect class="blue" x="372" y="30" width="130" height="90" rx="4"/><text class="t-b" x="384" y="52">frame 1</text><text class="fg sm" x="384" y="72">page 7</text><text class="fg sm" x="384" y="88">pin count 0</text><text class="t-w sm" x="384" y="104">dirty</text>
<rect class="never" x="514" y="30" width="110" height="90" rx="4"/><text class="dim" x="526" y="52">frame 2</text><text class="dim sm" x="526" y="72">empty</text>
<rect class="blue" x="636" y="30" width="104" height="90" rx="4"/><text class="t-b" x="646" y="52">frame 3</text><text class="fg sm" x="646" y="72">page 2</text><text class="fg sm" x="646" y="88">pin count 0</text><text class="dim sm" x="646" y="104">clean</text>
<text class="dim sm" x="230" y="160">free list</text><rect class="free" x="230" y="168" width="70" height="30" rx="3"/><text class="mid t-w" x="265" y="188">frame 2</text>
<text class="dim sm" x="400" y="160">replacer: evictable frames (pin count 0)</text>
<rect class="live" x="400" y="168" width="70" height="30" rx="3"/><text class="mid t-g" x="435" y="188">frame 1</text><rect class="live" x="476" y="168" width="70" height="30" rx="3"/><text class="mid t-g" x="511" y="188">frame 3</text>
<text class="dim sm" x="20" y="160">disk only</text><rect class="never" x="20" y="168" width="150" height="30" rx="3"/><text class="mid dim sm" x="95" y="188">page 9: not resident</text>
<text class="t-a sm" x="20" y="240">fetch_page(9): page table miss &#8594; take frame 2 from the free list &#8594; read page 9 into it &#8594; map it &#8594; pin it</text>
<text class="t-a sm" x="20" y="260">if the free list were empty: replacer.evict() would pick frame 1 or 3; frame 1 is dirty, so it is written first</text>
</svg>
```

## The life of a page in the pool

1. **Not resident.** The page exists only on disk (or nowhere yet, for a new id).
2. **Resident and pinned.** `fetch_page` found or made a frame for it and counted a pin. It is in the page table, and the replacer is told it is *not* evictable.
3. **Resident and unpinned.** The last user called `unpin_page`. It stays in memory (it may be wanted again), but now the replacer *may* choose it.
4. **Evicted.** The replacer chose it when a frame was needed. If it is **dirty** it is written to disk first; then the page-table entry goes and the frame is reused.

Every public method is a transition on that diagram:

| method | question it answers |
|---|---|
| `new_page()` | which id is unused? (no frame yet) |
| `fetch_page(id)` | is the page resident? if not, find a frame (free list, else evict) and read it; then pin |
| `unpin_page(id, dirty)` | drop one pin; remember that the page changed; if no pins remain, tell the replacer |
| `flush_page(id)` | write it to disk now, regardless of the dirty flag, and mark it clean |
| `delete_page(id)` | forget it (refuse if pinned) and free its disk space |
| `get_pin_count(id)` | for tests and debugging |

## Why each piece exists

- The **page table** makes "is it in memory?" an O(1) hash lookup instead of a scan of the frames.
- The **free list** separates "no page in this frame" from "an evictable page in this frame", so a pool that is not full never calls the replacer.
- The **pin count** stops the replacer from taking a page out from under someone using it (the next concept).
- The **dirty flag** avoids writing pages that have not changed.
- The **replacer** is deliberately ignorant: it knows frame ids and evictability, not page contents, which is why you could swap LRU for ARC with no change to the pool.

> [!NOTE] Textbook interface, then guards
> This module's interface is the textbook's: `fetch_page` and `unpin_page`, which you must pair by hand. It is also the interface that leaks: forget an unpin and the pool slowly fills with pinned pages and starts returning `None`. Module 1g wraps it in RAII guards so the pairing cannot be forgotten; the pool underneath is the same code.

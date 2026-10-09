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

## In real code

### Using it: a complete miniature pool

All five pieces of state and the six methods, with a `Vec<u8>` for a disk and a FIFO list of evictable frames as the replacer (swap in LRU-K or ARC and nothing else changes). Frames are 8 bytes so a test can print them.

```rust test
use std::collections::{HashMap, VecDeque};

type PageId = u64;
type FrameId = usize;

#[derive(Default)]
struct Disk { pages: HashMap<PageId, [u8; 8]>, reads: usize, writes: usize }
impl Disk {
    fn read(&mut self, id: PageId) -> [u8; 8] { self.reads += 1; self.pages.get(&id).copied().unwrap_or([0; 8]) }   // unknown page: zeros
    fn write(&mut self, id: PageId, data: [u8; 8]) { self.writes += 1; self.pages.insert(id, data); }
}

#[derive(Clone, Copy, Default)]
struct Meta { page_id: Option<PageId>, pin_count: usize, dirty: bool }

struct Pool {
    frames: Vec<[u8; 8]>,                       // the memory
    meta: Vec<Meta>,                            // per-frame page id, pin count, dirty flag
    table: HashMap<PageId, FrameId>,            // page table
    free: Vec<FrameId>,                         // frames holding nothing
    evictable: VecDeque<FrameId>,               // the replacer (FIFO here)
    next_page_id: PageId,
    disk: Disk,
}

impl Pool {
    fn new(n: usize) -> Self {
        Pool { frames: vec![[0; 8]; n], meta: vec![Meta::default(); n], table: HashMap::new(), free: (0..n).rev().collect(),
               evictable: VecDeque::new(), next_page_id: 0, disk: Disk::default() }
    }

    fn new_page(&mut self) -> PageId { self.next_page_id += 1; self.next_page_id - 1 }      // an id, no frame yet

    fn fetch_page(&mut self, id: PageId) -> Option<FrameId> {
        if let Some(&f) = self.table.get(&id) {                                 // hit: pin it, it is no longer evictable
            self.meta[f].pin_count += 1;
            self.evictable.retain(|&x| x != f);
            return Some(f);
        }
        let f = match self.free.pop() {                                         // miss: a free frame, else evict one
            Some(f) => f,
            None => {
                let f = self.evictable.pop_front()?;                            // every frame pinned: None, nothing changed
                let old = self.meta[f].page_id.take().unwrap();
                if self.meta[f].dirty { self.disk.write(old, self.frames[f]); } // write back BEFORE reading over it
                self.table.remove(&old);
                f
            }
        };
        self.frames[f] = self.disk.read(id);
        self.meta[f] = Meta { page_id: Some(id), pin_count: 1, dirty: false };
        self.table.insert(id, f);
        Some(f)
    }

    fn unpin_page(&mut self, id: PageId, dirty: bool) -> bool {
        let Some(&f) = self.table.get(&id) else { return false };
        if self.meta[f].pin_count == 0 { return false; }
        self.meta[f].pin_count -= 1;
        self.meta[f].dirty |= dirty;
        if self.meta[f].pin_count == 0 { self.evictable.push_back(f); }
        true
    }

    fn flush_page(&mut self, id: PageId) -> bool {
        let Some(&f) = self.table.get(&id) else { return false };
        self.disk.write(id, self.frames[f]);                                    // regardless of the dirty flag
        self.meta[f].dirty = false;
        true
    }

    fn delete_page(&mut self, id: PageId) -> bool {
        if let Some(&f) = self.table.get(&id) {
            if self.meta[f].pin_count > 0 { return false; }
            self.table.remove(&id);
            self.evictable.retain(|&x| x != f);
            self.meta[f] = Meta::default();
            self.free.push(f);
        }
        self.disk.pages.remove(&id);
        true
    }
}

#[test]
fn a_page_goes_to_disk_and_comes_back() {
    let mut p = Pool::new(2);
    let (a, b, c) = (p.new_page(), p.new_page(), p.new_page());
    let fa = p.fetch_page(a).unwrap();
    p.frames[fa][0] = 42;
    p.unpin_page(a, true);                                  // modified, no longer in use
    p.fetch_page(b).unwrap();
    assert!(p.fetch_page(c).is_some());                     // pool full: evicts a (the only evictable), writing it back
    assert_eq!((p.disk.writes, p.table.contains_key(&a)), (1, false));
    assert!(p.fetch_page(a).is_none(), "b and c are pinned: nothing can be evicted");
    p.unpin_page(b, false);
    let fa2 = p.fetch_page(a).unwrap();                     // evicts b (clean: no write), reads a back
    assert_eq!(p.frames[fa2][0], 42);
    assert_eq!(p.disk.writes, 1, "a clean eviction writes nothing");
}

#[test]
fn pins_count_flush_ignores_dirty_and_delete_refuses_pinned() {
    let mut p = Pool::new(2);
    let a = p.new_page();
    let f = p.fetch_page(a).unwrap();
    assert_eq!(p.fetch_page(a), Some(f));                   // a hit: same frame, second pin
    assert_eq!(p.meta[f].pin_count, 2);
    p.unpin_page(a, false);
    assert!(p.evictable.is_empty(), "one pin left: still not evictable");
    assert!(!p.delete_page(a), "pinned pages cannot be deleted");
    p.unpin_page(a, false);
    assert_eq!(p.evictable.len(), 1);
    assert!(p.flush_page(a));                               // clean page, flushed anyway
    assert_eq!(p.disk.writes, 1);
    assert!(p.delete_page(a));
    assert_eq!((p.free.len(), p.table.len()), (2, 0));
}
```

### In the exercises

- **1f-01 to 1f-03:** the struct above is the shape: `RwLock`-wrapped frames, a page table, a free list, per-frame metadata and a replacer behind one lock. The first test above is the trace to match, including "all pinned returns `None`"; the I/O counts are the invariant (a clean eviction writes nothing, a dirty one writes once, `flush_page` writes whatever the flag says).

### Where it is used

- **Every disk-based database**: PostgreSQL's `shared_buffers` (buffer descriptors with a refcount and dirty flag, a hash table from tag to buffer), MySQL InnoDB's buffer pool, SQLite's pager cache (`PCache`).
- **Operating systems**: the page cache is a buffer pool whose "page table" is the file's radix tree, with pins as page references and a dirty bit written back by flusher threads.
- **Application caches with write-back**: any cache that tracks `dirty` and must write before reusing an entry has the same shape, from a filesystem's block cache to an LSM tree's memtable flush.

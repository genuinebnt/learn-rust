---
title: Slot allocation, free lists and the invariant you must not break
summary: Why a page id is not an offset, how the page table and free list partition the slots, why doubling is cheap, and how to make an I/O error leave a consistent structure.
minutes: 10
---
The disk manager's second job is the first place in the course where the code has an **invariant** to protect instead of a function to compute. Most of the bugs you will chase in the next two projects are invariant bugs, so it is worth looking at this one carefully while it is small.

## Why a page id is not an offset

Everything above the disk manager names pages by `PageId`: an integer handed out by the buffer pool, increasing, never reused. Everything below it names *places in a file*. Keeping the two apart costs one hash map and buys three things:

- **Reuse.** Deleting a page frees its place for a later page, without renumbering anyone.
- **Freedom of layout.** The file may later be compacted, split into several files or striped without any page id changing.
- **Cheap deletion.** Removing a page is "forget the mapping, remember the slot": no data moves.

This is the same idea as a virtual-memory page table, one level down: virtual page → physical frame there, page id → file slot here. BusTub's `pages_` map and `free_slots_` list are exactly that, and the reference stores slot *numbers* where BusTub stores byte offsets; the arithmetic in `slot_offset` is the only place the two meet.

## Where a slot can be

Let `num_slots` be the number of slots ever handed out. Every slot below it is in exactly one of two places:

- **Live**: it is a value in the page table `pages: HashMap<PageId, usize>`.
- **Free**: it is an element of `free_slots: Vec<usize>`.

That is the invariant: *the live and free slots are disjoint, and together they are exactly `0..num_slots`.* Three methods move slots between the states, and nothing else may:

| operation | takes a slot from | puts it in |
|---|---|---|
| `allocate_slot`, free list non-empty | `free_slots` | (caller puts it in `pages`) |
| `allocate_slot`, free list empty | the fresh end (`num_slots += 1`) | (caller puts it in `pages`) |
| `delete_page` | `pages` | `free_slots` |

A slot that is in *neither* place is a **leak**: the file grows and nothing will ever use that hole. A slot in *both* is worse: two pages share a place and overwrite each other. Neither fails a simple test, and both are found by checking the invariant, so write the check once and use it:

```rust
#[cfg(debug_assertions)]
fn check(&self) {
    let mut seen = vec![false; self.num_slots];
    for &s in self.pages.values().chain(self.free_slots.iter()) {
        assert!(s < self.num_slots, "slot {s} was never handed out");
        assert!(!seen[s], "slot {s} is both live and free, or live twice");
        seen[s] = true;
    }
    assert!(seen.iter().all(|&b| b), "a slot is neither live nor free: leaked");
}
```

Call it at the end of every method that changes `pages`, `free_slots` or `num_slots`. In a release build it costs nothing because it is not compiled.

## Free-list policy

BusTub reuses the most recently freed slot, which is a stack (`Vec::pop`). The alternatives are all legitimate:

| policy | cost | what you get |
|---|---|---|
| stack (LIFO), the reference | O(1) | the hot, recently-used slot is reused: good for caches |
| queue (FIFO) | O(1) | slots age before reuse: gentler on flash wear and on stale-reader bugs |
| lowest-slot-first (a `BTreeSet`) | O(log n) | the file stays dense at the front, so it can be truncated |
| bitmap | O(n) scan, O(1) amortised with a hint | compact, and the on-disk form most real engines use |

None of them changes behaviour the tests can see. They change *fragmentation*, which is why real systems care and why this one does not yet.

> [!NOTE] Slots are reused, ids are not
> After `delete_page(p)`, the page id `p` stays dead: the table forgets it, and reading it gives zeros. The *slot* goes back to the free list and will hold some other page id. Reusing slots is invisible to callers; reusing ids would not be.

## Growing the file: why doubling

A fresh slot beyond `page_capacity` forces the file to grow. Growing by one page each time costs one `set_len` per allocation: `n` allocations, `n` system calls. Doubling costs `⌈log₂(n/c)⌉` calls for `n` allocations from an initial capacity `c`, because the total work is the geometric series `c + 2c + 4c + … ≤ 2n`: that is the usual *amortised O(1)* argument for `Vec::push`, applied to a file. And because a grown file is sparse, doubling costs address space, not disk blocks.

BusTub also keeps **one spare page** beyond the capacity (`file_size_for(capacity) = (capacity + 1) · P`). Treat it as a documented convention of this file format, not a law: the tests check it because the original does.

## One latch, one critical section per decision

The page table, the free list, the counters and the capacity are all shared mutable state, and every operation reads *and then writes* them. The decision "have I seen this page?" and the action "give it a slot" must be **one critical section**:

```rust
let mut io = self.db_io.lock().unwrap();
let slot = match io.pages.get(&page_id) {
    Some(&slot) => slot,                       // known page: overwrite in place
    None => {
        let slot = io.allocate_slot()?;        // unknown page: take a slot…
        io.pages.insert(page_id, slot);        // …and record it, still holding the lock
        slot
    }
};
write_slot(&io.file, slot, data)?;
```

If the lock were released between `get` and `insert`, two threads writing the same new page would both take a slot, the second `insert` would replace the first, and the first slot would be leaked. Putting the file *inside* the same `Mutex` as the bookkeeping (`DbIo`) also means there is exactly one lock in the whole module, so there is no lock ordering to get wrong. The cost is that I/O is serialised too; BusTub accepts that with its single `db_io_latch_`, because the disk is the bottleneck anyway and the layer above (the disk scheduler) is what provides parallelism.

An `RwLock` is tempting because `read_page` only *reads* the table. Resist it until a measurement says so: it saves nothing while writers hold the lock across disk I/O, and it makes the "one decision, one critical section" rule easier to break.

## What an error leaves behind

The growth step has two updates and one fallible call:

```rust
self.page_capacity *= 2;                                   // bookkeeping
self.file.set_len(file_size_for(self.page_capacity))?;     // the syscall that can fail
```

If `set_len` fails, the structure now *claims* room the file does not have. The general rule: **do the fallible step first, or be able to undo the bookkeeping**. Either of these is fine, and you should pick one and be able to say why:

```rust
// fallible first
let new_capacity = self.page_capacity * 2;
self.file.set_len(file_size_for(new_capacity))?;
self.page_capacity = new_capacity;
```

The same question applies to `num_slots += 1` before the growth: if growth fails, the slot number was consumed but never used. Decide whether that is a leak you accept (and document), or put the increment after the success. Rust helps here: `?` returns early, so the code after it only runs on success, and "everything after the `?`" is a natural place for the infallible updates.

> [!WHY] Why this matters later
> The buffer pool in project 1 has the same shape (a table plus a free list, protected by one latch), the B+ tree has it with page ids, and the lock manager in project 4 has it with lock requests. If you learn to name the invariant and write the checker now, every later stage gets a debugging tool you have already built.

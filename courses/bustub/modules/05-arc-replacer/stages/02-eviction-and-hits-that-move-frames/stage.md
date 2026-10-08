Two operations make the lists move. **Eviction** takes the oldest *evictable* frame from `mru` or `mfu` and turns its page into a ghost on the matching ghost list. A **hit** on a live frame moves it to the newest end of `mfu`: it has now been seen at least twice, so it belongs with the frequently used pages.

The delicate part is the interaction with *pinned* frames: the oldest frame in a list may not be evictable, so eviction walks the list from the old end and skips the pinned ones without disturbing their order.

## Part 1 · evict: take the oldest evictable frame, leave a ghost

**Where this fits.** Evicting is where ghosts are born.

### The task

Implement `evict()` in `src/buffer/arc_replacer.rs` for the case `p = 0` (so far nothing raises it): take the **oldest evictable** frame of `mru` (skipping pinned frames), and if `mru` has none, of `mfu`. Remove its live entry, lower `curr_size`, and **remember its page id as a ghost** at the newest end of `mru_ghost` (for a victim from `mru`) or `mfu_ghost` (from `mfu`). Return the frame; `None` if nothing is evictable. The helpers `oldest_evictable(status)` and `push_ghost` are suggestions.

### Tests

- Frames 1..4 evictable: victims 1, 2, 3, 4, then `None`; size follows. A pinned frame is skipped; a failed evict changes nothing.
- An evicted frame can be reused for another page.

### Syntax and methods

```rust
list.iter().copied().find(|frame| self.alive[frame].evictable)   // IndexList::iter, then the first evictable one
let alive = self.alive.remove(&frame).expect("a listed frame is alive");
self.mru.remove(alive.handle);
self.ghost.insert(page_id, Ghost { status: ArcStatus::MruGhost, handle: self.mru_ghost.push_back(page_id) });
for status in [ArcStatus::Mru, ArcStatus::Mfu] { /* arrays implement IntoIterator by value */ }
```

### Notes

Eviction is the one place where a **live frame becomes a memory of a page**. Keep the three updates together (list, map, ghost) so that a frame is never in two places. The `self.alive[frame]` index panics on a missing key, which is right here: the lists and the map are supposed to agree, and a disagreement is a bug to find loudly.

### In BusTub

"Find a frame to evict ... the evicted page's id goes to the corresponding ghost list: mru → mru_ghost, mfu → mfu_ghost ... Successful eviction should decrement the size of the replacer."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `for (auto it = mru_.rbegin(); it != mru_.rend(); ++it) { if (alive_map_[*it]->evictable_) {...} }` (reverse iterators; `operator[]` silently inserts) | `iter().find(..)` and `self.alive[..]` (panics if absent instead of inserting) |
| erase while iterating: iterator invalidation if you continue after `erase` | find first, then remove; the borrow checker rejects mutating a list you are iterating |
| `alive_map_.erase(frame_id)` | `alive.remove(&frame)` returns the removed value |

### Learn more
- [`Iterator::find`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.find) · [`Iterator::copied`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.copied) · The Rust Book: [`match` and enums](https://doc.rust-lang.org/book/ch06-02-match.html)

## Part 2 · A hit on a live frame moves it to mfu

**Where this fits.** The "frequently used" half of the policy.

### The task

In `record_access` (`src/buffer/arc_replacer.rs`), before treating a call as a new page: if `frame` is already **live**, this is a hit. A frame on `mru` moves to the newest end of `mfu`; a frame already on `mfu` moves to its newest end. Its evictable flag is unchanged.

### Tests

- Frames 1..4 evictable, then a hit on frame 1: victims come out 2, 3, 4, 1 (mfu is evicted last while `p = 0`). Hits within `mfu` refresh the order: after hits on 1, 2, 1, the mfu order is 2 then 1.
- A hit keeps the flag. The start of BusTub's `SampleTest`.

### Syntax and methods

```rust
if let Some(alive) = self.alive.get(&frame) {
    let (status, handle) = (alive.status, alive.handle);      // copy out what you need, so the borrow of `self.alive` ends
    ...
    return;
}
self.mfu.move_to_back(handle);   // O(1), keeps the handle valid
```

### Notes

The borrow checker will complain if you keep `alive` (a reference into `self.alive`) while calling `self.mru.remove(..)`: they are different fields, which Rust does allow, *but* as soon as a method call takes `&mut self` it borrows everything. Copy the two small values out (`status`, `handle` are `Copy`) and the problem goes away. Use direct field access (`self.mru.remove`) over `&mut self` helper methods inside such blocks.

### In BusTub

"Case I: the page is in mru or mfu (a hit): move it to the front of mfu."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `mru_.erase(it); mfu_.push_front(frame_id);` with a stored iterator `it` | `self.mru.remove(handle); self.mfu.push_back(frame)` (a new handle: store it) |
| `mfu_.splice(mfu_.begin(), mfu_, it)` for a move within a list | `move_to_back(handle)` |
| keeping `status` as a field inside a `shared_ptr<FrameStatus>` that both lists refer to | the status and handle live in the map entry; update them together |

### Learn more
- The Rust Book: [references and borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html) · [struct field borrows](https://doc.rust-lang.org/nomicon/borrow-splitting.html)

## Performance

A hit is O(1): one handle lookup, one `remove` from `mru` (or `move_to_back` in `mfu`) and one `push_back`. Eviction is O(1) when the oldest frame is evictable and **O(p)** where `p` is the number of pinned frames at the old end, because it scans from the front past pinned frames. In a buffer pool where most frames are unpinned that is a couple of steps; with many pinned frames at the front it degrades, which is a known limitation of this design (a separate list of evictable frames would fix it at the cost of more bookkeeping).

Creating a ghost allocates one list node and one map entry: no page data is touched.

**Measure it.** Pin 90% of 1 000 frames in a way that leaves them oldest, then time 100 000 `evict` + `record_access` rounds and compare with the all-unpinned case to see the scan cost.

## Hints

### Which list do you evict from first?

The rule compares `|mru|` with the target size `p`: if `mru` holds at least `p` frames, evict from `mru` first; otherwise from `mfu` first; and if the preferred list has **no evictable frame**, fall back to the other. In this stage `p` is still 0, so the preferred list is always `mru`: but write the code with `p` already in the condition, because the next stage turns it on.

### Skipping pinned frames without reordering them

Walk the list from the oldest end with an iterator and take the first frame whose `evictable` flag is set; do *not* rotate pinned frames to the back to get them out of the way, which would change the order they later age in. Then remove that frame through its handle (so the removal is O(1)) and create the ghost *from the page id you stored*, since the frame no longer knows it.

### A hit must update three things

Moving a frame from `mru` to `mfu` changes (1) which list holds it, (2) its `handle` (the new list gave it a new one), and (3) its `status`. Forget the handle and the next `remove` removes the wrong node or none; forget the status and eviction later looks in the wrong list. A hit in `mfu` only needs `move_to_back`. After either, the evictable flag and `curr_size` must be unchanged.
